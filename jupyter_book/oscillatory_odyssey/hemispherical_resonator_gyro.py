"""
Hemispherical Resonator Gyroscope physics module.

This module provides the physics model for a Hemispherical Resonator Gyroscope (HRG),
demonstrating the wine-glass mode vibrations, precession due to rotation via the Bryan effect,
frequency mismatch errors, and parametric excitation for sustaining oscillations.
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import os
import yaml
import json


class HemisphericalResonatorGyroSimulation:
    """
    A class to simulate a Hemispherical Resonator Gyroscope.
    
    This model simulates a 2D coupled oscillator representing the n=2 wine-glass
    vibration modes of an HRG. It includes Coriolis coupling via the Bryan factor,
    frequency mismatch effects, and parametric excitation.
    """
    def __init__(self, config_path=None):
        """
        Initialize the HRG simulation with default parameters or from a config file.
        
        Parameters:
        -----------
        config_path : str, optional
            Path to a YAML or JSON configuration file
        """
        # Default parameters
        self.params = {
            # Resonator geometric parameters
            "resonator_radius": 0.03,        # Radius of resonator (m)
            "resonator_thickness": 0.001,    # Thickness of resonator (m)
            
            # Material properties
            "youngs_modulus": 7e10,          # Young's modulus (Pa) - fused silica
            "density": 2200,                 # Density (kg/m³) - fused silica
            "poissons_ratio": 0.17,          # Poisson's ratio - fused silica
            
            # Oscillation parameters
            "natural_frequency": 10000,      # Natural frequency (Hz)
            "damping_ratio": 0.0001,         # Damping ratio (Q ≈ 5000)
            "frequency_mismatch": 0.0,       # Normalized frequency mismatch between modes
            
            # Rotation parameters
            "rotation_rate": 1.0,            # Rotation rate (rad/s)
            "bryan_factor": 0.3,             # Bryan factor (gyroscopic gain)
            
            # Excitation parameters
            "parametric_excitation_enabled": True,  # Enable parametric excitation
            "parametric_excitation_amp": 0.001,     # Parametric excitation amplitude
            "force_excitation_amp": 0.0,            # Direct force excitation amplitude
            
            # Nonlinearity parameters
            "cubic_stiffness": 0.01,         # Cubic stiffness coefficient for limit cycle

            # Initial conditions
            "x0": 1.0,                       # Initial x displacement
            "y0": 0.0,                       # Initial y displacement
            "dx0": 0.0,                      # Initial x velocity
            "dy0": 0.0,                      # Initial y velocity
            
            # Error modeling
            "noise_enabled": True,           # Enable noise modeling
            "noise_amplitude": 1e-5,         # Noise amplitude
            "bias_drift_enabled": True,      # Enable random walk bias drift
            "bias_drift_sigma": 1e-6,        # Bias drift standard deviation (rad/s/√Hz)
            
            # Simulation parameters
            "T": 5.0,                        # Total simulation time (s)
            "dt": 1e-5,                      # Time step for calculations (s)
            "output_dt": 5e-4,               # Time step for output data (s)
            "method": "RK45",                # Integration method
            "rtol": 1e-6,                    # Relative tolerance for solver
            "atol": 1e-9,                    # Absolute tolerance for solver
            "animation_speed_factor": 5.0,   # Factor to adjust visualization speed
            "mode_shape_amplitude": 0.3,     # Amplitude for mode shape visualization
        }
        
        # Load configuration if provided
        if config_path:
            self.load_config(config_path)
        
        # Calculate derived parameters
        self.update_derived_parameters()
            
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
    
    def save_config(self, config_path='hrg_config.yaml'):
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
    
    def update_derived_parameters(self):
        """
        Calculate and update derived parameters based on current settings.
        """
        # Calculate angular frequency (rad/s) from natural frequency (Hz)
        self.params["angular_frequency"] = 2 * np.pi * self.params["natural_frequency"]
        
        # Calculate oscillation period
        self.params["oscillation_period"] = 1.0 / self.params["natural_frequency"]
        
        # Calculate parametric excitation frequency (2× natural frequency)
        self.params["parametric_frequency"] = 2 * self.params["angular_frequency"]
        
        # Calculate quality factor from damping ratio
        self.params["quality_factor"] = 1.0 / (2.0 * self.params["damping_ratio"])
        
        # Calculate theoretical scale factor (rad/rad/s)
        # Scale factor is proportional to Bryan factor
        self.params["scale_factor"] = self.params["bryan_factor"] / self.params["natural_frequency"]
        
    def ode_system(self, t, y):
        """
        Define the ODE system for the HRG simulation.
        
        Parameters:
        -----------
        t : float
            Time (seconds)
        y : array_like
            State vector [x, dx/dt, y, dy/dt]
            
        Returns:
        --------
        array_like
            Derivatives [dx/dt, d²x/dt², dy/dt, d²y/dt²]
        """
        x, x_dot, y, y_dot = y
        
        # Extract parameters
        omega_n = self.params["angular_frequency"]
        zeta = self.params["damping_ratio"]
        Omega = self.params["rotation_rate"]
        beta = self.params["bryan_factor"]
        
        # Frequency mismatch (anisotropy)
        delta_omega = self.params["frequency_mismatch"] * omega_n
        
        # Parametric excitation (stiffness modulation at 2× natural frequency)
        p_amp = 0.0
        if self.params["parametric_excitation_enabled"]:
            p_amp = self.params["parametric_excitation_amp"]
            p_freq = self.params["parametric_frequency"]
            parametric_term = p_amp * np.cos(p_freq * t)
        else:
            parametric_term = 0.0
            
        # Force excitation (optional)
        f_amp = self.params["force_excitation_amp"]
        force_x = f_amp * np.cos(omega_n * t) if f_amp > 0 else 0.0
        force_y = f_amp * np.sin(omega_n * t) if f_amp > 0 else 0.0
        
        # Nonlinear cubic stiffness term for limit cycle formation
        cubic_k = self.params["cubic_stiffness"]
        nonlinear_x = cubic_k * omega_n**2 * x**3
        nonlinear_y = cubic_k * omega_n**2 * y**3
        
        # Noise terms (random excitation)
        noise_x = 0.0
        noise_y = 0.0
        if self.params["noise_enabled"]:
            noise_amp = self.params["noise_amplitude"]
            noise_x = noise_amp * np.random.normal()
            noise_y = noise_amp * np.random.normal()
        
        # Equations of motion for 2D coupled oscillator with Coriolis effect
        # x'' + 2ζω_n x' + ω_n²(1 + ε cos(2ω_n t))x - 2Ωβy' + δω y + k x³ = F_x + noise_x
        # y'' + 2ζω_n y' + ω_n²(1 + ε cos(2ω_n t))y + 2Ωβx' + δω x + k y³ = F_y + noise_y
        
        # Calculate accelerations
        x_ddot = (-2 * zeta * omega_n * x_dot
                 - omega_n**2 * (1 + parametric_term) * x
                 + 2 * Omega * beta * y_dot  # Coriolis term
                 - delta_omega * y           # Frequency mismatch term
                 - nonlinear_x               # Nonlinear stiffness
                 + force_x + noise_x)        # Force and noise
                 
        y_ddot = (-2 * zeta * omega_n * y_dot
                 - omega_n**2 * (1 + parametric_term) * y
                 - 2 * Omega * beta * x_dot  # Coriolis term
                 - delta_omega * x           # Frequency mismatch term
                 - nonlinear_y               # Nonlinear stiffness
                 + force_y + noise_y)        # Force and noise
        
        return [x_dot, x_ddot, y_dot, y_ddot]
    
    def simulate(self):
        """
        Run the HRG simulation.
        
        Returns:
        --------
        dict
            Simulation results including time, displacements, velocities,
            measured rotation rates, and comparison with actual values.
        """
        # Update derived parameters in case parameters have changed
        self.update_derived_parameters()
        
        # Set up time points
        t_span = (0, self.params["T"])
        t_eval = np.arange(0, self.params["T"], self.params["output_dt"])
        
        # Set up initial conditions [x, x_dot, y, y_dot]
        y0 = [
            self.params["x0"],
            self.params["dx0"],
            self.params["y0"],
            self.params["dy0"]
        ]
        
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
        x = solution.y[0]  # x displacement
        x_dot = solution.y[1]  # x velocity
        y = solution.y[2]  # y displacement
        y_dot = solution.y[3]  # y velocity
        
        # Calculate amplitude and phase information
        amplitude = np.sqrt(x**2 + y**2)  # Total vibration amplitude
        phase = np.arctan2(y, x)  # Phase angle of vibration pattern
        
        # Calculate energy in the oscillator
        omega_n = self.params["angular_frequency"]
        kinetic_energy = 0.5 * (x_dot**2 + y_dot**2)
        potential_energy = 0.5 * omega_n**2 * (x**2 + y**2)
        total_energy = kinetic_energy + potential_energy
        
        # Calculate measured rotation rate from phase change
        # The phase angle change rate is proportional to rotation rate by the Bryan factor
        phase_unwrapped = np.unwrap(phase)
        phase_diff = np.zeros_like(t)
        
        # Calculate instantaneous phase change rate (derivative of phase)
        dt = np.diff(t)
        dphase = np.diff(phase_unwrapped)
        phase_rate = np.zeros_like(t)
        phase_rate[1:] = dphase / dt
        
        # Calculate measured rotation rate from phase rate
        # Ω_measured = (phase_rate / bryan_factor)
        measured_rotation_rate = phase_rate / self.params["bryan_factor"]
        
        # Add bias drift if enabled
        if self.params["bias_drift_enabled"]:
            drift_sigma = self.params["bias_drift_sigma"]
            drift = np.cumsum(np.random.normal(0, drift_sigma * np.sqrt(self.params["output_dt"]), size=len(t)))
            measured_rotation_rate += drift
        
        # Calculate error between measured and actual rotation rates
        actual_rotation_rate = np.ones_like(t) * self.params["rotation_rate"]
        error = measured_rotation_rate - actual_rotation_rate
        
        # Calculate mode shapes for visualization
        mode_shapes = self.calculate_mode_shapes(t, x, y)
        
        # Package results
        results = {
            "t": t,
            "x": x,
            "x_dot": x_dot,
            "y": y,
            "y_dot": y_dot,
            "amplitude": amplitude,
            "phase": phase,
            "phase_unwrapped": phase_unwrapped,
            "phase_rate": phase_rate,
            "kinetic_energy": kinetic_energy,
            "potential_energy": potential_energy,
            "total_energy": total_energy,
            "measured_rotation_rate": measured_rotation_rate,
            "actual_rotation_rate": actual_rotation_rate,
            "error": error,
            "mode_shapes": mode_shapes,
            
            # Store simulation parameters
            "natural_frequency": self.params["natural_frequency"],
            "damping_ratio": self.params["damping_ratio"],
            "rotation_rate": self.params["rotation_rate"],
            "bryan_factor": self.params["bryan_factor"],
            "frequency_mismatch": self.params["frequency_mismatch"],
            "scale_factor": self.params["scale_factor"],
            "parametric_excitation_enabled": self.params["parametric_excitation_enabled"],
            "parametric_excitation_amp": self.params["parametric_excitation_amp"]
        }
        
        # Calculate additional statistics
        results["mean_error"] = np.mean(error)
        results["std_error"] = np.std(error)
        results["max_error"] = np.max(np.abs(error))
        
        return results
    
    def calculate_mode_shapes(self, t, x, y):
        """
        Calculate mode shapes for visualization.
        
        Parameters:
        -----------
        t : array_like
            Time points
        x : array_like
            X displacement
        y : array_like
            Y displacement
            
        Returns:
        --------
        dict
            Dictionary containing mode shape data for visualization
        """
        # Number of points around the circle for visualization
        n_points = 100
        theta = np.linspace(0, 2*np.pi, n_points)
        
        # Amplitude for visualization
        amplitude = self.params["mode_shape_amplitude"]
        
        # Base circular shape
        circle_x = np.cos(theta)
        circle_y = np.sin(theta)
        
        # Calculate n=2 mode shapes
        # First mode: cos(2θ) pattern
        mode1_pattern = np.cos(2*theta)
        
        # Second mode: sin(2θ) pattern
        mode2_pattern = np.sin(2*theta)
        
        # Number of time points
        n_times = len(t)
        
        # Initialize arrays to store mode shapes
        mode1_shapes = np.zeros((n_times, n_points, 2))
        mode2_shapes = np.zeros((n_times, n_points, 2))
        combined_shapes = np.zeros((n_times, n_points, 2))
        
        # Calculate mode shapes at each time point
        for i in range(n_times):
            # Mode 1 shape: circular shape + cos(2θ) pattern with x[i] amplitude
            r1 = 1 + amplitude * x[i] * mode1_pattern
            mode1_shapes[i, :, 0] = r1 * circle_x
            mode1_shapes[i, :, 1] = r1 * circle_y
            
            # Mode 2 shape: circular shape + sin(2θ) pattern with y[i] amplitude
            r2 = 1 + amplitude * y[i] * mode2_pattern
            mode2_shapes[i, :, 0] = r2 * circle_x
            mode2_shapes[i, :, 1] = r2 * circle_y
            
            # Combined shape: superposition of both modes
            r_combined = 1 + amplitude * (x[i] * mode1_pattern + y[i] * mode2_pattern)
            combined_shapes[i, :, 0] = r_combined * circle_x
            combined_shapes[i, :, 1] = r_combined * circle_y
        
        return {
            "theta": theta,
            "circle_x": circle_x,
            "circle_y": circle_y,
            "mode1_shapes": mode1_shapes,
            "mode2_shapes": mode2_shapes,
            "combined_shapes": combined_shapes
        }


if __name__ == "__main__":
    # Simple test of the HRG model
    hrg = HemisphericalResonatorGyroSimulation()
    results = hrg.simulate()
    
    # Plot the results
    plt.figure(figsize=(12, 10))
    
    # Plot displacements
    plt.subplot(3, 2, 1)
    plt.plot(results["t"], results["x"], label='X displacement')
    plt.plot(results["t"], results["y"], label='Y displacement')
    plt.xlabel("Time (s)")
    plt.ylabel("Displacement")
    plt.title("Mode Displacements")
    plt.grid(True)
    plt.legend()
    
    # Plot phase
    plt.subplot(3, 2, 2)
    plt.plot(results["t"], results["phase_unwrapped"])
    plt.xlabel("Time (s)")
    plt.ylabel("Phase (rad)")
    plt.title("Vibration Pattern Phase")
    plt.grid(True)
    
    # Plot phase space (x vs y)
    plt.subplot(3, 2, 3)
    plt.plot(results["x"], results["y"])
    plt.xlabel("X displacement")
    plt.ylabel("Y displacement")
    plt.title("Phase Space Trajectory")
    plt.grid(True)
    plt.axis('equal')
    
    # Plot energy
    plt.subplot(3, 2, 4)
    plt.plot(results["t"], results["kinetic_energy"], label='Kinetic')
    plt.plot(results["t"], results["potential_energy"], label='Potential')
    plt.plot(results["t"], results["total_energy"], label='Total')
    plt.xlabel("Time (s)")
    plt.ylabel("Energy")
    plt.title("System Energy")
    plt.grid(True)
    plt.legend()
    
    # Plot rotation rates
    plt.subplot(3, 2, 5)
    plt.plot(results["t"], results["measured_rotation_rate"], label='Measured')
    plt.plot(results["t"], results["actual_rotation_rate"], label='Actual')
    plt.xlabel("Time (s)")
    plt.ylabel("Rotation Rate (rad/s)")
    plt.title("Rotation Rate Measurement")
    plt.grid(True)
    plt.legend()
    
    # Plot error
    plt.subplot(3, 2, 6)
    plt.plot(results["t"], results["error"])
    plt.xlabel("Time (s)")
    plt.ylabel("Error (rad/s)")
    plt.title(f"Measurement Error (Mean: {results['mean_error']:.3e} rad/s)")
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
