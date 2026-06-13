# Nuevas Funcionalidades: Exportación y PDF Drag & Drop

## ✅ Funcionalidades Implementadas

### 1. Exportación de Facturas 📤

**Botón**: "Exportar" en el dashboard

**Características**:
- Exporta facturas visibles (respeta filtros activos)
- Dos formatos disponibles:
  - **CSV**: Compatible con Excel, Google Sheets, etc.
  - **Excel (.xlsx)**: Con formato profesional (headers coloreados, columnas autoajustadas)
- Diálogo para elegir ubicación de guardado
- Opción de abrir archivo automáticamente después de exportar

**Uso**:
1. Aplicar filtros si deseas exportar solo ciertas facturas
2. Click en botón "Exportar"
3. Elegir formato (CSV o Excel)
4. Seleccionar ubicación y nombre de archivo
5. Confirmar exportación
6. Opcionalmente abrir el archivo generado

**Columnas exportadas**:
- ID
- Número de Factura
- Proveedor
- Valor (con formato de moneda en Excel)
- Fecha de Vencimiento
- Estado
- Notas
- Horarios de Alerta (H1, H2, H3)

---

### 2. Importación Automática desde PDF 📄

**Función**: Drag & Drop de archivos PDF

**Características**:
- Detección automática de PDFs arrastrados
- Extracción inteligente de información:
  - **Número de Factura**: Busca patrones como "Factura #", "No.", etc.
  - **Proveedor**: Detecta nombres corporativos (S.A., LTDA, etc.)
  - **Monto**: Busca "Total", "Amount", "$", etc.
  - **Fecha de Vencimiento**: Múltiples formatos soportados (DD/MM/YYYY, etc.)
- Preview de datos extraídos
- Diálogo de confirmación antes de guardar
- Opción de ingresar manualmente si la extracción falla

**Uso**:
1. Tener un archivo PDF de factura
2. Arrastrar el PDF desde el explorador de archivos
3. Soltar sobre la tabla en el dashboard
4. Esperar extracción automática (progreso mostrado)
5. Revisar datos extraídos en el popup
6. Ajustar datos si es necesario
7. Guardar

**Patrones de Extracción**:

| Campo | Patrones Soportados |
|-------|---------------------|
| Número | "Factura:", "Invoice:", "No.", "# ABC-123" |
| Proveedor | Nombres con "S.A.", "LTDA", "S.L.", "INC.", "CORP." |
| Monto | "Total:", "$X,XXX.XX", "Amount:", "Valor:" |
| Fecha | "Vence:", "Due Date:", "DD/MM/YYYY", "DD-MM-YYYY" |

---

## 📦 Dependencias Nuevas

**Actualizar requirements.txt**:
```bash
pip install -r requirements.txt
```

**Librerías agregadas**:
- `openpyxl>=3.1.0` - Exportación a Excel
- `PyMuPDF>=1.23.0` - Lectura de PDFs
- `python-dateutil>=2.8.0` - Parsing de fechas

---

## 🧪 Pruebas Recomendadas

### Test 1: Exportación CSV

**Pasos**:
1. Agregar 2-3 facturas de prueba
2. Click en "Exportar"
3. Seleccionar "CSV"
4. Guardar en ubicación conocida
5. Abrir CSV con Excel/Google Sheets

**Resultado esperado**:
- Archivo CSV creado con todas las facturas
- Headers correctos
- Datos formateados correctamente

---

### Test 2: Exportación Excel

**Pasos**:
1. Tener facturas en la tabla
2. Click en "Exportar"
3. Seleccionar "Excel (.xlsx)"
4. Guardar y abrir

**Resultado esperado**:
- Archivo Excel con formato profesional
- Headers con fondo azul y texto blanco
- Columnas autoajustadas
- Valores monetarios con formato `$X,XXX.XX`

---

### Test 3: PDF Simple

**Preparar un PDF de prueba con**:
```
FACTURA: F-2026-001
PROVEEDOR: Servicios ABC S.A.
Total: $1,500.00
Vencimiento: 28/02/2026
```

**Pasos**:
1. Arrastrar PDF a la tabla
2. Esperar extracción
3. Verificar popup con datos

**Resultado esperado**:
- Número: "F-2026-001"
- Proveedor: "Servicios ABC S.A."
- Monto: 1500.00
- Fecha: 2026-02-28

---

### Test 4: PDF Complejo

**Con PDF real de factura**:
1. Arrastrar PDF complejo
2. Ver resultados de extracción
3. Ajustar datos manualmente si es necesario
4. Guardar

**Nota**: La precisión depende del formato del PDF. PDFs con texto nativo funcionan mejor que los escaneados (requeriría OCR adicional).

---

## 🔧 Solución de Problemas

### Problema: "openpyxl no disponible"

**Causa**: No se instaló la dependencia

**Solución**:
```bash
pip install openpyxl>=3.1.0
```

---

### Problema: "PyMuPDF no disponible"

**Causa**: No se instaló PyMuPDF

**Solución**:
```bash
pip install PyMuPDF>=1.23.0
```

---

### Problema: PDF no se extrae correctamente

**Causas posibles**:
- PDF escaneado (solo imagen, no texto)
- Formato no estándar
- Idioma no soportado

**Solución**:
1. Verificar que el PDF tiene texto seleccionable
2. Usar opción "Ingresar manualmente" si ofrecida
3. Revisar logs en `logs/facturas_YYYYMMDD.log` para debug

---

### Problema: Exportación falla

**Verificar**:
- Permisos de escritura en carpeta destino
- Que el archivo no esté abierto en otro programa
- Logs para error específico

---

## 💡 Tips de Uso

### Para Exportación:
- Aplica filtros antes de exportar para crear subconjuntos
- Usa Excel si necesitas formato profesional para reportes
- Usa CSV si necesitas importar a otra aplicación

### Para PDFs:
- Los PDFs con texto nativo (generados digitalmente) funcionan mejor
- PDFs escaneados requieren OCR (no incluido aún)
- Siempre revisa los datos extraídos antes de guardar
- El campo "Notas" automáticamente incluye el nombre del PDF

### Formatos de Fecha Soportados:
- DD/MM/YYYY (ej: 28/02/2026)
- DD-MM-YYYY (ej: 28-02-2026)
- DD.MM.YYYY (ej: 28.02.2026)
- Fechas en texto si `python-dateutil` está instalado

---

## 📝 Ejemplos Prácticos

### Ejemplo 1: Exportar Solo Pendientes

```
1. Filtro: "Pendiente"
2. Exportar → CSV
3. Resultado: Solo facturas pendientes en archivo
```

### Ejemplo 2: Importar Múltiples PDFs

```
1. Seleccionar 5 PDFs en explorador
2. Arrastrar todos a la tabla
3. Procesar uno por uno
4. 5 facturas nuevas creadas
```

### Ejemplo 3: Backup Mensual

```
1. Sin filtros (mostrar todas)
2. Exportar → Excel
3. Nombre: "Facturas_Enero_2026.xlsx"
4. Guardar en carpeta de backups
```

---

## 🚀 Próximas Mejoras

**Planeadas para futuras versiones**:
- OCR para PDFs escaneados
- Mejora de precisión en extracción
- Soporte para más formatos (XML de factura electrónica)
- Exportación a PDF
- Templates personalizables de exportación
- Importación desde Excel/CSV
- Batch processing de múltiples PDFs

---

## 📊 Logs y Debugging

**Para ver actividad de exportación**:
```
logs/facturas_YYYYMMDD.log
```

**Buscar**:
- `FacturasGanaTodo.export` - Eventos de exportación
- `FacturasGanaTodo.pdf_drop` - Eventos de drag & drop
- `FacturasGanaTodo.pdf_extractor` - Detalles de extracción

**Ejemplo de log exitoso**:
```
2026-01-18 11:00:00 - FacturasGanaTodo.pdf_drop - INFO - Procesando PDF: C:\facturas\F-001.pdf
2026-01-18 11:00:01 - FacturasGanaTodo.pdf_extractor - DEBUG - Número de factura encontrado: F-001
2026-01-18 11:00:01 - FacturasGanaTodo.pdf_extractor - DEBUG - Proveedor encontrado: ABC Corp S.A.
2026-01-18 11:00:01 - FacturasGanaTodo.pdf_extractor - DEBUG - Monto encontrado: 1500.0
2026-01-18 11:00:01 - FacturasGanaTodo.pdf_extractor - INFO - Datos extraídos: {'success': True, ...}
```

---

## ✅ Checklist de Funcionalidades

- [x] Botón Exportar conectado
- [x] Diálogo de selección de formato
- [x] Exportación a CSV
- [x] Exportación a Excel con formato
- [x] Drag & drop de PDFs habilitado
- [x] Extracción de número de factura
- [x] Extracción de proveedor
- [x] Extracción de monto
- [x] Extracción de fecha
- [x] Preview de datos extraídos
- [x] Diálogo de confirmación
- [x] Logging completo
- [x] Manejo de errores graceful

---

**Versión**: 5.0  
**Fecha**: 18 de enero de 2026  
**Estado**: ✅ Implementado y listo para pruebas
