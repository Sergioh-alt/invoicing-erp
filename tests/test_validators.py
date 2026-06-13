"""
Tests para app/utils/validators.py
Prueba funciones de validación de datos.
"""
import pytest
from app.utils.test_validators_helper import (
    validate_invoice_number,
    validate_amount,
    validate_date,
    validate_time
)


@pytest.mark.unit
class TestInvoiceNumberValidation:
    """Tests para validación de números de factura."""
    
    def test_valid_invoice_numbers(self, valid_invoice_numbers):
        """Test: Números de factura válidos son aceptados"""
        for num in valid_invoice_numbers:
            assert validate_invoice_number(num) == True, f"'{num}' debería ser válido"
    
    def test_invalid_invoice_numbers(self, invalid_invoice_numbers):
        """Test: Números de factura inválidos son rechazados"""
        for num in invalid_invoice_numbers:
            assert validate_invoice_number(num) == False, f"'{num}' debería ser inválido"
    
    def test_empty_string_is_invalid(self):
        """Test: String vacío es inválido"""
        assert validate_invoice_number("") == False
        assert validate_invoice_number("   ") == False
    
    def test_none_is_invalid(self):
        """Test: None es inválido"""
        assert validate_invoice_number(None) == False


@pytest.mark.unit
class TestAmountValidation:
    """Tests para validación de montos."""
    
    def test_valid_positive_amounts(self):
        """Test: Montos positivos válidos"""
        valid_amounts = [0.01, 1.0, 100.50, 1000.99, 999999.99]
        for amount in valid_amounts:
            assert validate_amount(amount) == True, f"{amount} debería ser válido"
    
    def test_zero_is_valid(self):
        """Test: Cero es válido"""
        assert validate_amount(0) == True
        assert validate_amount(0.0) == True
    
    def test_negative_amounts_are_invalid(self):
        """Test: Montos negativos son inválidos"""
        invalid_amounts = [-1, -0.01, -100.50, -999999.99]
        for amount in invalid_amounts:
            assert validate_amount(amount) == False, f"{amount} debería ser inválido"
    
    def test_none_is_invalid(self):
        """Test: None es inválido"""
        assert validate_amount(None) == False
    
    def test_string_numbers_are_converted(self):
        """Test: Strings numéricos se convierten"""
        assert validate_amount("100") == True
        assert validate_amount("100.50") == True
        assert validate_amount("-50") == False
    
    def test_non_numeric_strings_are_invalid(self):
        """Test: Strings no numéricos son inválidos"""
        assert validate_amount("abc") == False
        assert validate_amount("12.34.56") == False
        assert validate_amount("") == False


@pytest.mark.unit
class TestDateValidation:
    """Tests para validación de fechas."""
    
    def test_valid_iso_dates(self):
        """Test: Fechas ISO válidas"""
        valid_dates = [
            "2026-01-29",
            "2026-12-31",
            "2025-06-15",
            "2026-01-29T20:00:00",
            "2026-01-29T20:00:00.000"
        ]
        for date in valid_dates:
            assert validate_date(date) == True, f"'{date}' debería ser válido"
    
    def test_invalid_dates(self):
        """Test: Fechas inválidas"""
        invalid_dates = [
            "2026-13-01",  # Mes inválido
            "2026-01-32",  # Día inválido
            "2026-02-30",  # Día inexistente
            "01/29/2026",  # Formato incorrecto
            "29-01-2026",  # Formato incorrecto
            "",
            "abc",
            None
        ]
        for date in invalid_dates:
            assert validate_date(date) == False, f"'{date}' debería ser inválido"


@pytest.mark.unit
class TestTimeValidation:
    """Tests para validación de tiempos."""
    
    def test_valid_times(self, valid_times):
        """Test: Tiempos válidos en formato HH:MM"""
        for time in valid_times:
            assert validate_time(time) == True, f"'{time}' debería ser válido"
    
    def test_invalid_times(self, invalid_times):
        """Test: Tiempos inválidos"""
        for time in invalid_times:
            assert validate_time(time) == False, f"'{time}' debería ser inválido"
    
    def test_boundary_times(self):
        """Test: Tiempos en los límites"""
        assert validate_time("00:00") == True  # Medianoche
        assert validate_time("23:59") == True  # Último minuto del día
        assert validate_time("12:00") == True  # Mediodía
    
    def test_invalid_boundary_times(self):
        """Test: Tiempos fuera de límites"""
        assert validate_time("24:00") == False  # Hora inválida
        assert validate_time("23:60") == False  # Minuto inválido
        assert validate_time("-1:00") == False  # Hora negativa
    
    def test_empty_string_is_valid(self):
        """Test: String vacío es válido (opcional)"""
        assert validate_time("") == True
    
    def test_none_is_valid(self):
        """Test: None es válido (opcional)"""
        assert validate_time(None) == True
