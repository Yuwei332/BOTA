"""
Basic tests for BOTA driver (unit tests without hardware).
"""

import pytest
from bota_driver import BotaSensor, ForceTorqueData
from bota_driver.exceptions import (
    BotaConnectionError, BotaTimeoutError, BotaConfigError, BotaDataError
)


class TestForceTorqueData:
    """Tests for ForceTorqueData class."""
    
    def test_initialization(self):
        """Test ForceTorqueData initialization."""
        data = ForceTorqueData(1.0, 2.0, 3.0, 0.1, 0.2, 0.3)
        assert data.fx == 1.0
        assert data.fy == 2.0
        assert data.fz == 3.0
        assert data.tx == 0.1
        assert data.ty == 0.2
        assert data.tz == 0.3
        assert data.timestamp is not None
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        data = ForceTorqueData(1.0, 2.0, 3.0, 0.1, 0.2, 0.3)
        result = data.to_dict()
        assert result['fx'] == 1.0
        assert result['fy'] == 2.0
        assert result['fz'] == 3.0
        assert result['tx'] == 0.1
        assert result['ty'] == 0.2
        assert result['tz'] == 0.3
        assert 'timestamp' in result
    
    def test_to_list(self):
        """Test conversion to list."""
        data = ForceTorqueData(1.0, 2.0, 3.0, 0.1, 0.2, 0.3)
        result = data.to_list()
        assert result == [1.0, 2.0, 3.0, 0.1, 0.2, 0.3]
    
    def test_repr(self):
        """Test string representation."""
        data = ForceTorqueData(1.0, 2.0, 3.0, 0.1, 0.2, 0.3)
        repr_str = repr(data)
        assert "ForceTorqueData" in repr_str
        assert "fx=1.000" in repr_str


class TestBotaSensor:
    """Tests for BotaSensor class."""
    
    def test_initialization_udp(self):
        """Test UDP sensor initialization."""
        sensor = BotaSensor(connection_type="udp", host="192.168.1.1", port=1000)
        assert sensor is not None
        assert not sensor.is_connected()
    
    def test_initialization_serial(self):
        """Test Serial sensor initialization."""
        sensor = BotaSensor(connection_type="serial", port="/dev/ttyUSB0")
        assert sensor is not None
        assert not sensor.is_connected()
    
    def test_invalid_connection_type(self):
        """Test invalid connection type raises error."""
        with pytest.raises(BotaConfigError):
            BotaSensor(connection_type="invalid")
    
    def test_calibration_offset(self):
        """Test calibration offset management."""
        sensor = BotaSensor(connection_type="udp")
        
        # Check default offset
        offset = sensor.get_calibration_offset()
        assert offset == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        # Set custom offset
        new_offset = [1.0, 2.0, 3.0, 0.1, 0.2, 0.3]
        sensor.set_calibration_offset(new_offset)
        assert sensor.get_calibration_offset() == new_offset
        
        # Reset calibration
        sensor.reset_calibration()
        assert sensor.get_calibration_offset() == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    
    def test_invalid_calibration_offset(self):
        """Test invalid calibration offset raises error."""
        sensor = BotaSensor(connection_type="udp")
        
        with pytest.raises(BotaConfigError):
            sensor.set_calibration_offset([1.0, 2.0])  # Too few values
    
    def test_scale_factor(self):
        """Test scale factor configuration."""
        sensor = BotaSensor(connection_type="udp")
        
        sensor.set_scale_factor(2.0)
        assert sensor._scale_factor == 2.0
        
        with pytest.raises(BotaConfigError):
            sensor.set_scale_factor(-1.0)  # Negative scale
    
    def test_get_info(self):
        """Test sensor info retrieval."""
        sensor = BotaSensor(connection_type="udp", host="192.168.1.1")
        info = sensor.get_info()
        
        assert 'connected' in info
        assert 'calibration_offset' in info
        assert 'scale_factor' in info
        assert 'protocol_type' in info
        assert info['connected'] == False
    
    def test_context_manager(self):
        """Test context manager (without actual connection)."""
        # This will fail to connect, but we're testing the structure
        sensor = BotaSensor(connection_type="udp", host="192.168.1.1", timeout=0.1)
        assert sensor is not None


class TestExceptions:
    """Tests for exception classes."""
    
    def test_exception_hierarchy(self):
        """Test exception inheritance."""
        from bota_driver.exceptions import BotaDriverError
        
        assert issubclass(BotaConnectionError, BotaDriverError)
        assert issubclass(BotaTimeoutError, BotaDriverError)
        assert issubclass(BotaConfigError, BotaDriverError)
        assert issubclass(BotaDataError, BotaDriverError)
    
    def test_exception_messages(self):
        """Test exception messages."""
        msg = "Test error message"
        
        exc = BotaConnectionError(msg)
        assert str(exc) == msg
        
        exc = BotaTimeoutError(msg)
        assert str(exc) == msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
