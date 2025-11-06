"""
Example of using the BOTA force sensor driver with Serial/USB connection.
"""

from bota_driver import BotaSensor, BotaConnectionError
import time


def main():
    # Initialize sensor with Serial connection
    sensor = BotaSensor(
        connection_type="serial",
        port="/dev/ttyUSB0",  # Change to your serial port (COM3 on Windows)
        baudrate=115200,
        timeout=5.0
    )
    
    try:
        # Connect to sensor
        print("Connecting to BOTA sensor via Serial...")
        sensor.connect()
        print("Connected successfully!")
        
        # Read data continuously
        print("\nReading data (press Ctrl+C to stop)...")
        while True:
            data = sensor.read_data()
            print(f"Force: [{data.fx:6.2f}, {data.fy:6.2f}, {data.fz:6.2f}] N | "
                  f"Torque: [{data.tx:6.3f}, {data.ty:6.3f}, {data.tz:6.3f}] Nm")
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    except BotaConnectionError as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sensor.disconnect()
        print("Disconnected from sensor")


if __name__ == "__main__":
    main()
