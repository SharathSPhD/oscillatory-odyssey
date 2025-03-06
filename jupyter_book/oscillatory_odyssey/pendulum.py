"""
Pendulum physics module for simulating parametric excitation in a swing.

This module provides the core physics model for a parametric pendulum,
which is a pendulum with a time-varying length.
"""

import numpy as np

__all__ = ['ParametricPendulum']
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import os
import yaml
import json


class ParametricPendulum:
    """
    A class to simulate a parametric pendulum (swing) with variable length.
    
    This models a swing where the length changes over time, similar to how
    a person pumps a swing by standing and squatting at specific times.
    """
    def __init__(self, config_path=None):
        """
        Initialize the parametric pendulum with default parameters or from a config file.
        
        Parameters:
        -----------
        config_path : str, optional
            Path to a YAML or JSON configuration file
        """
        # Default parameters
        self.params = {
            "g": 9.81,                # Gravitational acceleration (m/s^2)
            "L0": 2.0,                # Base pendulum length (m)
            "delta_L": 0.15,          # Change in length during pumping (m)
            "m": 30.0,                # Mass (kg)
            "damping": 0.1,           # Damping coefficient
            "pumping_freq": 0.705,    # Frequency of length change (Hz)
            "pumping_phase": 0.0,     # Phase offset for pumping (radians)
            "theta0": 0.1,            # Initial angle (radians)
            "omega0": 0.0,            # Initial angular velocity (radians/s)
            "T": 30.0,                # Total simulation time (s)
            "dt": 0.03,               # Time step for output (s)
            "method": "RK45",         # Integration method
            "rtol": 1e-6,             # Relative tolerance for solver
            "atol": 1e-9,             # Absolute tolerance for solver
            "pumping_strategy": "sinusoidal",  # Strategy for length variation
            "standing_time": 0.2,     # Fraction of half-period to stand (for square wave)
            "pumping_amp_factor": 1.0, # Amplitude factor for pumping
            "resonant_tuning": True,  # Whether to tune pumping to resonant frequency
            "adaptive_threshold": 0.1 # Threshold for adaptive pumping (radians)
        }
        
        # Current state (will be updated during simulation)
        self.current_state = [self.params["theta0"], self.params["omega0"]]
        
        # Load configuration if provided
        if config_path:
            self.load_config(config_path)
            
        # Calculate natural frequency
        # Ensure base length is positive to prevent division by zero
        self.params["L0"] = max(0.1, self.params["L0"])
        self.omega_n = np.sqrt(self.params["g"] / self.params["L0"])
        
        # Adjust pumping frequency if resonant tuning is enabled
        if self.params["resonant_tuning"]:
            # For parametric resonance, pumping at twice the natural frequency is optimal
            self.params["pumping_freq"] = self.omega_n / np.pi  # Converts rad/s to Hz
            # No print statement here to avoid duplicate messages
    
    def load_config(self, config_path):
        """
        Load parameters from a configuration file.
        
        Parameters:
        -----------
        config_path : str
            Path to the configuration file (YAML or JSON)
        """
        _, ext = os.path.splitext(config_path)
        try:
            if ext.lower() == '.json':
                with open(config_path, 'r') as f:
                    loaded_params = json.load(f)
            elif ext.lower() in ['.yaml', '.yml']:
                with open(config_path, 'r') as f:
                    loaded_params = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported config file format: {ext}")
                
            # Update parameters with loaded values
            for key, value in loaded_params.items():
                if key in self.params:
                    self.params[key] = value
                else:
                    print(f"Warning: Unknown parameter '{key}' in config file")
                    
        except Exception as e:
            print(f"Error loading config file: {e}")
    
    def save_config(self, config_path='swing_config.yaml'):
        """
        Save current parameters to a configuration file.
        
        Parameters:
        -----------
        config_path : str
            Path to save the configuration file
        """
        _, ext = os.path.splitext(config_path)
        try:
            if ext.lower() == '.json':
                with open(config_path, 'w') as f:
                    json.dump(self.params, f, indent=4)
            elif ext.lower() in ['.yaml', '.yml']:
                with open(config_path, 'w') as f:
                    yaml.dump(self.params, f, default_flow_style=False)
            else:
                raise ValueError(f"Unsupported config file format: {ext}")
                
            print(f"Configuration saved to {config_path}")
                
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def length_function(self, t):
        """
        Calculate the pendulum length at time t based on the pumping strategy.
        
        Parameters:
        -----------
        t : float
            Time (seconds)
        
        Returns:
        --------
        float
            Pendulum length at time t
        """
        # Ensure minimum length to prevent numerical instability
        min_length = 0.1
        L0 = self.params["L0"]
        delta_L = self.params["delta_L"]
        freq = self.params["pumping_freq"]
        phase = self.params["pumping_phase"]
        amp_factor = self.params["pumping_amp_factor"]
        
        if self.params["pumping_strategy"] == "sinusoidal":
            # Smooth sinusoidal variation
            length = L0 + amp_factor * delta_L * np.sin(2 * np.pi * freq * t + phase)
            return max(min_length, length)
        
        elif self.params["pumping_strategy"] == "square":
            # Square wave - sharp transitions between lengths
            period = 1.0 / freq
            t_mod = t % period
            standing_duration = self.params["standing_time"] * period / 2
            
            if t_mod < standing_duration or (period/2 < t_mod < period/2 + standing_duration):
                return max(min_length, L0 + amp_factor * delta_L)  # Stand (longer)
            else:
                return max(min_length, L0 - amp_factor * delta_L)  # Squat (shorter)
        
        elif self.params["pumping_strategy"] == "adaptive":
            # Adaptive strategy: shorten near the equilibrium, lengthen at extremes
            # This approximates what a human might do on a swing
            theta, omega = self.current_state
            theta_threshold = self.params["adaptive_threshold"]
            
            if abs(theta) < theta_threshold:
                # Near the equilibrium position, squat (shorten) to increase angular velocity
                return L0 - amp_factor * delta_L
            else:
                # Near the extremes, stand (lengthen) to increase potential energy
                return L0 + amp_factor * delta_L
        
        else:
            # Default to constant length if strategy is unknown
            print(f"Warning: Unknown pumping strategy '{self.params['pumping_strategy']}'")
            return L0
    
    def length_derivative(self, t):
        """
        Calculate the derivative of pendulum length at time t.
        
        Parameters:
        -----------
        t : float
            Time (seconds)
        
        Returns:
        --------
        float
            Rate of change of pendulum length at time t
        """
        delta_L = self.params["delta_L"]
        freq = self.params["pumping_freq"]
        phase = self.params["pumping_phase"]
        amp_factor = self.params["pumping_amp_factor"]
        
        if self.params["pumping_strategy"] == "sinusoidal":
            # Derivative of sinusoidal function
            return amp_factor * delta_L * 2 * np.pi * freq * np.cos(2 * np.pi * freq * t + phase)
        
        elif self.params["pumping_strategy"] == "square":
            # Derivative of square wave is technically infinite at transitions
            # For numerical purposes, we return 0 (the function is constant between transitions)
            return 0.0
        
        elif self.params["pumping_strategy"] == "adaptive":
            # For adaptive strategy, the derivative depends on state changes
            # This is a simplified approximation
            return 0.0
        
        else:
            # Default to zero derivative for constant length
            return 0.0
    
    def ode_system(self, t, y):
        """
        Define the ODE system for the parametric pendulum.
        
        Parameters:
        -----------
        t : float
            Time (seconds)
        y : array_like
            State vector [theta, omega]
        
        Returns:
        --------
        array_like
            Derivatives [dtheta/dt, domega/dt]
        """
        theta, omega = y
        self.current_state = [theta, omega]
        
        # Get current length and its derivative
        l_t = self.length_function(t)
        dl_dt = self.length_derivative(t)
        
        # Calculate derivatives
        dtheta_dt = omega
        domega_dt = -(self.params["g"] / l_t) * np.sin(theta) - \
                    self.params["damping"] * omega - \
                    (2 / l_t) * dl_dt * omega
        
        return [dtheta_dt, domega_dt]
    
    def simulate(self):
        """
        Run the simulation of the parametric pendulum.
        
        Returns:
        --------
        dict
            Simulation results including time, theta, omega, and length arrays
        """
        # Set up time points
        t_span = (0, self.params["T"])
        t_eval = np.arange(0, self.params["T"], self.params["dt"])
        
        # Set up initial conditions
        y0 = [self.params["theta0"], self.params["omega0"]]
        
        # Solve the ODE system
        solution = solve_ivp(
            self.ode_system,
            t_span,
            y0,
            method=self.params["method"],
            t_eval=t_eval,
            rtol=self.params["rtol"],
            atol=self.params["atol"]
        )
        
        # Extract results
        t = solution.t
        theta = solution.y[0]
        omega = solution.y[1]
        
        # Calculate length at each time point
        length = np.array([self.length_function(t_i) for t_i in t])
        
        # Calculate energies
        kinetic_energy = self.calculate_kinetic_energy(theta, omega, length)
        potential_energy = self.calculate_potential_energy(theta, length)
        total_energy = kinetic_energy + potential_energy
        
        # Calculate Cartesian coordinates
        x = length * np.sin(theta)
        y = -length * np.cos(theta)
        
        # Package results
        results = {
            "t": t,
            "theta": theta,
            "omega": omega,
            "length": length,
            "x": x,
            "y": y,
            "kinetic_energy": kinetic_energy,
            "potential_energy": potential_energy,
            "total_energy": total_energy
        }
        
        return results
    
    def calculate_kinetic_energy(self, theta, omega, length):
        """
        Calculate the kinetic energy at each time point.
        
        Parameters:
        -----------
        theta : array_like
            Angle array
        omega : array_like
            Angular velocity array
        length : array_like
            Pendulum length array
        
        Returns:
        --------
        array_like
            Kinetic energy at each time point
        """
        m = self.params["m"]
        
        # KE = (1/2) * m * (l * omega)^2
        return 0.5 * m * (length * omega)**2
    
    def calculate_potential_energy(self, theta, length):
        """
        Calculate the potential energy at each time point.
        
        Parameters:
        -----------
        theta : array_like
            Angle array
        length : array_like
            Pendulum length array
        
        Returns:
        --------
        array_like
            Potential energy at each time point
        """
        m = self.params["m"]
        g = self.params["g"]
        
        # PE = m * g * l * (1 - cos(theta))
        # (reference level is at the pivot)
        return m * g * length * (1 - np.cos(theta))


if __name__ == "__main__":
    # Simple test of the pendulum model
    pendulum = ParametricPendulum()
    results = pendulum.simulate()
    
    # Plot the results
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.plot(results["time"], results["theta"])
    plt.xlabel("Time (s)")
    plt.ylabel("Angle (rad)")
    plt.title("Pendulum Angle")
    
    plt.subplot(2, 2, 2)
    plt.plot(results["time"], results["length"])
    plt.xlabel("Time (s)")
    plt.ylabel("Length (m)")
    plt.title("Pendulum Length")
    
    plt.subplot(2, 2, 3)
    plt.plot(results["theta"], results["omega"])
    plt.xlabel("Angle (rad)")
    plt.ylabel("Angular Velocity (rad/s)")
    plt.title("Phase Space")
    
    plt.subplot(2, 2, 4)
    plt.plot(results["time"], results["kinetic_energy"], label="Kinetic")
    plt.plot(results["time"], results["potential_energy"], label="Potential")
    plt.plot(results["time"], results["total_energy"], label="Total")
    plt.xlabel("Time (s)")
    plt.ylabel("Energy (J)")
    plt.title("Energy")
    plt.legend()
    
    plt.tight_layout()
    plt.show()
