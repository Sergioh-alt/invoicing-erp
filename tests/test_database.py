"""
Tests para app/model/database.py
Prueba operaciones CRUD y funcionalidad de la base de datos.
"""
import pytest
from datetime import datetime, timedelta
from app.model.database import Database


@pytest.mark.database
@pytest.mark.unit
class TestDatabaseInitialization:
    """Tests de inicialización de base de datos."""
    
    def test_create_database_in_memory(self, temp_db):
        """Test: Crear BD temporal"""
        assert temp_db is not None
        assert temp_db.db_path is not None
        assert len(temp_db.db_path) > 0
    
    def test_create_database_with_file(self, temp_db_file):
        """Test: Crear BD en archivo"""
        db, path = temp_db_file
        assert db is not None
        assert path.endswith('.sqlite')
        import os
        assert os.path.exists(path)
    
    def test_schema_version_is_set(self, temp_db):
        """Test: Versión del schema se establece correctamente"""
        with temp_db.connect() as conn:
            row = conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
            assert row is not None
            assert int(row["value"]) == 4  # SCHEMA_VERSION actual


@pytest.mark.database
@pytest.mark.unit
class TestAddFactura:
    """Tests para agregar facturas."""
    
    def test_add_factura_basic(self, temp_db, sample_factura):
        """Test: Agregar factura básica"""
        factura_id = temp_db.add_factura(
            sample_factura["numero_factura"],
            sample_factura["proveedor"],
            sample_factura["valor"],
            sample_factura["notas"],
            sample_factura["fecha_vencimiento"],
            sample_factura["hora_alerta_1"],
            sample_factura["hora_alerta_2"],
            sample_factura["hora_alerta_3"]
        )
        
        assert factura_id > 0
        assert isinstance(factura_id, int)
    
    def test_add_factura_returns_unique_ids(self, temp_db, sample_factura):
        """Test: Cada factura obtiene un ID único"""
        id1 = temp_db.add_factura(
            "F-001", "Proveedor 1", 100.0, "", datetime.now().isoformat(),
            "09:00", "14:00", "18:00"
        )
        id2 = temp_db.add_factura(
            "F-002", "Proveedor 2", 200.0, "", datetime.now().isoformat(),
            "09:00", "14:00", "18:00"
        )
        
        assert id1 != id2
        assert id2 == id1 + 1
    
    def test_add_factura_with_pdf_path(self, temp_db, sample_factura):
        """Test: Agregar factura con ruta de PDF"""
        pdf_path = "/path/to/factura.pdf"
        factura_id = temp_db.add_factura(
            sample_factura["numero_factura"],
            sample_factura["proveedor"],
            sample_factura["valor"],
            sample_factura["notas"],
            sample_factura["fecha_vencimiento"],
            sample_factura["hora_alerta_1"],
            sample_factura["hora_alerta_2"],
            sample_factura["hora_alerta_3"],
            pdf_path=pdf_path
        )
        
        # Verificar que se guardó
        facturas = temp_db.list_facturas()
        factura = next((f for f in facturas if f["id"] == factura_id), None)
        
        assert factura is not None
        assert factura["pdf_path"] == pdf_path
    
    def test_add_factura_with_none_values(self, temp_db):
        """Test: Agregar factura con valores opcionales None"""
        factura_id = temp_db.add_factura(
            "F-001",
            None,  # proveedor
            None,  # valor
            None,  # notas
            datetime.now().isoformat(),
            "", "", ""  # horas vacías
        )
        
        assert factura_id > 0
        
        facturas = temp_db.list_facturas()
        factura = facturas[0]
        
        assert factura["proveedor"] is None
        assert factura["valor"] is None


@pytest.mark.database
@pytest.mark.unit
class TestListFacturas:
    """Tests para listar facturas."""
    
    def test_list_empty_database(self, temp_db):
        """Test: Listar facturas en BD vacía"""
        facturas = temp_db.list_facturas()
        assert facturas == []
        assert len(facturas) == 0
    
    def test_list_single_factura(self, temp_db, sample_factura):
        """Test: Listar una sola factura"""
        temp_db.add_factura(
            sample_factura["numero_factura"],
            sample_factura["proveedor"],
            sample_factura["valor"],
            sample_factura["notas"],
            sample_factura["fecha_vencimiento"],
            sample_factura["hora_alerta_1"],
            sample_factura["hora_alerta_2"],
            sample_factura["hora_alerta_3"]
        )
        
        facturas = temp_db.list_facturas()
        assert len(facturas) == 1
        assert facturas[0]["numero_factura"] == sample_factura["numero_factura"]
    
    def test_list_multiple_facturas(self, temp_db, multiple_facturas):
        """Test: Listar múltiples facturas"""
        # Agregar todas las facturas
        for f in multiple_facturas:
            temp_db.add_factura(
                f["numero_factura"], f["proveedor"], f["valor"], f["notas"],
                f["fecha_vencimiento"], f["hora_alerta_1"], f["hora_alerta_2"], f["hora_alerta_3"]
            )
        
        facturas = temp_db.list_facturas()
        assert len(facturas) == len(multiple_facturas)
    
    def test_filter_by_status_pendiente(self, temp_db, multiple_facturas):
        """Test: Filtrar por estado Pendiente"""
        # Agregar facturas y marcar algunas como pagadas según fixture
        for f in multiple_facturas:
            fid = temp_db.add_factura(
                f["numero_factura"], f["proveedor"], f["valor"], f["notas"],
                f["fecha_vencimiento"], "", "", ""
            )
            # Marcar como pagada si corresponde (según fixture: impares son Pagadas)
            if f["estado"] == "Pagada":
                temp_db.mark_pagada(fid)
        
        pendientes = temp_db.list_facturas(status_filter="Pendiente")
        expected_count = sum(1 for f in multiple_facturas if f["estado"] == "Pendiente")
        
        assert len(pendientes) == expected_count
        assert all(f["estado"] == "Pendiente" for f in pendientes)
    
    def test_search_by_numero_factura(self, temp_db, multiple_facturas):
        """Test: Buscar por número de factura"""
        for f in multiple_facturas:
            temp_db.add_factura(
                f["numero_factura"], f["proveedor"], f["valor"], f["notas"],
                f["fecha_vencimiento"], "", "", ""
            )
        
        # Buscar "001"
        resultados = temp_db.list_facturas(search="001")
        assert len(resultados) == 1
        assert "001" in resultados[0]["numero_factura"]
    
    def test_search_by_proveedor(self, temp_db, multiple_facturas):
        """Test: Buscar por proveedor"""
        for f in multiple_facturas:
            temp_db.add_factura(
                f["numero_factura"], f["proveedor"], f["valor"], f["notas"],
                f["fecha_vencimiento"], "", "", ""
            )
        
        # Buscar "Proveedor 1"
        resultados = temp_db.list_facturas(search="Proveedor 1")
        assert len(resultados) == 1
        assert "Proveedor 1" in resultados[0]["proveedor"]


@pytest.mark.database
@pytest.mark.unit
class TestUpdateFactura:
    """Tests para actualizar facturas."""
    
    def test_update_factura_basic(self, temp_db, sample_factura):
        """Test: Actualizar factura completa"""
        # Crear factura
        factura_id = temp_db.add_factura(
            sample_factura["numero_factura"],
            sample_factura["proveedor"],
            sample_factura["valor"],
            sample_factura["notas"],
            sample_factura["fecha_vencimiento"],
            "", "", ""
        )
        
        # Actualizar
        temp_db.update_factura(
            factura_id,
            "F-UPDATED",  # Nuevo número
            "Nuevo Proveedor",
            2000.00,  # Nuevo valor
            "Notas actualizadas",
            sample_factura["fecha_vencimiento"],
            "Pendiente",
            "10:00", "15:00", "20:00"
        )
        
        # Verificar
        facturas = temp_db.list_facturas()
        factura = facturas[0]
        
        assert factura["numero_factura"] == "F-UPDATED"
        assert factura["proveedor"] == "Nuevo Proveedor"
        assert factura["valor"] == 2000.00
        assert factura["notas"] == "Notas actualizadas"
    
    def test_update_preserves_pdf_path(self, temp_db, sample_factura):
        """Test: Actualizar preserva pdf_path"""
        pdf_path = "/path/to/original.pdf"
        
        # Crear con PDF
        factura_id = temp_db.add_factura(
            sample_factura["numero_factura"],
            sample_factura["proveedor"],
            sample_factura["valor"],
            sample_factura["notas"],
            sample_factura["fecha_vencimiento"],
            "", "", "",
            pdf_path=pdf_path
        )
        
        # Actualizar pasando el mismo pdf_path
        temp_db.update_factura(
            factura_id,
            "F-UPDATED",
            sample_factura["proveedor"],
            sample_factura["valor"],
            sample_factura["notas"],
            sample_factura["fecha_vencimiento"],
            "Pendiente",
            "", "", "",
            pdf_path=pdf_path
        )
        
        # Verificar que se preservó
        facturas = temp_db.list_facturas()
        assert facturas[0]["pdf_path"] == pdf_path


@pytest.mark.database
@pytest.mark.unit
class TestDeleteFactura:
    """Tests para eliminar facturas."""
    
    def test_delete_factura(self, temp_db, sample_factura):
        """Test: Eliminar factura"""
        # Crear
        factura_id = temp_db.add_factura(
            sample_factura["numero_factura"],
            sample_factura["proveedor"],
            sample_factura["valor"],
            sample_factura["notas"],
            sample_factura["fecha_vencimiento"],
            "", "", ""
        )
        
        # Verificar que existe
        assert len(temp_db.list_facturas()) == 1
        
        # Eliminar
        temp_db.delete_factura(factura_id)
        
        # Verificar que se eliminó
        assert len(temp_db.list_facturas()) == 0
    
    def test_delete_nonexistent_factura(self, temp_db):
        """Test: Eliminar factura inexistente no causa error"""
        # No debería lanzar excepción
        temp_db.delete_factura(9999)
        assert len(temp_db.list_facturas()) == 0


@pytest.mark.database
@pytest.mark.unit
class TestMarkPagada:
    """Tests para marcar facturas como pagadas."""
    
    def test_mark_pagada(self, temp_db, sample_factura):
        """Test: Marcar factura como pagada"""
        # Crear factura pendiente
        factura_id = temp_db.add_factura(
            sample_factura["numero_factura"],
            sample_factura["proveedor"],
            sample_factura["valor"],
            sample_factura["notas"],
            sample_factura["fecha_vencimiento"],
            "", "", ""
        )
        
        # Marcar como pagada
        temp_db.mark_pagada(factura_id)
        
        # Verificar
        facturas = temp_db.list_facturas()
        assert facturas[0]["estado"] == "Pagada"


@pytest.mark.database
@pytest.mark.unit
class TestSnooze:
    """Tests para funcionalidad de snooze."""
    
    def test_set_snooze(self, temp_db, sample_factura):
        """Test: Establecer snooze"""
        factura_id = temp_db.add_factura(
            sample_factura["numero_factura"],
            sample_factura["proveedor"],
            sample_factura["valor"],
            sample_factura["notas"],
            sample_factura["fecha_vencimiento"],
            "", "", ""
        )
        
        snooze_until = (datetime.now() + timedelta(minutes=30)).isoformat()
        temp_db.set_snooze_until(factura_id, snooze_until)
        
        # Verificar
        facturas = temp_db.list_facturas()
        assert facturas[0]["snooze_until"] == snooze_until
    
    def test_clear_snooze(self, temp_db, sample_factura):
        """Test: Limpiar snooze"""
        factura_id = temp_db.add_factura(
            sample_factura["numero_factura"],
            sample_factura["proveedor"],
            sample_factura["valor"],
            sample_factura["notas"],
            sample_factura["fecha_vencimiento"],
            "", "", ""
        )
        
        # Establecer snooze
        snooze_until = (datetime.now() + timedelta(minutes=30)).isoformat()
        temp_db.set_snooze_until(factura_id, snooze_until)
        
        # Limpiar
        temp_db.clear_snooze(factura_id)
        
        # Verificar
        facturas = temp_db.list_facturas()
        assert facturas[0]["snooze_until"] is None
