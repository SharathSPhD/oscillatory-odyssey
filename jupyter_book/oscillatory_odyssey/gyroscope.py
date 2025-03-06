"""
Gyroscope physics module for simulating gyroscopic effects.

This module provides the physics model for a gyroscope (specifically a bicycle wheel),
demonstrating precession, nutation, and angular momentum conservation.
The model is designed to show how a spinning object resists changes to its orientation,
resulting in gyroscopic stability and precession.
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import os
import yaml
import json


class GyroscopeSimulation:
    """
    A class to simulate a gyroscope (bicycle wheel) demonstrating gyroscopic effects.
    
    This models a bicycle wheel mounted on a rod, with one end of the rod fixed at a pivot point.
    The wheel spins around its axis, while the whole assembly can rotate about the pivot.
    The simulation demonstrates concepts like conservation of angular momentum, precession,
    and gyroscopic stability.
    """
    def __init__(self, config_path=None):
        """
        Initialize the gyroscope simulation with default parameters or from a config file.
        
        Parameters:
        -----------
        config_path : str, optional
            Path to a YAML or JSON configuration file
        """
        # Default parameters
        self.params = {
            "g": 9.81,                  # Gravitational acceleration (m/s^2)
            "wheel_radius": 0.3,        # Bicycle wheel radius (m)
            "wheel_mass": 1.0,          # Wheel mass (kg)
            "wheel_thickness": 0.05,    # Wheel thickness (m)
            "rod_length": 0.5,          # Length of the rod from pivot to wheel center (m)
            "rod_mass": 0.2,            # Mass of the rod (kg)
            "initial_spin_rate": 20.0,  # Initial spinning rate of wheel (rad/s)
            "damping": 0.05,            # Damping coefficient
            "theta0": 0.3,              # Initial theta angle (rad) - tilt from vertical
            "phi0": 0.0,                # Initial phi angle (rad) - azimuthal angle
            "psi0": 0.0,                # Initial psi angle (rad) - wheel spin angle
            "moment_of_inertia_type": "rim",  # "rim" or "solid" for different wheel types
            "T": 10.0,                  # Total simulation time (s)
            "dt": 0.01,                 # Time step for output (s)
            "method": "RK45",           # Integration method
            "rtol": 1e-6,               # Relative tolerance for solver
            "atol": 1e-9,               # Absolute tolerance for solver
            "demo_speed_factor": 1.0,   # Factor to adjust visualization speed
        }
        
        # Current state (will be updated during simulation)
        self.current_state = [
            self.params["theta0"],    # theta - tilt angle from vertical
            self.params["phi0"],      # phi - azimuthal angle
            self.params["psi0"],      # psi - wheel spin angle
            0.0,                      # theta_dot - rate of change of tilt
            0.0,                      # phi_dot - rate of change of azimuthal angle
            self.params["initial_spin_rate"]  # psi_dot - wheel spin rate
        ]
        
        # Load configuration if provided
        if config_path:
            self.load_config(config_path)
        
        # Calculate moment of inertia
        self.update_inertia()
            
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
    
    def save_config(self, config_path='gyroscope_config.yaml'):
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
    
    def update_inertia(self):
        """
        Calculate and update the moments of inertia for the bicycle wheel.
        
        This calculates different moments of inertia:
        - Ix, Iy: Moment of inertia for rotation around the x/y axis (perpendicular to wheel)
        - Iz: Moment of inertia for rotation around the wheel's axis (spin axis)
        """
        # Extract parameters
        radius = self.params["wheel_radius"]
        mass = self.params["wheel_mass"]
        thickness = self.params["wheel_thickness"]
        inertia_type = self.params["moment_of_inertia_type"]
        
        # Calculate moments of inertia based on distribution type
        if inertia_type == "rim":
            # For a ring/rim, most mass is at the perimeter
            # Iz = moment of inertia about the wheel's axis (spin axis)
            self.Iz = mass * radius**2
            
            # Ix = Iy = moment of inertia about a diameter
            # For a thin hoop: I = (1/2) * M * R^2
            self.Ix = self.Iy = 0.5 * mass * radius**2
        else:
            # For a solid disk
            # Iz = moment of inertia about the wheel's axis (spin axis)
            self.Iz = 0.5 * mass * radius**2
            
            # Ix = Iy = moment of inertia about a diameter
            # For a solid disk: I = (1/4) * M * R^2 + (1/12) * M * h^2
            self.Ix = self.Iy = 0.25 * mass * radius**2 + (1/12) * mass * thickness**2
            
        # Rod's contribution to moment of inertia
        rod_length = self.params["rod_length"]
        rod_mass = self.params["rod_mass"]
        
        # Add rod's contribution to Ix and Iy (assuming thin rod)
        # Thin rod about perpendicular axis through one end: I = (1/3) * M * L^2
        self.Ix += (1/3) * rod_mass * rod_length**2
        self.Iy += (1/3) * rod_mass * rod_length**2
        
        # Store for convenience
        self.inertia = {
            "Ix": self.Ix,
            "Iy": self.Iy,
            "Iz": self.Iz
        }
    
    def ode_system(self, t, y):
        """
        Define the ODE system for the gyroscope.
        
        Parameters:
        -----------
        t : float
            Time (seconds)
        y : array_like
            State vector [theta, phi, psi, theta_dot, phi_dot, psi_dot]
            representing angles and angular velocities
        
        Returns:
        --------
        array_like
            Derivatives [dtheta/dt, dphi/dt, dpsi/dt, dtheta_dot/dt, dphi_dot/dt, dpsi_dot/dt]
        """
        theta, phi, psi, theta_dot, phi_dot, psi_dot = y
        self.current_state = y
        
        # Extract parameters
        g = self.params["g"]
        L = self.params["rod_length"]  # rod length
        m = self.params["wheel_mass"] + self.params["rod_mass"]  # total mass
        d = self.params["damping"]
        
        # The center of mass distance from pivot
        # This is approximately the rod length (simplified model)
        r_cm = L
        
        # Calculate torque due to gravity
        # The torque is m*g*r_cm*sin(theta) and acts to increase theta
        torque_gravity = m * g * r_cm * np.sin(theta)
        
        # Calculate the derivatives of the angles
        theta_dot_dot = 0
        phi_dot_dot = 0
        psi_dot_dot = 0
        
        # For a spinning top, the equations of motion are complex due to coupling.
        # These are the Euler's equations of motion for a symmetric top.
        
        # Factor to handle the case when theta is close to 0 or pi
        # This prevents division by zero and numerical instabilities
        sin_theta_factor = np.sin(theta)
        if abs(sin_theta_factor) < 1e-6:
            sin_theta_factor = np.sign(sin_theta_factor) * 1e-6
            
        # Angular momentum components
        L_x = self.Ix * (-phi_dot * np.sin(theta) * np.sin(psi) + theta_dot * np.cos(psi))
        L_y = self.Iy * (phi_dot * np.sin(theta) * np.cos(psi) + theta_dot * np.sin(psi))
        L_z = self.Iz * (psi_dot + phi_dot * np.cos(theta))
        
        # Torque components (gravity acts along the negative x-axis when phi=0)
        tau_x = -torque_gravity * np.cos(phi)
        tau_y = -torque_gravity * np.sin(phi)
        tau_z = 0  # No torque along the wheel's spin axis
        
        # Calculate angular accelerations from torque and angular momentum
        # This is a simplified approximation of the rigid body dynamics
        
        # theta_dot_dot = d²θ/dt²
        theta_dot_dot = (tau_x * np.cos(psi) + tau_y * np.sin(psi) - 
                         L_z * phi_dot * np.sin(theta)) / self.Ix - d * theta_dot
        
        # phi_dot_dot = d²φ/dt²
        # For phi, the equation includes the gyroscopic effect from the spinning wheel
        phi_dot_dot = ((tau_y * np.cos(psi) - tau_x * np.sin(psi)) / 
                       (self.Iy * np.sin(theta)) + 
                       L_z * theta_dot / (self.Iy * np.sin(theta))) - d * phi_dot
        
        # psi_dot_dot = d²ψ/dt²
        # Damping affects the wheel's spin rate
        psi_dot_dot = -d * psi_dot
        
        # For very small theta, phi_dot can become unstable
        # Add stability constraints
        if abs(theta) < 1e-3:
            phi_dot_dot = 0
            
        # Return the derivatives
        return [
            theta_dot,
            phi_dot,
            psi_dot,
            theta_dot_dot,
            phi_dot_dot,
            psi_dot_dot
        ]
    
    def simulate(self):
        """
        Run the gyroscope simulation.
        
        Returns:
        --------
        dict
            Simulation results including time, angles, angular velocities, and derived quantities
        """
        # Update inertia in case parameters have changed
        self.update_inertia()
        
        # Set up time points
        t_span = (0, self.params["T"])
        t_eval = np.arange(0, self.params["T"], self.params["dt"])
        
        # Set up initial conditions
        y0 = [
            self.params["theta0"],  # Initial theta
            self.params["phi0"],    # Initial phi
            self.params["psi0"],    # Initial psi
            0.0,                    # Initial theta_dot
            0.0,                    # Initial phi_dot
            self.params["initial_spin_rate"]  # Initial wheel spin rate
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
        theta = solution.y[0]  # Tilt angle
        phi = solution.y[1]    # Azimuthal angle
        psi = solution.y[2]    # Wheel spin angle
        theta_dot = solution.y[3]  # Rate of change of tilt
        phi_dot = solution.y[4]    # Rate of change of azimuthal angle
        psi_dot = solution.y[5]    # Wheel spin rate
        
        # Unwrap phi and psi angles to avoid discontinuities
        phi_unwrapped = np.unwrap(phi)
        psi_unwrapped = np.unwrap(psi)
        
        # Calculate 3D positions for visualization
        positions = self.calculate_positions(theta, phi, psi)
        
        # Calculate energies
        energies = self.calculate_energies(theta, phi, psi, theta_dot, phi_dot, psi_dot)
        
        # Calculate angular momentum components
        angular_momentum = self.calculate_angular_momentum(theta, phi, psi, theta_dot, phi_dot, psi_dot)
        
        # Calculate precession rate
        precession_rate = self.calculate_theoretical_precession_rate()
        
        # Measure actual precession rate from simulation
        measured_precession = self.measure_precession_rate(t, phi_unwrapped)
        
        # Package results
        results = {
            "t": t,
            "theta": theta,
            "phi": phi,
            "psi": psi,
            "phi_unwrapped": phi_unwrapped,
            "psi_unwrapped": psi_unwrapped,
            "theta_dot": theta_dot,
            "phi_dot": phi_dot,
            "psi_dot": psi_dot,
            
            # 3D positions
            "pivot": positions["pivot"],
            "wheel_center": positions["wheel_center"],
            "rim_points": positions["rim_points"],
            "spin_axis": positions["spin_axis"],
            "rod_vector": positions["rod_vector"],
            
            # Energy components
            "kinetic_energy": energies["kinetic"],
            "potential_energy": energies["potential"],
            "total_energy": energies["total"],
            
            # Angular momentum
            "L_x": angular_momentum["L_x"],
            "L_y": angular_momentum["L_y"],
            "L_z": angular_momentum["L_z"],
            "L_magnitude": angular_momentum["L_magnitude"],
            
            # Precession information
            "theoretical_precession_rate": precession_rate,
            "measured_precession_rate": measured_precession["rate"],
            "precession_error_percent": measured_precession["error_percent"],
            
            # Store simulation parameters
            "wheel_radius": self.params["wheel_radius"],
            "rod_length": self.params["rod_length"],
            "initial_spin_rate": self.params["initial_spin_rate"],
            "Ix": self.Ix,
            "Iy": self.Iy,
            "Iz": self.Iz
        }
        
        return results
    
    def calculate_positions(self, theta, phi, psi):
        """
        Calculate 3D positions of gyroscope components for visualization.
        
        Parameters:
        -----------
        theta, phi, psi : array_like
            Arrays of angles from the simulation
            
        Returns:
        --------
        dict
            Dictionary with position arrays for different components
        """
        # Extract parameters
        wheel_radius = self.params["wheel_radius"]
        rod_length = self.params["rod_length"]
        
        # Number of points for visualization
        n_frames = len(theta)
        n_rim_points = 36  # Number of points to use for wheel rim visualization
        
        # Initialize position arrays
        pivot = np.zeros((n_frames, 3))  # Fixed pivot at origin
        wheel_center = np.zeros((n_frames, 3))  # Center of the wheel
        rod_vector = np.zeros((n_frames, 3))    # Vector from pivot to wheel center
        spin_axis = np.zeros((n_frames, 3))     # Unit vector along wheel's axis
        rim_points = np.zeros((n_frames, n_rim_points, 3))  # Points around the wheel rim
        
        # Calculate positions for each time frame
        for i in range(n_frames):
            # Rod vector = direction from pivot to wheel center
            # This is along direction (sin(theta)*cos(phi), sin(theta)*sin(phi), cos(theta))
            rod_vector[i] = np.array([
                np.sin(theta[i]) * np.cos(phi[i]),
                np.sin(theta[i]) * np.sin(phi[i]),
                np.cos(theta[i])
            ]) * rod_length
            
            # Wheel center is at the end of the rod
            wheel_center[i] = rod_vector[i]
            
            # The spin axis should be the wheel's natural axis of rotation,
            # which is perpendicular to the wheel's plane
            
            # For a bicycle wheel, the spin axis is perpendicular to the wheel's plane
            # We can define this axis directly in the world frame based on our Euler angles
            
            # Compute the rotation matrices as we did for angular momentum
            # Rotation about z-axis by phi
            R_z = np.array([
                [np.cos(phi[i]), -np.sin(phi[i]), 0],
                [np.sin(phi[i]), np.cos(phi[i]), 0],
                [0, 0, 1]
            ])
            
            # Rotation about x-axis by theta
            R_x = np.array([
                [1, 0, 0],
                [0, np.cos(theta[i]), -np.sin(theta[i])],
                [0, np.sin(theta[i]), np.cos(theta[i])]
            ])
            
            # Rotation about z-axis (wheel axis) by psi
            R_z2 = np.array([
                [np.cos(psi[i]), -np.sin(psi[i]), 0],
                [np.sin(psi[i]), np.cos(psi[i]), 0],
                [0, 0, 1]
            ])
            
            # Combined rotation matrix (world to body)
            R_world_to_body = R_z2 @ R_x @ R_z
            
            # In the body frame, the spin axis is simply along the z-axis [0,0,1]
            # Transform this from body to world using the rotation matrices
            spin_axis_body = np.array([0, 0, 1])  # Z-axis in body frame = wheel's rotation axis
            
            # Transform to world frame (transpose = inverse for rotation matrices)
            spin_axis[i] = (R_world_to_body.T @ spin_axis_body)
            
            # Normalize to ensure unit length
            spin_axis[i] = spin_axis[i] / np.linalg.norm(spin_axis[i])
            
            # Now calculate points around the rim
            for j in range(n_rim_points):
                angle = 2 * np.pi * j / n_rim_points
                
                # Calculate a point on the rim in the plane perpendicular to the spin axis
                # We need a vector perpendicular to the spin axis to define the rim plane
                # If the spin axis is not aligned with the z-axis, use z as reference
                if abs(spin_axis[i][2]) < 0.99:
                    ref = np.array([0, 0, 1])
                else:
                    ref = np.array([1, 0, 0])
                
                # First perpendicular vector
                perp1 = np.cross(spin_axis[i], ref)
                perp1 = perp1 / np.linalg.norm(perp1)
                
                # Second perpendicular vector to form a basis in the rim plane
                perp2 = np.cross(spin_axis[i], perp1)
                
                # Point on the rim
                rim_point = wheel_center[i] + wheel_radius * (
                    perp1 * np.cos(angle) + perp2 * np.sin(angle)
                )
                rim_points[i, j] = rim_point
        
        return {
            "pivot": pivot,
            "wheel_center": wheel_center,
            "rim_points": rim_points,
            "spin_axis": spin_axis,
            "rod_vector": rod_vector
        }
    
    def calculate_energies(self, theta, phi, psi, theta_dot, phi_dot, psi_dot):
        """
        Calculate energy components for the gyroscope system.
        
        Parameters:
        -----------
        theta, phi, psi, theta_dot, phi_dot, psi_dot : array_like
            Arrays of angles and angular velocities from the simulation
            
        Returns:
        --------
        dict
            Dictionary with energy component arrays
        """
        # Extract parameters
        m = self.params["wheel_mass"] + self.params["rod_mass"]  # total mass
        g = self.params["g"]
        L = self.params["rod_length"]
        
        # Initialize energy arrays
        n_frames = len(theta)
        kinetic = np.zeros(n_frames)
        potential = np.zeros(n_frames)
        total = np.zeros(n_frames)
        
        # Calculate energy for each time step
        for i in range(n_frames):
            # Potential energy (relative to pivot)
            # U = mgh = mgL(1-cos(theta))
            potential[i] = m * g * L * (1 - np.cos(theta[i]))
            
            # Kinetic energy calculation is complex for a gyroscope
            # We need to calculate contributions from different types of motion
            
            # Rotational kinetic energy
            # For rotation about the center of mass
            # T_rot = 0.5 * Ix * omega_x^2 + 0.5 * Iy * omega_y^2 + 0.5 * Iz * omega_z^2
            
            # Angular velocities in the body frame
            # This is a simplified approximation - a complete treatment 
            # would require the full tensor of inertia and transformation
            omega_x = -phi_dot[i] * np.sin(theta[i]) * np.sin(psi[i]) + theta_dot[i] * np.cos(psi[i])
            omega_y = phi_dot[i] * np.sin(theta[i]) * np.cos(psi[i]) + theta_dot[i] * np.sin(psi[i])
            omega_z = psi_dot[i] + phi_dot[i] * np.cos(theta[i])
            
            # Rotational kinetic energy
            T_rot = 0.5 * self.Ix * omega_x**2 + 0.5 * self.Iy * omega_y**2 + 0.5 * self.Iz * omega_z**2
            
            # Translational kinetic energy from the center of mass moving
            # v_cm = omega × r_cm
            # For simplified model: T_trans = 0.5 * m * (L * sin(theta) * phi_dot)^2
            T_trans = 0.5 * m * (L * np.sin(theta[i]) * phi_dot[i])**2
            
            kinetic[i] = T_rot + T_trans
            total[i] = kinetic[i] + potential[i]
        
        return {
            "kinetic": kinetic,
            "potential": potential,
            "total": total
        }
    
    def calculate_angular_momentum(self, theta, phi, psi, theta_dot, phi_dot, psi_dot):
        """
        Calculate angular momentum components of the gyroscope.
        
        Parameters:
        -----------
        theta, phi, psi, theta_dot, phi_dot, psi_dot : array_like
            Arrays of angles and angular velocities from the simulation
            
        Returns:
        --------
        dict
            Dictionary with angular momentum component arrays
        """
        # Initialize arrays
        n_frames = len(theta)
        L_x = np.zeros(n_frames)
        L_y = np.zeros(n_frames)
        L_z = np.zeros(n_frames)
        L_magnitude = np.zeros(n_frames)
        
        # Calculate angular momentum for each time step
        for i in range(n_frames):
            # Angular velocities in the body frame
            omega_x = -phi_dot[i] * np.sin(theta[i]) * np.sin(psi[i]) + theta_dot[i] * np.cos(psi[i])
            omega_y = phi_dot[i] * np.sin(theta[i]) * np.cos(psi[i]) + theta_dot[i] * np.sin(psi[i])
            omega_z = psi_dot[i] + phi_dot[i] * np.cos(theta[i])
            
            # Angular momentum components in the body frame
            L_body_x = self.Ix * omega_x
            L_body_y = self.Iy * omega_y
            L_body_z = self.Iz * omega_z
            L_body = np.array([L_body_x, L_body_y, L_body_z])
            
            # Transform from body frame to world frame using Euler angles
            # First, compute the rotation matrix
            # Rotation about z-axis by phi
            R_z = np.array([
                [np.cos(phi[i]), -np.sin(phi[i]), 0],
                [np.sin(phi[i]), np.cos(phi[i]), 0],
                [0, 0, 1]
            ])
            
            # Rotation about x-axis by theta
            R_x = np.array([
                [1, 0, 0],
                [0, np.cos(theta[i]), -np.sin(theta[i])],
                [0, np.sin(theta[i]), np.cos(theta[i])]
            ])
            
            # Rotation about z-axis (wheel axis) by psi
            R_z2 = np.array([
                [np.cos(psi[i]), -np.sin(psi[i]), 0],
                [np.sin(psi[i]), np.cos(psi[i]), 0],
                [0, 0, 1]
            ])
            
            # Combined rotation matrix (world to body)
            # For body to world, use the transpose (inverse for rotation matrices)
            R_world_to_body = R_z2 @ R_x @ R_z
            R_body_to_world = R_world_to_body.T
            
            # Transform angular momentum from body to world frame
            L_world = R_body_to_world @ L_body
            
            # Store world frame components
            L_x[i], L_y[i], L_z[i] = L_world
            
            # Magnitude of angular momentum (ensure positive value)
            L_magnitude[i] = np.sqrt(np.maximum(L_x[i]**2 + L_y[i]**2 + L_z[i]**2, 1e-10))
        
        return {
            "L_x": L_x,
            "L_y": L_y,
            "L_z": L_z,
            "L_magnitude": L_magnitude
        }
    
    def calculate_theoretical_precession_rate(self):
        """
        Calculate the theoretical precession rate for a gyroscope.
        
        Returns:
        --------
        float
            Theoretical precession rate in rad/s
        """
        # Extract parameters
        m = self.params["wheel_mass"] + self.params["rod_mass"]  # total mass
        g = self.params["g"]
        L = self.params["rod_length"]
        omega_spin = self.params["initial_spin_rate"]
        I_spin = self.Iz  # Moment of inertia about spin axis
        
        # For a perfect gyroscope, the precession rate is:
        # Omega = m*g*L / (I_spin * omega_spin)
        # This assumes a small tilt angle and fast spinning
        
        if abs(omega_spin) < 1e-6:
            # Avoid division by zero
            return 0
        
        precession_rate = m * g * L / (I_spin * omega_spin)
        return precession_rate
    
    def measure_precession_rate(self, t, phi_unwrapped):
        """
        Measure the precession rate from the simulation data.
        
        Parameters:
        -----------
        t : array_like
            Time array
        phi_unwrapped : array_like
            Unwrapped phi angle array
            
        Returns:
        --------
        dict
            Dictionary with measured precession rate and error
        """
        # Need substantial data for linear regression
        if len(t) < 10:
            return {"rate": 0, "error_percent": 0}
            
        # Linear regression on phi_unwrapped to find rate
        from scipy.stats import linregress
        
        # Skip the first few points to avoid initial transients
        start_idx = min(int(len(t) * 0.1), 20)  # Skip first 10% or 20 points, whichever is smaller
        
        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = linregress(
            t[start_idx:], phi_unwrapped[start_idx:]
        )
        
        # Calculate error percentage
        theoretical_rate = self.calculate_theoretical_precession_rate()
        if abs(theoretical_rate) < 1e-6:
            error_percent = 0
        else:
            error_percent = 100 * (slope - theoretical_rate) / theoretical_rate
        
        return {
            "rate": slope,
            "error_percent": error_percent,
            "r_value": r_value,
            "intercept": intercept,
            "std_err": std_err,
            "p_value": p_value
        }


if __name__ == "__main__":
    # Simple test of the gyroscope model
    gyro = GyroscopeSimulation()
    results = gyro.simulate()
    
    # Plot the results
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.plot(results["t"], np.degrees(results["theta"]))
    plt.xlabel("Time (s)")
    plt.ylabel("Tilt Angle (degrees)")
    plt.title("Theta vs Time")
    
    plt.subplot(2, 2, 2)
    plt.plot(results["t"], np.degrees(results["phi_unwrapped"]))
    plt.xlabel("Time (s)")
    plt.ylabel("Azimuthal Angle (degrees)")
    plt.title("Phi vs Time (Precession)")
    
    plt.subplot(2, 2, 3)
    plt.plot(
        np.degrees(results["theta"]), 
        np.degrees(results["theta_dot"]), 
        'b-', label="Theta vs dTheta/dt"
    )
    plt.xlabel("Theta (degrees)")
    plt.ylabel("dTheta/dt (degrees/s)")
    plt.title("Phase Space")
    plt.grid(True)
    
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
