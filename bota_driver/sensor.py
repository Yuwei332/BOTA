"""
Main BOTA force sensor driver class.
"""

import struct
import time
from typing import Dict, List, Optional, Tuple, Union

from .exceptions import BotaConnectionError, BotaConfigError, BotaDataError
from .protocol import CommunicationProtocol, UDPProtocol, SerialProtocol


class ForceTorqueData:
    """Container for force-torque sensor data."""
    
    def __init__(self, fx: float = 0.0, fy: float = 0.0, fz: float = 0.0,
                 tx: float = 0.0, ty: float = 0.0, tz: float = 0.0,
                 timestamp: Optional[float] = None):
        """
        Initialize force-torque data.
        
        Args:
            fx: Force in X direction (N)
            fy: Force in Y direction (N)
            fz: Force in Z direction (N)
            tx: Torque around X axis (Nm)
            ty: Torque around Y axis (Nm)
            tz: Torque around Z axis (Nm)
            timestamp: Timestamp of measurement
        """
        self.fx = fx
        self.fy = fy
        self.fz = fz
        self.tx = tx
        self.ty = ty
        self.tz = tz
        self.timestamp = timestamp if timestamp is not None else time.time()
    
    def to_dict(self) -> Dict[str, float]:
        """Convert data to dictionary."""
        return {
            'fx': self.fx,
            'fy': self.fy,
            'fz': self.fz,
            'tx': self.tx,
            'ty': self.ty,
            'tz': self.tz,
            'timestamp': self.timestamp
        }
    
    def to_list(self) -> List[float]:
        """Convert force-torque data to list [fx, fy, fz, tx, ty, tz]."""
        return [self.fx, self.fy, self.fz, self.tx, self.ty, self.tz]
    
    def __repr__(self) -> str:
        return (f"ForceTorqueData(fx={self.fx:.3f}, fy={self.fy:.3f}, fz={self.fz:.3f}, "
                f"tx={self.tx:.3f}, ty={self.ty:.3f}, tz={self.tz:.3f})")


class BotaSensor:
    """
    Main driver class for BOTA force-torque sensors.
    
    Supports both UDP/Ethernet and Serial/USB connections.
    """
    
    def __init__(self, protocol: Optional[CommunicationProtocol] = None,
                 connection_type: str = "udp", **kwargs):
        """
        Initialize BOTA sensor driver.
        
        Args:
            protocol: Custom communication protocol instance
            connection_type: Type of connection ("udp" or "serial")
            **kwargs: Connection parameters (host, port, baudrate, etc.)
        """
        if protocol:
            self.protocol = protocol
        elif connection_type.lower() == "udp":
            host = kwargs.get('host', '192.168.1.1')
            port = kwargs.get('port', 1000)
            timeout = kwargs.get('timeout', 5.0)
            self.protocol = UDPProtocol(host=host, port=port, timeout=timeout)
        elif connection_type.lower() == "serial":
            port = kwargs.get('port', '/dev/ttyUSB0')
            baudrate = kwargs.get('baudrate', 115200)
            timeout = kwargs.get('timeout', 5.0)
            self.protocol = SerialProtocol(port=port, baudrate=baudrate, timeout=timeout)
        else:
            raise BotaConfigError(f"Invalid connection type: {connection_type}")
        
        self._calibration_offset = [0.0] * 6
        self._scale_factor = 1.0
    
    def connect(self) -> None:
        """Connect to the sensor."""
        self.protocol.connect()
    
    def disconnect(self) -> None:
        """Disconnect from the sensor."""
        self.protocol.disconnect()
    
    def is_connected(self) -> bool:
        """Check if sensor is connected."""
        return self.protocol.is_connected()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def read_data(self) -> ForceTorqueData:
        """
        Read force-torque data from the sensor.
        
        Returns:
            ForceTorqueData object with current measurements
        """
        if not self.is_connected():
            raise BotaConnectionError("Sensor is not connected")
        
        # Send data request command (implementation depends on sensor protocol)
        # This is a simplified example
        try:
            # Request data (example command)
            self.protocol.send(b'\x01\x00')
            
            # Receive response
            data = self.protocol.receive(48)  # 6 floats * 4 bytes + header
            
            # Parse data (example format: 6 float32 values)
            if len(data) >= 24:
                values = struct.unpack('<6f', data[:24])
                
                # Apply calibration
                calibrated_values = [
                    (values[i] - self._calibration_offset[i]) * self._scale_factor
                    for i in range(6)
                ]
                
                return ForceTorqueData(*calibrated_values)
            else:
                raise BotaDataError("Insufficient data received from sensor")
        
        except struct.error as e:
            raise BotaDataError(f"Failed to parse sensor data: {e}")
    
    def calibrate(self, samples: int = 100, verbose: bool = True, sample_interval: float = 0.01) -> None:
        """
        Calibrate sensor by taking zero offset.
        
        Args:
            samples: Number of samples to average for calibration
            verbose: Whether to print calibration progress
            sample_interval: Time interval between samples in seconds
        """
        if not self.is_connected():
            raise BotaConnectionError("Sensor is not connected")
        
        if verbose:
            print(f"Calibrating sensor with {samples} samples...")
        
        accumulated = [0.0] * 6
        successful_samples = 0
        max_retries = samples * 2  # Allow up to 2x retries
        
        for i in range(max_retries):
            if successful_samples >= samples:
                break
            try:
                data = self.read_data()
                values = data.to_list()
                accumulated = [accumulated[j] + values[j] for j in range(6)]
                successful_samples += 1
                time.sleep(sample_interval)
            except Exception as e:
                if verbose:
                    print(f"Warning: Failed to read sample {i+1}: {e}")
                continue
        
        if successful_samples < samples:
            raise BotaConnectionError(f"Calibration failed: only {successful_samples}/{samples} samples collected")
        
        self._calibration_offset = [val / successful_samples for val in accumulated]
        if verbose:
            print(f"Calibration complete. Offset: {self._calibration_offset}")
    
    def set_scale_factor(self, scale: float) -> None:
        """
        Set scale factor for measurements.
        
        Args:
            scale: Scale factor to apply to all measurements
        """
        if scale <= 0:
            raise BotaConfigError("Scale factor must be positive")
        self._scale_factor = scale
    
    def get_calibration_offset(self) -> List[float]:
        """Get current calibration offset."""
        return self._calibration_offset.copy()
    
    def set_calibration_offset(self, offset: List[float]) -> None:
        """
        Set calibration offset manually.
        
        Args:
            offset: List of 6 offset values [fx, fy, fz, tx, ty, tz]
        """
        if len(offset) != 6:
            raise BotaConfigError("Offset must contain exactly 6 values")
        self._calibration_offset = offset.copy()
    
    def reset_calibration(self) -> None:
        """Reset calibration to zero offset."""
        self._calibration_offset = [0.0] * 6
        self._scale_factor = 1.0
    
    def read_continuous(self, duration: float = 1.0, rate: float = 100.0, verbose: bool = False) -> List[ForceTorqueData]:
        """
        Read data continuously for a specified duration.
        
        Args:
            duration: Duration to read data in seconds
            rate: Desired sampling rate in Hz
            verbose: Whether to print warnings for failed reads
        
        Returns:
            List of ForceTorqueData readings
        """
        if not self.is_connected():
            raise BotaConnectionError("Sensor is not connected")
        
        readings = []
        interval = 1.0 / rate
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                data = self.read_data()
                readings.append(data)
                time.sleep(interval)
            except Exception as e:
                if verbose:
                    print(f"Warning: Failed to read data: {e}")
                continue
        
        return readings
    
    def get_info(self) -> Dict[str, Union[str, float, List[float]]]:
        """
        Get sensor information and current configuration.
        
        Returns:
            Dictionary with sensor info
        """
        return {
            'connected': self.is_connected(),
            'calibration_offset': self._calibration_offset,
            'scale_factor': self._scale_factor,
            'protocol_type': type(self.protocol).__name__
        }
