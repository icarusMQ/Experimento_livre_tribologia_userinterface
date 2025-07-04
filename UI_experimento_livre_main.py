import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from datetime import datetime
import os

from config import Config
from serial_comm import SerialCommunication
from data_manager import DataManager
from version import APP_NAME, APP_VERSION, APP_AUTHOR

class TribologyExperimentGUI:
    """Main GUI application for the tribology experiment control."""
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.config = Config()
        self.serial_comm = SerialCommunication()
        self.data_manager = DataManager(self.config.get("data_settings", "save_directory"))
        
        # GUI state variables
        self.is_experiment_running = False
        self.experiment_start_time = None
        
        # Setup GUI
        self.setup_gui()
        self.setup_serial_callback()
        
        # Start GUI update timer
        self.update_gui()
    
    def setup_gui(self):
        """Setup the main GUI layout."""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Setup tabs
        self.setup_config_tab()
        self.setup_control_tab()
        self.setup_data_tab()
        
    def setup_config_tab(self):
        """Setup configuration tab."""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuration")
        
        # Serial settings frame
        serial_frame = ttk.LabelFrame(config_frame, text="Serial Settings", padding=10)
        serial_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Serial port selection
        ttk.Label(serial_frame, text="Serial Port:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.port_var = tk.StringVar(value=self.config.get("serial_settings", "port"))
        self.port_combo = ttk.Combobox(serial_frame, textvariable=self.port_var, width=15)
        self.port_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # Refresh ports button
        ttk.Button(serial_frame, text="Refresh", 
                  command=self.refresh_ports).grid(row=0, column=2, padx=5, pady=2)
        
        # Baudrate
        ttk.Label(serial_frame, text="Baudrate:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.baudrate_var = tk.IntVar(value=self.config.get("serial_settings", "baudrate"))
        baudrate_combo = ttk.Combobox(serial_frame, textvariable=self.baudrate_var, 
                                     values=[9600, 19200, 38400, 57600, 115200], width=15)
        baudrate_combo.grid(row=1, column=1, padx=5, pady=2)
        
        # Connection status and button
        self.connection_status = tk.StringVar(value="Disconnected")
        ttk.Label(serial_frame, text="Status:").grid(row=2, column=0, sticky=tk.W, pady=2)
        status_label = ttk.Label(serial_frame, textvariable=self.connection_status)
        status_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        self.connect_button = ttk.Button(serial_frame, text="Connect", 
                                        command=self.toggle_connection)
        self.connect_button.grid(row=2, column=2, padx=5, pady=2)
        
        # Experiment parameters frame
        params_frame = ttk.LabelFrame(config_frame, text="Experiment Parameters", padding=10)
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Force control mode
        self.force_mode_var = tk.BooleanVar(value=self.config.get_experiment_params()["USE_FORCE_CONTROL_MODE"])
        ttk.Checkbutton(params_frame, text="Use Force Control Mode", 
                       variable=self.force_mode_var,
                       command=self.update_config).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # RPM settings
        params = [
            ("RPM Pump:", "RPM_PUMP"),
            ("RPM Axis:", "RPM_AXIS"), 
            ("RPM Force:", "RPM_FORCE"),
            ("Experiment Duration (s):", "EXPERIMENT_DURATION_S")
        ]
        
        self.param_vars = {}
        for i, (label, key) in enumerate(params, start=1):
            ttk.Label(params_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            var = tk.DoubleVar(value=self.config.get_experiment_params()[key])
            self.param_vars[key] = var
            entry = ttk.Entry(params_frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, padx=5, pady=2)
            entry.bind('<FocusOut>', lambda e, k=key: self.update_config())
        
        # Save/Load configuration
        config_buttons_frame = ttk.Frame(config_frame)
        config_buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(config_buttons_frame, text="Save Configuration", 
                  command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(config_buttons_frame, text="Load Configuration", 
                  command=self.load_config).pack(side=tk.LEFT, padx=5)
        
        # Initialize port list
        self.refresh_ports()
    
    def setup_control_tab(self):
        """Setup experiment control tab."""
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="Experiment Control")
        
        # Control buttons frame
        buttons_frame = ttk.LabelFrame(control_frame, text="Experiment Control", padding=10)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_button = ttk.Button(buttons_frame, text="Start Experiment", 
                                      command=self.start_experiment)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(buttons_frame, text="Stop Experiment", 
                                     command=self.stop_experiment, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(control_frame, text="Experiment Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(pady=5)
        
        self.progress_label = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.progress_label).pack()
        
        # Status frame
        status_frame = ttk.LabelFrame(control_frame, text="System Status", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Status text widget with scrollbar
        status_text_frame = ttk.Frame(status_frame)
        status_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(status_text_frame, height=10, width=60)
        status_scrollbar = ttk.Scrollbar(status_text_frame, orient=tk.VERTICAL, 
                                        command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Clear status button
        ttk.Button(status_frame, text="Clear Status", 
                  command=self.clear_status).pack(pady=5)
    
    def setup_data_tab(self):
        """Setup data visualization tab."""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="Data & Analysis")
        
        # Data control frame
        data_control_frame = ttk.LabelFrame(data_frame, text="Data Control", padding=10)
        data_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(data_control_frame, text="Save Data", 
                  command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(data_control_frame, text="Load Data", 
                  command=self.load_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(data_control_frame, text="Export Report", 
                  command=self.export_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(data_control_frame, text="Clear Data", 
                  command=self.clear_data).pack(side=tk.LEFT, padx=5)
        
        # Plot frame
        plot_frame = ttk.LabelFrame(data_frame, text="Real-time Data Plot", padding=10)
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize plots
        self.init_plots()
    
    def init_plots(self):
        """Initialize the data plots."""
        self.ax1.set_title("Force X (N) vs Time")
        self.ax1.set_xlabel("Time (s)")
        self.ax1.set_ylabel("Force X (N)")
        self.ax1.grid(True)
        
        self.ax2.set_title("Force Z (N) vs Time")
        self.ax2.set_xlabel("Time (s)")
        self.ax2.set_ylabel("Force Z (N)")
        self.ax2.grid(True)
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def setup_serial_callback(self):
        """Setup callback for serial data."""
        self.serial_comm.set_data_callback(self.handle_serial_data)
    
    def refresh_ports(self):
        """Refresh available serial ports."""
        ports = self.serial_comm.get_available_ports()
        self.port_combo['values'] = ports
        if ports and not self.port_var.get() in ports:
            self.port_var.set(ports[0])
    
    def toggle_connection(self):
        """Toggle serial connection."""
        if self.serial_comm.is_connected:
            self.disconnect_serial()
        else:
            self.connect_serial()
    
    def connect_serial(self):
        """Connect to serial port."""
        port = self.port_var.get()
        baudrate = self.baudrate_var.get()
        
        if self.serial_comm.connect(port, baudrate):
            self.connection_status.set("Connected")
            self.connect_button.config(text="Disconnect")
            self.log_status(f"Connected to {port} at {baudrate} baud")
        else:
            self.connection_status.set("Connection Failed")
            self.log_status(f"Failed to connect to {port}")
    
    def disconnect_serial(self):
        """Disconnect from serial port."""
        self.serial_comm.disconnect()
        self.connection_status.set("Disconnected")
        self.connect_button.config(text="Connect")
        self.log_status("Disconnected from serial port")
    
    def update_config(self):
        """Update configuration with current GUI values."""
        # Update experiment parameters
        self.config.set_experiment_param("USE_FORCE_CONTROL_MODE", self.force_mode_var.get())
        
        for key, var in self.param_vars.items():
            self.config.set_experiment_param(key, var.get())
        
        # Update serial settings
        self.config.set("serial_settings", "port", self.port_var.get())
        self.config.set("serial_settings", "baudrate", self.baudrate_var.get())
    
    def save_config(self):
        """Save current configuration to file."""
        self.update_config()
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.config.config_file = filename
            self.config.save_config()
            self.log_status(f"Configuration saved to {filename}")
    
    def load_config(self):
        """Load configuration from file."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.config.config_file = filename
            self.config = Config(filename)
            self.update_gui_from_config()
            self.log_status(f"Configuration loaded from {filename}")
    
    def update_gui_from_config(self):
        """Update GUI elements from loaded configuration."""
        params = self.config.get_experiment_params()
        self.force_mode_var.set(params["USE_FORCE_CONTROL_MODE"])
        
        for key, var in self.param_vars.items():
            var.set(params[key])
        
        serial_settings = self.config.get("serial_settings")
        self.port_var.set(serial_settings["port"])
        self.baudrate_var.set(serial_settings["baudrate"])
    
    def start_experiment(self):
        """Start the experiment."""
        if not self.serial_comm.is_connected:
            messagebox.showerror("Error", "Please connect to serial port first")
            return
        
        # Update configuration before starting
        self.update_config()
        
        # Start data collection
        self.data_manager.start_experiment()
        
        # Send start command to device
        if self.serial_comm.start_experiment():
            self.is_experiment_running = True
            self.experiment_start_time = datetime.now()
            
            # Update GUI state
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.progress_var.set(0)
            self.progress_label.set("Experiment Running...")
            
            self.log_status("Experiment started successfully")
        else:
            self.data_manager.stop_experiment()
            messagebox.showerror("Error", "Failed to start experiment")
    
    def stop_experiment(self):
        """Stop the experiment."""
        # Send stop command to device
        self.serial_comm.stop_experiment()
        
        # Stop data collection
        self.data_manager.stop_experiment()
        
        # Update GUI state
        self.is_experiment_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_label.set("Experiment Stopped")
        
        self.log_status("Experiment stopped")
    
    def handle_serial_data(self, data):
        """Handle incoming serial data."""
        # Add data to manager
        self.data_manager.add_data_point(data)
        
        # Log messages
        if "message" in data:
            self.log_status(f"Device: {data['message']}")
    
    def update_plots(self):
        """Update the data plots."""
        df = self.data_manager.get_current_data()
        
        if not df.empty:
            # Clear previous plots
            self.ax1.clear()
            self.ax2.clear()
            
            # Plot Force X
            if "force_x" in df.columns and not df["force_x"].isna().all():
                self.ax1.plot(df["time"], df["force_x"], 'b-', linewidth=1)
                self.ax1.set_title("Force X (N) vs Time")
                self.ax1.set_xlabel("Time (s)")
                self.ax1.set_ylabel("Force X (N)")
                self.ax1.grid(True)
            
            # Plot Force Z
            if "force_z" in df.columns and not df["force_z"].isna().all():
                self.ax2.plot(df["time"], df["force_z"], 'r-', linewidth=1)
                self.ax2.set_title("Force Z (N) vs Time")
                self.ax2.set_xlabel("Time (s)")
                self.ax2.set_ylabel("Force Z (N)")
                self.ax2.grid(True)
            
            self.fig.tight_layout()
            self.canvas.draw()
    
    def update_progress(self):
        """Update experiment progress."""
        if self.is_experiment_running:
            duration = self.config.get_experiment_params()["EXPERIMENT_DURATION_S"]
            progress = self.data_manager.get_experiment_progress(duration)
            self.progress_var.set(progress)
            
            # Check if experiment should be finished
            if progress >= 100:
                self.stop_experiment()
                self.log_status("Experiment completed automatically")
    
    def log_status(self, message):
        """Log a status message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        self.status_text.insert(tk.END, full_message)
        self.status_text.see(tk.END)
        
        # Limit status text length
        lines = self.status_text.get(1.0, tk.END).count('\n')
        if lines > 100:
            self.status_text.delete(1.0, f"{lines-50}.0")
    
    def clear_status(self):
        """Clear status text."""
        self.status_text.delete(1.0, tk.END)
    
    def save_data(self):
        """Save experiment data."""
        if self.data_manager.experiment_data:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if filename:
                self.data_manager.save_experiment_data(os.path.basename(filename))
                self.log_status(f"Data saved to {filename}")
        else:
            messagebox.showinfo("Info", "No data to save")
    
    def load_data(self):
        """Load experiment data."""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            df = self.data_manager.load_experiment_data(filename)
            if not df.empty:
                self.data_manager.current_data = df
                self.update_plots()
                self.log_status(f"Data loaded from {filename}")
            else:
                messagebox.showerror("Error", "Failed to load data")
    
    def export_report(self):
        """Export experiment report."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.data_manager.export_summary_report(filename)
            self.log_status(f"Report exported to {filename}")
    
    def clear_data(self):
        """Clear current data."""
        if messagebox.askyesno("Confirm", "Clear all current data?"):
            self.data_manager.clear_current_data()
            self.init_plots()
            self.progress_var.set(0)
            self.progress_label.set("Ready")
            self.log_status("Data cleared")
    
    def update_gui(self):
        """Main GUI update loop."""
        try:
            # Update plots if data is available
            if self.data_manager.current_data is not None and not self.data_manager.current_data.empty:
                self.update_plots()
            
            # Update progress
            self.update_progress()
            
        except Exception as e:
            print(f"GUI update error: {e}")
        
        # Schedule next update
        self.root.after(100, self.update_gui)
    
    def on_closing(self):
        """Handle application closing."""
        if self.is_experiment_running:
            if messagebox.askyesno("Confirm Exit", "Experiment is running. Stop and exit?"):
                self.stop_experiment()
            else:
                return
        
        self.disconnect_serial()
        self.root.destroy()

def main():
    """Main application entry point."""
    root = tk.Tk()
    app = TribologyExperimentGUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()
