"""
Quick test to verify the dynamic UI functionality works correctly.
"""

import tkinter as tk
from config import Config

def test_config_with_force_mode():
    """Test configuration with force control mode enabled."""
    config = Config()
    
    # Test with force mode enabled
    config.set_experiment_param("USE_FORCE_CONTROL_MODE", True)
    params = config.get_experiment_params()
    
    print("=== Force Control Mode ENABLED ===")
    for key, value in params.items():
        print(f"{key}: {value}")
    
    # Test with force mode disabled  
    config.set_experiment_param("USE_FORCE_CONTROL_MODE", False)
    params = config.get_experiment_params()
    
    print("\n=== Force Control Mode DISABLED ===")
    for key, value in params.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    print("Testing Dynamic UI Configuration...")
    test_config_with_force_mode()
    print("\nConfiguration test completed!")
    print("\nTo test the GUI:")
    print("1. Run: python UI_experimento_livre_main.py")
    print("2. Go to Configuration tab")
    print("3. Toggle 'Use Force Control Mode' checkbox")
    print("4. Watch RPM Force and Target Force fields show/hide")
