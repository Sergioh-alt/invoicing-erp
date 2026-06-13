"""
Generador de comprobantes de pago en PDF.
Genera PDFs profesionales cuando una factura es marcada como pagada.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
from typing import Optional
import os
import logging

logger = logging.getLogger("FacturasGanaTodo.payment_receipt")


class PaymentReceiptGenerator:
    """Genera comprobantes de pago en PDF."""
    
    def generate_receipt(self, factura_data: dict, output_path: str) -> bool:
        """
        Genera un comprobante de pago en PDF.
        
        Args:
            factura_data: Diccionario con datos de la factura
            output_path: Ruta completa donde guardar el PDF
            
        Returns:
            True si se generó exitosamente, False en caso contrario
        """
        try:
            # Crear documento
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            # Contenido
            story = []
            styles = getSampleStyleSheet()
            
            # Estilo personalizado para título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            # Título
            title = Paragraph("COMPROBANTE DE PAGO", title_style)
            story.append(title)
            story.append(Spacer(1, 0.3*inch))
            
            # Fecha de emisión del comprobante
            fecha_pago = datetime.now()
            fecha_text = Paragraph(
                f"<b>Fecha de emisión:</b> {fecha_pago.strftime('%d/%m/%Y %H:%M')}",
                styles['Normal']
            )
            story.append(fecha_text)
            story.append(Spacer(1, 0.2*inch))
            
            # Datos de la factura en tabla
            data = [
                ['CONCEPTO', 'DETALLE'],
                ['Número de Factura:', factura_data.get('numero_factura', 'N/A')],
                ['Proveedor:', factura_data.get('proveedor', 'N/A')],
                ['Monto Pagado:', f"${factura_data.get('valor', 0):,.2f}"],
                ['Fecha Vencimiento Original:', self._format_date(factura_data.get('fecha_vencimiento'))],
                ['Fecha de Pago:', fecha_pago.strftime('%d/%m/%Y')],
                ['Estado:', 'PAGADA ✓'],
            ]
            
            # Agregar notas si existen
            if factura_data.get('notas'):
                data.append(['Notas:', factura_data.get('notas', '')[:100]])  # Limitar a 100 caracteres
            
            # Crear tabla
            table = Table(data, colWidths=[2.5*inch, 4*inch])
            table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Data
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('LEFTPADDING', (0, 1), (-1, -1), 10),
                
                # Borders
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1e40af')),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.5*inch))
            
            # Nota al pie
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=10
            )
            
            footer_text = Paragraph(
                "Este comprobante fue generado automáticamente por Facturas GanaTodo.<br/>"
                "Para cualquier consulta, conserve este documento.",
                footer_style
            )
            story.append(footer_text)
            
            # Construir PDF
            doc.build(story)
            
            logger.info(f"Comprobante generado exitosamente: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generando comprobante de pago: {e}", exc_info=True)
            return False
    
    def _format_date(self, date_str: Optional[str]) -> str:
        """Formatea fecha ISO a formato legible."""
        if not date_str:
            return "N/A"
        
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            return date_str
