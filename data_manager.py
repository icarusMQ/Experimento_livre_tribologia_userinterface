import pandas as pd
import numpy as np
from datetime import datetime
import os
from typing import Dict, List, Any, Optional
from collections import deque
import csv
import shutil

class DataManager:
    """Manages experiment data collection, storage, and analysis."""
    
    def __init__(self, save_directory: str = "experiment_data", plot_max_points: int = 5000, auto_save: bool = True):
        self.save_directory = save_directory
        self.plot_max_points = max(100, int(plot_max_points))
        self.auto_save = auto_save

        self.current_data = pd.DataFrame()
        self.experiment_start_time: Optional[datetime] = None
        # For long experiments, keep plotting data bounded and stream full data to CSV.
        self.experiment_data = []
        self.is_experiment_running = False

        self._plot_time = deque(maxlen=self.plot_max_points)
        self._plot_fx = deque(maxlen=self.plot_max_points)
        self._plot_fz = deque(maxlen=self.plot_max_points)
        self._plot_timestamp = deque(maxlen=self.plot_max_points)

        self._live_csv_path: Optional[str] = None
        self._csv_file = None
        self._csv_writer: Optional[csv.DictWriter] = None
        self._rows_written = 0
        self._flush_every = 200
        
        # Create save directory if it doesn't exist
        os.makedirs(save_directory, exist_ok=True)
    
    def start_experiment(self):
        """Start a new experiment data collection."""
        self.experiment_start_time = datetime.now()
        self.experiment_data = []
        self.is_experiment_running = True

        # Reset plotting buffers
        self._plot_time.clear()
        self._plot_fx.clear()
        self._plot_fz.clear()
        self._plot_timestamp.clear()
        self.current_data = pd.DataFrame()

        # Create a live CSV file immediately so long runs don't depend on RAM
        timestamp = self.experiment_start_time.strftime("%Y%m%d_%H%M%S")
        self._live_csv_path = os.path.join(self.save_directory, f"experiment_{timestamp}.csv")
        self._open_live_csv(self._live_csv_path)
        print(f"Started experiment data collection at {self.experiment_start_time}")
    
    def stop_experiment(self):
        """Stop experiment data collection."""
        self.is_experiment_running = False
        self._close_live_csv()
        # Live CSV is already written during acquisition; keep behavior of "auto-save".
        if self.auto_save and self._live_csv_path and os.path.exists(self._live_csv_path):
            print(f"Experiment data saved to: {self._live_csv_path}")
        print("Stopped experiment data collection")

    def _open_live_csv(self, filepath: str):
        # Fixed schema for stability (avoid dynamic headers mid-run)
        fieldnames = [
            "timestamp",
            "is_experiment",
            "time",
            "force_x",
            "force_z",
            "fixed_x",
            "fixed_z",
            "fx",
            "fz",
            "raw",
            "message",
        ]
        self._close_live_csv()
        self._csv_file = open(filepath, "w", newline="", encoding="utf-8")
        self._csv_writer = csv.DictWriter(self._csv_file, fieldnames=fieldnames)
        self._csv_writer.writeheader()
        self._rows_written = 0

    def _close_live_csv(self):
        try:
            if self._csv_file:
                try:
                    self._csv_file.flush()
                except Exception:
                    pass
                self._csv_file.close()
        finally:
            self._csv_file = None
            self._csv_writer = None
    
    def add_data_point(self, data: Dict[str, Any]):
        """Add a data point to the current experiment."""
        if not self.is_experiment_running:
            return
            
        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.now()

        # Stream to CSV (full-resolution storage)
        if self._csv_writer:
            row = {
                "timestamp": data.get("timestamp"),
                "is_experiment": bool(data.get("is_experiment", False)),
                "time": data.get("time"),
                "force_x": data.get("force_x"),
                "force_z": data.get("force_z"),
                "fixed_x": data.get("fixed_x"),
                "fixed_z": data.get("fixed_z"),
                "fx": data.get("fx"),
                "fz": data.get("fz"),
                "raw": data.get("raw"),
                "message": data.get("message"),
            }
            try:
                self._csv_writer.writerow(row)
                self._rows_written += 1
                if self._csv_file and (self._rows_written % self._flush_every) == 0:
                    self._csv_file.flush()
            except Exception:
                # Avoid killing acquisition if disk write fails
                pass
        
        # Update current dataframe for real-time plotting
        if data.get("is_experiment", False):
            t = data.get("time", 0)
            fx = data.get("force_x", np.nan)
            fz = data.get("force_z", np.nan)
            ts = data.get("timestamp")

            self._plot_time.append(t)
            self._plot_fx.append(fx)
            self._plot_fz.append(fz)
            self._plot_timestamp.append(ts)

            # Materialize a small DataFrame view for plotting/analysis
            self.current_data = pd.DataFrame(
                {
                    "time": list(self._plot_time),
                    "force_x": list(self._plot_fx),
                    "force_z": list(self._plot_fz),
                    "timestamp": list(self._plot_timestamp),
                }
            )
    
    def get_current_data(self) -> pd.DataFrame:
        """Get current experiment data as DataFrame."""
        return self.current_data.copy()
    
    def get_experiment_progress(self, total_duration: float) -> float:
        """Get experiment progress as percentage (0-100)."""
        if not self.is_experiment_running or self.current_data.empty:
            return 0.0
        
        current_time = self.current_data["time"].max() if not self.current_data["time"].isna().all() else 0
        progress = min((current_time / total_duration) * 100, 100) if total_duration > 0 else 0
        return progress
    
    def save_experiment_data(self, filename: Optional[str] = None) -> str:
        """Save experiment data to CSV file."""
        # Data is streamed to the live CSV during acquisition.
        if not self._live_csv_path or not os.path.exists(self._live_csv_path):
            # Back-compat: if someone filled experiment_data in-memory, fall back.
            if not self.experiment_data:
                return ""
            if filename is None:
                timestamp = self.experiment_start_time.strftime("%Y%m%d_%H%M%S") if self.experiment_start_time else datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"experiment_{timestamp}.csv"
            filepath = os.path.join(self.save_directory, filename)
            df = pd.DataFrame(self.experiment_data)
            df.to_csv(filepath, index=False)
            print(f"Experiment data saved to: {filepath}")
            return filepath

        if filename is None:
            return self._live_csv_path

        dest_path = os.path.join(self.save_directory, filename)
        if os.path.abspath(dest_path) == os.path.abspath(self._live_csv_path):
            return dest_path

        shutil.copyfile(self._live_csv_path, dest_path)
        print(f"Experiment data saved to: {dest_path}")
        return dest_path
    
    def load_experiment_data(self, filepath: str) -> pd.DataFrame:
        """Load experiment data from CSV file."""
        try:
            df = pd.read_csv(filepath)
            # Convert timestamp column if it exists
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            return df
        except Exception as e:
            print(f"Error loading data from {filepath}: {e}")
            return pd.DataFrame()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get basic statistics of current experiment data."""
        if self.current_data.empty:
            return {}
        
        stats = {}
        
        # Time statistics
        if not self.current_data["time"].isna().all():
            stats["duration"] = self.current_data["time"].max()
            stats["data_points"] = len(self.current_data)
        
        # Force statistics
        for force_col in ["force_x", "force_z"]:
            if force_col in self.current_data.columns and not self.current_data[force_col].isna().all():
                force_data = self.current_data[force_col].dropna()
                stats[f"{force_col}_mean"] = force_data.mean()
                stats[f"{force_col}_std"] = force_data.std()
                stats[f"{force_col}_min"] = force_data.min()
                stats[f"{force_col}_max"] = force_data.max()
        
        return stats
    
    def clear_current_data(self):
        """Clear current experiment data."""
        self.current_data = pd.DataFrame()
        self.experiment_data = []
        self.is_experiment_running = False
        self._plot_time.clear()
        self._plot_fx.clear()
        self._plot_fz.clear()
        self._plot_timestamp.clear()
        self._close_live_csv()
        self._live_csv_path = None
        self._rows_written = 0
    
    def export_summary_report(self, filepath: str = None) -> str:
        """Export a summary report of the experiment."""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.save_directory, f"experiment_summary_{timestamp}.txt")
        
        stats = self.get_statistics()
        
        with open(filepath, 'w') as f:
            f.write("Tribology Experiment Summary Report\n")
            f.write("=" * 50 + "\n\n")
            
            if self.experiment_start_time:
                f.write(f"Experiment Start Time: {self.experiment_start_time}\n")
            
            f.write(f"Generated: {datetime.now()}\n\n")
            
            if stats:
                f.write("Statistics:\n")
                f.write("-" * 20 + "\n")
                for key, value in stats.items():
                    if isinstance(value, float):
                        f.write(f"{key}: {value:.3f}\n")
                    else:
                        f.write(f"{key}: {value}\n")
            else:
                f.write("No data available for statistics.\n")
        
        print(f"Summary report saved to: {filepath}")
        return filepath
