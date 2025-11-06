"""
Advanced example showing data logging and visualization.
"""

from bota_driver import BotaSensor
import time
import csv
from datetime import datetime


def log_data_to_csv(sensor, duration=10.0, rate=100.0, filename=None):
    """
    Log sensor data to CSV file.
    
    Args:
        sensor: BotaSensor instance
        duration: Duration to log in seconds
        rate: Sampling rate in Hz
        filename: Output filename (auto-generated if None)
    """
    if filename is None:
        filename = f"force_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    print(f"Logging data to {filename} for {duration} seconds at {rate} Hz...")
    
    # Read continuous data
    readings = sensor.read_continuous(duration=duration, rate=rate)
    
    # Write to CSV
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'fx', 'fy', 'fz', 'tx', 'ty', 'tz']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for reading in readings:
            writer.writerow(reading.to_dict())
    
    print(f"Logged {len(readings)} samples to {filename}")
    return filename


def calculate_statistics(readings):
    """Calculate basic statistics from readings."""
    if not readings:
        return None
    
    n = len(readings)
    stats = {}
    
    for axis in ['fx', 'fy', 'fz', 'tx', 'ty', 'tz']:
        values = [getattr(r, axis) for r in readings]
        stats[axis] = {
            'mean': sum(values) / n,
            'min': min(values),
            'max': max(values),
            'range': max(values) - min(values)
        }
    
    return stats


def main():
    with BotaSensor(connection_type="udp", host="192.168.1.1") as sensor:
        # Calibrate
        print("Calibrating...")
        sensor.calibrate(samples=100)
        
        # Log data
        readings = sensor.read_continuous(duration=10.0, rate=50.0)
        
        # Calculate statistics
        stats = calculate_statistics(readings)
        
        print("\nStatistics:")
        for axis, values in stats.items():
            print(f"{axis}:")
            print(f"  Mean: {values['mean']:.4f}")
            print(f"  Range: [{values['min']:.4f}, {values['max']:.4f}]")
        
        # Save to CSV
        log_data_to_csv(sensor, duration=5.0, rate=100.0)


if __name__ == "__main__":
    main()
