"""
Funciones helper para tests - compatibilidad con nombres simples
"""


def validate_invoice_number(numero):
    """Wrapper para tests - valida número de factura"""
    if numero is None:
        return False
    if not isinstance(numero, str):
        return False
    numero = numero.strip()
    if not numero:
        return False
    if len(numero) > 100:
        return False
    return True


def validate_amount(amount):
    """Wrapper para tests - valida monto"""
    if amount is None:
        return False
    
    # Intentar convertir string a float
    if isinstance(amount, str):
        try:
            amount = float(amount)
        except ValueError:
            return False
    
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return False
    
    if amount < 0:
        return False
    
    return True


def validate_date(date_str):
    """Wrapper para tests - valida fecha ISO"""
    if not date_str or date_str is None:
        return False
    
    try:
        from datetime import datetime
        if isinstance(date_str, str):
            # Intentar parsear como ISO
            if 'T' in date_str:
                datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                datetime.fromisoformat(date_str)
            return True
    except (ValueError, AttributeError):
        return False
    
    return False


def validate_time(time_str):
    """Wrapper para tests - valida hora HH:MM"""
    # Vacío y None son válidos (opcional)
    if not time_str or time_str is None:
        return True
    
    time_str = time_str.strip()
    
    try:
        parts = time_str.split(":")
        if len(parts) != 2:
            return False
        
        hour = int(parts[0])
        minute = int(parts[1])
        
        if hour < 0 or hour > 23:
            return False
        
        if minute < 0 or minute > 59:
            return False
        
        return True
    
    except (ValueError, AttributeError):
        return False
