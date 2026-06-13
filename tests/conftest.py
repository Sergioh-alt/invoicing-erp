"""
Fixtures compartidas para tests de Facturas GanaTodo
"""
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from app.model.database import Database


@pytest.fixture(scope="function")
def temp_db():
    """
    Crea una base de datos temporal completamente nueva para cada test.
    Garantiza aislamiento total entre tests.
    """
    import tempfile
    import os
    import shutil
    import uuid
    
    # Crear directorio temporal único con UUID
    test_id = str(uuid.uuid4())[:8]
    temp_dir = tempfile.mkdtemp(prefix=f"facturas_test_{test_id}_")
    db_path = os.path.join(temp_dir, f"test_{test_id}.db")
    
    # Asegurar que NO existe antes
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Crear y inicializar BD fresca
    db = Database(db_path)
    db.initialize()
    
    yield db
    
    # Cleanup agresivo
    try:
        # Cerrar todas las conexiones
        del db
    except:
        pass
    
    # Esperar un momento para cerrar conexiones
    import time
    time.sleep(0.05)
    
    # Eliminar directorio completo
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass


@pytest.fixture
def temp_db_file():
    """
    Crea una base de datos temporal en archivo real.
    Útil para tests que necesitan persistencia o verificar archivos.
    """
    # Crear archivo temporal
    fd, path = tempfile.mkstemp(suffix='.sqlite')
    os.close(fd)
    
    db = Database(path)
    db.initialize()
    
    yield db, path
    
    # Cleanup: eliminar archivo temporal
    try:
        os.unlink(path)
    except:
        pass


@pytest.fixture
def sample_factura():
    """
    Datos de ejemplo de una factura para tests.
    Retorna dict con todos los campos necesarios.
    """
    return {
        "numero_factura": "F-TEST-001",
        "proveedor": "Acme Corporation S.A.",
        "valor": 1500.50,
        "notas": "Factura de prueba para testing",
        "fecha_vencimiento": (datetime.now() + timedelta(days=10)).isoformat(),
        "estado": "Pendiente",
        "hora_alerta_1": "09:00",
        "hora_alerta_2": "14:00",
        "hora_alerta_3": "18:00",
        "pdf_path": None
    }


@pytest.fixture
def multiple_facturas():
    """
    Lista de múltiples facturas para tests de batch.
    Retorna lista de dicts.
    """
    base_date = datetime.now()
    facturas = []
    
    for i in range(1, 6):  # 5 facturas
        facturas.append({
            "numero_factura": f"F-TEST-{i:03d}",
            "proveedor": f"Proveedor {i} S.A.",
            "valor": 1000.0 * i,
            "notas": f"Factura de prueba #{i}",
            "fecha_vencimiento": (base_date + timedelta(days=i*2)).isoformat(),
            "estado": "Pendiente" if i % 2 == 0 else "Pagada",
            "hora_alerta_1": "09:00",
            "hora_alerta_2": "14:00",
            "hora_alerta_3": "18:00",
            "pdf_path": None
        })
    
    return facturas


@pytest.fixture
def factura_vencida():
    """Factura con fecha de vencimiento en el pasado."""
    return {
        "numero_factura": "F-VENC-001",
        "proveedor": "Proveedor Vencido S.A.",
        "valor": 500.00,
        "notas": "Factura vencida",
        "fecha_vencimiento": (datetime.now() - timedelta(days=5)).isoformat(),
        "estado": "Pendiente",
        "hora_alerta_1": "10:00",
        "hora_alerta_2": "15:00",
        "hora_alerta_3": "17:00",
        "pdf_path": None
    }


@pytest.fixture
def factura_hoy():
    """Factura que vence hoy."""
    now = datetime.now()
    vence_hoy = now.replace(hour=23, minute=59, second=59)
    
    return {
        "numero_factura": "F-HOY-001",
        "proveedor": "Proveedor Urgente S.A.",
        "valor": 2500.00,
        "notas": "Vence hoy",
        "fecha_vencimiento": vence_hoy.isoformat(),
        "estado": "Pendiente",
        "hora_alerta_1": "09:00",
        "hora_alerta_2": "12:00",
        "hora_alerta_3": "15:00",
        "pdf_path": None
    }


@pytest.fixture
def sample_pdf_data():
    """
    Datos de ejemplo extraídos de un PDF.
    Simula el resultado de pdf_extractor.
    """
    return {
        "success": True,
        "numero_factura": "FVE 12345",
        "proveedor": "EMPRESA DEMO S.A.S",
        "valor": 1234.56,
        "fecha_vencimiento": datetime.now() + timedelta(days=15),
        "notas": "Datos extraídos automáticamente del PDF"
    }


@pytest.fixture
def mock_pdf_file():
    """
    Crea un archivo PDF temporal falso para tests.
    No es un PDF real, solo simula la existencia del archivo.
    """
    fd, path = tempfile.mkstemp(suffix='.pdf')
    os.close(fd)
    
    # Escribir contenido dummy (no es un PDF válido, solo para tests de existencia)
    with open(path, 'wb') as f:
        f.write(b'%PDF-1.4\nDummy PDF for testing\n%%EOF\n')
    
    yield path
    
    # Cleanup
    try:
        os.unlink(path)
    except:
        pass


# Fixtures para validación
@pytest.fixture
def valid_invoice_numbers():
    """Números de factura válidos para tests de validación."""
    return [
        "F-001",
        "FAC-2024-001",
        "INV-123456",
        "FVE 12345",
        "FACT001",
        "A-123-B"
    ]


@pytest.fixture
def invalid_invoice_numbers():
    """Números de factura inválidos para tests de validación."""
    return [
        "",           # Vacío
        "   ",        # Solo espacios
        None,         # None
        "F",          # Muy corto
        "123",        # Solo números (dependiendo de reglas)
    ]


# Fixture para tiempos
@pytest.fixture
def valid_times():
    """Tiempos válidos en formato HH:MM."""
    return ["00:00", "09:30", "14:45", "23:59"]


@pytest.fixture
def invalid_times():
    """Tiempos inválidos."""
    return ["25:00", "12:60", "abc", "", "12:5", "1:30"]


# Helper para limpiar base de datos entre tests
@pytest.fixture(autouse=True)
def reset_test_state():
    """
    Se ejecuta automáticamente antes de cada test.
    Útil para limpiar estados globales si los hay.
    """
    # Antes del test
    yield
    # Después del test (cleanup)
    pass
