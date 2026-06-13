"""Test rápido para diagnosticar problema de schema"""
import sys
sys.path.insert(0, r'C:\Users\Usuario\Desktop\Facturas_GanaTodo_v4')

from app.model.database import Database
import tempfile
import os

# Crear BD temporal
temp_dir = tempfile.mkdtemp()
db_path = os.path.join(temp_dir, "test_diag.db")

print(f"Creando BD en: {db_path}")

db = Database(db_path)
db.initialize()

# Verificar schema
with db.connect() as conn:
    # Ver versión
    row = conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
    print(f"Schema version: {row['value'] if row else 'N/A'}")
    
    # Ver columnas de facturas
    cols = conn.execute("PRAGMA table_info(facturas)").fetchall()
    print(f"\nColumnas en tabla facturas:")
    for col in cols:
        print(f"  - {col['name']} ({col['type']})")
    
    # Verificar si existe pdf_path
    col_names = [c['name'] for c in cols]
    print(f"\n¿Existe pdf_path? {'SÍ' if 'pdf_path' in col_names else 'NO'}")

# Cleanup
import shutil
shutil.rmtree(temp_dir, ignore_errors=True)

print("\n✅ Diagnóstico completado")
