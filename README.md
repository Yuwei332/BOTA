# BOTA Force Sensor Driver

A Python driver for controlling BOTA Systems force-torque sensors. This driver provides a simple and intuitive interface for communicating with BOTA sensors via UDP/Ethernet or Serial/USB connections.

## Features

- 🔌 Multiple connection types: UDP/Ethernet and Serial/USB
- 📊 Real-time force-torque data reading
- 🎯 Built-in calibration support
- 📈 Continuous data acquisition
- 🛡️ Comprehensive error handling
- 📝 Context manager support for safe resource management
- 🔧 Configurable sampling rates and timeouts

## Installation

### From source

```bash
git clone https://github.com/Yuwei332/BOTA.git
cd BOTA
pip install -e .
```

### Requirements

- Python 3.7+
- pyserial (for Serial/USB connections)

## Quick Start

### UDP/Ethernet Connection

```python
from bota_driver import BotaSensor

# Create sensor instance
sensor = BotaSensor(
    connection_type="udp",
    host="192.168.1.1",
    port=1000
)

# Connect and read data
sensor.connect()
sensor.calibrate()
data = sensor.read_data()
print(f"Force: [{data.fx}, {data.fy}, {data.fz}] N")
sensor.disconnect()
```

### Serial/USB Connection

```python
from bota_driver import BotaSensor

# Create sensor instance
sensor = BotaSensor(
    connection_type="serial",
    port="/dev/ttyUSB0",  # or "COM3" on Windows
    baudrate=115200
)

sensor.connect()
data = sensor.read_data()
sensor.disconnect()
```

### Using Context Manager

```python
from bota_driver import BotaSensor

with BotaSensor(connection_type="udp", host="192.168.1.1") as sensor:
    sensor.calibrate()
    data = sensor.read_data()
    print(data)
```

## API Reference

### BotaSensor

Main driver class for BOTA force-torque sensors.

#### Constructor

```python
BotaSensor(protocol=None, connection_type="udp", **kwargs)
```

**Parameters:**
- `protocol`: Custom communication protocol instance (optional)
- `connection_type`: Type of connection - "udp" or "serial"
- `**kwargs`: Connection parameters
  - For UDP: `host`, `port`, `timeout`
  - For Serial: `port`, `baudrate`, `timeout`

#### Methods

##### `connect()`
Establish connection to the sensor.

##### `disconnect()`
Close connection to the sensor.

##### `is_connected()`
Check if sensor is connected.

**Returns:** `bool` - Connection status

##### `read_data()`
Read current force-torque data from the sensor.

**Returns:** `ForceTorqueData` object with measurements

##### `calibrate(samples=100)`
Calibrate sensor by taking zero offset.

**Parameters:**
- `samples`: Number of samples to average for calibration

##### `read_continuous(duration=1.0, rate=100.0)`
Read data continuously for a specified duration.

**Parameters:**
- `duration`: Duration to read data in seconds
- `rate`: Desired sampling rate in Hz

**Returns:** List of `ForceTorqueData` readings

##### `set_scale_factor(scale)`
Set scale factor for measurements.

**Parameters:**
- `scale`: Scale factor to apply

##### `get_calibration_offset()`
Get current calibration offset.

**Returns:** List of 6 offset values

##### `set_calibration_offset(offset)`
Set calibration offset manually.

**Parameters:**
- `offset`: List of 6 offset values [fx, fy, fz, tx, ty, tz]

##### `reset_calibration()`
Reset calibration to zero offset.

##### `get_info()`
Get sensor information and current configuration.

**Returns:** Dictionary with sensor info

### ForceTorqueData

Container for force-torque sensor data.

#### Attributes

- `fx`: Force in X direction (N)
- `fy`: Force in Y direction (N)
- `fz`: Force in Z direction (N)
- `tx`: Torque around X axis (Nm)
- `ty`: Torque around Y axis (Nm)
- `tz`: Torque around Z axis (Nm)
- `timestamp`: Timestamp of measurement

#### Methods

##### `to_dict()`
Convert data to dictionary.

##### `to_list()`
Convert force-torque data to list [fx, fy, fz, tx, ty, tz].

## Examples

See the `examples/` directory for more detailed examples:

- `basic_usage.py`: Basic sensor reading with UDP
- `serial_usage.py`: Serial/USB connection example
- `advanced_usage.py`: Data logging and statistics

## Exception Handling

The driver provides specific exceptions for different error conditions:

- `BotaConnectionError`: Connection-related errors
- `BotaTimeoutError`: Communication timeout
- `BotaConfigError`: Invalid configuration
- `BotaDataError`: Data parsing errors

Example:

```python
from bota_driver import BotaSensor, BotaConnectionError, BotaTimeoutError

try:
    sensor = BotaSensor(connection_type="udp", host="192.168.1.1")
    sensor.connect()
    data = sensor.read_data()
except BotaConnectionError as e:
    print(f"Connection failed: {e}")
except BotaTimeoutError as e:
    print(f"Timeout: {e}")
finally:
    sensor.disconnect()
```

## Architecture

The driver is organized into several modules:

- `sensor.py`: Main `BotaSensor` class and `ForceTorqueData` container
- `protocol.py`: Communication protocol implementations (UDP, Serial)
- `exceptions.py`: Custom exception classes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/Yuwei332/BOTA).

## Acknowledgments

This driver is designed to work with BOTA Systems force-torque sensors. Please refer to your sensor's documentation for specific communication protocol details.
