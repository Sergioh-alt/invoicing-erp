"""
Tests para Facturas GanaTodo v5.0

Esta carpeta contiene tests automatizados usando pytest.

Estructura:
- conftest.py: Fixtures compartidas
- test_database.py: Tests de operaciones de BD
- test_validators.py: Tests de validaciones
- test_datetime_helpers.py: Tests de utilidades de fecha/hora
- test_pdf_extractor.py: Tests de extracción de PDFs
- test_export.py: Tests de exportación

Ejecutar tests:
    pytest                          # Todos los tests
    pytest -v                       # Verbose
    pytest tests/test_database.py   # Solo tests de database
    pytest -k "factura"             # Tests que contengan "factura"
    pytest --cov                    # Con cobertura

Markers disponibles:
    @pytest.mark.slow: Tests lentos (>1 segundo)
    @pytest.mark.unit: Tests unitarios
    @pytest.mark.integration: Tests de integración
    @pytest.mark.database: Tests que usan BD
    @pytest.mark.pdf: Tests relacionados con PDFs
"""
