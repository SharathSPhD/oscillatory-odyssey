"""
Ring Laser Gyroscope physics module based on the Sagnac effect.

This module provides the physics model for a ring laser gyroscope (RLG),
demonstrating the Sagnac effect, lock-in phenomenon, and dithering as a solution.
The model shows how counter-propagating laser beams can be used to measure rotation
without mechanical moving parts.
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import os
import yaml
import json


class RingLaserGyroSimulation:
    """
    A class to simulate a Ring Laser Gyroscope demonstrating the Sagnac effect.
    
    This models a closed optical path with counter-propagating laser beams,
    where rotation causes a phase difference between the beams due to the Sagnac effect.
    The simulation demonstrates the lock-in phenomenon at low rotation rates and
    how dithering (adding a small vibration) can mitigate this issue.
    """
    def __init__(self, config_path=None):
        """
        Initialize the RLG simulation with default parameters or from a config file.
        
        Parameters:
        -----------
        config_path : str, optional
            Path to a YAML or JSON configuration file
        """
        # Default parameters
        self.params = {
            # Geometric parameters
            "cavity_radius": 0.1,        # Radius of cavity (m)
            "cavity_shape": "square",    # Shape ("square", "triangle", "circle")
            "cavity_perimeter": None,    # Will be calculated based on shape and radius
            
            # Optical parameters
            "wavelength": 632.8e-9,      # Laser wavelength (m) - HeNe laser
            "beam_power": 0.005,         # Beam power (W)
            "quality_factor": 1e10,      # Cavity quality factor
            
            # Rotation parameters
            "rotation_rate": 1.0,        # Rotation rate (rad/s)
            "rotation_axis": [0, 0, 1],  # Rotation axis (z-axis by default)
            
            # Lock-in phenomenon and dithering
            "coupling_factor": 0.01,     # Backscatter coupling between counter-propagating beams
            "dithering_enabled": True,   # Enable dithering to prevent lock-in
            "dithering_amplitude": 0.5,  # Dithering amplitude (rad/s)
            "dithering_frequency": 400,  # Dithering frequency (Hz)

            # Environmental parameters
            "temperature": 293.15,       # Temperature (K)
            "temperature_gradient": 0.0, # Temperature gradient across cavity (K/m)
            
            # Noise and error modeling
            "shot_noise_enabled": True,  # Enable shot noise modeling
            "random_walk_enabled": True, # Enable random walk bias
            "random_walk_sigma": 1e-7,   # Random walk standard deviation (rad/s/√Hz)
            
            # Simulation parameters
            "T": 1.0,                    # Total simulation time (s)
            "dt": 1e-5,                  # Time step for calculations (s)
            "output_dt": 1e-3,           # Time step for output data (s)
            "method": "RK45",            # Integration method
            "rtol": 1e-6,                # Relative tolerance for solver
            "atol": 1e-9,                # Absolute tolerance for solver
            "demo_speed_factor": 10.0,   # Factor to adjust visualization speed
        }
        
        # Load configuration if provided
        if config_path:
            self.load_config(config_path)
        
        # Calculate derived parameters
        self.update_derived_parameters()
        
        # Current state (will be updated during simulation)
        self.current_state = {
            "phase_difference": 0.0,      # Current phase difference between beams
            "rotation_rate_measured": 0.0, # Current measured rotation rate
            "time": 0.0                   # Current simulation time
        }
            
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
    
    def save_config(self, config_path='ring_laser_gyro_config.yaml'):
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
        # Calculate cavity perimeter based on shape and radius
        shape = self.params["cavity_shape"]
        radius = self.params["cavity_radius"]
        
        if shape == "square":
            # For a square cavity, perimeter = 4 * side
            # If radius is the distance from center to side, then side = 2*radius
            self.params["cavity_perimeter"] = 8 * radius
        elif shape == "triangle":
            # For an equilateral triangle, perimeter = 3 * side
            # If radius is the distance from center to vertex, side = sqrt(3) * radius
            self.params["cavity_perimeter"] = 3 * np.sqrt(3) * radius
        elif shape == "circle":
            # For a circle, perimeter = 2 * π * radius
            self.params["cavity_perimeter"] = 2 * np.pi * radius
        else:
            # Default to circle if shape is not recognized
            print(f"Warning: Unrecognized cavity shape '{shape}'. Using circle.")
            self.params["cavity_perimeter"] = 2 * np.pi * radius
        
        # Calculate cavity area
        if shape == "square":
            self.params["cavity_area"] = 4 * radius**2
        elif shape == "triangle":
            # Area of equilateral triangle
            self.params["cavity_area"] = 3 * np.sqrt(3) * radius**2 / 4
        elif shape == "circle":
            self.params["cavity_area"] = np.pi * radius**2
        else:
            self.params["cavity_area"] = np.pi * radius**2
            
        # Calculate Sagnac scale factor
        # Scale factor = (4 * A) / (λ * c)
        # Where A = area, λ = wavelength, c = speed of light
        c = 299792458  # Speed of light (m/s)
        area = self.params["cavity_area"]
        wavelength = self.params["wavelength"]
        
        # Use enhanced scale factor for better visualization
        # This is an artificial enhancement for demonstration purposes
        # In a real RLG, the area would be much larger and therefore the scale factor would be larger
        area_enhancement = 1000.0  # Simulate a much larger cavity for better visualization
        self.params["scale_factor"] = 4 * area * area_enhancement / (wavelength * c)
        
        # Calculate sensitivity threshold (minimum detectable rotation rate)
        # Affected by shot noise and cavity parameters
        h = 6.626e-34  # Planck constant (J⋅s)
        laser_freq = c / wavelength
        power = self.params["beam_power"]
        quality = self.params["quality_factor"]
        integration_time = self.params["T"]
        
        # Calculate shot noise limited sensitivity (theoretical limit)
        # This is a simplified model - real systems have additional noise sources
        self.params["shot_noise_limit"] = (c * wavelength / (8 * np.pi * area)) * \
                                          np.sqrt(h * laser_freq / (power * quality * integration_time))
        
        # Calculate lock-in threshold
        # Below this rotation rate, lock-in occurs without dithering
        coupling = self.params["coupling_factor"]
        self.params["lock_in_threshold"] = wavelength * c * coupling / (4 * area)
        
    def calculate_phase_difference(self, rotation_rate, time):
        """
        Calculate the phase difference between counter-propagating beams due to rotation.
        
        Parameters:
        -----------
        rotation_rate : float
            Rotation rate in rad/s
        time : float
            Current time in seconds
            
        Returns:
        --------
        float
            Phase difference in radians
        """
        # Basic Sagnac phase difference: Δφ = (4*A*Ω)/(λ*c)
        # Where A = area, Ω = rotation rate, λ = wavelength, c = speed of light
        
        # First, calculate the ideal Sagnac phase shift
        ideal_phase_diff = self.params["scale_factor"] * rotation_rate
        
        # Apply dithering if enabled
        if self.params["dithering_enabled"]:
            dither_amp = self.params["dithering_amplitude"]
            dither_freq = self.params["dithering_frequency"]
            
            # Dithering creates a sinusoidal modulation of the rotation rate
            # Use a higher frequency component for better visualization
            dither_effect = dither_amp * np.sin(2 * np.pi * dither_freq * time) \
                           + 0.2 * dither_amp * np.sin(2 * np.pi * dither_freq * 2.7 * time)
            
            # Add dithering effect to the phase difference
            ideal_phase_diff += self.params["scale_factor"] * dither_effect
        
        # Model lock-in effect
        # When rotation rate is below threshold, beams tend to synchronize
        lock_in_threshold = self.params["lock_in_threshold"]
        coupling_factor = self.params["coupling_factor"]
        
        # Without dithering, rotation rates below the lock-in threshold result in no phase difference
        if not self.params["dithering_enabled"] and abs(rotation_rate) < lock_in_threshold:
            # Apply lock-in effect (reduced sensitivity at low rotation rates)
            # This is a simplified model of the complex lock-in behavior
            lock_in_factor = np.sqrt(max(0, (abs(rotation_rate) / lock_in_threshold - 1)**2))
            if lock_in_factor < 1e-6:
                lock_in_factor = 0
            ideal_phase_diff *= lock_in_factor
        
        # Add noise if enabled
        if self.params["shot_noise_enabled"]:
            # Shot noise is proportional to sqrt(laser frequency)
            shot_noise_amplitude = self.params["shot_noise_limit"] * np.sqrt(1 / self.params["dt"])
            shot_noise = np.random.normal(0, shot_noise_amplitude)
            ideal_phase_diff += shot_noise
        
        # Add random walk if enabled (to model bias drift)
        if self.params["random_walk_enabled"]:
            # Random walk step is proportional to sqrt(dt)
            step_size = self.params["random_walk_sigma"] * np.sqrt(self.params["dt"])
            random_walk_step = np.random.normal(0, step_size)
            
            # Store random walk value for consistent bias during the time step
            if not hasattr(self, 'random_walk_bias'):
                self.random_walk_bias = 0
                
            self.random_walk_bias += random_walk_step
            ideal_phase_diff += self.random_walk_bias
        
        return ideal_phase_diff
        
    def ode_system(self, t, y):
        """
        Define the ODE system for the RLG simulation.
        
        Parameters:
        -----------
        t : float
            Time (seconds)
        y : array_like
            State vector [phase_difference, integrated_phase]
            
        Returns:
        --------
        array_like
            Derivatives [d(phase_difference)/dt, d(integrated_phase)/dt]
        """
        phase_difference, integrated_phase = y
        
        # Get current rotation rate (may include time-varying effects)
        base_rotation_rate = self.params["rotation_rate"]
        
        # Calculate derivatives
        # 1. The rate of change of phase difference depends on the current rotation rate
        d_phase_diff_dt = self.calculate_phase_difference(base_rotation_rate, t) - phase_difference
        
        # 2. The integrated phase simply accumulates the phase difference
        # This gives us the total angle of rotation over time
        d_integrated_phase_dt = phase_difference
        
        return [d_phase_diff_dt, d_integrated_phase_dt]
    
    def simulate(self):
        """
        Run the RLG simulation.
        
        Returns:
        --------
        dict
            Simulation results including time, phase differences, measured rotation rates,
            and comparison with theoretical values.
        """
        # Update derived parameters in case parameters have changed
        self.update_derived_parameters()
        
        # Set up time points
        t_span = (0, self.params["T"])
        t_eval = np.arange(0, self.params["T"], self.params["output_dt"])
        
        # Set up initial conditions
        y0 = [0.0, 0.0]  # [initial phase difference, initial integrated phase]
        
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
        phase_difference = solution.y[0]
        integrated_phase = solution.y[1]
        
        # Calculate measured rotation rate from phase difference
        # Invert the Sagnac formula: Ω = (λ*c*Δφ)/(4*A)
        measured_rotation_rate = phase_difference / self.params["scale_factor"]
        
        # Calculate theoretical rotation rate at each time step
        # This includes base rotation rate and any dithering effect
        theoretical_rotation_rate = np.ones_like(t) * self.params["rotation_rate"]
        
        if self.params["dithering_enabled"]:
            dither_amp = self.params["dithering_amplitude"]
            dither_freq = self.params["dithering_frequency"]
            dither_effect = dither_amp * np.sin(2 * np.pi * dither_freq * t)
            theoretical_rotation_rate += dither_effect
        
        # Calculate error between measured and theoretical rotation rates
        error = measured_rotation_rate - theoretical_rotation_rate
        
        # Calculate interference pattern between the two beams
        # Intensity varies as I = I0 * (1 + cos(phase_difference))
        # where I0 is the intensity of each beam
        interference_intensity = 1 + np.cos(phase_difference)
        
        # Calculate photodiode signals (90° phase offset for quadrature detection)
        # Amplify the phase difference for more visible changes in photodiode signals
        # This is for visualization purposes only - the actual physics remains correct
        visualization_amplification = 5.0  # Amplification factor for visibility
        photodiode1 = np.cos(phase_difference * visualization_amplification)
        photodiode2 = np.sin(phase_difference * visualization_amplification)
        
        # Package results
        results = {
            "t": t,
            "phase_difference": phase_difference,
            "integrated_phase": integrated_phase,
            "measured_rotation_rate": measured_rotation_rate,
            "theoretical_rotation_rate": theoretical_rotation_rate,
            "error": error,
            "interference_intensity": interference_intensity,
            "photodiode1": photodiode1,
            "photodiode2": photodiode2,
            
            # Store simulation parameters
            "cavity_radius": self.params["cavity_radius"],
            "cavity_shape": self.params["cavity_shape"],
            "cavity_perimeter": self.params["cavity_perimeter"],
            "cavity_area": self.params["cavity_area"],
            "scale_factor": self.params["scale_factor"],
            "rotation_rate": self.params["rotation_rate"],
            "lock_in_threshold": self.params["lock_in_threshold"],
            "dithering_enabled": self.params["dithering_enabled"],
            "dithering_amplitude": self.params["dithering_amplitude"],
            "dithering_frequency": self.params["dithering_frequency"],
            "random_walk_enabled": self.params["random_walk_enabled"],
            "shot_noise_enabled": self.params["shot_noise_enabled"],
        }
        
        # Calculate additional statistics
        results["mean_error"] = np.mean(error)
        results["std_error"] = np.std(error)
        results["max_error"] = np.max(np.abs(error))
        
        # Calculate cavity vertices for visualization
        results.update(self.calculate_cavity_vertices())
        
        # Calculate beam positions for animation
        results.update(self.calculate_beam_positions(t))
        
        return results
    
    def calculate_cavity_vertices(self):
        """
        Calculate the vertices of the cavity for visualization.
        
        Returns:
        --------
        dict
            Dictionary with cavity vertices and related geometry.
        """
        shape = self.params["cavity_shape"]
        radius = self.params["cavity_radius"]
        
        # Handle different cavity shapes
        if shape == "square":
            # Square vertices (counterclockwise from bottom-left)
            vertices = np.array([
                [-radius, -radius, 0],  # Bottom-left
                [radius, -radius, 0],   # Bottom-right
                [radius, radius, 0],    # Top-right
                [-radius, radius, 0]    # Top-left
            ])
            
            # Mirror positions (middle of each side)
            mirrors = np.array([
                [0, -radius, 0],  # Bottom
                [radius, 0, 0],   # Right
                [0, radius, 0],   # Top
                [-radius, 0, 0]   # Left
            ])
            
        elif shape == "triangle":
            # Equilateral triangle vertices (counterclockwise from bottom-left)
            angle = 2 * np.pi / 3  # 120 degrees
            vertices = np.array([
                [radius * np.cos(np.pi/6), radius * np.sin(np.pi/6) - radius, 0],  # Bottom
                [radius * np.cos(np.pi/6 + angle), radius * np.sin(np.pi/6 + angle) - radius, 0],  # Top-left
                [radius * np.cos(np.pi/6 + 2*angle), radius * np.sin(np.pi/6 + 2*angle) - radius, 0]  # Top-right
            ])
            
            # Mirror positions (middle of each side)
            mirrors = np.array([
                [(vertices[0, 0] + vertices[1, 0])/2, (vertices[0, 1] + vertices[1, 1])/2, 0],  # Left side
                [(vertices[1, 0] + vertices[2, 0])/2, (vertices[1, 1] + vertices[2, 1])/2, 0],  # Right side
                [(vertices[2, 0] + vertices[0, 0])/2, (vertices[2, 1] + vertices[0, 1])/2, 0]   # Bottom side
            ])
            
        elif shape == "circle":
            # For a circle, we'll use 36 points around the circumference
            angles = np.linspace(0, 2*np.pi, 37)[:-1]  # 36 points (exclude last duplicate)
            x = radius * np.cos(angles)
            y = radius * np.sin(angles)
            z = np.zeros_like(x)
            vertices = np.column_stack((x, y, z))
            
            # For mirrors, we'll use 4 points at 90° intervals
            mirror_angles = np.linspace(0, 2*np.pi, 5)[:-1]  # 4 points
            mx = radius * np.cos(mirror_angles)
            my = radius * np.sin(mirror_angles)
            mz = np.zeros_like(mx)
            mirrors = np.column_stack((mx, my, mz))
            
        else:
            # Default to circle if shape is not recognized
            print(f"Warning: Unrecognized cavity shape '{shape}'. Using circle.")
            # Same as circle case above
            angles = np.linspace(0, 2*np.pi, 37)[:-1]
            x = radius * np.cos(angles)
            y = radius * np.sin(angles)
            z = np.zeros_like(x)
            vertices = np.column_stack((x, y, z))
            
            mirror_angles = np.linspace(0, 2*np.pi, 5)[:-1]
            mx = radius * np.cos(mirror_angles)
            my = radius * np.sin(mirror_angles)
            mz = np.zeros_like(mx)
            mirrors = np.column_stack((mx, my, mz))
        
        # Calculate path segments for beam visualization
        if shape == "circle":
            # For circle, we use a parameterized path
            beam_path = vertices
        else:
            # For polygon, the beam follows the mirrors
            beam_path = mirrors
        
        return {
            "cavity_vertices": vertices,
            "mirror_positions": mirrors,
            "beam_path": beam_path
        }
    
    def calculate_beam_positions(self, t):
        """
        Calculate beam positions for animation.
        
        Parameters:
        -----------
        t : array_like
            Time points from simulation
            
        Returns:
        --------
        dict
            Dictionary with beam position arrays
        """
        beam_path = self.calculate_cavity_vertices()["beam_path"]
        n_segments = len(beam_path)
        n_frames = len(t)
        
        # Calculate beam speeds based on cavity perimeter
        perimeter = self.params["cavity_perimeter"]
        c = 299792458  # Speed of light (m/s)
        
        # For visualization, we drastically slow down the beam
        # Using the demo_speed_factor parameter
        scaling = self.params["demo_speed_factor"] / c
        
        # Scale beam speed up by 50000x to make movement visible in visualization
        visual_scaling_factor = 50000
        
        n_beam_points = 20
        
        # Initialize beam position arrays
        cw_beam_positions = np.zeros((n_frames, n_beam_points, 3))
        ccw_beam_positions = np.zeros((n_frames, n_beam_points, 3))
        
        # Calculate beam positions for each frame
        for i, time in enumerate(t):
            # Clockwise beam positions (red dots)
            for j in range(n_beam_points):
                # Calculate position along the path based on time and index
                # Use the large scaling factor to make motion more visible
                position = (time * scaling * visual_scaling_factor + j/n_beam_points) % 1.0
                
                # Find the segment and interpolate
                if self.params["cavity_shape"] == "circle":
                    # For a circle, use angular interpolation
                    angle = position * 2 * np.pi
                    x = self.params["cavity_radius"] * np.cos(angle)
                    y = self.params["cavity_radius"] * np.sin(angle)
                    cw_beam_positions[i, j] = [x, y, 0]
                else:
                    # For polygons, interpolate between vertices
                    segment_length = 1.0 / n_segments
                    segment_idx = int(position / segment_length)
                    segment_pos = (position % segment_length) / segment_length
                    
                    # Ensure we handle the wrap-around correctly
                    start_idx = segment_idx % n_segments
                    end_idx = (segment_idx + 1) % n_segments
                    
                    # Linear interpolation between vertices
                    start_pos = beam_path[start_idx]
                    end_pos = beam_path[end_idx]
                    
                    cw_beam_positions[i, j] = start_pos + segment_pos * (end_pos - start_pos)
            
            # Counter-clockwise beam positions (blue dots)
            for j in range(n_beam_points):
                # Calculate position along the path based on time and index
                # Note the negative sign to go counter-clockwise
                # Use much higher scaling for counter-clockwise beam to ensure visible movement
                # Use different starting positions for CCW beam to make both beams visible
                # Add a time-dependent offset to ensure movement even with very small time changes
                ccw_scaling_factor = visual_scaling_factor * 1.5  # Make CCW beam move faster
                position = (1.0 - (time * scaling * ccw_scaling_factor + j/n_beam_points + 0.5 + time)) % 1.0
                
                # Find the segment and interpolate
                if self.params["cavity_shape"] == "circle":
                    # For a circle, use angular interpolation
                    angle = position * 2 * np.pi
                    x = self.params["cavity_radius"] * np.cos(angle)
                    y = self.params["cavity_radius"] * np.sin(angle)
                    ccw_beam_positions[i, j] = [x, y, 0]
                else:
                    # For polygons, interpolate between vertices
                    segment_length = 1.0 / n_segments
                    segment_idx = int(position / segment_length)
                    segment_pos = (position % segment_length) / segment_length
                    
                    # Ensure we handle the wrap-around correctly
                    start_idx = segment_idx % n_segments
                    end_idx = (segment_idx + 1) % n_segments
                    
                    # Linear interpolation between vertices
                    start_pos = beam_path[start_idx]
                    end_pos = beam_path[end_idx]
                    
                    ccw_beam_positions[i, j] = start_pos + segment_pos * (end_pos - start_pos)
        
        return {
            "cw_beam_positions": cw_beam_positions,
            "ccw_beam_positions": ccw_beam_positions
        }


if __name__ == "__main__":
    # Simple test of the RLG model
    rlg = RingLaserGyroSimulation()
    results = rlg.simulate()
    
    # Plot the results
    plt.figure(figsize=(12, 10))
    
    # Plot phase difference
    plt.subplot(3, 2, 1)
    plt.plot(results["t"], results["phase_difference"])
    plt.xlabel("Time (s)")
    plt.ylabel("Phase Difference (rad)")
    plt.title("Phase Difference vs Time")
    plt.grid(True)
    
    # Plot rotation rates
    plt.subplot(3, 2, 2)
    plt.plot(results["t"], results["theoretical_rotation_rate"], 'b-', label='Theoretical')
    plt.plot(results["t"], results["measured_rotation_rate"], 'r-', label='Measured')
    plt.xlabel("Time (s)")
    plt.ylabel("Rotation Rate (rad/s)")
    plt.title("Rotation Rate")
    plt.grid(True)
    plt.legend()
    
    # Plot error
    plt.subplot(3, 2, 3)
    plt.plot(results["t"], results["error"])
    plt.xlabel("Time (s)")
    plt.ylabel("Error (rad/s)")
    plt.title("Measurement Error")
    plt.grid(True)
    
    # Plot interference pattern
    plt.subplot(3, 2, 4)
    plt.plot(results["t"], results["interference_intensity"])
    plt.xlabel("Time (s)")
    plt.ylabel("Intensity (a.u.)")
    plt.title("Interference Pattern")
    plt.grid(True)
    
    # Plot photodiode signals (quadrature detection)
    plt.subplot(3, 2, 5)
    plt.plot(results["t"], results["photodiode1"], 'b-', label='PD1 (cos)')
    plt.plot(results["t"], results["photodiode2"], 'r-', label='PD2 (sin)')
    plt.xlabel("Time (s)")
    plt.ylabel("Signal (a.u.)")
    plt.title("Photodiode Signals")
    plt.grid(True)
    plt.legend()
    
    # Plot Lissajous figure (PD1 vs PD2)
    plt.subplot(3, 2, 6)
    plt.plot(results["photodiode1"], results["photodiode2"])
    plt.xlabel("PD1 Signal")
    plt.ylabel("PD2 Signal")
    plt.title("Lissajous Figure")
    plt.grid(True)
    plt.axis('equal')
    
    plt.tight_layout()
    plt.show()
