"""Tests for audit log functionality."""
import pytest
from datetime import datetime
from app.model.database import Database
import os
import tempfile


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = Database(db_path)
    db.initialize()
    
    yield db
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


def test_log_audit_basic(test_db):
    """Test basic audit logging."""
    test_db.log_audit("CREATE", factura_id=1, user="test_user", details="Test creation")
    
    logs = test_db.get_audit_logs(limit=10)
    
    assert len(logs) == 1
    assert logs[0]['operation'] == "CREATE"
    assert logs[0]['factura_id'] == 1
    assert logs[0]['user'] == "test_user"
    assert logs[0]['details'] == "Test creation"
    assert 'timestamp' in logs[0]


def test_log_multiple_operations(test_db):
    """Test logging multiple operations."""
    test_db.log_audit("CREATE", factura_id=1, user="user1", details="Created invoice 1")
    test_db.log_audit("UPDATE", factura_id=1, user="user1", details="Updated invoice 1")
    test_db.log_audit("DELETE", factura_id=1, user="user2", details="Deleted invoice 1")
    
    logs = test_db.get_audit_logs(limit=10)
    
    assert len(logs) == 3
    # Should be in reverse chronological order (newest first)
    assert logs[0]['operation'] == "DELETE"
    assert logs[1]['operation'] == "UPDATE"
    assert logs[2]['operation'] == "CREATE"


def test_get_audit_logs_with_factura_filter(test_db):
    """Test filtering audit logs by factura_id."""
    test_db.log_audit("CREATE", factura_id=1, user="user1", details="Invoice 1")
    test_db.log_audit("CREATE", factura_id=2, user="user1", details="Invoice 2")
    test_db.log_audit("UPDATE", factura_id=1, user="user1", details="Updated invoice 1")
    
    logs = test_db.get_audit_logs(factura_id=1)
    
    assert len(logs) == 2
    assert all(log['factura_id'] == 1 for log in logs)


def test_get_audit_logs_limit(test_db):
    """Test limit parameter in get_audit_logs."""
    # Create 10 audit entries
    for i in range(10):
        test_db.log_audit("CREATE", factura_id=i, user="user1", details=f"Invoice {i}")
    
    logs = test_db.get_audit_logs(limit=5)
    
    assert len(logs) == 5


def test_audit_stats_empty(test_db):
    """Test audit stats with no entries."""
    stats = test_db.get_audit_stats()
    
    assert stats['total_operations'] == 0
    assert stats['operations_24h'] == 0
    assert stats['by_operation'] == {}


def test_audit_stats_with_data(test_db):
    """Test audit stats with data."""
    test_db.log_audit("CREATE", factura_id=1, user="user1")
    test_db.log_audit("CREATE", factura_id=2, user="user1")
    test_db.log_audit("UPDATE", factura_id=1, user="user1")
    test_db.log_audit("DELETE", factura_id=3, user="user2")
    
    stats = test_db.get_audit_stats()
    
    assert stats['total_operations'] == 4
    assert stats['operations_24h'] == 4  # All recent
    assert stats['by_operation']['CREATE'] == 2
    assert stats['by_operation']['UPDATE'] == 1
    assert stats['by_operation']['DELETE'] == 1


def test_audit_log_without_factura_id(test_db):
    """Test audit logging without factura_id (system operations)."""
    test_db.log_audit("BACKUP", factura_id=None, user="system", details="Daily backup")
    
    logs = test_db.get_audit_logs(limit=10)
    
    assert len(logs) == 1
    assert logs[0]['operation'] == "BACKUP"
    assert logs[0]['factura_id'] is None
    assert logs[0]['user'] == "system"


def test_audit_log_with_ip_address(test_db):
    """Test audit logging with IP address."""
    test_db.log_audit("CREATE", factura_id=1, user="user1", details="Test", ip_address="192.168.1.1")
    
    logs = test_db.get_audit_logs(limit=1)
    
    assert logs[0]['ip_address'] == "192.168.1.1"


def test_audit_log_timestamp_format(test_db):
    """Test that timestamps are in correct ISO format."""
    test_db.log_audit("CREATE", factura_id=1, user="user1")
    
    logs = test_db.get_audit_logs(limit=1)
    timestamp_str = logs[0]['timestamp']
    
    # Should be parseable as ISO datetime
    parsed = datetime.fromisoformat(timestamp_str)
    assert isinstance(parsed, datetime)


def test_audit_integration_with_crud(test_db):
    """Test that CRUD operations are properly logged (integration test)."""
    # Add a factura
    factura_id = test_db.add_factura(
        "FAC-001", "Test Provider", 100.0, "Test notes",
        "2026-02-01T12:00:00", "09:00", "14:00", "18:00"
    )
    
    # Log the creation
    test_db.log_audit("CREATE", factura_id, "user", f"Created factura FAC-001")
    
    # Update it
    test_db.update_factura(
        factura_id, "FAC-001-UPDATED", "Test Provider", 150.0, "Updated notes",
        "2026-02-01T12:00:00", "Pendiente", "09:00", "14:00", "18:00"
    )
    
    # Log the update
    test_db.log_audit("UPDATE", factura_id, "user", "Updated factura")
    
    # Delete it
    test_db.delete_factura(factura_id)
    
    # Log the deletion
    test_db.log_audit("DELETE", factura_id, "user", "Deleted factura")
    
    # Verify all operations logged
    logs = test_db.get_audit_logs(factura_id=factura_id)
    
    assert len(logs) == 3
    operations = [log['operation'] for log in logs]
    assert "CREATE" in operations
    assert "UPDATE" in operations
    assert "DELETE" in operations
