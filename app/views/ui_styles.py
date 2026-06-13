def qss_dark_premium() -> str:
    return """
    * { font-family: 'Segoe UI'; font-size: 10.5pt; }
    QWidget { background: #0b1220; color: #e5e7eb; }
    
    /* Sidebar */
    QFrame#sidebar { background: #0f172a; border-right: 1px solid rgba(255,255,255,0.08); }
    
    /* KPI Cards */
    QFrame#KPI {
        background: rgba(15,26,47,0.92);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
    }
    
    /* Labels */
    QLabel#H1 { font-size: 18pt; font-weight: 900; color: #f9fafb; }
    QLabel#Muted { color: rgba(229,231,235,0.72); }
    QLabel#KpiNumber { font-size: 22pt; font-weight: 950; }
    QLabel#KpiLabel { color: rgba(229,231,235,0.70); font-weight: 800; letter-spacing: 0.5px; }
    QLabel { color: #e5e7eb; }
    
    /* Buttons */
    QPushButton {
        background: rgba(22,163,74,0.92);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 10px;
        padding: 8px 12px;
        font-weight: 800;
        color: white;
    }
    QPushButton:hover { background: rgba(34,197,94,0.92); }
    QPushButton#Secondary { background: rgba(255,255,255,0.08); }
    QPushButton#Danger { background: rgba(239,68,68,0.90); }
    
    /* Input Fields */
    QLineEdit, QTextEdit, QDoubleSpinBox, QComboBox, QDateTimeEdit, QTimeEdit {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 10px;
        padding: 7px 10px;
        color: #e5e7eb;
        selection-background-color: rgba(37,99,235,0.55);
    }
    QComboBox::drop-down { border: none; }
    QComboBox::down-arrow { image: none; }
    
    /* Tables */
    QTableWidget {
        background: #0f1a2f;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        gridline-color: rgba(255,255,255,0.06);
    }
    QHeaderView::section {
        background: rgba(255,255,255,0.06);
        border: 0px;
        padding: 10px;
        font-weight: 900;
        color: rgba(229,231,235,0.85);
    }
    QTableWidget::item { padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    
    /* Scrollbars */
    QScrollBar { background: rgba(255,255,255,0.03); }
    QScrollBar::handle { background: rgba(255,255,255,0.15); border-radius: 4px; }
    
    /* Dialogs */
    QDialog { background: #0b1220; color: #e5e7eb; }
    """

def qss_light_premium() -> str:
    """Tema claro premium."""
    return """
    * { font-family: 'Segoe UI'; font-size: 10.5pt; }
    QWidget { background: #f8fafc; color: #1e293b; }
    
    /* Sidebar */
    QFrame#sidebar { background: #ffffff; border-right: 1px solid rgba(0,0,0,0.08); }
    
    /* KPI Cards */
    QFrame#KPI {
        background: rgba(255,255,255,0.98);
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 18px;
    }
    
    /* Labels */
    QLabel#H1 { font-size: 18pt; font-weight: 900; color: #0f172a; }
    QLabel#Muted { color: rgba(30,41,59,0.72); }
    QLabel#KpiNumber { font-size: 22pt; font-weight: 950; color: #1e293b; }
    QLabel#KpiLabel { color: rgba(30,41,59,0.70); font-weight: 800; letter-spacing: 0.5px; }
    QLabel { color: #1e293b; }
    
    /* Buttons */
    QPushButton {
        background: rgba(22,163,74,0.92);
        border: 1px solid rgba(0,0,0,0.10);
        border-radius: 10px;
        padding: 8px 12px;
        font-weight: 800;
        color: white;
    }
    QPushButton:hover { background: rgba(34,197,94,0.95); }
    QPushButton#Secondary { background: rgba(0,0,0,0.06); color: #1e293b; }
    QPushButton#Danger { background: rgba(239,68,68,0.92); color: white; }
    
    /* Input Fields */
    QLineEdit, QTextEdit, QDoubleSpinBox, QComboBox, QDateTimeEdit, QTimeEdit {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.12);
        border-radius: 10px;
        padding: 7px 10px;
        color: #1e293b;
        selection-background-color: rgba(37,99,235,0.25);
    }
    QComboBox::drop-down { border: none; }
    QComboBox::down-arrow { image: none; }
    
    /* Tables */
    QTableWidget {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 14px;
        gridline-color: rgba(0,0,0,0.06);
    }
    QHeaderView::section {
        background: rgba(0,0,0,0.04);
        border: 0px;
        padding: 10px;
        font-weight: 900;
        color: rgba(30,41,59,0.85);
    }
    QTableWidget::item { padding: 8px; border-bottom: 1px solid rgba(0,0,0,0.04); }
    
    /* Scrollbars */
    QScrollBar { background: rgba(0,0,0,0.03); }
    QScrollBar::handle { background: rgba(0,0,0,0.15); border-radius: 4px; }
    
    /* Dialogs */
    QDialog { background: #f8fafc; color: #1e293b; }
    """
