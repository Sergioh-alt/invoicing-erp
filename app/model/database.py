import os
import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

SCHEMA_VERSION = 6

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("""
            CREATE TABLE IF NOT EXISTS meta(
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS facturas(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_factura TEXT NOT NULL,
                proveedor TEXT,
                valor REAL,
                notas TEXT,
                fecha_vencimiento TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'Pendiente',

                ultimo_aviso TEXT,
                ultimo_aviso_tipo TEXT,

                aviso_h1_ts TEXT,
                aviso_h2_ts TEXT,
                aviso_h3_ts TEXT,

                snooze_until TEXT,

                hora_alerta_1 TEXT,
                hora_alerta_2 TEXT,
                hora_alerta_3 TEXT,
                
                pdf_path TEXT,
                comprobante_path TEXT
            );
            """)
            # Índices para optimización de rendimiento
            conn.execute("CREATE INDEX IF NOT EXISTS idx_facturas_estado ON facturas(estado);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_facturas_venc ON facturas(fecha_vencimiento);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_facturas_proveedor ON facturas(proveedor);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_facturas_numero ON facturas(numero_factura);")
            
            # Tabla de auditoría para tracking de operaciones
            conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                factura_id INTEGER,
                user TEXT,
                details TEXT,
                ip_address TEXT
            );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_factura ON audit_log(factura_id);")

            row = conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
            if row is None:
                conn.execute("INSERT INTO meta(key,value) VALUES('schema_version',?)", (str(SCHEMA_VERSION),))
            else:
                current = int(row["value"])
                if current < SCHEMA_VERSION:
                    self._migrate(conn, current)
                    conn.execute("UPDATE meta SET value=? WHERE key='schema_version'", (str(SCHEMA_VERSION),))

    def _migrate(self, conn: sqlite3.Connection, current: int) -> None:
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(facturas)").fetchall()]
        def add(col, ddl):
            if col not in cols:
                conn.execute(ddl)

        if current < 2:
            add("ultimo_aviso_tipo", "ALTER TABLE facturas ADD COLUMN ultimo_aviso_tipo TEXT;")
        if current < 3:
            add("aviso_h1_ts", "ALTER TABLE facturas ADD COLUMN aviso_h1_ts TEXT;")
            add("aviso_h2_ts", "ALTER TABLE facturas ADD COLUMN aviso_h2_ts TEXT;")
            add("aviso_h3_ts", "ALTER TABLE facturas ADD COLUMN aviso_h3_ts TEXT;")
            add("snooze_until", "ALTER TABLE facturas ADD COLUMN snooze_until TEXT;")
        if current < 4:
            add("pdf_path", "ALTER TABLE facturas ADD COLUMN pdf_path TEXT;")
            add("hora_alerta_1", "ALTER TABLE facturas ADD COLUMN hora_alerta_1 TEXT;")
            add("hora_alerta_2", "ALTER TABLE facturas ADD COLUMN hora_alerta_2 TEXT;")
            add("hora_alerta_3", "ALTER TABLE facturas ADD COLUMN hora_alerta_3 TEXT;")
        
        if current < 5:
            # Crear tabla audit_log si no existe (migración v5)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                factura_id INTEGER,
                user TEXT,
                details TEXT,
                ip_address TEXT
            );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_factura ON audit_log(factura_id);")
        
        if current < 6:
            # Agregar columna para comprobantes de pago (migración v6)
            add("comprobante_path", "ALTER TABLE facturas ADD COLUMN comprobante_path TEXT;")
        
        conn.execute("UPDATE meta SET value=? WHERE key='schema_version'", (str(SCHEMA_VERSION),))

    # ==================== MÉTODOS DE VALIDACIÓN ====================
    
    def check_duplicate_invoice(self, numero_factura: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si ya existe una factura con el mismo número.
        
        Args:
            numero_factura: Número de factura a verificar
            exclude_id: ID de factura a excluir (para edición)
            
        Returns:
            True si existe duplicado, False si no
        """
        with self.connect() as conn:
            if exclude_id:
                result = conn.execute(
                    "SELECT COUNT(*) as count FROM facturas WHERE numero_factura = ? AND id != ?",
                    (numero_factura.strip(), exclude_id)
                ).fetchone()
            else:
                result = conn.execute(
                    "SELECT COUNT(*) as count FROM facturas WHERE numero_factura = ?",
                    (numero_factura.strip(),)
                ).fetchone()
            
            return result["count"] > 0

    def add_factura(self, numero_factura: str, proveedor: str, valor: Optional[float], notas: str,
                    fecha_vencimiento_iso: str, hora1: str, hora2: str, hora3: str, 
                    pdf_path: Optional[str] = None) -> int:
        with self.connect() as conn:
            cur = conn.execute("""
                INSERT INTO facturas(
                    numero_factura, proveedor, valor, notas, fecha_vencimiento, estado,
                    ultimo_aviso, ultimo_aviso_tipo, aviso_h1_ts, aviso_h2_ts, aviso_h3_ts, snooze_until,
                    hora_alerta_1, hora_alerta_2, hora_alerta_3, pdf_path
                ) VALUES(?,?,?,?,?,'Pendiente',NULL,NULL,NULL,NULL,NULL,NULL,?,?,?,?)
            """, (numero_factura.strip(),
                  proveedor.strip() if proveedor else None,
                  valor,
                  notas.strip() if notas else None,
                  fecha_vencimiento_iso,
                  hora1, hora2, hora3, pdf_path))
            return int(cur.lastrowid)

    def update_factura(self, factura_id: int, numero_factura: str, proveedor: str, valor: Optional[float],
                       notas: str, fecha_vencimiento_iso: str, estado: str, hora1: str, hora2: str, hora3: str,
                       pdf_path: Optional[str] = None) -> None:
        with self.connect() as conn:
            conn.execute("""
                UPDATE facturas
                SET numero_factura=?, proveedor=?, valor=?, notas=?, fecha_vencimiento=?, estado=?,
                    hora_alerta_1=?, hora_alerta_2=?, hora_alerta_3=?, pdf_path=?
                WHERE id=?
            """, (numero_factura.strip(),
                  proveedor.strip() if proveedor else None,
                  valor,
                  notas.strip() if notas else None,
                  fecha_vencimiento_iso,
                  estado,
                  hora1, hora2, hora3, pdf_path,
                  factura_id))

    def delete_factura(self, factura_id: int) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM facturas WHERE id=?", (factura_id,))

    def mark_pagada(self, factura_id: int) -> None:
        with self.connect() as conn:
            conn.execute("UPDATE facturas SET estado='Pagada' WHERE id=?", (factura_id,))

    def set_last_day_alert(self, factura_id: int, when_iso: str, alert_code: str) -> None:
        with self.connect() as conn:
            conn.execute("UPDATE facturas SET ultimo_aviso=?, ultimo_aviso_tipo=? WHERE id=?", (when_iso, alert_code, factura_id))

    def set_day0_slot_fired(self, factura_id: int, slot: int, when_iso: str) -> None:
        col = {1: "aviso_h1_ts", 2: "aviso_h2_ts", 3: "aviso_h3_ts"}[slot]
        with self.connect() as conn:
            conn.execute(f"UPDATE facturas SET {col}=? WHERE id=?", (when_iso, factura_id))

    def set_snooze_until(self, factura_id: int, until_iso: str) -> None:
        with self.connect() as conn:
            conn.execute("UPDATE facturas SET snooze_until=? WHERE id=?", (until_iso, factura_id))

    def clear_snooze(self, factura_id: int) -> None:
        with self.connect() as conn:
            conn.execute("UPDATE facturas SET snooze_until=NULL WHERE id=?", (factura_id,))

    def list_facturas(self, status_filter: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        q = "SELECT * FROM facturas"
        params = []
        where = []
        if status_filter and status_filter != "Todas":
            where.append("estado=?")
            params.append(status_filter)
        if search:
            where.append("(numero_factura LIKE ? OR proveedor LIKE ? OR notas LIKE ?)")
            s = f"%{search}%"
            params.extend([s, s, s])
        if where:
            q += " WHERE " + " AND ".join(where)
        q += " ORDER BY datetime(fecha_vencimiento) ASC;"
        with self.connect() as conn:
            rows = conn.execute(q, params).fetchall()
            return [dict(r) for r in rows]
    
    # ==================== MÉTODOS DE AUDITORÍA ====================
    
    def log_audit(self, operation: str, factura_id: Optional[int] = None, 
                  user: str = "system", details: str = "", ip_address: str = "") -> None:
        """
        Registra una operación en el log de auditoría.
        
        Args:
            operation: Tipo de operación (CREATE, UPDATE, DELETE, EXPORT, etc.)
            factura_id: ID de la factura afectada (opcional)
            user: Usuario que realizó la operación
            details: Detalles adicionales de la operación
            ip_address: Dirección IP del usuario (opcional)
        """
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        
        with self.connect() as conn:
            conn.execute("""
                INSERT INTO audit_log (timestamp, operation, factura_id, user, details, ip_address)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, operation, factura_id, user, details, ip_address))
    
    def get_audit_logs(self, limit: int = 100, factura_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtiene logs de auditoría.
        
        Args:
            limit: Número máximo de registros a retornar
            factura_id: Filtrar por ID de factura específica (opcional)
            
        Returns:
            Lista de registros de auditoría
        """
        with self.connect() as conn:
            if factura_id:
                rows = conn.execute("""
                    SELECT * FROM audit_log 
                    WHERE factura_id = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (factura_id, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM audit_log 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,)).fetchall()
            
            return [dict(r) for r in rows]
    
    def get_audit_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del log de auditoría.
        
        Returns:
            Dict con estadísticas de operaciones
        """
        with self.connect() as conn:
            total = conn.execute("SELECT COUNT(*) as count FROM audit_log").fetchone()["count"]
            
            by_operation = conn.execute("""
                SELECT operation, COUNT(*) as count 
                FROM audit_log 
                GROUP BY operation 
                ORDER BY count DESC
            """).fetchall()
            
            recent_24h = conn.execute("""
                SELECT COUNT(*) as count FROM audit_log 
                WHERE datetime(timestamp) > datetime('now', '-1 day')
            """).fetchone()["count"]
            
            return {
                "total_operations": total,
                "operations_24h": recent_24h,
                "by_operation": {r["operation"]: r["count"] for r in by_operation}
            }
