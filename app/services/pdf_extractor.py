"""
Módulo para extraer información de facturas desde archivos PDF.
Usa PyMuPDF (fitz) para leer PDFs y extraer texto.
"""
import re
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger("FacturasGanaTodo.pdf_extractor")

try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyMuPDF no disponible - extracción de PDF deshabilitada")

try:
    from dateutil import parser as date_parser
    DATEUTIL_AVAILABLE = True
except ImportError:
    DATEUTIL_AVAILABLE = False
    logger.warning("python-dateutil no disponible - parsing de fechas limitado")


class PDFExtractor:
    """Extrae información de facturas desde archivos PDF."""
    
    def __init__(self):
        self.patterns = {
            # Patrones para número de factura (mejorados para facturas electrónicas)
            'numero_factura': [
                r'(?:No\.?\s*|Número\s*:?\s*)?([A-Z]{2,5}\s*\d{4,})',  # FVE 11108, ABC 12345
                r'(?:factura|invoice)\s+(?:electr[óo]nica\s+)?(?:de\s+venta\s+)?(?:No\.?\s*)?([A-Z]{2,5}\s*\d{4,})',
                r'(?:factura|invoice|no\.?|#)\s*:?\s*([A-Z0-9\-]+)',
                r'(?:número|numero)\s*:?\s*([A-Z0-9\-]+)',
            ],
            
            # Patrones para proveedor (mejorados para nombres largos)
            'proveedor': [
                # Buscar nombres corporativos completos en las primeras líneas
                r'^([A-ZÑÁÉÍÓÚ][A-ZÑÁÉÍÓÚa-zñáéíóú\s]{5,60}(?:S\.?A\.?S\.?|S\.?A\.?|LTDA\.?|S\.?L\.?|INC\.?|CORP\.?))',
                r'(?:razón social|razon social|proveedor|supplier|vendedor)\s*:?\s*([A-ZÑÁÉÍÓÚ][A-ZÑÁÉÍÓÚa-zñáéíóú\s]{5,60}(?:S\.?A\.?S\.?|S\.?A\.?|LTDA\.?)?)',
                # Para "COMUNICACIONES GANA TODO APP SAS"
                r'([A-ZÑÁÉÍÓÚ]{3,}\s+[A-ZÑÁÉÍÓÚ\s]{10,60}(?:S\.?A\.?S\.?|S\.?A\.?|LTDA\.?))',
            ],
            
            # Patrones para monto
            'monto': [
                r'(?:total|amount|monto|valor|pagar)\s*:?\s*\$?\s*([\d,\.]+)',
                r'\$\s*([\d,\.]+)\s*(?:USD|COP|EUR|MXN)?',
                r'(?:sub)?total\s*:?\s*\$?\s*([\d,\.]+)',
            ],
            
            # Patrones para fecha de vencimiento (PRIORIDAD a "vencimiento" sobre "expedición")
            'fecha_vencimiento': [
                # Alta prioridad: Líneas que dicen explícitamente "Vencimiento"
                r'vencimiento\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                r'(?:fecha\s+de\s+)?vencimiento\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                r'vence\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                r'due\s+date\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                # Media prioridad: Fechas después de mencionar vencimiento
                r'vencimiento[^\d]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                # Baja prioridad: Cualquier fecha (solo si no se encontró arriba)
                r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
            ],
        }
    
    def extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extrae información de un PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Diccionario con datos extraídos
        """
        if not PDF_AVAILABLE:
            logger.error("PyMuPDF no disponible")
            return self._empty_result()
        
        try:
            # Leer PDF
            doc = fitz.open(pdf_path)
            text = ""
            
            # Extraer texto de todas las páginas (máximo 3 para rendimiento)
            for page_num in range(min(len(doc), 3)):
                page = doc[page_num]
                text += page.get_text()
            
            doc.close()
            
            logger.debug(f"Texto extraído del PDF ({len(text)} caracteres)")
            
            # Extraer información
            result = {
                'numero_factura': self._extract_numero_factura(text),
                'proveedor': self._extract_proveedor(text),
                'valor': self._extract_monto(text),
                'fecha_vencimiento': self._extract_fecha(text),
                'notas': '',  # Dejar vacío - NO incluir nombre del PDF
                'success': True,
            }
            
            logger.info(f"Datos extraídos: {result}")
            return result
        
        except Exception as e:
            logger.exception(f"Error al extraer datos del PDF: {e}")
            return self._empty_result(error=str(e))
    
    def _empty_result(self, error: Optional[str] = None) -> Dict[str, Any]:
        """Retorna resultado vacío."""
        return {
            'numero_factura': '',
            'proveedor': '',
            'valor': 0.0,
            'fecha_vencimiento': None,
            'notas': f"Error: {error}" if error else "No se pudo extraer información",
            'success': False,
        }
    
    def _extract_numero_factura(self, text: str) -> str:
        """Extrae número de factura del texto."""
        for pattern in self.patterns['numero_factura']:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                numero = match.group(1).strip()
                logger.debug(f"Número de factura encontrado: {numero}")
                return numero
        
        logger.warning("No se encontró número de factura")
        return ""
    
    def _extract_proveedor(self, text: str) -> str:
        """Extrae nombre del proveedor."""
        lines = text.split('\n')
        
        # Primero buscar con patrones específicos
        for pattern in self.patterns['proveedor']:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                proveedor = match.group(1).strip()
                # Limpiar espacios múltiples
                proveedor = ' '.join(proveedor.split())
                if len(proveedor) >= 5:  # Mínimo 5 caracteres
                    logger.debug(f"Proveedor encontrado (patrón): {proveedor}")
                    return proveedor
        
        # Buscar en las primeras 10 líneas nombres corporativos
        for line in lines[:10]:
            line = line.strip()
            if len(line) < 5 or len(line) > 100:
                continue
            
            # Si contiene sufijo corporativo (S.A.S, S.A., LTDA, etc.)
            if re.search(r'S\.?A\.?S\.?|S\.?A\.?|LTDA\.?|S\.?L\.?|INC\.?|CORP\.?', line, re.IGNORECASE):
                # Limpiar la línea
                proveedor = ' '.join(line.split())
                logger.debug(f"Proveedor encontrado: {proveedor}")
                return proveedor
            
            # Si es una línea con muchas mayúsculas (probablemente razón social)
            mayusculas = sum(1 for c in line if c.isupper())
            if mayusculas > len(line) * 0.6 and len(line) > 10:  # Más del 60% mayúsculas
                proveedor = ' '.join(line.split())
                logger.debug(f"Proveedor encontrado (mayúsculas): {proveedor}")
                return proveedor
        
        logger.warning("No se encontró proveedor")
        return ""
    
    def _extract_monto(self, text: str) -> float:
        """Extrae monto/valor de la factura."""
        amounts = []
        
        for pattern in self.patterns['monto']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Limpiar y convertir a float
                    amount_str = match.group(1).replace(',', '').replace('.', '')
                    # Asumir últimos 2 dígitos son decimales
                    if len(amount_str) > 2:
                        amount = float(amount_str[:-2] + '.' + amount_str[-2:])
                    else:
                        amount = float(amount_str)
                    
                    if 0 < amount < 999_999_999:
                        amounts.append(amount)
                except (ValueError, IndexError):
                    continue
        
        if amounts:
            # Retornar el mayor (usualmente el total)
            monto = max(amounts)
            logger.debug(f"Monto encontrado: {monto}")
            return monto
        
        logger.warning("No se encontró monto")
        return 0.0
    
    def _extract_fecha(self, text: str) -> Optional[str]:
        """Extrae fecha de vencimiento."""
        for pattern in self.patterns['fecha_vencimiento']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                
                # Intentar parsear la fecha
                if DATEUTIL_AVAILABLE:
                    try:
                        dt = date_parser.parse(date_str, dayfirst=True)
                        fecha_iso = dt.isoformat()
                        logger.debug(f"Fecha encontrada: {fecha_iso}")
                        return fecha_iso
                    except:
                        pass
                
                # Fallback: parseo manual
                try:
                    # Intentar DD/MM/YYYY o DD-MM-YYYY
                    parts = re.split(r'[\/\-\.]', date_str)
                    if len(parts) == 3:
                        day, month, year = parts
                        
                        # Ajustar año de 2 dígitos
                        if len(year) == 2:
                            year = "20" + year
                        
                        dt = datetime(int(year), int(month), int(day))
                        fecha_iso = dt.isoformat()
                        logger.debug(f"Fecha encontrada (manual): {fecha_iso}")
                        return fecha_iso
                except:
                    pass
        
        logger.warning("No se encontró fecha de vencimiento")
        return None


# Instancia global
pdf_extractor = PDFExtractor()


def extract_invoice_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Función helper para extraer datos de PDF.
    
    Args:
        pdf_path: Ruta al archivo PDF
        
    Returns:
        Diccionario con datos extraídos
    """
    return pdf_extractor.extract_from_pdf(pdf_path)
