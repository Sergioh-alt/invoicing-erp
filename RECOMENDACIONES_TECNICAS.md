# 🔧 RECOMENDACIONES TÉCNICAS DETALLADAS

**Programa**: Facturas GanaTodo v5.0  
**Fecha**: 29 de enero de 2026  
**Tipo de documento**: Guía de mejoras técnicas  

---

## 📋 TABLA DE CONTENIDOS

1. [Bugs Críticos a Arreglar](#-bugs-críticos-a-arreglar)
2. [Refactorización de Código](#-refactorización-de-código)
3. [Optimizaciones de Rendimiento](#-optimizaciones-de-rendimiento)
4. [Mejoras en Base de Datos](#-mejoras-en-base-de-datos)
5. [Testing y Calidad](#-testing-y-calidad)
6. [Seguridad](#-seguridad)
7. [Configuración y Flexibilidad](#-configuración-y-flexibilidad)

---

## 🔴 BUGS CRÍTICOS A ARREGLAR

### 1. Persistencia de PDFs en Base de Datos

**Problema Actual**:
```python
# En ui_main.py (línea ~2100)
self._pdf_paths = {}  # Diccionario EN MEMORIA - se pierde al cerrar
```

**Solución**:

**Paso 1**: Actualizar `database.py` - método `add_factura`:
```python
def add_factura(self, numero_factura: str, proveedor: str, valor: Optional[float], 
                notas: str, fecha_vencimiento_iso: str, hora1: str, hora2: str, 
                hora3: str, pdf_path: Optional[str] = None) -> int:
    with self.connect() as conn:
        cur = conn.execute("""
            INSERT INTO facturas(
                numero_factura, proveedor, valor, notas, fecha_vencimiento, estado,
                ultimo_aviso, ultimo_aviso_tipo, aviso_h1_ts, aviso_h2_ts, aviso_h3_ts, snooze_until,
                hora_alerta_1, hora_alerta_2, hora_alerta_3, pdf_path  -- ← AGREGAR AQUÍ
            ) VALUES(?,?,?,?,?,'Pendiente',NULL,NULL,NULL,NULL,NULL,NULL,?,?,?,?)  -- ← +1 parámetro
        """, (numero_factura.strip(), proveedor.strip() if proveedor else None,
              valor, notas.strip() if notas else None, fecha_vencimiento_iso,
              hora1, hora2, hora3, pdf_path))  -- ← AGREGAR AQUÍ
        return int(cur.lastrowid)
```

**Paso 2**: Actualizar `database.py` - método `update_factura`:
```python
def update_factura(self, factura_id: int, numero_factura: str, proveedor: str, 
                   valor: Optional[float], notas: str, fecha_vencimiento_iso: str, 
                   estado: str, hora1: str, hora2: str, hora3: str, 
                   pdf_path: Optional[str] = None) -> None:  -- ← AGREGAR parámetro
    with self.connect() as conn:
        conn.execute("""
            UPDATE facturas
            SET numero_factura=?, proveedor=?, valor=?, notas=?, fecha_vencimiento=?, estado=?,
                hora_alerta_1=?, hora_alerta_2=?, hora_alerta_3=?, pdf_path=?  -- ← AGREGAR
            WHERE id=?
        """, (numero_factura.strip(), proveedor.strip() if proveedor else None,
              valor, notas.strip() if notas else None, fecha_vencimiento_iso, estado,
              hora1, hora2, hora3, pdf_path, factura_id))  -- ← AGREGAR
```

**Paso 3**: Actualizar `ui_main.py` - método `_dashboard_drop`:
```python
def _dashboard_drop(self, event: QtGui.QDropEvent):
    # ... código existente de extracción ...
    
    # ANTES de abrir el diálogo:
    payload["pdf_path"] = pdf_path  # Guardar ruta
    
    dialog = InvoiceDialogWithPDFPreview(..., data=payload)
    if dialog.exec() == QtWidgets.QDialog.Accepted:
        data = dialog.get_payload()
        # IMPORTANTE: Pasar pdf_path a add_factura
        new_id = self.db.add_factura(
            data["numero_factura"], data["proveedor"], data["valor"],
            data["notas"], data["fecha_vencimiento"],
            data["hora_alerta_1"], data["hora_alerta_2"], data["hora_alerta_3"],
            pdf_path=pdf_path  # ← AGREGAR ESTO
        )
```

**Paso 4**: Actualizar `refresh_table` para leer de BD:
```python
def refresh_table(self, fecha_filtro=None):
    # ... código existente ...
    
    for row in facturas:
        # ... código existente de columnas ...
        
        # Columna PDF (ahora desde BD)
        pdf_path = row.get("pdf_path")
        pdf_item = QtWidgets.QTableWidgetItem("Sí" if pdf_path else "No")
        if pdf_path:
            pdf_item.setForeground(QtGui.QColor("#10b981"))
            pdf_item.setFont(font_bold)
        else:
            pdf_item.setForeground(QtGui.QColor("#6b7280"))
        self.table.setItem(r, COL_PDF, pdf_item)
```

**Verificación**:
```python
# Test manual:
# 1. Arrastrar PDF → Crear factura
# 2. Cerrar app
# 3. Abrir app
# 4. Verificar que columna PDF sigue mostrando "Sí"
# 5. Click en "Sí" → Debe abrir PDF
```

---

### 2. Conectar Filtros de ID y Proveedor

**Problema**: Los campos existen pero no hacen nada.

**Solución en `ui_main.py`**:
```python
# En __init__ del MainWindow, después de crear los filtros:

self.filter_id_input.textChanged.connect(self._on_id_filter_changed)
self.filter_prov_input.textChanged.connect(self._on_prov_filter_changed)

# Nuevos métodos:
def _on_id_filter_changed(self):
    """Filtra por ID de factura"""
    id_text = self.filter_id_input.text().strip()
    if id_text:
        try:
            factura_id = int(id_text)
            # Buscar factura específica
            facturas = self.db.list_facturas()
            factura = next((f for f in facturas if f["id"] == factura_id), None)
            if factura:
                self._current_filter_date = None
                self.filter_status.setCurrentText("Todas")
                self.filter_search.clear()
                self.filter_prov_input.clear()
                self.refresh_table()
                # Seleccionar fila
                for row in range(self.table.rowCount()):
                    if self.table.item(row, 0).text() == str(factura_id):
                        self.table.selectRow(row)
                        break
            else:
                QtWidgets.QMessageBox.information(self, "No encontrado", f"No existe factura con ID {factura_id}")
        except ValueError:
            pass  # No es un número válido
    else:
        self.refresh_table()

def _on_prov_filter_changed(self):
    """Filtra por proveedor"""
    prov_text = self.filter_prov_input.text().strip().lower()
    if prov_text:
        self._current_filter_date = None
        self.filter_status.setCurrentText("Todas")
        self.filter_search.clear()
        self.filter_id_input.clear()
        # refresh_table ya maneja búsqueda por texto
        self.refresh_table()
```

**Alternativa más simple** (usar búsqueda existente):
```python
def _on_id_filter_changed(self):
    id_text = self.filter_id_input.text().strip()
    self.filter_search.setText(id_text)
    self.filter_prov_input.clear()

def _on_prov_filter_changed(self):
    prov_text = self.filter_prov_input.text().strip()
    self.filter_search.setText(prov_text)
    self.filter_id_input.clear()
```

---

## 🔧 REFACTORIZACIÓN DE CÓDIGO

### Problema: `ui_main.py` tiene 2280 líneas

**Solución**: Dividir en módulos especializados.

**Nueva estructura propuesta**:
```
app/views/
├── ui_main.py (coordinador principal - 300 líneas)
├── dashboard/
│   ├── __init__.py
│   ├── kpi_cards.py (KPIWidget y lógica)
│   ├── table_manager.py (Gestión de tabla)
│   └── filter_manager.py (Gestión de filtros)
├── calendar_view.py (existente)
├── settings_view.py (nuevo, separado de ui_main)
└── dialogs/
    ├── invoice_dialog.py (existente)
    ├── preferences_dialog.py (mover de ui_main)
    └── export_dialog.py (nuevo)
```

**Ejemplo - Nuevo archivo `app/views/dashboard/table_manager.py`**:
```python
from PySide6 import QtWidgets, QtCore, QtGui
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger("FacturasGanaTodo.table_manager")

class TableManager:
    """Gestiona la tabla de facturas del dashboard"""
    
    def __init__(self, parent_widget: QtWidgets.QWidget, db):
        self.parent = parent_widget
        self.db = db
        self.table = None
        self._setup_table()
    
    def _setup_table(self):
        """Crea y configura la tabla"""
        self.table = QtWidgets.QTableWidget()
        # ... configuración de columnas ...
    
    def refresh(self, facturas: List[Dict[str, Any]]):
        """Actualiza contenido de la tabla"""
        self.table.setRowCount(len(facturas))
        for row_idx, factura in enumerate(facturas):
            self._populate_row(row_idx, factura)
    
    def _populate_row(self, row: int, factura: Dict[str, Any]):
        """Llena una fila con datos de factura"""
        # ... código de llenado ...
    
    def get_selected_id(self) -> Optional[int]:
        """Retorna ID de factura seleccionada"""
        row = self.table.currentRow()
        if row < 0:
            return None
        id_item = self.table.item(row, 0)
        return int(id_item.text()) if id_item else None
```

**Uso en `ui_main.py`**:
```python
from app.views.dashboard.table_manager import TableManager

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, ...):
        super().__init__()
        # ...
        self.table_manager = TableManager(self, db)
        # ...
    
    def refresh_table(self):
        facturas = self.db.list_facturas(...)
        self.table_manager.refresh(facturas)
```

**Beneficios**:
- Cada archivo tiene <500 líneas
- Más fácil de mantener
- Más fácil de testear (mock de componentes)
- Mejor organización

---

## ⚡ OPTIMIZACIONES DE RENDIMIENTO

### 1. Paginación en Tabla

**Implementación**:

```python
# En ui_main.py o table_manager.py

class PaginatedTableManager:
    def __init__(self, items_per_page: int = 50):
        self.items_per_page = items_per_page
        self.current_page = 0
        self.total_items = 0
    
    def refresh(self, all_facturas: List[Dict]):
        """Actualiza con paginación"""
        self.total_items = len(all_facturas)
        self.total_pages = (self.total_items + self.items_per_page - 1) // self.items_per_page
        
        # Calcular índices
        start = self.current_page * self.items_per_page
        end = min(start + self.items_per_page, self.total_items)
        
        # Mostrar solo página actual
        page_facturas = all_facturas[start:end]
        self._populate_table(page_facturas)
        
        # Actualizar controles de paginación
        self._update_pagination_controls()
    
    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.refresh(self._cached_facturas)
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.refresh(self._cached_facturas)
```

**UI de paginación**:
```python
# Crear barra de paginación
pagination_layout = QtWidgets.QHBoxLayout()
self.btn_prev = QtWidgets.QPushButton("◄ Anterior")
self.lbl_page = QtWidgets.QLabel("Página 1 de 1")
self.btn_next = QtWidgets.QPushButton("Siguiente ►")

self.btn_prev.clicked.connect(self.table_manager.prev_page)
self.btn_next.clicked.connect(self.table_manager.next_page)

pagination_layout.addStretch()
pagination_layout.addWidget(self.btn_prev)
pagination_layout.addWidget(self.lbl_page)
pagination_layout.addWidget(self.btn_next)
pagination_layout.addStretch()
```

---

### 2. Índices en Base de Datos

**Agregar en `database.py` - método `initialize()`**:
```python
def initialize(self):
    with self.connect() as conn:
        # ... código existente ...
        
        # NUEVOS ÍNDICES para búsqueda más rápida
        conn.execute("CREATE INDEX IF NOT EXISTS idx_facturas_proveedor ON facturas(proveedor);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_facturas_numero ON facturas(numero_factura);")
        
        # Ya existentes (verificar que estén)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_facturas_estado ON facturas(estado);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_facturas_venc ON facturas(fecha_vencimiento);")
```

**Beneficio**: Búsquedas 10-100x más rápidas en bases de datos grandes.

---

### 3. Lazy Loading en Calendario

**Problema**: Crea 30-42 widgets cada vez que cambia de mes.

**Solución**:
```python
# En calendar_view.py

class OptimizedCalendarView:
    def __init__(self):
        self._day_widget_pool = []  # Pool de widgets reutilizables
        self._max_pool_size = 42    # Máximo de días en un mes
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Crea pool de widgets una sola vez"""
        for _ in range(self._max_pool_size):
            widget = CalendarDayWidget(datetime.now(), [], True)
            widget.hide()
            self._day_widget_pool.append(widget)
    
    def _load_month(self):
        """Reutiliza widgets del pool en lugar de crear nuevos"""
        days = self._get_days_in_month()  # Lista de fechas
        
        for idx, day_data in enumerate(days):
            widget = self._day_widget_pool[idx]
            widget.update_data(day_data["date"], day_data["facturas"])  # Método nuevo
            widget.show()
        
        # Ocultar widgets sobrantes
        for idx in range(len(days), self._max_pool_size):
            self._day_widget_pool[idx].hide()
```

---

## 💾 MEJORAS EN BASE DE DATOS

### 1. Backup Automático

**Nuevo archivo: `app/services/backup.py`**:
```python
import shutil
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger("FacturasGanaTodo.backup")

class BackupManager:
    def __init__(self, db_path: str, backup_dir: str, max_backups: int = 7):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self) -> bool:
        """Crea backup con timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"facturas_backup_{timestamp}.sqlite"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"✓ Backup creado: {backup_path}")
            
            self._cleanup_old_backups()
            return True
        except Exception as e:
            logger.exception(f"Error al crear backup: {e}")
            return False
    
    def _cleanup_old_backups(self):
        """Mantiene solo los últimos N backups"""
        backups = sorted(self.backup_dir.glob("facturas_backup_*.sqlite"))
        while len(backups) > self.max_backups:
            oldest = backups.pop(0)
            oldest.unlink()
            logger.info(f"Backup antiguo eliminado: {oldest}")
    
    def restore_backup(self, backup_file: str) -> bool:
        """Restaura desde un backup"""
        try:
            backup_path = self.backup_dir / backup_file
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup no encontrado: {backup_file}")
            
            # Hacer backup del actual antes de restaurar
            current_backup = self.db_path.with_suffix(".sqlite.before_restore")
            shutil.copy2(self.db_path, current_backup)
            
            # Restaurar
            shutil.copy2(backup_path, self.db_path)
            logger.info(f"✓ Restaurado desde: {backup_file}")
            return True
        except Exception as e:
            logger.exception(f"Error al restaurar: {e}")
            return False
```

**Usar en `main.py`**:
```python
from app.services.backup import BackupManager

def main():
    # ... código existente ...
    
    # Crear backup diario
    backup_mgr = BackupManager(
        db_path=cfg.db_path,
        backup_dir=os.path.join(app_dir, "backups"),
        max_backups=7
    )
    
    # Verificar si toca backup hoy
    last_backup_file = ".last_backup_date"
    today = datetime.now().date().isoformat()
    
    if os.path.exists(last_backup_file):
        with open(last_backup_file, "r") as f:
            last_date = f.read().strip()
    else:
        last_date = ""
    
    if last_date != today:
        logger.info("Creando backup diario...")
        if backup_mgr.create_backup():
            with open(last_backup_file, "w") as f:
                f.write(today)
```

---

### 2. Validación de Integridad

**Nuevo método en `database.py`**:
```python
def verify_integrity(self) -> bool:
    """Verifica integridad de la BD"""
    try:
        with self.connect() as conn:
            result = conn.execute("PRAGMA integrity_check;").fetchone()
            is_ok = result[0] == "ok"
            if is_ok:
                logger.info("✓ Base de datos íntegra")
            else:
                logger.error(f"⚠️ Problemas de integridad: {result[0]}")
            return is_ok
    except Exception as e:
        logger.exception(f"Error al verificar integridad: {e}")
        return False

def optimize(self):
    """Optimiza la BD (VACUUM)"""
    try:
        with self.connect() as conn:
            conn.execute("VACUUM;")
            logger.info("✓ Base de datos optimizada")
    except Exception as e:
        logger.exception(f"Error al optimizar: {e}")
```

---

## 🧪 TESTING Y CALIDAD

### Estructura de Tests

**Crear carpeta `tests/`**:
```
tests/
├── __init__.py
├── conftest.py (fixtures de pytest)
├── test_database.py
├── test_scheduler.py
├── test_pdf_extractor.py
├── test_validators.py
└── test_export.py
```

**Ejemplo - `tests/conftest.py`**:
```python
import pytest
from app.model.database import Database
from datetime import datetime

@pytest.fixture
def temp_db():
    """Base de datos temporal en memoria"""
    db = Database(":memory:")
    db.initialize()
    yield db
    # Cleanup automático al terminar el test

@pytest.fixture
def sample_factura():
    """Factura de ejemplo para tests"""
    return {
        "numero_factura": "F-TEST-001",
        "proveedor": "Test S.A.",
        "valor": 1500.00,
        "notas": "Factura de prueba",
        "fecha_vencimiento": "2026-02-15T10:00:00",
        "hora1": "09:00",
        "hora2": "14:00",
        "hora3": "18:00"
    }
```

**Ejemplo - `tests/test_database.py`**:
```python
import pytest
from datetime import datetime

def test_add_factura(temp_db, sample_factura):
    """Test de agregar factura"""
    factura_id = temp_db.add_factura(
        sample_factura["numero_factura"],
        sample_factura["proveedor"],
        sample_factura["valor"],
        sample_factura["notas"],
        sample_factura["fecha_vencimiento"],
        sample_factura["hora1"],
        sample_factura["hora2"],
        sample_factura["hora3"]
    )
    
    assert factura_id > 0
    facturas = temp_db.list_facturas()
    assert len(facturas) == 1
    assert facturas[0]["numero_factura"] == "F-TEST-001"

def test_update_factura(temp_db, sample_factura):
    """Test de actualizar factura"""
    # Agregar
    factura_id = temp_db.add_factura(...)
    
    # Actualizar
    temp_db.update_factura(
        factura_id,
        "F-TEST-002",  # Nuevo número
        sample_factura["proveedor"],
        2000.00,  # Nuevo valor
        ...
    )
    
    # Verificar
    facturas = temp_db.list_facturas()
    assert facturas[0]["numero_factura"] == "F-TEST-002"
    assert facturas[0]["valor"] == 2000.00

def test_mark_pagada(temp_db, sample_factura):
    """Test de marcar como pagada"""
    factura_id = temp_db.add_factura(...)
    temp_db.mark_pagada(factura_id)
    
    facturas = temp_db.list_facturas()
    assert facturas[0]["estado"] == "Pagada"
```

**Ejecutar tests**:
```bash
# Instalar pytest
pip install pytest pytest-cov

# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app tests/

# Reporte HTML
pytest --cov=app --cov-report=html tests/
# Ver en: htmlcov/index.html
```

---

## 🔒 SEGURIDAD

### 1. Encriptación del Código de Activación

**En `app/services/activation.py`**:
```python
import hashlib

class ActivationManager:
    ACTIVATION_CODE_HASH = "a1b2c3d4e5f6..."  # SHA-256 de SHEDULE-36-2
    
    def activate(self, code: str) -> bool:
        """Valida código usando hash"""
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        if code_hash == self.ACTIVATION_CODE_HASH:
            # Guardar solo el hash
            with open(self.activation_file, "w") as f:
                f.write(code_hash)
            logger.info("✓ Aplicación activada")
            return True
        
        logger.warning(f"✗ Código incorrecto")
        return False
    
    def is_activated(self) -> bool:
        """Verifica si está activado leyendo hash"""
        if not os.path.exists(self.activation_file):
            return False
        
        with open(self.activation_file, "r") as f:
            stored_hash = f.read().strip()
        
        return stored_hash == self.ACTIVATION_CODE_HASH
```

**Generar hash del código**:
```python
import hashlib
code = "SHEDULE-36-2"
hash_value = hashlib.sha256(code.encode()).hexdigest()
print(f"Hash: {hash_value}")
# Copiar este valor a ACTIVATION_CODE_HASH
```

---

### 2. Validación de Rutas de Archivos

**Prevenir Path Traversal**:
```python
import os
from pathlib import Path

def is_safe_path(base_dir: str, user_path: str) -> bool:
    """Valida que user_path esté dentro de base_dir"""
    base = Path(base_dir).resolve()
    target = Path(user_path).resolve()
    
    try:
        target.relative_to(base)
        return True
    except ValueError:
        return False

# Uso en _dashboard_drop:
def _dashboard_drop(self, event):
    # ...
    pdf_path = ...
    
    # Validar que no sea un path malicioso
    app_dir = os.path.dirname(self.db.db_path)
    if not is_safe_path(app_dir, pdf_path):
        logger.warning(f"Ruta de PDF sospechosa rechazada: {pdf_path}")
        return
```

---

## ⚙️ CONFIGURACIÓN Y FLEXIBILIDAD

### 1. Archivo de Configuración Extendido

**Actualizar `config.json`** (o crear `settings.json`):
```json
{
  "database": {
    "path": "data/facturas_ganatodo.sqlite",
    "backup_enabled": true,
    "backup_dir": "backups",
    "max_backups": 7
  },
  "ui": {
    "theme": "dark",
    "language": "es",
    "date_format": "DD/MM/YYYY",
    "time_format": "24h",
    "items_per_page": 50
  },
  "notifications": {
    "sound_enabled": true,
    "sound_file": "assets/notification.wav",
    "volume": 0.7,
    "position": "bottom_right"
  },
  "export": {
    "default_format": "xlsx",
    "open_after_export": true
  },
  "autostart": {
    "enabled": false,
    "minimized": true
  },
  "pdf": {
    "auto_extract": true,
    "ocr_enabled": false
  }
}
```

**Nuevo `app/config/settings.py`**:
```python
import json
from pathlib import Path
from typing import Any, Dict

class Settings:
    DEFAULT_SETTINGS = {
        "ui": {
            "theme": "dark",
            "language": "es",
            "date_format": "DD/MM/YYYY"
        }
        # ... resto de defaults
    }
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.settings = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Carga settings o crea con defaults"""
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                return json.load(f)
        return self.DEFAULT_SETTINGS.copy()
    
    def get(self, key_path: str, default=None):
        """
        Obtiene valor usando notación de punto
        Ejemplo: settings.get("ui.theme") → "dark"
        """
        keys = key_path.split(".")
        value = self.settings
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key_path: str, value: Any):
        """Establece valor y guarda"""
        keys = key_path.split(".")
        current = self.settings
        for k in keys[:-1]:
            current = current.setdefault(k, {})
        current[keys[-1]] = value
        self._save()
    
    def _save(self):
        """Guarda a archivo"""
        with open(self.config_path, "w") as f:
            json.dump(self.settings, f, indent=2)
```

---

## 📏 MEJORES PRÁCTICAS

### 1. Logging Estructurado

**En lugar de**:
```python
logger.info(f"Factura {id} actualizada")
```

**Usar**:
```python
logger.info("Factura actualizada", extra={
    "factura_id": id,
    "cambios": ["proveedor", "valor"],
    "usuario": "admin"
})
```

### 2. Constantes en Lugar de Strings Mágicos

**Crear `app/constants.py`**:
```python
# Estados de factura
ESTADO_PENDIENTE = "Pendiente"
ESTADO_PAGADA = "Pagada"

# Códigos de alerta
ALERT_D5 = "D5"
ALERT_D3 = "D3"
ALERT_D1 = "D1"
ALERT_H1 = "H1"
ALERT_H2 = "H2"
ALERT_H3 = "H3"
ALERT_SNOOZE = "SNZ"

# Tiempos de snooze (en minutos)
SNOOZE_5MIN = 5
SNOOZE_15MIN = 15
SNOOZE_30MIN = 30
SNOOZE_1HOUR = 60
```

**Usar en código**:
```python
from app.constants import ESTADO_PENDIENTE, ALERT_D5

if estado == ESTADO_PENDIENTE:  # Mejor que "Pendiente"
    ...

if code == ALERT_D5:  # Mejor que "D5"
    ...
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Prioridad Crítica (Sprint 1 - 1 semana)
- [ ] ✅ Persistencia de PDFs en BD
- [ ] ✅ Conectar filtros ID y Proveedor
- [ ] ✅ Tests básicos de database.py

### Prioridad Alta (Sprint 2 - 2 semanas)
- [ ] 🔧 Refactorizar ui_main.py
- [ ] ⚡ Paginación en tabla
- [ ] 💾 Backup automático
- [ ] 📏 Mover a constantes

### Prioridad Media (Sprint 3+ - 3+ semanas)
- [ ] 🔒 Encriptación de código de activación
- [ ] ⚙️ Sistema de configuración extendido
- [ ] 🧪 Tests completos (60% cobertura)
- [ ] 📊 Índices adicionales en BD

---

**Documento creado por**: Antigravity AI  
**Versión**: 1.0  
**Última actualización**: 29 de enero de 2026
