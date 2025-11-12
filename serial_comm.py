import serial
import threading
import time
import queue
from typing import Optional, Callable, Dict, Any
import re

class SerialCommunication:
    """Handles serial communication with the tribology experiment device."""
    
    def __init__(self):
        self.serial_port: Optional[serial.Serial] = None
        self.is_connected = False
        self.is_reading = False
        self.read_thread: Optional[threading.Thread] = None
        self.data_queue = queue.Queue()
        self.data_callback: Optional[Callable] = None
        
    def connect(self, port: str, baudrate: int = 115200, timeout: float = 1.0) -> bool:
        """Connect to the serial port."""
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            self.is_connected = True
            self.start_reading()
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to {port}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the serial port."""
        self.stop_reading()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.is_connected = False
    
    def start_reading(self):
        """Start reading data from serial port in a separate thread."""
        if self.is_connected and not self.is_reading:
            self.is_reading = True
            self.read_thread = threading.Thread(target=self._read_data, daemon=True)
            self.read_thread.start()
    
    def stop_reading(self):
        """Stop reading data from serial port."""
        self.is_reading = False
        if self.read_thread:
            self.read_thread.join(timeout=2.0)
    
    def _read_data(self):
        """Internal method to read data from serial port."""
        buffer = ""
        while self.is_reading and self.is_connected:
            try:
                if self.serial_port and self.serial_port.in_waiting > 0:
                    chunk = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8', errors='ignore')
                    buffer += chunk
                    
                    # Process complete lines
                    while '\n' in buffer or '\r' in buffer:
                        if '\r\n' in buffer:
                            line, buffer = buffer.split('\r\n', 1)
                        elif '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                        elif '\r' in buffer:
                            line, buffer = buffer.split('\r', 1)
                        
                        if line.strip():
                            self._process_line(line.strip())
                
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
            except Exception as e:
                print(f"Error reading serial data: {e}")
                break
    
    def _process_line(self, line: str):
        """Process a received line of data."""
        data = self.parse_data_line(line)
        if data:
            self.data_queue.put(data)
            if self.data_callback:
                self.data_callback(data)
    
    def parse_data_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a line of data from the device."""
        # Check for experiment marker
        is_experiment_data = line.startswith('>')
        if is_experiment_data:
            line = line[1:]  # Remove the '>' marker
        
        # Parse the data format: Time:123.45,Fixed_X:1.23,Fixed_Z:4.56
        data = {"is_experiment": is_experiment_data, "raw": line}
        
        # Extract time
        time_match = re.search(r'Time:([\d.-]+)', line)
        if time_match:
            data["time"] = float(time_match.group(1))
        
        # Extract X force (supports both Simple and Force-Control modes)
        # Simple mode: Fixed_X:<val>, Force mode: Fx:<val>
        fx_match_fixed = re.search(r'Fixed_X:([\d.-]+)', line)
        fx_match_fx = re.search(r'\bFx:([\d.-]+)', line)
        if fx_match_fixed:
            val = float(fx_match_fixed.group(1))
            data["fixed_x"] = val
            data["force_x"] = val if "force_x" not in data else data["force_x"]
        if fx_match_fx:
            val = float(fx_match_fx.group(1))
            data["fx"] = val
            # Prefer explicit Fx if no prior force_x set
            if "force_x" not in data:
                data["force_x"] = val
        
        # Extract Z force (supports both Simple and Force-Control modes)
        # Simple mode: Fixed_Z:<val>, Force mode: Fz:<val>
        fz_match_fixed = re.search(r'Fixed_Z:([\d.-]+)', line)
        fz_match_fz = re.search(r'\bFz:([\d.-]+)', line)
        if fz_match_fixed:
            val = float(fz_match_fixed.group(1))
            data["fixed_z"] = val
            data["force_z"] = val if "force_z" not in data else data["force_z"]
        if fz_match_fz:
            val = float(fz_match_fz.group(1))
            data["fz"] = val
            if "force_z" not in data:
                data["force_z"] = val
        
        # Only return data if we have force readings
        if "force_x" in data or "force_z" in data:
            return data
        
        # If no force data, check for status messages
        if any(keyword in line.lower() for keyword in ["experiment", "started", "finished", "pump", "motor"]):
            data["message"] = line
            return data
            
        return None
    
    def send_command(self, command: str) -> bool:
        """Send a command to the device."""
        if not self.is_connected or not self.serial_port:
            return False
        
        try:
            self.serial_port.write(f"{command}\n".encode('utf-8'))
            self.serial_port.flush()
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    
    def start_experiment(self) -> bool:
        """Send command to start the experiment."""
        return self.send_command("3")  # Button press simulation
    
    def stop_experiment(self) -> bool:
        """Send command to stop the experiment."""
        return self.send_command("stop")
    
    def get_available_ports(self) -> list:
        """Get list of available serial ports."""
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def set_data_callback(self, callback: Callable):
        """Set callback function for incoming data."""
        self.data_callback = callback
    
    def get_queued_data(self) -> list:
        """Get all queued data and clear the queue."""
        data_list = []
        while not self.data_queue.empty():
            try:
                data_list.append(self.data_queue.get_nowait())
            except queue.Empty:
                break
        return data_list
