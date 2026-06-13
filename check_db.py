import sqlite3
import os

# Check both possible locations
db_files = [
    'data/facturas.db',
    'data/facturas_ganatodo.sqlite'
]

for db_file in db_files:
    if os.path.exists(db_file):
        print(f'\n{"="*60}')
        print(f'Checking: {db_file}')
        print(f'{"="*60}')
        
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row

        # Check tables
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print(f'\nTables: {tables}')

        # Schema version
        if 'meta' in tables:
            version = conn.execute('SELECT value FROM meta WHERE key="schema_version"').fetchone()
            print(f'Schema version: {version[0] if version else "NOT SET"}')

        # Check facturas table
        if 'facturas' in tables:
            cols = [r[1] for r in conn.execute('PRAGMA table_info(facturas)').fetchall()]
            print(f'\nFacturas columns ({len(cols)}): {cols[-5:]}')  # Last 5 columns
            print(f'comprobante_path exists: {"comprobante_path" in cols}')
            
            # Check for paid invoices
            rows = conn.execute('SELECT id, numero_factura, estado, comprobante_path FROM facturas WHERE estado="Pagada" LIMIT 5').fetchall()
            print(f'\nPaid invoices ({len(rows)}):')
            for row in rows:
                print(f'  ID {row[0]}: {row[1]} | Comprobante: {row[3] or "(None)"}')
        
        conn.close()
    else:
        print(f'\n{db_file}: NOT FOUND')
