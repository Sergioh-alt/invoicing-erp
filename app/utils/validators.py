"""
Validadores de datos para Facturas GanaTodo.
"""
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger("FacturasGanaTodo.validators")


class ValidationError(Exception):
    """Excepción personalizada para errores de validación."""
    pass


def validate_numero_factura(numero: str) -> str:
    """
    Valida número de factura.
    
    Args:
        numero: Número de factura a validar
        
    Returns:
        Número de factura validado y limpio
        
    Raises:
        ValidationError: Si la validación falla
    """
    numero = numero.strip()
    
    if not numero:
        raise ValidationError("El número de factura es obligatorio")
    
    if len(numero) > 100:
        raise ValidationError("El número de factura es demasiado largo (máximo 100 caracteres)")
    
    # Validar caracteres permitidos (opcional)
    # if not re.match(r'^[A-Za-z0-9\-_]+$', numero):
    #     raise ValidationError("El número de factura contiene caracteres no válidos")
    
    logger.debug(f"Número de factura validado: {numero}")
    return numero


def validate_proveedor(proveedor: Optional[str]) -> Optional[str]:
    """
    Valida nombre de proveedor.
    
    Args:
        proveedor: Nombre del proveedor (puede ser None)
        
    Returns:
        Nombre del proveedor validado o None
    """
    if not proveedor:
        return None
    
    proveedor = proveedor.strip()
    
    if len(proveedor) > 200:
        raise ValidationError("El nombre del proveedor es demasiado largo (máximo 200 caracteres)")
    
    return proveedor


def validate_valor(valor: Optional[float], moneda: str = "USD") -> float:
    """
    Valida monto monetario.
    
    Args:
        valor: Valor a validar
        moneda: Código de moneda (para contexto en errores)
        
    Returns:
        Valor validado y redondeado a 2 decimales
        
    Raises:
        ValidationError: Si el valor es inválido
    """
    if valor is None:
        return 0.0
    
    if valor < 0:
        raise ValidationError("El valor no puede ser negativo")
    
    if valor > 999_999_999.99:
        raise ValidationError("El valor excede el límite permitido (999,999,999.99)")
    
    # Redondear a 2 decimales
    valor_redondeado = round(valor, 2)
    
    logger.debug(f"Valor validado: {valor_redondeado} {moneda}")
    return valor_redondeado


def validate_datetime_iso(dt_iso: str) -> datetime:
    """
    Valida y parsea fecha en formato ISO.
    
    Args:
        dt_iso: String de fecha en formato ISO
        
    Returns:
        Objeto datetime validado
        
    Raises:
        ValidationError: Si el formato es inválido o la fecha está fuera de rango
    """
    try:
        dt = datetime.fromisoformat(dt_iso)
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Formato de fecha inválido: {e}")
    
    # Validar rango de años razonable
    if dt.year < 2000:
        raise ValidationError("El año no puede ser anterior a 2000")
    
    if dt.year > 2100:
        raise ValidationError("El año no puede ser posterior a 2100")
    
    logger.debug(f"Fecha validada: {dt.isoformat()}")
    return dt


def validate_time_hhmm(time_str: Optional[str]) -> Optional[str]:
    """
    Valida formato de hora HH:MM.
    
    Args:
        time_str: String de hora en formato HH:MM
        
    Returns:
        String validado en formato HH:MM o None
        
    Raises:
        ValidationError: Si el formato es inválido
    """
    if not time_str:
        return None
    
    time_str = time_str.strip()
    
    try:
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError("Debe contener exactamente un ':'")
        
        hour = int(parts[0])
        minute = int(parts[1])
        
        if hour < 0 or hour > 23:
            raise ValueError("La hora debe estar entre 0 y 23")
        
        if minute < 0 or minute > 59:
            raise ValueError("Los minutos deben estar entre 0 y 59")
        
        # Retornar en formato normalizado
        return f"{hour:02d}:{minute:02d}"
    
    except (ValueError, AttributeError) as e:
        raise ValidationError(f"Formato de hora inválido (debe ser HH:MM): {e}")


def validate_codigo_activacion(codigo: str) -> bool:
    """
    Valida código de activación.
    
    Args:
        codigo: Código de activación ingresado
        
    Returns:
        True si el código es válido, False en caso contrario
    """
    codigo_valido = "SHEDULE-36-2"
    es_valido = codigo.strip().upper() == codigo_valido
    
    if es_valido:
        logger.info("Código de activación válido ingresado")
    else:
        logger.warning(f"Intento de activación con código inválido: {codigo}")
    
    return es_valido


def validate_moneda(moneda: str, monedas_permitidas: list[str]) -> str:
    """
    Valida código de moneda.
    
    Args:
        moneda: Código de moneda (ej: USD, EUR)
        monedas_permitidas: Lista de códigos de moneda permitidos
        
    Returns:
        Código de moneda validado
        
    Raises:
        ValidationError: Si la moneda no está permitida
    """
    moneda = moneda.strip().upper()
    
    if moneda not in monedas_permitidas:
        raise ValidationError(
            f"Moneda '{moneda}' no permitida. Monedas válidas: {', '.join(monedas_permitidas)}"
        )
    
    return moneda


def validate_notas(notas: Optional[str], max_length: int = 5000) -> Optional[str]:
    """
    Valida campo de notas.
    
    Args:
        notas: Texto de notas
        max_length: Longitud máxima permitida
        
    Returns:
        Notas validadas o None
        
    Raises:
        ValidationError: Si excede la longitud máxima
    """
    if not notas:
        return None
    
    notas = notas.strip()
    
    if len(notas) > max_length:
        raise ValidationError(f"Las notas exceden la longitud máxima ({max_length} caracteres)")
    
    return notas
