import json
import os
from datetime import datetime
from typing import Dict, Any

class Config:
    """Configuration manager for the tribology experiment."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = {
            "experiment_parameters": {
                "USE_FORCE_CONTROL_MODE": False,
                "RPM_PUMP": 500.0,
                "RPM_AXIS": 80.0,
                "RPM_FORCE": 60.0,
                "EXPERIMENT_DURATION_S": 282.1
            },
            "serial_settings": {
                "port": "COM3",
                "baudrate": 115200,
                "timeout": 1.0
            },
            "data_settings": {
                "save_directory": "experiment_data",
                "auto_save": True,
                "plot_update_interval": 100  # milliseconds
            }
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create with defaults."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_config(self.default_config, config)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return self.default_config.copy()
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded config with defaults."""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, section: str, key: str = None) -> Any:
        """Get configuration value."""
        if key is None:
            return self.config.get(section, {})
        return self.config.get(section, {}).get(key)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set configuration value."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()
    
    def get_experiment_params(self) -> Dict[str, Any]:
        """Get experiment parameters."""
        return self.config["experiment_parameters"]
    
    def set_experiment_param(self, key: str, value: Any) -> None:
        """Set experiment parameter."""
        self.set("experiment_parameters", key, value)
