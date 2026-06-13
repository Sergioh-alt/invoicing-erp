# Invoicing ERP — Financial Management System

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![PyInstaller](https://img.shields.io/badge/Build-PyInstaller-blue)](https://pyinstaller.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-brightgreen)]()

Desktop invoicing and ERP application for Colombian businesses. Features PDF generation, system tray operation, database persistence, and audit logging — all in a single lightweight `.exe` build.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.10+ |
| **UI** | Tkinter / CustomTkinter |
| **Database** | SQLite |
| **PDF** | ReportLab / FPDF |
| **Build** | PyInstaller (single-file, no console) |
| **Persistence** | SQLAlchemy + migration system |
| **Background** | System Tray (pystray / infi.systray) |
| **Testing** | pytest + coverage |

## Features

- **Invoice Management**: Full CRUD for invoices with Colombian tax formatting
- **PDF Export**: Professional invoice generation with company branding
- **Audit System**: Complete action log with timestamps and user attribution
- **Database Migrations**: Schema versioning with rollback support
- **System Tray**: Background operation — window hides on close
- **Portable Build**: Single `.exe` with no runtime dependencies
- **Backup System**: Automated database backups with rotation
- **Dashboard**: Real-time financial summary metrics

## Quick Start

### Development
```bash
pip install -r requirements.txt
python main.py
```

### Production Build
```bash
pyinstaller --noconsole --onefile --name "InvoicingERP" ^
  --add-data "assets;assets" ^
  --icon "assets/app.ico" ^
  main.py
```

## System Tray Behavior

| Action | Result |
|--------|--------|
| Click X | Window hides (continues in tray) |
| Right-click tray icon | Context menu: Open / Exit |
| Double-click tray icon | Restore window |

## Project Structure
```
├── app/                  # Application modules
│   ├── controllers/      # Business logic
│   ├── models/           # SQLAlchemy models
│   ├── views/            # UI screens
│   └── utils/            # Helpers (PDF, audit, export)
├── assets/               # Icons, images
├── data/                 # SQLite databases
├── backups/              # Automatic backups
├── tests/                # pytest suite
├── main.py               # Entry point
└── requirements.txt      # Dependencies
```