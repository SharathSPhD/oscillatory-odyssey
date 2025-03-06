"""
Utility functions for the oscillatory_odyssey package.

This module provides helper functions for configuration management,
data processing, and other common tasks.
"""

import os
import yaml
import json
import numpy as np
import matplotlib.pyplot as plt


def save_config(params, filename='config.yaml'):
    """
    Save a configuration dictionary to a file.
    
    Parameters:
    -----------
    params : dict
        Dictionary of parameters to save
    filename : str, optional
        Filename to save the configuration to
    
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Determine file type and save accordingly
        _, ext = os.path.splitext(filename)
        if ext.lower() == '.json':
            with open(filename, 'w') as f:
                json.dump(params, f, indent=4)
        elif ext.lower() in ['.yaml', '.yml']:
            with open(filename, 'w') as f:
                yaml.dump(params, f, default_flow_style=False)
        else:
            print(f"Unsupported file format: {ext}. Use .yaml, .yml, or .json")
            return False
        
        print(f"Configuration saved to {filename}")
        return True
    
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False


def load_config(filename):
    """
    Load a configuration dictionary from a file.
    
    Parameters:
    -----------
    filename : str
        Path to the configuration file
        
    Returns:
    --------
    dict or None
        Dictionary of parameters if successful, None otherwise
    """
    try:
        if not os.path.exists(filename):
            print(f"Config file not found: {filename}")
            return None
        
        _, ext = os.path.splitext(filename)
        if ext.lower() == '.json':
            with open(filename, 'r') as f:
                return json.load(f)
        elif ext.lower() in ['.yaml', '.yml']:
            with open(filename, 'r') as f:
                return yaml.safe_load(f)
        else:
            print(f"Unsupported file format: {ext}. Use .yaml, .yml, or .json")
            return None
    
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None


def generate_example_configs(base_dir='config'):
    """
    Generate example configuration files for different scenarios.
    
    Parameters:
    -----------
    base_dir : str, optional
        Directory to save the configuration files
        
    Returns:
    --------
    list
        List of saved configuration filenames
    """
    # Create directory if it doesn't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Basic configuration (default values)
    basic_config = {
        "g": 9.81,                # Gravitational acceleration (m/s^2)
        "L0": 2.0,                # Base pendulum length (m)
        "delta_L": 0.5,           # Change in length during pumping (m)
        "m": 30.0,                # Mass (kg)
        "damping": 0.1,           # Damping coefficient
        "pumping_freq": 1.0,      # Frequency of length change (Hz)
        "pumping_phase": 0.0,     # Phase offset for pumping (radians)
        "theta0": 0.1,            # Initial angle (radians)
        "omega0": 0.0,            # Initial angular velocity (radians/s)
        "T": 30.0,                # Total simulation time (s)
        "dt": 0.05,               # Time step for output (s)
        "method": "RK45",         # Integration method
        "rtol": 1e-6,             # Relative tolerance for solver
        "atol": 1e-9,             # Absolute tolerance for solver
        "pumping_strategy": "sinusoidal",  # Strategy for length variation
        "standing_time": 0.2,     # Fraction of half-period to stand (for square wave)
        "pumping_amp_factor": 1.0, # Amplitude factor for pumping
        "resonant_tuning": True,  # Whether to tune pumping to resonant frequency
        "adaptive_threshold": 0.1 # Threshold for adaptive pumping (radians)
    }
    
    # Resonant excitation (optimal frequency)
    resonant_config = basic_config.copy()
    resonant_config["pumping_freq"] = 1.0  # Will be overridden by resonant_tuning
    resonant_config["resonant_tuning"] = True
    resonant_config["T"] = 60.0  # Longer simulation to see effect
    
    # High damping
    damped_config = basic_config.copy()
    damped_config["damping"] = 0.5
    damped_config["delta_L"] = 1.0  # Increase pumping to overcome damping
    
    # Square wave pumping
    square_config = basic_config.copy()
    square_config["pumping_strategy"] = "square"
    square_config["standing_time"] = 0.2
    
    # Adaptive pumping
    adaptive_config = basic_config.copy()
    adaptive_config["pumping_strategy"] = "adaptive"
    adaptive_config["adaptive_threshold"] = 0.1
    adaptive_config["theta0"] = 0.2  # Start with a larger angle
    
    # Playground swing
    playground_config = basic_config.copy()
    playground_config["L0"] = 3.0  # Longer swing
    playground_config["delta_L"] = 0.8  # Larger change in length
    playground_config["m"] = 35.0  # Child mass
    playground_config["damping"] = 0.15  # Realistic damping
    playground_config["theta0"] = 0.3  # Start with a push
    
    # Foucault pendulum like
    foucault_config = basic_config.copy()
    foucault_config["L0"] = 10.0  # Long pendulum
    foucault_config["delta_L"] = 0.0  # No length change
    foucault_config["damping"] = 0.05  # Low damping
    foucault_config["theta0"] = 0.2  # Initial angle
    foucault_config["pumping_freq"] = 0.0  # No pumping
    foucault_config["T"] = 120.0  # Long simulation
    
    # Save all configurations
    configs = {
        "default_config.yaml": basic_config,
        "resonant_config.yaml": resonant_config,
        "damped_config.yaml": damped_config,
        "square_config.yaml": square_config,
        "adaptive_config.yaml": adaptive_config,
        "playground_config.yaml": playground_config,
        "foucault_config.yaml": foucault_config
    }
    
    saved_files = []
    for filename, config in configs.items():
        full_path = os.path.join(base_dir, filename)
        if save_config(config, full_path):
            saved_files.append(full_path)
    
    return saved_files


def export_results(results, filename='simulation_results.npz'):
    """
    Export simulation results to a file.
    
    Parameters:
    -----------
    results : dict
        Dictionary of simulation results
    filename : str, optional
        Filename to save the results to
        
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Save the results using numpy's compressed format
        np.savez_compressed(filename, **results)
        print(f"Results saved to {filename}")
        return True
    
    except Exception as e:
        print(f"Error exporting results: {e}")
        return False


def import_results(filename):
    """
    Import simulation results from a file.
    
    Parameters:
    -----------
    filename : str
        Path to the results file
        
    Returns:
    --------
    dict or None
        Dictionary of simulation results if successful, None otherwise
    """
    try:
        if not os.path.exists(filename):
            print(f"Results file not found: {filename}")
            return None
        
        # Load the results
        data = np.load(filename)
        
        # Convert to dictionary
        results = {}
        for key in data.files:
            results[key] = data[key]
        
        return results
    
    except Exception as e:
        print(f"Error importing results: {e}")
        return None


def calculate_parametric_resonance_frequency(L0, g=9.81):
    """
    Calculate the parametric resonance frequency for a pendulum.
    
    Parameters:
    -----------
    L0 : float
        Base length of the pendulum (m)
    g : float, optional
        Gravitational acceleration (m/s^2)
        
    Returns:
    --------
    float
        Parametric resonance frequency (Hz)
    """
    # Natural frequency (rad/s)
    omega_n = np.sqrt(g / L0)
    
    # For parametric resonance, pumping at twice the natural frequency is optimal
    # Convert from rad/s to Hz
    return omega_n / np.pi


if __name__ == "__main__":
    # Generate example configuration files
    saved_files = generate_example_configs()
    print(f"Generated {len(saved_files)} configuration files.")
    
    # Test calculation of parametric resonance frequency
    L0 = 2.0  # m
    freq = calculate_parametric_resonance_frequency(L0)
    print(f"Parametric resonance frequency for L0={L0}m: {freq:.3f} Hz")
