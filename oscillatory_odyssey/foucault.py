"""
Foucault pendulum physics module for simulating Earth's rotation.

This module provides the physics model for a Foucault pendulum,
demonstrating the apparent precession of the oscillation plane due to Earth's rotation.
The model also includes support for spherical oscillators which precess at half the
rotation rate.
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import os
import yaml
import json


class FoucaultPendulum:
    """
    A class to simulate a Foucault pendulum demonstrating Earth's rotation.
    
    This models a pendulum whose oscillation plane appears to rotate relative to
    an observer on Earth, due to the conservation of angular momentum in an
    inertial frame while Earth rotates beneath it.
    """
    def __init__(self, config_path=None):
        """
        Initialize the Foucault pendulum with default parameters or from a config file.
        
        Parameters:
        -----------
        config_path : str, optional
            Path to a YAML or JSON configuration file
        """
        # Default parameters
        self.params = {
            "g": 9.81,                  # Gravitational acceleration (m/s^2)
            "L": 10.0,                  # Pendulum length (m)
            "m": 5.0,                   # Mass (kg)
            "damping": 0.05,            # Damping coefficient
            "theta0": 0.1,              # Initial angle amplitude (radians)
            "phi0": 0.0,                # Initial angle direction (radians)
            "omega0": 0.0,              # Initial angular velocity (radians/s)
            "latitude": 45.0,           # Latitude in degrees (0 = equator, 90 = pole)
            "rotation_rate": 7.292e-5,  # Earth's rotation rate (rad/s) - one rotation per sidereal day
            "rotation_demo_factor": 100, # Factor to amplify rotation effects for demo purposes
            "T": 100.0,                 # Total simulation time (s)
            "dt": 0.05,                 # Time step for output (s)
            "method": "RK45",           # Integration method
            "rtol": 1e-6,               # Relative tolerance for solver
            "atol": 1e-9,               # Absolute tolerance for solver
            "pendulum_type": "foucault", # Type: "foucault" or "spherical_oscillator"
            "quadrature": 0.0,          # Frequency mismatch parameter (for elliptical orbits)
            "isotropy_defect": 0.0,     # Relative difference between principal frequencies (%)
            "principal_axes_angle": 0.0, # Angle of the principal axes (degrees)
            "use_charron_ring": False,   # Whether to use a Charron ring to minimize elliptical motion
            "onnes_correction": False,  # Whether to apply Kamerlingh Onnes' correction to balance the pendulum
        }
        
        # Current state (will be updated during simulation)
        self.current_state = [
            self.params["theta0"] * np.cos(self.params["phi0"]),  # x-component of angle
            self.params["theta0"] * np.sin(self.params["phi0"]),  # y-component of angle
            0.0,  # x-component of angular velocity
            0.0   # y-component of angular velocity
        ]
        
        # Ensure all parameters are properly initialized
        if "principal_axes_angle" not in self.params:
            self.params["principal_axes_angle"] = 0.0
            
        if "onnes_correction" not in self.params:
            self.params["onnes_correction"] = False
        
        # Load configuration if provided
        if config_path:
            self.load_config(config_path)
            
        # Calculate natural frequency
        self.omega_n = np.sqrt(self.params["g"] / self.params["L"])
        
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
    
    def save_config(self, config_path='foucault_config.yaml'):
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
    
    def calculate_real_rotation_rate(self):
        """
        Calculate the real physical rotation rate based on latitude and pendulum type.
        This does NOT include the demo factor and represents the actual physics.
        
        Returns:
        --------
        float
            Real rotation rate in rad/s (no demo factor)
        """
        latitude_rad = np.radians(self.params["latitude"])
        base_rate = self.params["rotation_rate"]
        
        # At the equator (latitude=0), there's no rotation effect (sin(0) = 0)
        # At the poles (latitude=90), full rotation effect (sin(90) = 1)
        apparent_rate = base_rate * np.sin(latitude_rad)
        
        # For spherical oscillators, the precession is half the rotation rate
        # as described in the paper by Flückiger et al. (2020)
        if self.params["pendulum_type"] == "spherical_oscillator":
            return apparent_rate / 2
        else:
            return apparent_rate
    
    def calculate_effective_rotation_rate(self):
        """
        Calculate the effective rotation rate based on latitude and type,
        including the demo factor for visualization purposes.
        
        This is used for visualizing the precession at a faster rate, but should
        NOT be used for the actual physics calculations.
        
        Returns:
        --------
        float
            Effective rotation rate in rad/s, including demo factor for visualization
        """
        # Get the real rate first
        real_rate = self.calculate_real_rotation_rate()
        
        # Apply demo factor to speed up the effect for visualization purposes
        return real_rate * self.params["rotation_demo_factor"]
    
    def ode_system(self, t, y):
        """
        Define the ODE system for the Foucault pendulum.
        
        Parameters:
        -----------
        t : float
            Time (seconds)
        y : array_like
            State vector [x, y, vx, vy] representing angles and angular velocities
        
        Returns:
        --------
        array_like
            Derivatives [dx/dt, dy/dt, dvx/dt, dvy/dt]
        """
        x, y, vx, vy = y
        self.current_state = [x, y, vx, vy]
        
        # Calculate the amplitude of oscillation
        theta = np.sqrt(x**2 + y**2)
        
        # Get rotation rate and calculate Coriolis effect
        # Use the real physical rate WITHOUT demo factor for the actual physics simulation
        # The demo factor should only affect visualization, not the underlying physics
        omega_rotation = self.calculate_real_rotation_rate()
        
        # Natural frequency of the pendulum
        omega_n = self.omega_n
        
        # Frequency mismatch due to quadrature (for elliptical orbits)
        delta = 2 * np.pi * (self.params["quadrature"] / 2)
        
        # Parameters for isotropy defect (difference in principal frequencies)
        # This models Kamerlingh Onnes' key insight about mechanical asymmetry
        isotropy_defect = self.params["isotropy_defect"] / 100
        isotropy_x_factor = 1 + isotropy_defect
        isotropy_y_factor = 1 - isotropy_defect
        
        # Principal axes orientation - the angle of mechanical potential
        # This represents the direction where Kamerlingh Onnes identified asymmetry
        principal_angle = np.radians(self.params["principal_axes_angle"])
        
        # Calculate derivatives
        # For small amplitudes, approximating sin(theta) as theta
        if self.params["pendulum_type"] == "foucault":
            # Standard Foucault pendulum equations with Coriolis effect
            # Transform to principal axes coordinate system
            x_principal = x * np.cos(principal_angle) + y * np.sin(principal_angle)
            y_principal = -x * np.sin(principal_angle) + y * np.cos(principal_angle)
            vx_principal = vx * np.cos(principal_angle) + vy * np.sin(principal_angle)
            vy_principal = -vx * np.sin(principal_angle) + vy * np.cos(principal_angle)
            
            # Apply asymmetric forces in principal axes
            ax_principal = -omega_n**2 * x_principal * isotropy_x_factor - self.params["damping"] * vx_principal
            ay_principal = -omega_n**2 * y_principal * isotropy_y_factor - self.params["damping"] * vy_principal
            
            # Apply Coriolis force
            ax_principal += 2 * omega_rotation * vy_principal
            ay_principal -= 2 * omega_rotation * vx_principal
            
            # Transform back to original coordinates
            ax = ax_principal * np.cos(principal_angle) - ay_principal * np.sin(principal_angle)
            ay = ax_principal * np.sin(principal_angle) + ay_principal * np.cos(principal_angle)
            
            dx_dt = vx
            dy_dt = vy
            dvx_dt = ax
            dvy_dt = ay
        else:
            # Spherical oscillator model with half-rate precession
            # Transform to principal axes coordinate system
            x_principal = x * np.cos(principal_angle) + y * np.sin(principal_angle)
            y_principal = -x * np.sin(principal_angle) + y * np.cos(principal_angle)
            vx_principal = vx * np.cos(principal_angle) + vy * np.sin(principal_angle)
            vy_principal = -vx * np.sin(principal_angle) + vy * np.cos(principal_angle)
            
            # Apply asymmetric forces in principal axes
            ax_principal = -omega_n**2 * x_principal * isotropy_x_factor - self.params["damping"] * vx_principal
            ay_principal = -omega_n**2 * y_principal * isotropy_y_factor - self.params["damping"] * vy_principal
            
            # Apply half-rate Coriolis force (spherical oscillator)
            ax_principal += omega_rotation * vy_principal
            ay_principal -= omega_rotation * vx_principal
            
            # Transform back to original coordinates
            ax = ax_principal * np.cos(principal_angle) - ay_principal * np.sin(principal_angle)
            ay = ax_principal * np.sin(principal_angle) + ay_principal * np.cos(principal_angle)
            
            dx_dt = vx
            dy_dt = vy
            dvx_dt = ax
            dvy_dt = ay
        
        # If using a Charron ring, add a restoring force to keep motion planar
        if self.params["use_charron_ring"]:
            # The Charron ring works by providing a contact force that suppresses
            # elliptical motion when the pendulum passes through the ring
            if theta > 0:
                phi = np.arctan2(y, x)
                v_tangential = -vx * np.sin(phi) + vy * np.cos(phi)
                v_radial = vx * np.cos(phi) + vy * np.sin(phi)
                
                # Charron ring effect: reduce tangential velocity component
                # The effect is stronger when the pendulum is moving fast
                charron_strength = 0.2
                correction = charron_strength * v_tangential
                
                dvx_dt -= correction * np.sin(phi)
                dvy_dt += correction * np.cos(phi)
        
        # Apply Kamerlingh Onnes' correction if enabled
        if self.params["onnes_correction"]:
            # Kamerlingh Onnes' approach: dynamically correct the asymmetry
            # This effectively cancels out the isotropy defect
            if self.params["isotropy_defect"] != 0:
                # Apply a corrective torque proportional to the asymmetry
                # This is similar to adding balancing weights to the pendulum
                correction_strength = self.params["isotropy_defect"] / 100 * omega_n**2
                
                # The correction is in the principal axes reference frame
                x_principal = x * np.cos(principal_angle) + y * np.sin(principal_angle)
                y_principal = -x * np.sin(principal_angle) + y * np.cos(principal_angle)
                
                # Correct for the difference in frequencies
                correction_x = correction_strength * x_principal
                correction_y = -correction_strength * y_principal
                
                # Transform correction back to original coordinates
                dvx_dt += correction_x * np.cos(principal_angle) - correction_y * np.sin(principal_angle)
                dvy_dt += correction_x * np.sin(principal_angle) + correction_y * np.cos(principal_angle)
        
        return [dx_dt, dy_dt, dvx_dt, dvy_dt]
    
    def simulate(self):
        """
        Run the simulation of the Foucault pendulum.
        
        Returns:
        --------
        dict
            Simulation results including time, position, velocity, and energy arrays
        """
        # Set up time points
        t_span = (0, self.params["T"])
        t_eval = np.arange(0, self.params["T"], self.params["dt"])
        
        # Set up initial conditions
        phi0 = self.params["phi0"]
        theta0 = self.params["theta0"]
        x0 = theta0 * np.cos(phi0)
        y0 = theta0 * np.sin(phi0)
        vx0 = self.params["omega0"] * np.cos(phi0 + np.pi/2)
        vy0 = self.params["omega0"] * np.sin(phi0 + np.pi/2)
        y0 = [x0, y0, vx0, vy0]
        
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
        x = solution.y[0]  # x-angle component
        y = solution.y[1]  # y-angle component
        vx = solution.y[2]  # x-angular velocity component
        vy = solution.y[3]  # y-angular velocity component
        
        # Calculate derived quantities
        theta = np.sqrt(x**2 + y**2)  # Amplitude
        phi = np.arctan2(y, x)        # Direction
        omega = np.sqrt(vx**2 + vy**2)  # Angular velocity magnitude
        
        # Enforce phi continuity (avoid jumps from -pi to pi)
        phi_unwrapped = np.unwrap(phi)
        
        # Calculate Cartesian coordinates
        L = self.params["L"]
        bob_x = L * np.sin(theta) * np.cos(phi)
        bob_y = L * np.sin(theta) * np.sin(phi)
        bob_z = -L * np.cos(theta)
        
        # Calculate energies
        kinetic_energy = self.calculate_kinetic_energy(vx, vy)
        potential_energy = self.calculate_potential_energy(theta)
        total_energy = kinetic_energy + potential_energy
        
        # Analyze elliptical behavior
        # This is similar to Kamerlingh Onnes' approach for identifying mechanical asymmetry
        elliptical_analysis = self.analyze_elliptical_orbits(t, x, y, vx, vy, theta, phi)
        
        # Package results
        results = {
            "t": t,
            "x": x,
            "y": y,
            "vx": vx,
            "vy": vy,
            "theta": theta,
            "phi": phi,
            "phi_unwrapped": phi_unwrapped,
            "omega": omega,
            "bob_x": bob_x,
            "bob_y": bob_y,
            "bob_z": bob_z,
            "kinetic_energy": kinetic_energy,
            "potential_energy": potential_energy,
            "total_energy": total_energy,
            "natural_frequency": self.omega_n / (2 * np.pi),  # Convert to Hz
            
            # Real physical precession rate (without demo factor)
            "real_precession_rate": self.calculate_real_rotation_rate() * 180 / np.pi,  # deg/s
            
            # Accelerated precession rate for visualization (with demo factor)
            "expected_precession_rate": self.calculate_effective_rotation_rate() * 180 / np.pi,  # deg/s
            
            # Elliptical orbit analysis
            "ellipticity": elliptical_analysis["ellipticity"],  # Ratio of minor to major axis
            "major_axis_angle": elliptical_analysis["major_axis_angle"],  # In degrees
            "ellipse_parameters": elliptical_analysis["ellipse_parameters"],  # Time series of ellipse parameters
            "detected_asymmetry": elliptical_analysis["detected_asymmetry"],  # Measured asymmetry
            "measured_isotropy_defect": elliptical_analysis["measured_isotropy_defect"]  # Measured in %
        }
        
        # Calculate precession rate from simulation results
        # This is the rate at which the oscillation plane appears to rotate
        if len(t) > 10:
            # Linear regression on phi_unwrapped to find rate
            from scipy.stats import linregress
            slope, intercept, r_value, p_value, std_err = linregress(t, phi_unwrapped)
            
            # Store regression quality for debugging
            results["regression_r_value"] = r_value
            
            # Convert slope to degrees per second
            measured_precession_rate = slope * 180 / np.pi
            
            # Since demo factor is only for visualization and not used in the physics,
            # we need to directly compare with the real physical rate
            results["measured_precession_rate"] = measured_precession_rate
            
            # Store raw regression results for advanced diagnosis
            results["regression_slope_raw"] = slope 
            results["regression_intercept"] = intercept
            results["regression_std_err"] = std_err
            results["regression_p_value"] = p_value
            
            # Calculate theoretical precession rate for comparison
            # Use the real physical rate without demo factor
            theoretical_rate = self.calculate_real_rotation_rate() * 180 / np.pi
            results["theoretical_precession_rate"] = theoretical_rate
            
            # Calculate error percentage
            if theoretical_rate != 0:
                error_percent = 100 * (measured_precession_rate - theoretical_rate) / theoretical_rate
                results["precession_error_percent"] = error_percent
                
            # Add comprehensive debug information
            results["precession_debug"] = {
                "raw_measured_rate": measured_precession_rate,
                "demo_factor": self.params["rotation_demo_factor"],
                "theoretical_rate": theoretical_rate,
                "visualization_rate": theoretical_rate * self.params["rotation_demo_factor"],
                "simulation_time": t[-1] - t[0],
                "total_change_rad": phi_unwrapped[-1] - phi_unwrapped[0],
                "total_change_deg": (phi_unwrapped[-1] - phi_unwrapped[0]) * 180 / np.pi,
                "isotropy_defect": self.params.get("isotropy_defect", 0),
                "quadrature": self.params.get("quadrature", 0),
                "principal_axes_angle": self.params.get("principal_axes_angle", 0),
                "onnes_correction": self.params.get("onnes_correction", False),
                "pendulum_type": self.params.get("pendulum_type", "foucault")
            }
        
        return results
    
    def calculate_kinetic_energy(self, vx, vy):
        """
        Calculate the kinetic energy at each time point.
        
        Parameters:
        -----------
        vx, vy : array_like
            Angular velocity components
        
        Returns:
        --------
        array_like
            Kinetic energy at each time point
        """
        m = self.params["m"]
        L = self.params["L"]
        
        # KE = (1/2) * m * (L * omega)^2
        return 0.5 * m * (L**2) * (vx**2 + vy**2)
    
    def calculate_potential_energy(self, theta):
        """
        Calculate the potential energy at each time point.
        
        Parameters:
        -----------
        theta : array_like
            Angle amplitude array
        
        Returns:
        --------
        array_like
            Potential energy at each time point
        """
        m = self.params["m"]
        g = self.params["g"]
        L = self.params["L"]
        
        # PE = m * g * L * (1 - cos(theta))
        # (reference level is at the pivot)
        return m * g * L * (1 - np.cos(theta))
    
    def analyze_elliptical_orbits(self, t, x, y, vx, vy, theta, phi):
        """
        Analyze the elliptical nature of pendulum orbits.
        This implements Kamerlingh Onnes' approach to identify mechanical asymmetry.
        
        Parameters:
        -----------
        t, x, y, vx, vy, theta, phi : array_like
            Time series data from the simulation
            
        Returns:
        --------
        dict
            Dictionary with elliptical analysis results
        """
        # Initialize results
        result = {
            "ellipticity": 0.0,
            "major_axis_angle": 0.0,
            "ellipse_parameters": [],
            "detected_asymmetry": 0.0,
            "measured_isotropy_defect": 0.0
        }
        
        # We need reasonable amount of data for analysis
        if len(t) < 100:
            return result
        
        # Determine oscillation period from natural frequency
        period = 2 * np.pi / self.omega_n
        points_per_period = int(period / (t[1] - t[0]))
        
        # We'll analyze the orbit evolution by fitting ellipses to segments of the trajectory
        n_segments = min(20, len(t) // points_per_period)
        if n_segments < 2:
            return result
        
        segment_size = len(t) // n_segments
        ellipse_params = []
        
        for i in range(n_segments):
            # Get segment data
            start_idx = i * segment_size
            end_idx = min((i + 1) * segment_size, len(t))
            
            # Skip segments with very small amplitude
            if np.max(theta[start_idx:end_idx]) < 0.01:
                continue
                
            # Try to fit an ellipse to this segment of the trajectory
            segment_x = x[start_idx:end_idx]
            segment_y = y[start_idx:end_idx]
            
            # Simple method: use PCA to find the principal axes of the ellipse
            try:
                # Center the data
                centered_x = segment_x - np.mean(segment_x)
                centered_y = segment_y - np.mean(segment_y)
                points = np.column_stack([centered_x, centered_y])
                
                # Skip if too few points or nearly zero amplitude
                if len(points) < 10 or np.max(np.abs(points)) < 1e-6:
                    continue
                    
                # Calculate covariance matrix and its eigenvectors/eigenvalues
                cov_matrix = np.cov(points, rowvar=False)
                eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
                
                # The eigenvalues are the squared lengths of the ellipse axes
                # Make sure they're sorted in descending order
                sort_indices = np.argsort(eigenvalues)[::-1]
                eigenvalues = eigenvalues[sort_indices]
                eigenvectors = eigenvectors[:, sort_indices]
                
                # Calculate ellipse parameters
                major_axis = 2 * np.sqrt(eigenvalues[0])  # 2 * standard deviation along major axis
                minor_axis = 2 * np.sqrt(eigenvalues[1])  # 2 * standard deviation along minor axis
                
                # Ellipticity (ratio of minor to major axis, 0=line, 1=circle)
                ellipticity = minor_axis / major_axis if major_axis > 0 else 0
                
                # Angle of the major axis (in degrees)
                major_axis_angle = np.degrees(np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0]))
                
                # Store the parameters
                ellipse_params.append({
                    "t": t[start_idx],
                    "major_axis": major_axis,
                    "minor_axis": minor_axis,
                    "ellipticity": ellipticity,
                    "angle": major_axis_angle
                })
            except Exception:
                # Skip this segment if fitting fails
                continue
        
        # If we couldn't analyze any segments, return defaults
        if not ellipse_params:
            return result
            
        # Get the final ellipticity and major axis angle
        final_ellipticity = ellipse_params[-1]["ellipticity"]
        final_angle = ellipse_params[-1]["angle"]
        
        # Estimate asymmetry from elliptical evolution
        # In Kamerlingh Onnes' approach, the asymmetry is related to
        # how quickly linear oscillations evolve into elliptical ones
        if len(ellipse_params) > 1:
            # Rate of change of ellipticity
            ellipticity_values = [params["ellipticity"] for params in ellipse_params]
            time_values = [params["t"] for params in ellipse_params]
            
            # Simple linear regression to find rate of change
            if time_values[-1] > time_values[0]:
                rate_of_ellipticity_change = (ellipticity_values[-1] - ellipticity_values[0]) / (time_values[-1] - time_values[0])
            else:
                rate_of_ellipticity_change = 0
                
            # Detected asymmetry is proportional to this rate
            detected_asymmetry = abs(rate_of_ellipticity_change) * 10  # Scale factor based on testing
            
            # Convert to percent isotropy defect (similar scale as the input parameter)
            measured_isotropy_defect = detected_asymmetry * 100
        else:
            detected_asymmetry = 0
            measured_isotropy_defect = 0
        
        # Return the results
        return {
            "ellipticity": final_ellipticity,
            "major_axis_angle": final_angle,
            "ellipse_parameters": ellipse_params,
            "detected_asymmetry": detected_asymmetry,
            "measured_isotropy_defect": measured_isotropy_defect
        }


if __name__ == "__main__":
    # Simple test of the Foucault pendulum model
    pendulum = FoucaultPendulum()
    results = pendulum.simulate()
    
    # Plot the results
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.plot(results["t"], results["theta"])
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude (rad)")
    plt.title("Pendulum Amplitude")
    
    plt.subplot(2, 2, 2)
    plt.plot(results["t"], results["phi_unwrapped"] * 180/np.pi)
    plt.xlabel("Time (s)")
    plt.ylabel("Direction (deg)")
    plt.title("Oscillation Direction")
    
    plt.subplot(2, 2, 3)
    plt.plot(results["x"], results["y"])
    plt.xlabel("x-angle")
    plt.ylabel("y-angle")
    plt.title("Phase Space Projection")
    plt.axis('equal')
    
    plt.subplot(2, 2, 4)
    plt.plot(results["t"], results["kinetic_energy"], label="Kinetic")
    plt.plot(results["t"], results["potential_energy"], label="Potential")
    plt.plot(results["t"], results["total_energy"], label="Total")
    plt.xlabel("Time (s)")
    plt.ylabel("Energy (J)")
    plt.title("Energy")
    plt.legend()
    
    plt.tight_layout()
    plt.show()
