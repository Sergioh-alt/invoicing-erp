# 🔧 PLAN DE REFACTORIZACIÓN - ui_main.py

**Fecha**: 29 de Enero de 2026, 10:15 PM  
**Archivo objetivo**: `app/views/ui_main.py` (2259 líneas)  
**Objetivo**: Dividir en módulos manejables y bien organizados

---

## 📊 ANÁLISIS ACTUAL

### Estructura del archivo:
- **Funciones globales**: 6 (helpers)
- **Clase PreferencesDialog**: 1 (165 líneas)
- **Clase MainWindow**: 1 (1900+ líneas) ⚠️
- **Total métodos en MainWindow**: 40+

### Responsabilidades identificadas en MainWindow:

#### 1. **Dashboard y UI** (~600 líneas)
- `_create_dashboard_view()` - Crea vista principal
- `_create_calendar_placeholder()` - Placeholder calendario
- `_create_settings_placeholder()` - Placeholder ajustes
- `_on_view_changed()` - Navegación entre vistas
- `closeEvent()`, `set_allow_quit()` - Gestión de ventana

#### 2. **Gestión de Tabla** (~400 líneas)
- `refresh_table()` - Actualiza tabla con filtros
- `_populate_table_rows()` - Llena filas de página actual
- `_on_table_cell_clicked()` - Clicks en celdas
- `_on_header_clicked()` - Clicks en headers
- `_toggle_sort_order()` - Ordenamiento
- `_refresh_countdown_only()` - Actualiza cuenta regresiva

#### 3. **Filtros** (~200 líneas)
- `_on_text_filter_changed()` - Filtros de texto
- `_update_filter_status()` - Estado de filtros
- `_clear_filters()` - Limpiar filtros

#### 4. **CRUD de Facturas** (~400 líneas)
- `add_factura()` - Agregar
- `edit_selected()` - Editar
- `delete_selected()` - Eliminar
- `mark_selected_paid()` - Marcar pagada
- `_open_invoice_dialog_from_pdf()` - Desde PDF

#### 5. **Exportación** (~200 líneas)
- `export_visible()` - Exportar a CSV/Excel

#### 6. **Notificaciones** (~150 líneas)
- `show_notification()` - Mostrar notificaciones
- `_notif_mark_paid()` - Acción marcar pagada
- `_notif_snooze()` - Acción snooze

#### 7. **Preferencias** (~100 líneas)
- ` open_preferences()` - Abrir diálogo

---

## 🎯 ARQUITECTURA OBJETIVO

### Módulos a crear:

```
app/views/
├── ui_main.py                    # 400-500 líneas (núcleo)
├── controllers/
│   ├── __init__.py
│   ├── dashboard_controller.py   # Gestión de dashboard
│   ├── table_controller.py       # Gestión de tabla
│   ├── filter_controller.py      # Lógica de filtros
│   ├── crud_controller.py        # CRUD facturas
│   └── export_controller.py      # Exportación
├── helpers/
│   ├── __init__.py
│   ├── formatting_helpers.py     # Funciones formato
│   └── kpi_calculator.py         # Cálculo de KPIs
└── (archivos existentes)
```

### Distribución de líneas:

| Módulo | Líneas | Responsabilidad |
|--------|--------|-----------------|
| `ui_main.py` | ~450 | Ventana principal, inicialización, coordinación |
| `dashboard_controller.py` | ~400 | Creación de vistas, layouts |
| `table_controller.py` | ~500 | Gestión completa de tabla |
| `filter_controller.py` | ~250 | Lógica de filtros |
| `crud_controller.py` | ~450 | CRUD de facturas |
| `export_controller.py` | ~200 | Exportación |
| `formatting_helpers.py` | ~150 | Helpers de formato |
| **TOTAL** | **~2400** | (incluye código nuevo) |

---

## 🚀 PLAN DE IMPLEMENTACIÓN

### FASE 1: Preparación (15 min)
- ✅ Crear estructura de carpetas
- ✅ Crear archivos __init__.py
- ✅ Crear archivos base vacíos

### FASE 2: Helpers (30 min)
- Mover funciones globales a formatting_helpers.py
- Crear kpi_calculator.py
- Actualizar imports en ui_main.py

### FASE 3: Controllers (2 horas)
- **Paso 3.1**: filter_controller.py (~30 min)
- **Paso 3.2**: export_controller.py (~20 min)
- **Paso 3.3**: table_controller.py (~40 min)
- **Paso 3.4**: crud_controller.py (~30 min)

### FASE 4: Dashboard (30 min)
- dashboard_controller.py
- Simplificar _create_dashboard_view

### FASE 5: Limpieza de ui_main.py (30 min)
- Eliminar código movido
- Actualizar imports
- Delegación a controllers

### FASE 6: Testing (20 min)
- Ejecutar app y verificar
- Ejecutar pytest
- Verificar funcionalidad

### FASE 7: Documentación (10 min)
- Documentar cambios
- Crear REFACTORIZACION.md

---

## 🎨 PATRÓN DE DISEÑO

### Controladores como Mixins:

```python
# ui_main.py
from app.views.controllers.filter_controller import FilterController
from app.views.controllers.table_controller import TableController
# ... otros

class MainWindow(QtWidgets.QMainWindow, 
                 FilterController,
                 TableController,
                 # ...
                 ):
    def __init__(self, ...):
        # Inicialización compartida
        pass
```

### Ventajas:
- ✅ Acceso directo a `self.db`, `self.table`, etc.
- ✅ No rompe código existente
- ✅ Fácil migración incremental
- ✅ Mantiene toda la funcionalidad

### Alternativa (si Mixins no funciona):
- Controladores como clases independientes
- MainWindow delega a ellos
- Requiere más refactorización

---

## ⚠️ RIESGOS Y MITIGACIONES

### Riesgo 1: Imports circulares
**Mitigación**: Usar imports relativos, estructura clara

### Riesgo 2: Referencias a self
**Mitigación**: Usar mixins o pasar `self` a métodos

### Riesgo 3: Romper funcionalidad
**Mitigación**: Tests como red de seguridad, commit frecuente

### Riesgo 4: Estado compartido
**Mitigación**: Documentar dependencias, inicialización clara

---

## ✅ CRITERIOS DE ÉXITO

1. ✅ ui_main.py < 500 líneas
2. ✅ Cada módulo < 600 líneas
3. ✅ Todos los tests pasan
4. ✅ Aplicación funciona idéntica
5. ✅ Código más mantenible

---

## 📝 NOTAS IMPORTANTES

- **NO modificar lógica de negocio**, solo reorganizar
- **NO cambiar nombres de métodos públicos** (mantener compatibilidad)
- **SÍ agregar docstrings** donde falten
- **SÍ mejorar nombres** de variables internas si ayuda

---

**Tiempo estimado total**: 3.5-4 horas  
**Inicio**: 22:15 PM  
**Finalización estimada**: ~2:00 AM  

¿Procedemos? 🚀
