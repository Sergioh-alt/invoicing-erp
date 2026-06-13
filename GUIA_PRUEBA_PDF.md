# 🧪 GUÍA DE PRUEBA - Fix de Persistencia de PDFs

**Aplicación**: EJECUTÁNDOSE  
**Objetivo**: Verificar que los PDFs se guardan en la BD y persisten entre reinicios

---

## ✅ PRUEBA 1: Crear Factura desde PDF

### Paso 1: Arrastra un PDF
1. Busca CUALQUIER archivo PDF en tu computadora
2. Arrástralo al área de la tabla en el dashboard
3. ⏳ Espera a que extraiga los datos

### Paso 2: Verifica la Extracción
✅ Debe aparecer un diálogo con:
- Vista previa del PDF a la derecha
- Datos extraídos (número, proveedor, monto, fecha)
- Botón "Guardar"

### Paso 3: Guarda la Factura
1. Haz click en "Guardar"
2. ✅ La factura debe aparecer en la tabla
3. ✅ **Columna PDF debe mostrar "Sí" en VERDE**

### Paso 4: Verifica que se puede Abrir
1. Haz click en la palabra "Sí" (columna PDF)
2. ✅ **El PDF debe abrirse en tu visor predeterminado**

---

## 🎯 PRUEBA 2: PERSISTENCIA (CRÍTICA)

### Esta es la prueba del BUG que arreglamos:

### Paso 1: Cierra la Aplicación
1. Ve a la bandeja del sistema (junto al reloj)
2. Click derecho en el icono de Facturas GanaTodo
3. **"Salir completamente"**
4. ⏳ Espera a que se cierre completamente

### Paso 2: Reabre la Aplicación
Ejecuta de nuevo:
```
.venv\Scripts\activate.ps1; python main.py
```

### Paso 3: VERIFICA EL FIX
Cuando cargue la aplicación:

✅ **La columna PDF debe seguir mostrando "Sí" en verde**  
   ← **ANTES del fix: mostraba "No"**

✅ **El click en "Sí" debe seguir abriendo el PDF**  
   ← **ANTES del fix: no funcionaba**

🎉 **Si funciona = BUG RESUELTO**

---

## ✅ PRUEBA 3: Editar Factura con PDF

### Paso 1: Edita una Factura con PDF
1. Selecciona la factura que tiene PDF (la que creaste)
2. Click en botón "Editar"
3. Cambia algo (ej: proveedor o monto)
4. Click "Guardar"

### Paso 2: Verifica Preservación
✅ **La columna PDF debe seguir mostrando "Sí"**  
✅ **El click en "Sí" debe seguir abriendo el PDF**

---

## ✅ PRUEBA 4: Factura Manual (Sin PDF)

### Paso 1: Crear Factura Manual
1. Click en botón "Añadir"
2. Llena los campos manualmente
3. Click "Guardar"

### Paso 2: Verifica Columna PDF
✅ **Debe mostrar "No" en GRIS**

### Paso 3: Click en "No"
1. Haz click en la palabra "No"
2. ✅ **Debe aparecer mensaje**: "Esta factura no tiene un PDF vinculado"

---

## ❌ PRUEBA 5: PDF Eliminado (Manejo de Errores)

### Paso 1: Ubicar el PDF Original
1. Busca el archivo PDF que arrastraste
2. Elimínalo o muévelo a otra carpeta

### Paso 2: Intenta Abrirlo desde la App
1. En la app, click en "Sí" de esa factura
2. ✅ **Debe aparecer advertencia**: "El archivo PDF no existe... posible que haya sido movido o eliminado"

---

## 📊 RESULTADO ESPERADO

| Prueba | Estado | Descripción |
|--------|--------|-------------|
| **Crear desde PDF** | ✅ | Extrae y muestra "Sí" |
| **PERSISTENCIA** | ✅ | **Sigue mostrando "Sí" tras reinicio** |
| **Editar con PDF** | ✅ | Preserva el PDF vinculado |
| **Factura manual** | ✅ | Muestra "No" en gris |
| **PDF eliminado** | ✅ | Advertencia clara |

---

## 🐛 SI ALGO FALLA

### Si la persistencia NO funciona:
1. Revisa que cerró COMPLETAMENTE la app
2. Revisa los logs en `logs/facturas_YYYYMMDD.log`
3. Verifica que no haya errores en consola

### Si el PDF no abre:
1. Verifica que el archivo existe
2. Prueba abrir el PDF manualmente (fuera de la app)
3. Revisa permisos del archivo

---

## 🎉 CONFIRMACIÓN DE FIX

**El bug está RESUELTO si**:
- ✅ Columna PDF muestra "Sí" después de reiniciar
- ✅ Click en "Sí" abre el PDF después de reiniciar

**Antes del fix**:
- ❌ Columna PDF mostraba "No" tras reiniciar
- ❌ Click no funcionaba (no había referencia)

---

**Aplicación en ejecución** - ID: 811fcb76-9015-4b7a-9776-2347418b97ee  
**Instrucciones**: Sigue los pasos de arriba para verificar el fix  
**Tiempo estimado**: 5-10 minutos
