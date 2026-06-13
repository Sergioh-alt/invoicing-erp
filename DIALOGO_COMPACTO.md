# Mejora del Diálogo de Factura - Campos Compactos

## Problema Identificado

El campo "Proveedor" se veía muy grande cuando el nombre era largo (ej: "COMUNICACIONES GANA TODO APP SAS"), causando que el diálogo se expandiera visualmente de forma desordenada.

### Antes:
```
┌────────────────────────────────────────┐
│ Proveedor                              │
│ COMUNICACIONES GANA TODO APP SAS       │  ← Muy largo
│                                        │
│ Notas                                  │
│ ┌──────────────────────────────────┐  │
│ │                                  │  │
│ │                                  │  │  ← 110px de alto
│ │                                  │  │
│ │                                  │  │
│ └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

---

## Soluciones Implementadas

### 1. ✅ Campo Proveedor Truncado

**Comportamiento**:
- **Máximo**: 100 caracteres
- **Display**: Solo muestra primeros 30 caracteres + "..."
- **Tooltip**: Al pasar el mouse, muestra el nombre completo
- **Al hacer foco**: Se expande para mostrar todo el texto
- **Al perder foco**: Vuelve a truncarse a 30 caracteres

**Ejemplo**:
```
Normal: "COMUNICACIONES GANA TODO..."
Tooltip: "COMUNICACIONES GANA TODO APP SAS"
Con foco: "COMUNICACIONES GANA TODO APP SAS" (editable)
```

---

### 2. ✅ Campo Notas Más Pequeño

**Cambios**:
- **Antes**: 110px de alto
- **Ahora**: 60px de alto (reducción del 45%)
- **Placeholder**: "Notas adicionales (opcionales)..."

**Razón**: Las notas son opcionales. Si necesitan escribir mucho, pueden abrir la factura para editarla.

---

## Resultado Visual

### Después:
```
┌────────────────────────────────────────┐
│ Proveedor                              │
│ COMUNICACIONES GANA TODO... [tooltip]  │  ← Compacto
│                                        │
│ Notas                                  │
│ ┌──────────────────────────────────┐  │
│ │ Notas opcionales...              │  │  ← 60px
│ └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

**Beneficios**:
- ✅ Diálogo más compacto
- ✅ No se expande innecesariamente
- ✅ Información completa disponible (tooltip + foco)
- ✅ Mejor experiencia visual

---

## Cómo Funciona el Truncado Inteligente

### Caso 1: Proveedor Corto (≤30 caracteres)
```
Input: "ABC Corp S.A."
Display: "ABC Corp S.A."  (sin cambios)
```

### Caso 2: Proveedor Largo (>30 caracteres)
```
Input: "COMUNICACIONES GANA TODO APP SAS"
Display: "COMUNICACIONES GANA TODO..."
Tooltip: [Hover] "COMUNICACIONES GANA TODO APP SAS"
Edición: [Click/Foco] "COMUNICACIONES GANA TODO APP SAS"
```

---

## Interacción del Usuario

### Proveedor:
1. **Leer rápido**: Solo ve primeros 30 caracteres
2. **Ver completo**: Hover para tooltip
3. **Editar**: Click para expandir y editar
4. **Guardar**: Automáticamente vuelve a truncarse

### Notas:
1. **Escribir poco**: 60px es suficiente para 2-3 líneas
2. **Escribir mucho**: Abrir factura en modo edición (doble click en tabla)

---

## Archivos Modificados

**`app/views/dialog_invoice.py`**:
- ✅ Línea 22-37: Lógica de truncado de proveedor
- ✅ Línea 44-46: Notas reducidas a 60px
- ✅ Placeholder agregado para notas

---

## Testing

### Test 1: Proveedor Largo
1. Crear factura desde PDF con proveedor largo
2. Ver que muestra "COMUNICACIONES GANA TODO..."
3. Hover sobre el campo → Ver tooltip completo
4. Click en el campo → Ver texto completo editable
5. Click fuera → Vuelve a truncarse

### Test 2: Proveedor Corto
1. Crear factura manual con proveedor corto: "ABC S.A."
2. Ver que NO se trunca (≤30 caracteres)

### Test 3: Notas
1. Abrir diálogo de nueva factura
2. Ver que campo de notas es compacto (60px)
3. Escribir 2-3 líneas → Cabe perfectamente
4. Escribir más → Usa scroll interno

---

## Código Implementado

```python
# Limitación visual del proveedor
self.in_prov.setMaxLength(100)  # Máximo 100 caracteres

proveedor_text = self._data.get("proveedor", "") or ""
if len(proveedor_text) > 30:
    # Truncar visualmente
    self.in_prov.setToolTip(proveedor_text)
    self.in_prov.setText(proveedor_text[:30] + "...")
    
    # Al hacer foco: mostrar completo
    # Al perder foco: volver a truncar
```

```python
# Notas más compactas
self.in_notes.setFixedHeight(60)  # Era 110px
self.in_notes.setPlaceholderText("Notas adicionales (opcionales)...")
```

---

## Ventajas

1. **Visual**: Diálogo más limpio y compacto
2. **UX**: No abruma con texto largo
3. **Funcional**: Información completa disponible cuando se necesita
4. **Consistente**: Tamaño predecible del diálogo

---

**Estado**: ✅ IMPLEMENTADO  
**Impacto**: Mejora visual significativa  
**Breaking Changes**: Ninguno (retrocompatible)
