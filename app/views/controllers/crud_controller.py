"""
CRUDController - Maneja operaciones CRUD de facturas.
Mixin para MainWindowque gestiona creación, edición, eliminación y marcado como pagada.
"""
from PySide6 import QtWidgets
import os
import subprocess
import logging

from app.views.dialog_invoice import InvoiceDialog

logger = logging.getLogger("FacturasGanaTodo.crud")


class CRUDController:
    """
    Controlador de operaciones CRUD para facturas.
    Se usa como mixin en MainWindow.
    
    Requiere que la clase que lo use tenga:
    - self.db: Database
    - self.table: QTableWidget
    - self.refresh_table(): método
    """
    
    def selected_id(self):
        """
        Obtiene el ID de la factura seleccionada en la tabla.
        
        Returns:
            int: ID de la factura o None si no hay selección
        """
        items = self.table.selectedItems()
        if not items:
            return None
        return int(self.table.item(items[0].row(), 0).text())
    
    def add_factura(self):
        """
        Abre diálogo para agregar nueva factura.
        Si se confirma, guarda en BD y refresca tabla.
        """
        dlg = InvoiceDialog(self, title="Nueva factura")
        if dlg.exec():
            p = dlg.get_payload()
            factura_id = self.db.add_factura(
                p["numero_factura"], p["proveedor"], p["valor"], p["notas"], p["fecha_vencimiento"],
                p["hora_alerta_1"], p["hora_alerta_2"], p["hora_alerta_3"]
            )
            
            # Registrar en audit log
            details = f"Factura #{p['numero_factura']} - {p['proveedor']} - ${p['valor']:.2f}"
            self.db.log_audit("CREATE", factura_id, "user", details)
            
            self.refresh_table()
    
    def edit_selected(self):
        """
        Abre diálogo para editar factura seleccionada.
        Preserva el PDF vinculado al actualizar.
        """
        fid = self.selected_id()
        if not fid:
            return
        
        data = next((r for r in self.db.list_facturas() if int(r["id"]) == fid), None)
        if not data:
            return
        
        dlg = InvoiceDialog(self, title="Editar factura", data=data)
        if dlg.exec():
            p = dlg.get_payload()
            
            # Preservar el pdf_path existente al actualizar
            existing_pdf_path = data.get("pdf_path")
            self.db.update_factura(
                fid, p["numero_factura"], p["proveedor"], p["valor"], p["notas"], p["fecha_vencimiento"], p["estado"],
                p["hora_alerta_1"], p["hora_alerta_2"], p["hora_alerta_3"],
                pdf_path=existing_pdf_path
            )
            
            # Registrar en audit log
            details = f"Factura #{p['numero_factura']} actualizada - Estado: {p['estado']}"
            self.db.log_audit("UPDATE", fid, "user", details)
            
            self.refresh_table()
    
    def delete_selected(self):
        """
        Elimina la factura seleccionada después de confirmación.
        """
        fid = self.selected_id()
        if not fid:
            return
        
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("Confirmar")
        msg.setText("¿Eliminar esta factura?")
        msg.setIcon(QtWidgets.QMessageBox.Question)
        btn_yes = msg.addButton("Sí", QtWidgets.QMessageBox.YesRole)
        btn_no = msg.addButton("No", QtWidgets.QMessageBox.NoRole)
        msg.exec()
        
        if msg.clickedButton() == btn_yes:
            # Registrar en audit log ANTES de eliminar
            self.db.log_audit("DELETE", fid, "user", f"Factura ID {fid} eliminada")
            
            self.db.delete_factura(fid)
            self.refresh_table()
    
    def mark_selected_paid(self):
        """
        Marca la factura seleccionada como pagada.
        Si el generador de comprobantes está activado, genera PDF automáticamente.
        """
        # print("★★★ mark_selected_paid CALLED! ★★★")
        
        fid = self.selected_id()
        if not fid:
            # print("No invoice selected")
            return
        
        # print(f"Selected invoice ID: {fid}")
        
        # Obtener datos de factura ANTES de marcar como pagada
        factura_data = next((r for r in self.db.list_facturas() if int(r["id"]) == fid), None)
        # print(f"Factura data: {factura_data}")
        
        # Marcar como pagada
        self.db.mark_pagada(fid)
        
        # Registrar en audit log
        self.db.log_audit("MARK_PAID", fid, "user", f"Factura ID {fid} marcada como pagada")
        
        # NUEVO: Generar comprobante si la función está habilitada
        config = self.cfg_manager.get()
        # print(f"Config loaded: payment_receipt_generator_enabled = {config.payment_receipt_generator_enabled}")
        
        if config.payment_receipt_generator_enabled and factura_data:
            # print("★★★ GENERATING RECEIPT! ★★★")
            self._generate_payment_receipt(fid, factura_data)
        # else:
        #     print(f"NOT generating receipt: enabled={config.payment_receipt_generator_enabled}, has_data={factura_data is not None}")
        
        self.refresh_table()
    
    def _generate_payment_receipt(self, factura_id: int, factura_data: dict):
        """
        Genera un comprobante de pago en PDF.
        
        Args:
            factura_id: ID de la factura
            factura_data: Diccionario con datos de la factura
        """
        from app.services.payment_receipt_generator import PaymentReceiptGenerator
        from datetime import datetime
        
        try:
            # Crear directorio de comprobantes si no existe
            data_dir = os.path.dirname(self.db.db_path)
            receipts_dir = os.path.join(data_dir, "comprobantes_pago")
            os.makedirs(receipts_dir, exist_ok=True)
            
            # Nombre del archivo
            fecha_pago = datetime.now().strftime("%Y%m%d")
            numero_factura = factura_data.get("numero_factura", "SIN_NUMERO").replace("/", "-").replace("\\", "-")
            filename = f"comprobante_{numero_factura}_{fecha_pago}.pdf"
            output_path = os.path.join(receipts_dir, filename)
            
            # Generar PDF
            generator = PaymentReceiptGenerator()
            success = generator.generate_receipt(factura_data, output_path)
            
            if success:
                # Mostrar notificación al usuario
                reply = QtWidgets.QMessageBox.information(
                    self,
                    "Comprobante Generado",
                    f"Se ha generado el comprobante de pago:\n\n{filename}\n\n¿Deseas abrirlo ahora?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.Yes
                )
                
                # Abrir PDF si el usuario lo desea
                if reply == QtWidgets.QMessageBox.Yes:
                    if os.name == 'nt':  # Windows
                        os.startfile(output_path)
                    elif os.name == 'posix' and os.uname().sysname == 'Darwin':  # macOS
                        subprocess.call(['open', output_path])
                    else:  # Linux
                        subprocess.call(['xdg-open', output_path])
                
                logger.info(f"Comprobante generado exitosamente: {output_path}")
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Error",
                    "No se pudo generar el comprobante de pago."
                )
        
        except Exception as e:
            logger.exception(f"Error al generar comprobante de pago: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Error al generar el comprobante de pago:\n{str(e)}"
            )
    
    def _on_table_cell_clicked(self, row: int, column: int):
        """
        Maneja clicks en celdas de la tabla.
        Si se hace click en la columna PDF, abre el PDF vinculado.
        
        Args:
            row: Fila clickeada
            column: Columna clickeada
        """
        # Si clickeó en la columna PDF (índice 10)
        if column == 10:
            # Obtener ID de la factura
            fid_item = self.table.item(row, 0)
            if fid_item:
                factura_id = int(fid_item.text())
                
                # Obtener datos de factura desde BD para leer pdf_path
                data = next((r for r in self.db.list_facturas() if int(r["id"]) == factura_id), None)
                
                if data and data.get("pdf_path"):
                    pdf_path = data["pdf_path"]
                    
                    # Abrir PDF
                    try:
                        if os.path.exists(pdf_path):
                            logger.info(f"Abriendo PDF: {pdf_path}")
                            
                            # Windows
                            if os.name == 'nt':
                                os.startfile(pdf_path)
                            # macOS
                            elif os.name == 'posix' and os.uname().sysname == 'Darwin':
                                subprocess.call(['open', pdf_path])
                            # Linux
                            else:
                                subprocess.call(['xdg-open', pdf_path])
                        else:
                            QtWidgets.QMessageBox.warning(
                                self,
                                "PDF no encontrado",
                                f"El archivo PDF no existe:\n{pdf_path}\n\n"
                                "Es posible que haya sido movido o eliminado."
                            )
                    except Exception as e:
                        logger.exception(f"Error al abrir PDF: {e}")
                        QtWidgets.QMessageBox.critical(
                            self,
                            "Error al Abrir PDF",
                            f"No se pudo abrir el archivo PDF:\n{str(e)}"
                        )
                else:
                    # No tiene PDF vinculado
                    QtWidgets.QMessageBox.information(
                        self,
                        "Sin PDF",
                        "Esta factura no tiene un PDF vinculado."
                    )
