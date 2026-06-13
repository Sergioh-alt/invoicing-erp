"""Test rápido del sistema de auditoría"""
from app.model.database import Database
import os

# Crear BD de prueba
test_db_path = os.path.join(os.getcwd(), 'test_audit.db')
db = Database(test_db_path)
db.initialize()

# Obtener versión de schema
with db.connect() as conn:
    version = conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()["value"]
    print(f"✅ BD inicializada, schema v{version}")

# Probar logging de auditoría
db.log_audit('TEST_CREATE', 1, 'admin', 'Prueba de creación')
db.log_audit('TEST_UPDATE', 1, 'admin', 'Prueba de actualización')
db.log_audit('TEST_DELETE', 2, 'admin', 'Prueba de eliminación')

# Obtener logs
logs = db.get_audit_logs()
print(f"\n✅ Audit logs registrados: {len(logs)} entradas")

for log in logs:
    print(f"  - {log['timestamp']}: {log['operation']} en factura {log['factura_id']} por {log['user']}")

# Estadísticas
stats = db.get_audit_stats()
print(f"\n✅ Estadísticas:")
print(f"  Total operaciones: {stats['total_operations']}")
print(f"  Últimas 24h: {stats['operations_24h']}")
print(f"  Por tipo: {stats['by_operation']}")

print("\n✅ Sistema de auditoría funcionando correctamente!")

# Limpiar
import os
os.remove('test_audit.db')
print("✅ BD de prueba eliminada")
