"""
Basic example of using the BOTA force sensor driver with UDP connection.
"""

from bota_driver import BotaSensor, BotaConnectionError
import time


def main():
    # Initialize sensor with UDP connection
    sensor = BotaSensor(
        connection_type="udp",
        host="192.168.1.1",  # Change to your sensor's IP
        port=1000,
        timeout=5.0
    )
    
    try:
        # Connect to sensor
        print("Connecting to BOTA sensor...")
        sensor.connect()
        print("Connected successfully!")
        
        # Calibrate sensor (remove zero offset)
        print("\nCalibrating sensor...")
        sensor.calibrate(samples=50)
        
        # Read single measurement
        print("\nReading single measurement:")
        data = sensor.read_data()
        print(data)
        print(f"Dictionary format: {data.to_dict()}")
        
        # Read continuous data for 5 seconds
        print("\nReading continuous data for 5 seconds at 10 Hz...")
        readings = sensor.read_continuous(duration=5.0, rate=10.0)
        print(f"Collected {len(readings)} samples")
        
        # Display some statistics
        if readings:
            avg_fz = sum(r.fz for r in readings) / len(readings)
            print(f"Average Fz: {avg_fz:.3f} N")
        
        # Get sensor info
        print("\nSensor information:")
        info = sensor.get_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        
    except BotaConnectionError as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Disconnect from sensor
        sensor.disconnect()
        print("\nDisconnected from sensor")


# Alternative: Using context manager
def context_manager_example():
    """Example using context manager for automatic connection handling."""
    
    with BotaSensor(connection_type="udp", host="192.168.1.1") as sensor:
        # Calibrate
        sensor.calibrate()
        
        # Read data
        for i in range(10):
            data = sensor.read_data()
            print(f"Sample {i+1}: Fz={data.fz:.3f} N, Tz={data.tz:.3f} Nm")
            time.sleep(0.1)


if __name__ == "__main__":
    main()
    # context_manager_example()
