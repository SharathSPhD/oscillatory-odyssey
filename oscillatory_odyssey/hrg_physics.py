"""
Physics module for Hemispherical Resonator Gyroscope simulation.

This module provides the core mathematical functions and physics calculations
for simulating a Hemispherical Resonator Gyroscope (HRG).
"""

import numpy as np


def calculate_mode_shapes(theta, x, y, amplitude=0.3):
    """
    Calculate mode shapes for visualization.
    
    Parameters:
    -----------
    theta : array_like
        Angular coordinates around the resonator
    x : array_like
        X displacement time series
    y : array_like
        Y displacement time series
    amplitude : float
        Scaling factor for mode shape visualization
        
    Returns:
    --------
    dict
        Dictionary containing mode shape data for visualization
    """
    # Number of points around the circle for visualization
    n_points = len(theta)
    
    # Base circular shape
    circle_x = np.cos(theta)
    circle_y = np.sin(theta)
    
    # Calculate n=2 mode shapes
    # First mode: cos(2θ) pattern
    mode1_pattern = np.cos(2*theta)
    
    # Second mode: sin(2θ) pattern
    mode2_pattern = np.sin(2*theta)
    
    # Number of time points
    n_times = len(x)
    
    # Initialize arrays to store mode shapes
    mode1_shapes = np.zeros((n_times, n_points, 2))
    mode2_shapes = np.zeros((n_times, n_points, 2))
    combined_shapes = np.zeros((n_times, n_points, 2))
    
    # Calculate mode shapes at each time point
    for i in range(n_times):
        # Mode 1 shape: circular shape + cos(2θ) pattern with x[i] amplitude
        r1 = 1 + amplitude * x[