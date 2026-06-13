# Cambios en Fase 3: Navegación y UI Renovada

## Implementado ✅

### 1. Navegación Lateral (Sidebar)
- **Archivo**: `app/views/navigation.py`
- Widget de navegación con 3 vistas:
  - 📊 Dashboard
  - 📅 Calendario (placeholder)
  - ⚙️ Ajustes (placeholder)
- Diseño moderno con gradiente
- Botones con estado activo visual
- Badge de versión v5.0

### 2. Reestructuración de MainWindow
- **Layout horizontal**: Sidebar (200px) + Contenido
- **QStackedWidget** para intercambiar vistas
- **Dashboard renovado**:
  - 4 KPIs en lugar de 3 (agregado "Total (vista)")
  - Búsqueda con icono 🔍
  - Filtros mejorados (ID, Proveedor, Estado)
  - Botón "Limpiar" para filtros
  - Botón "Exportar" agregado
  - **Columna PDF** en la tabla (muestra 📄 si existe)
  - Tip de drag & drop destacado

### 3. Mejoras Visuales
- Título actualizado: "Facturas GanaTodo v5.0"
- Resolución mínima: 1280x760 (era 1180x720)
- Espaciado y márgenes mejorados
- Botón "Añadir" con color azul destacado
- Tip de drag & drop con borde izquierdo coloreado

### 4. Placeholders
- **Vista Calendario**: Estructura básica lista
- **Vista Ajustes**: Incluye botón "Preferencias (Legacy)" temporalmente

## Próximos Pasos (Fase 4)

- Implementar vista de Calendario funcional
- Implementar vista de Ajustes completa
- Agregar funcionalidad de drag & drop
- Conectar botón "Exportar"
- Implementar filtros avanzados

## Cómo Probar

```bash
# Activar entorno virtual
.venv\Scripts\activate

# Ejecutar
python main.py

# Navegar entre vistas:
# - Click en "Dashboard" → Vista principal con tabla
# - Click en "Calendario" → Placeholder
# - Click en "Ajustes" → Placeholder con botón de preferencias
```

## Screenshot Esperado

```
┌─────────────────────────────────────────────────────┐
│ ┌──────────┐ Dashboard                              │
│ │ Facturas │                                         │
│ │ GanaTodo │ ┌────┐ ┌────┐ ┌────┐ ┌────┐           │
│ │  [v5.0]  │ │ P  │ │ V  │ │ V  │ │ T  │           │
│ │          │ │ 2  │ │ 0  │ │ 0  │ │ 2  │           │
│ │─────────│ └────┘ └────┘ └────┘ └────┘           │
│ │ 📊 Dashb │                                         │
│ │ 📅 Calen │ [Filtros...] [Añadir] [Editar] ...   │
│ │ ⚙️ Ajust │                                         │
│ │          │ ┌───────────────────────────────────┐ │
│ │          │ │ TABLA DE FACTURAS                 │ │
│ │          │ │ ID | Factura | Proveedor | PDF   │ │
│ │─────────│ └───────────────────────────────────┘ │
│ │ ● Activo │                                         │
│ └──────────┘                                         │
└─────────────────────────────────────────────────────┘
```

## Cambios en Base de Datos

**Nota**: La columna `pdf_path` aún no existe en el schema. Se agregará en una fase posterior con migración automática.

Por ahora, `r.get('pdf_path')` retornará `None`, por lo que todos los PDFs mostrarán "-".
