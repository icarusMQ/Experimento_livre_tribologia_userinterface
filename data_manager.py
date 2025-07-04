import pandas as pd
import numpy as np
from datetime import datetime
import os
from typing import Dict, List, Any, Optional

class DataManager:
    """Manages experiment data collection, storage, and analysis."""
    
    def __init__(self, save_directory: str = "experiment_data"):
        self.save_directory = save_directory
        self.current_data = pd.DataFrame()
        self.experiment_start_time: Optional[datetime] = None
        self.experiment_data = []
        self.is_experiment_running = False
        
        # Create save directory if it doesn't exist
        os.makedirs(save_directory, exist_ok=True)
    
    def start_experiment(self):
        """Start a new experiment data collection."""
        self.experiment_start_time = datetime.now()
        self.experiment_data = []
        self.is_experiment_running = True
        print(f"Started experiment data collection at {self.experiment_start_time}")
    
    def stop_experiment(self):
        """Stop experiment data collection."""
        self.is_experiment_running = False
        if self.experiment_data:
            self.save_experiment_data()
        print("Stopped experiment data collection")
    
    def add_data_point(self, data: Dict[str, Any]):
        """Add a data point to the current experiment."""
        if not self.is_experiment_running:
            return
            
        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.now()
        
        # Add to experiment data
        self.experiment_data.append(data)
        
        # Update current dataframe for real-time plotting
        if data.get("is_experiment", False):
            df_row = {
                "time": data.get("time", 0),
                "force_x": data.get("force_x", np.nan),
                "force_z": data.get("force_z", np.nan),
                "timestamp": data["timestamp"]
            }
            
            # Convert to DataFrame and append
            new_row = pd.DataFrame([df_row])
            if self.current_data.empty:
                self.current_data = new_row
            else:
                self.current_data = pd.concat([self.current_data, new_row], ignore_index=True)
    
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
        if not self.experiment_data:
            return ""
        
        if filename is None:
            timestamp = self.experiment_start_time.strftime("%Y%m%d_%H%M%S") if self.experiment_start_time else datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"experiment_{timestamp}.csv"
        
        filepath = os.path.join(self.save_directory, filename)
        
        # Convert experiment data to DataFrame
        df = pd.DataFrame(self.experiment_data)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        print(f"Experiment data saved to: {filepath}")
        return filepath
    
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
