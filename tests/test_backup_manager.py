"""Tests for BackupManager service."""
import pytest
import os
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from app.services.backup_manager import BackupManager


@pytest.fixture
def temp_db():
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        f.write("fake database content")
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def backup_dir():
    """Create a temporary backup directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    
    # Cleanup
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def test_backup_manager_init(temp_db, backup_dir):
    """Test BackupManager initialization."""
    manager = BackupManager(temp_db, backup_dir_path=backup_dir, keep_days=30)
    
    assert manager.db_path == Path(temp_db)
    assert manager.backup_dir == Path(backup_dir)
    assert manager.keep_days == 30
    assert manager.backup_dir.exists()


def test_create_manual_backup(temp_db, backup_dir):
    """Test creating a manual backup."""
    manager = BackupManager(temp_db, backup_dir_path=backup_dir)
    
    backup_path = manager.create_backup(auto=False)
    
    assert backup_path is not None
    assert os.path.exists(backup_path)
    assert backup_path.endswith('.zip')
    assert 'manual' in os.path.basename(backup_path)
    
    # Verify ZIP contains database file
    with zipfile.ZipFile(backup_path, 'r') as zipf:
        files = zipf.namelist()
        assert any('.db' in f for f in files)
        assert 'backup_info.txt' in files


def test_create_auto_backup(temp_db, backup_dir):
    """Test creating an automatic backup."""
    manager = BackupManager(temp_db, backup_dir_path=backup_dir)
    
    backup_path = manager.create_backup(auto=True)
    
    assert backup_path is not None
    assert 'auto' in os.path.basename(backup_path)


def test_list_backups(temp_db, backup_dir):
    """Test listing backups."""
    manager = BackupManager(temp_db, backup_dir_path=backup_dir)
    
    # Create some backups
    manager.create_backup(auto=False)
    manager.create_backup(auto=True)
    
    backups = manager.list_backups()
    
    assert len(backups) == 2
    assert all('name' in b for b in backups)
    assert all('type' in b for b in backups)
    assert all('date' in b for b in backups)
    assert all('size_kb' in b for b in backups)


def test_get_stats(temp_db, backup_dir):
    """Test getting backup statistics."""
    manager = BackupManager(temp_db, backup_dir_path=backup_dir)
    
    # Create backups
    manager.create_backup(auto=False)
    manager.create_backup(auto=True)
    
    stats = manager.get_stats()
    
    assert stats['total_backups'] == 2
    assert stats['automatic'] == 1
    assert stats['manual'] == 1
    assert 'total_size_mb' in stats
    assert 'newest' in stats
    assert 'oldest' in stats


def test_should_create_daily_backup(temp_db, backup_dir):
    """Test daily backup check logic."""
    manager = BackupManager(temp_db, backup_dir_path=backup_dir)
    
    # Should create backup if no backups exist
    assert manager.should_create_daily_backup() is True
    
    # Create an auto backup
    manager.create_backup(auto=True)
    
    # Should NOT create another backup immediately
    assert manager.should_create_daily_backup() is False


def test_cleanup_old_backups(temp_db, backup_dir):
    """Test cleanup of old backups."""
    manager = BackupManager(temp_db, backup_dir_path=backup_dir, keep_days=1)
    
    # Create a backup
    backup_path = manager.create_backup(auto=True)
    
    # Modify the file's timestamp to be 2 days old
    old_time = (datetime.now() - timedelta(days=2)).timestamp()
    os.utime(backup_path, (old_time, old_time))
    
    # Run cleanup
    deleted = manager.cleanup_old_backups()
    
    assert deleted == 1
    assert not os.path.exists(backup_path)


def test_restore_backup(temp_db, backup_dir):
    """Test restoring from a backup."""
    manager = BackupManager(temp_db, backup_dir_path=backup_dir)
    
    # Create a backup
    backup_path = manager.create_backup(auto=False)
    
    # Modify the original database
    with open(temp_db, 'w') as f:
        f.write("modified content")
    
    # Restore from backup
    result = manager.restore_backup(backup_path)
    
    assert result is True
    
    # Verify content was restored
    with open(temp_db, 'r') as f:
        content = f.read()
        assert content == "fake database content"


def test_backup_nonexistent_db():
    """Test backup creation fails gracefully for non-existent database."""
    with tempfile.TemporaryDirectory() as backup_dir:
        manager = BackupManager("nonexistent.db", backup_dir_path=backup_dir)
        
        backup_path = manager.create_backup(auto=False)
        
        assert backup_path is None  # Should return None for non-existent DB


def test_multiple_backups_ordering(temp_db, backup_dir):
    """Test that backups are returned in correct order (newest first)."""
    manager = BackupManager(temp_db, backup_dir_path=backup_dir)
    
    # Create multiple backups with small delays
    import time
    manager.create_backup(auto=False)
    time.sleep(0.1)
    manager.create_backup(auto=True)
    time.sleep(0.1)
    manager.create_backup(auto=False)
    
    backups = manager.list_backups()
    
    # Should be ordered by date, newest first
    assert len(backups) == 3
    dates = [b['date'] for b in backups]
    assert dates == sorted(dates, reverse=True)
