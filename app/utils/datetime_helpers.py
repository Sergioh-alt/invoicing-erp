"""
Utilidades de fecha y hora consolidadas.
Elimina duplicación de código en múltiples módulos.
"""
from datetime import datetime, time
from typing import Optional
import logging

logger = logging.getLogger("FacturasGanaTodo.datetime_helpers")


def parse_iso_safe(iso_str: Optional[str]) -> Optional[datetime]:
    """
    Parse ISO datetime string, returns None on error.
    
    Args:
        iso_str: String en formato ISO 8601
        
    Returns:
        datetime object o None si hay error
        
    Examples:
        >>> parse_iso_safe("2026-01-18T10:30:00")
        datetime(2026, 1, 18, 10, 30, 0)
        >>> parse_iso_safe("invalid")
        None
        >>> parse_iso_safe(None)
        None
    """
    if not iso_str:
        return None
    
    try:
        return datetime.fromisoformat(iso_str)
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Error parsing ISO datetime '{iso_str}': {e}")
        return None


def parse_time_hhmm(hhmm: Optional[str]) -> Optional[time]:
    """
    Parse HH:MM format, returns None on error.
    
    Args:
        hhmm: String en formato HH:MM (ej: "09:30")
        
    Returns:
        time object o None si hay error
        
    Examples:
        >>> parse_time_hhmm("09:30")
        time(9, 30)
        >>> parse_time_hhmm("25:00")
        None
        >>> parse_time_hhmm("invalid")
        None
    """
    if not hhmm:
        return None
    
    try:
        parts = hhmm.strip().split(":")
        if len(parts) != 2:
            return None
        
        hour = int(parts[0])
        minute = int(parts[1])
        
        # Validar rangos
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return None
        
        return time(hour=hour, minute=minute)
    
    except (ValueError, AttributeError, IndexError) as e:
        logger.debug(f"Error parsing time '{hhmm}': {e}")
        return None


def format_datetime_display(dt: datetime, include_time: bool = True) -> str:
    """
    Formatea datetime para mostrar al usuario.
    
    Args:
        dt: datetime a formatear
        include_time: Si incluir la hora o solo la fecha
        
    Returns:
        String formateado
        
    Examples:
        >>> dt = datetime(2026, 1, 18, 14, 30)
        >>> format_datetime_display(dt, True)
        "18/01/2026 02:30 PM"
        >>> format_datetime_display(dt, False)
        "18/01/2026"
    """
    if include_time:
        return dt.strftime("%d/%m/%Y %I:%M %p")
    else:
        return dt.strftime("%d/%m/%Y")


def now_local() -> datetime:
    """
    Retorna datetime actual sin microsegundos.
    
    Returns:
        datetime actual con microsegundos en 0
    """
    return datetime.now().replace(microsecond=0)


def is_same_day(dt1: datetime, dt2: datetime) -> bool:
    """
    Verifica si dos datetimes son del mismo día.
    
    Args:
        dt1: Primer datetime
        dt2: Segundo datetime
        
    Returns:
        True si son del mismo día
    """
    return dt1.date() == dt2.date()


def is_due_date_trigger(now: datetime, due: datetime, days_before: int) -> bool:
    """
    Verifica si es momento de disparar alerta X días antes del vencimiento.
    
    Args:
        now: Fecha/hora actual
        due: Fecha/hora de vencimiento
        days_before: Días antes del vencimiento
        
    Returns:
        True si corresponde disparar la alerta
    """
    days_diff = (due.date() - now.date()).days
    return days_diff == days_before


def days_until(target: datetime, reference: Optional[datetime] = None) -> int:
    """
    Calcula días hasta una fecha objetivo.
    
    Args:
        target: Fecha objetivo
        reference: Fecha de referencia (por defecto: ahora)
        
    Returns:
        Número de días (negativo si ya pasó)
    """
    if reference is None:
        reference = now_local()
    
    delta = target.date() - reference.date()
    return delta.days
