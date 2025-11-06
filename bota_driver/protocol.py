"""
Communication protocol implementations for BOTA force sensors.

Supports Serial/USB and UDP/Ethernet connections.
"""

import socket
import struct
import time
from abc import ABC, abstractmethod
from typing import Optional, Tuple

from .exceptions import BotaConnectionError, BotaTimeoutError


class CommunicationProtocol(ABC):
    """Abstract base class for communication protocols."""
    
    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the sensor."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the sensor."""
        pass
    
    @abstractmethod
    def send(self, data: bytes) -> None:
        """Send data to the sensor."""
        pass
    
    @abstractmethod
    def receive(self, size: int) -> bytes:
        """Receive data from the sensor."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connection is active."""
        pass


class UDPProtocol(CommunicationProtocol):
    """UDP/Ethernet communication protocol for BOTA sensors."""
    
    def __init__(self, host: str = "192.168.1.1", port: int = 1000, timeout: float = 5.0):
        """
        Initialize UDP protocol.
        
        Args:
            host: IP address of the sensor
            port: UDP port number
            timeout: Communication timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket: Optional[socket.socket] = None
        self._connected = False
    
    def connect(self) -> None:
        """Establish UDP connection to the sensor."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(self.timeout)
            self._connected = True
        except socket.error as e:
            raise BotaConnectionError(f"Failed to create UDP socket: {e}")
    
    def disconnect(self) -> None:
        """Close UDP connection."""
        if self.socket:
            self.socket.close()
            self.socket = None
        self._connected = False
    
    def send(self, data: bytes) -> None:
        """Send data via UDP."""
        if not self._connected or not self.socket:
            raise BotaConnectionError("Not connected to sensor")
        
        try:
            self.socket.sendto(data, (self.host, self.port))
        except socket.error as e:
            raise BotaConnectionError(f"Failed to send data: {e}")
    
    def receive(self, size: int = 1024) -> bytes:
        """Receive data via UDP."""
        if not self._connected or not self.socket:
            raise BotaConnectionError("Not connected to sensor")
        
        try:
            data, _ = self.socket.recvfrom(size)
            return data
        except socket.timeout:
            raise BotaTimeoutError("Timeout waiting for sensor response")
        except socket.error as e:
            raise BotaConnectionError(f"Failed to receive data: {e}")
    
    def is_connected(self) -> bool:
        """Check if UDP connection is active."""
        return self._connected


class SerialProtocol(CommunicationProtocol):
    """Serial/USB communication protocol for BOTA sensors."""
    
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200, timeout: float = 5.0):
        """
        Initialize Serial protocol.
        
        Args:
            port: Serial port device path
            baudrate: Communication baud rate
            timeout: Communication timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self._connected = False
        
        try:
            import serial
            self.serial_module = serial
        except ImportError:
            raise ImportError("pyserial is required for Serial communication. Install with: pip install pyserial")
    
    def connect(self) -> None:
        """Establish serial connection to the sensor."""
        try:
            self.serial = self.serial_module.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self._connected = True
        except Exception as e:
            raise BotaConnectionError(f"Failed to open serial port: {e}")
    
    def disconnect(self) -> None:
        """Close serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
        self._connected = False
    
    def send(self, data: bytes) -> None:
        """Send data via serial."""
        if not self._connected or not self.serial:
            raise BotaConnectionError("Not connected to sensor")
        
        try:
            self.serial.write(data)
        except Exception as e:
            raise BotaConnectionError(f"Failed to send data: {e}")
    
    def receive(self, size: int = 1024) -> bytes:
        """Receive data via serial."""
        if not self._connected or not self.serial:
            raise BotaConnectionError("Not connected to sensor")
        
        try:
            data = self.serial.read(size)
            if not data:
                raise BotaTimeoutError("Timeout waiting for sensor response")
            return data
        except Exception as e:
            raise BotaConnectionError(f"Failed to receive data: {e}")
    
    def is_connected(self) -> bool:
        """Check if serial connection is active."""
        return self._connected and self.serial and self.serial.is_open
