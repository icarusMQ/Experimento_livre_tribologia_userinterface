"""
Test script for serial communication with the tribology experiment device.
Use this to test connection and data parsing before running the full GUI.
"""

import time
import sys
from serial_comm import SerialCommunication

def test_serial_communication():
    """Test serial communication functionality."""
    print("Tribology Experiment - Serial Communication Test")
    print("=" * 50)
    
    # Create serial communication instance
    serial_comm = SerialCommunication()
    
    # Get available ports
    ports = serial_comm.get_available_ports()
    print(f"Available ports: {ports}")
    
    if not ports:
        print("No serial ports found!")
        return False
    
    # Ask user to select port
    if len(ports) == 1:
        selected_port = ports[0]
        print(f"Using port: {selected_port}")
    else:
        print("\nSelect a port:")
        for i, port in enumerate(ports):
            print(f"{i+1}. {port}")
        
        try:
            choice = int(input("Enter choice (1-{}): ".format(len(ports)))) - 1
            selected_port = ports[choice]
        except (ValueError, IndexError):
            print("Invalid selection!")
            return False
    
    # Connect to selected port
    print(f"\nConnecting to {selected_port}...")
    if not serial_comm.connect(selected_port, 115200):
        print("Failed to connect!")
        return False
    
    print("Connected successfully!")
    print("Listening for data... (Press Ctrl+C to stop)")
    print("-" * 50)
    
    # Set up data callback
    def data_callback(data):
        print(f"Received: {data}")
    
    serial_comm.set_data_callback(data_callback)
    
    try:
        # Listen for data
        start_time = time.time()
        while time.time() - start_time < 30:  # Test for 30 seconds
            # Check for user input
            time.sleep(0.1)
            
            # Send test command every 10 seconds
            if int(time.time() - start_time) % 10 == 0:
                print("Sending test command...")
                serial_comm.send_command("test")
                time.sleep(1)  # Avoid sending multiple times in the same second
    
    except KeyboardInterrupt:
        print("\nStopping test...")
    
    finally:
        serial_comm.disconnect()
        print("Disconnected.")
    
    return True

def test_data_parsing():
    """Test data parsing functionality."""
    print("\nTesting data parsing...")
    print("-" * 30)
    
    serial_comm = SerialCommunication()
    
    # Test data samples
    test_lines = [
        "Time:123.45,Fixed_X:1.23,Fixed_Z:4.56",
        ">Time:234.56,Fixed_X:2.34,Fixed_Z:5.67",
        "Experiment started!",
        "Pump running. Force adjustment stage active.",
        "Invalid data line",
        ">Time:345.67,Fixed_X:-1.45,Fixed_Z:0.89"
    ]
    
    for line in test_lines:
        parsed = serial_comm.parse_data_line(line)
        print(f"Input:  {line}")
        print(f"Output: {parsed}")
        print()

if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Test serial communication")
    print("2. Test data parsing only")
    print("3. Both")
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice in ["2", "3"]:
            test_data_parsing()
        
        if choice in ["1", "3"]:
            if not test_serial_communication():
                sys.exit(1)
        
        print("Test completed successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)
