"""
Funciones helper para formateo de datos en la aplicación.
Movido desde ui_main.py para mejor organización.
"""
from datetime import datetime
from PySide6 import QtGui
from app.services.snooze_manager import snooze_status


def parse_iso(s: str):
    """
    Parsea string ISO a datetime.
    
    Args:
        s: String en formato ISO
        
    Returns:
        datetime object o None si falla
    """
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def compute_counts(rows):
    """
    Calcula KPIs de facturas (pendientes, vencen hoy, vencidas).
    
    Args:
        rows: Lista de facturas
        
    Returns:
        Tupla (pending, due_today, overdue)
    """
    now = datetime.now()
    pending = due_today = overdue = 0
    
    for r in rows:
        if r.get("estado") != "Pendiente":
            continue
        pending += 1
        
        due = parse_iso(r.get("fecha_vencimiento",""))
        if not due:
            continue
        
        if due.date() == now.date():
            due_today += 1
        
        if due < now:
            overdue += 1
    
    return pending, due_today, overdue


def status_text(row):
    """
    Genera texto de estado y tipo para una factura.
    
    Args:
        row: Dict con datos de factura
        
    Returns:
        Tupla (texto, kind) donde kind es: paid, snoozed, overdue, today, pending
    """
    if row.get("estado") == "Pagada":
        return ("Pagada", "paid")
    
    due = parse_iso(row.get("fecha_vencimiento",""))
    now = datetime.now()
    
    if row.get("snooze_until"):
        is_s, hhmmss, sec = snooze_status(row["snooze_until"])
        if is_s and hhmmss and sec is not None:
            h = sec // 3600
            m = (sec % 3600) // 60
            s = sec % 60
            return (f"Pospuesta (Vuelve: {hhmmss})  ⏳ {h:02d}:{m:02d}:{s:02d}", "snoozed")
    
    if due and due < now:
        return ("Vencida", "overdue")
    
    if due and due.date() == now.date():
        return ("Vence hoy", "today")
    
    return ("Pendiente", "pending")


def kind_color(kind: str) -> QtGui.QColor:
    """
    Retorna color para un tipo de estado.
    
    Args:
        kind: Tipo de estado (paid, snoozed, overdue, today, pending)
        
    Returns:
        QColor correspondiente
    """
    if kind == "paid":
        return QtGui.QColor(34, 197, 94)  # Verde
    
    if kind == "snoozed":
        return QtGui.QColor(245, 158, 11)  # Naranja
    
    if kind == "overdue":
        return QtGui.QColor(239, 68, 68)  # Rojo
    
    if kind == "today":
        return QtGui.QColor(251, 191, 36)  # Amarillo
    
    return QtGui.QColor(229, 231, 235)  # Gris


def remaining_text(row):
    """
    Calcula y formatea el tiempo restante para una factura.
    
    Args:
        row: Dict con datos de factura
        
    Returns:
        String formateado con tiempo restante (ej: "5 días, 3 h" o "-2 h, 30 min")
    """
    due = parse_iso(row.get("fecha_vencimiento",""))
    if not due:
        return "-"
    
    now = datetime.now()
    td = due - now
    total = int(td.total_seconds())
    
    sign = "-" if total < 0 else ""
    total = abs(total)
    
    days = total // 86400
    hours = (total % 86400) // 3600
    minutes = (total % 3600) // 60
    
    if days > 0:
        return f"{sign}{days} días, {hours} h"
    
    if hours > 0:
        return f"{sign}{hours} h, {minutes} min"
    
    return f"{sign}{minutes} min"
