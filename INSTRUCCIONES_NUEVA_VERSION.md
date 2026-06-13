# FacturasGanaTodo - Nueva Versión

## ✅ CAMBIOS REALIZADOS

### 1. Nueva Ubicación de Datos
- **Antes**: Las carpetas `data`, `backups` y `config` se creaban en el escritorio
- **Ahora**: Todo se guarda en `C:\TERA TOSHIBA\FacturasGanaTodo\`

### 2. Ubicación del Ejecutable
- **Archivo**: `C:\TERA TOSHIBA\FacturasGanaTodo\FacturasGanatodo.exe`
- **Tamaño**: 282 MB (incluye todas las librerías necesarias)

## 📁 ESTRUCTURA DE CARPETAS

Cuando ejecutes la aplicación por primera vez desde TERA TOSHIBA, se crearán automáticamente:

```
C:\TERA TOSHIBA\FacturasGanaTodo\
├── FacturasGanatodo.exe      (ejecutable)
├── data\                      (base de datos)
├── backups\                   (copias de seguridad automáticas)
└── logs\                      (archivos de registro)
```

## 🗑️ LIMPIEZA DEL ESCRITORIO

Puedes eliminar las siguientes carpetas del escritorio de forma segura:
- `data`
- `backups`
- `config`

**OPCIÓN 1 - Manual:**
Simplemente elimina esas carpetas del escritorio

**OPCIÓN 2 - Script automático:**
Ejecuta el archivo `limpiar_escritorio.bat` (ubicado en el proyecto)

## 🚀 CÓMO USAR LA NUEVA VERSIÓN

1. **Ejecuta la aplicación** desde: `C:\TERA TOSHIBA\FacturasGanaTodo\FacturasGanatodo.exe`

2. **Primera ejecución**: Se crearán automáticamente las carpetas necesarias en TERA TOSHIBA

3. **Opcional**: Crea un acceso directo al escritorio:
   - Haz clic derecho en `FacturasGanatodo.exe`
   - Selecciona "Crear acceso directo"
   - Mueve el acceso directo al escritorio

## ⚠️ IMPORTANTE

- **NO se crearán más carpetas en el escritorio**
- **Todos los datos se guardan en TERA TOSHIBA**
- **Las copias de seguridad automáticas** se crean cada 24 horas
- **Los backups antiguos** (más de 30 días) se eliminan automáticamente

## 🔄 MIGRACIÓN DE DATOS (Si es necesario)

Si tenías datos en la versión anterior del escritorio:

1. Copia la carpeta `data` del escritorio
2. Pégala en `C:\TERA TOSHIBA\FacturasGanaTodo\`
3. Copia la carpeta `backups` del escritorio (opcional)
4. Pégala en `C:\TERA TOSHIBA\FacturasGanaTodo\`

## 📝 NOTAS TÉCNICAS

- **Modo desarrollador**: Ctrl+Shift+D (sigue funcionando)
- **Autostart**: Se configurará automáticamente si lo habilitas desde la configuración
- **Configuración de usuario**: Se guarda en `C:\Users\Usuario\.ganatodo\settings.json`

## 🆕 COMPILAR NUEVAS VERSIONES

Si necesitas compilar una nueva versión en el futuro:

```batch
cd "C:\Users\Usuario\Desktop\Facturas_GanaTodo_v4"
.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm FacturasGanatodo.spec
Copy-Item "dist\FacturasGanatodo.exe" -Destination "C:\TERA TOSHIBA\FacturasGanaTodo\FacturasGanatodo.exe" -Force
```

O simplemente ejecuta: `compilar_tera_auto.bat`

---

**Fecha de compilación**: 2026-02-09
**Versión**: Final con ubicación en TERA TOSHIBA
