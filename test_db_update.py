import sqlite3
import os

db_path = 'data/facturas_ganatodo.sqlite'

print(f"Testing direct UPDATE on {db_path}\n")

# Test: actualizar una factura
test_id = 13  # FVE 11109
test_path = r"data\comprobantes_pago\test_comprobante.pdf"

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

# Antes
before = conn.execute('SELECT id, numero_factura, comprobante_path FROM facturas WHERE id = ?', (test_id,)).fetchone()
print(f"BEFORE: ID {before[0]} | {before[1]} | comprobante_path = {before[2]!r}")

# Ejecutar UPDATE
cursor = conn.execute(
    "UPDATE facturas SET comprobante_path = ? WHERE id = ?",
    (test_path, test_id)
)
conn.commit()  # IMPORTANTE: commit explícito
print(f"\nUPDATE executed, rows affected: {cursor.rowcount}")

# Después
after = conn.execute('SELECT id, numero_factura, comprobante_path FROM facturas WHERE id = ?', (test_id,)).fetchone()
print(f"AFTER:  ID {after[0]} | {after[1]} | comprobante_path = {after[2]!r}")

conn.close()

print("\n✅ Test complete!")
