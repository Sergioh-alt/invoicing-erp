# Facturas GanaTodo — Invoicing ERP (Desktop)

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![PyInstaller](https://img.shields.io/badge/Build-PyInstaller-FF6600?logo=python)](https://pyinstaller.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows)](https://www.microsoft.com/windows)
[![Status](https://img.shields.io/badge/Status-Production-brightgreen)]()

Desktop invoicing and ERP application for Colombian businesses. Features PDF generation, system tray operation, database persistence, and audit logging — all in a single lightweight `.exe` build.

## Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **UI** | Tkinter / CustomTkinter |
| **Database** | SQLite |
| **PDF** | ReportLab / FPDF |
| **Build** | PyInstaller (single-file, no console) |
| **Persistence** | SQLAlchemy + migration system |
| **Background** | System Tray (pystray / infi.systray) |
| **Testing** | pytest + coverage |

## Features

- **Invoice Creation & Management**: Full CRUD for invoices with Colombian tax formatting (RUT, NIT, IVA)
- **PDF Export**: Professional invoice generation with company branding
- **Audit System**: Complete action log with timestamps and user attribution
- **Database Migrations**: Schema versioning with rollback support
- **Background Operation**: System Tray icon — window hides on close, stays alive in tray
- **Portable Build**: Single `.exe` with no runtime dependencies
- **Backup System**: Automated database backups with rotation
- **Dashboard**: Real-time financial summary metrics

## Screenshots

<!-- Add screenshots here:
![Main Dashboard](screenshots/dashboard.png)
![Invoice Editor](screenshots/invoice.png)
![PDF Preview](screenshots/pdf_preview.png)
-->

## Quick Start

### Development Mode

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Production Build

```bash
# Single-file executable (no console)
pyinstaller --noconsole --onefile --name "FacturasGanaTodo" ^
  --add-data "assets;assets" ^
  --icon "assets/app.ico" ^
  main.py
```

The `.exe` will be at `dist/FacturasGanaTodo.exe`.

> **PowerShell users**: Replace `^` with backtick ` `` ` or write as a single line.

## System Tray Behavior

| Action | Result |
|---|---|
| Click **X** | Window hides (continues in tray) |
| Right-click tray icon | Context menu: Open / Exit |
| Double-click tray icon | Restore window |
| Alerts | Popup notifications even when hidden |

## Project Structure

```
├── app/                  # Application modules
│   ├── controllers/      # Business logic
│   ├── models/           # SQLAlchemy models
│   ├── views/            # UI screens
│   └── utils/            # Helpers (PDF, audit, export)
├── assets/               # Icons, images, templates
├── data/                 # SQLite databases
├── backups/              # Automatic backups
├── tests/                # pytest suite
├── logs/                 # Application logs
├── main.py               # Entry point
└── requirements.txt      # Dependencies
```

## Build Variants

| Script | Description |
|---|---|
| `compilar.bat` | Standard single-file build |
| `compilar_portable.bat` | Portable (folder) build with updater |
| `compilar_tera.bat` | Large-scale deployment build |
| `compilar_tera_auto.bat` | Automated tera-build with version bump |

## Testing

```bash
pytest tests/ --cov=app --cov-report=html
```

## Configuration

Edit `config.json` for runtime settings:

```json
{
  "company": {
    "name": "Tu Empresa SAS",
    "nit": "123456789-0",
    "address": "Calle 123 #45-67"
  },
  "database": {
    "backup_interval_days": 7,
    "max_backups": 10
  }
}
```

## License

MIT — see [LICENSE](LICENSE).

## Related

- [EEA-2026-ANT](https://github.com/YOUR_USER/EEA-2026-ANT) — Autonomous trading system
- [DJ Copilot](https://github.com/YOUR_USER/dj-copilot) — AI music production assistant
- [Shura](https://github.com/YOUR_USER/shura) — Financial analysis dashboard
