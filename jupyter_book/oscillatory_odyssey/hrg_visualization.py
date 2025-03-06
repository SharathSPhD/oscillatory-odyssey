"""Visualization components for Hemispherical Resonator Gyroscope simulation."""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_animation_figure(results):
    """Create Plotly figure for HRG mode shape animation.
    
    Args:
        results: Simulation results dictionary
        
    Returns:
        go.FigureWidget: Plotly figure with 2D and 3D visualizations
    """
    # Create a figure with two subplots side by side
    fig = go.FigureWidget(make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'scatter'}, {'type': 'scatter3d'}]],
        subplot_titles=('Mode Shape - 2D View', 'Mode Shape - 3D View')
    ))
    
    # Get the first frame's mode shapes
    theta = results['mode_shapes']['theta']
    initial_shape = results['mode_shapes']['combined_shapes'][0]
    
    # Add 2D mode shape view (left subplot)
    fig.add_trace(
        go.Scatter(
            x=initial_shape[:, 0],
            y=initial_shape[:, 1],
            mode='lines',
            line=dict(color='blue', width=3),
            name='Combined Mode',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Add reference circle
    circle_x = results['mode_shapes']['circle_x']
    circle_y = results['mode_shapes']['circle_y']
    fig.add_trace(
        go.Scatter(
            x=circle_x,
            y=circle_y,
            mode='lines',
            line=dict(color='gray', width=1, dash='dash'),
            name='Reference Circle',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Add node points (4 points at 0, 90, 180, 270 degrees)
    node_indices = [0, len(theta)//4, len(theta)//2, 3*len(theta)//4]
    node_x = [initial_shape[i, 0] for i in node_indices]
    node_y = [initial_shape[i, 1] for i in node_indices]
    
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers',
            marker=dict(size=8, color='red'),
            name='Nodes',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Add antinodes (4 points at 45, 135, 225, 315 degrees)
    antinode_indices = [len(theta)//8, 3*len(theta)//8, 5*len(theta)//8, 7*len(theta)//8]
    antinode_x = [initial_shape[i, 0] for i in antinode_indices]
    antinode_y = [initial_shape[i, 1] for i in antinode_indices]
    
    fig.add_trace(
        go.Scatter(
            x=antinode_x,
            y=antinode_y,
            mode='markers',
            marker=dict(size=8, color='green'),
            name='Antinodes',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Add reference axis (for visualizing pattern rotation)
    fig.add_trace(
        go.Scatter(
            x=[0, 1.5],
            y=[0, 0],
            mode='lines',
            line=dict(color='black', width=1, dash='dot'),
            name='Reference Axis',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Update 2D layout
    fig.update_xaxes(title='X', range=[-1.5, 1.5], row=1, col=1)
    fig.update_yaxes(title='Y', range=[-1.5, 1.5], row=1, col=1)
    
    # Update overall grid layout
    fig.update_layout(grid=dict(rows=1, columns=2, pattern='independent'))
    
    # Add 3D view with surface plot (right subplot)
    # First, convert the 2D shape to 3D by adding a z-coordinate
    # Create a meshgrid for 3D surface
    r = np.linspace(0, 1, 10)  # Radial distance from center
    theta_3d = results['mode_shapes']['theta']  # Angular coordinates
    
    r_grid, theta_grid = np.meshgrid(r, theta_3d)
    
    # Calculate base shape (circular disk)
    x_grid = r_grid * np.cos(theta_grid)
    y_grid = r_grid * np.sin(theta_grid)
    
    # Add displacement in z direction based on initial mode shape
    # We'll use the combined mode shape to modulate the z height
    z_factor = 0.5  # Scale factor for z displacement
    
    # Get normalized displacement (distance from unit circle)
    initial_r = np.sqrt(initial_shape[:, 0]**2 + initial_shape[:, 1]**2)
    displacement = initial_r - 1.0
    
    # Create z displacement field
    z_grid = np.zeros_like(r_grid)
    for i, disp in enumerate(displacement):
        z_grid[i, :] = disp * z_factor * r_grid[i, :]
    
    # Add 3D surface plot
    fig.add_trace(
        go.Surface(
            x=x_grid,
            y=y_grid,
            z=z_grid,
            colorscale='Viridis',
            showscale=False,
            opacity=0.8
        ),
        row=1, col=2
    )
    
    # Add reference circle on the 3D plot (at z=0)
    x_circle_3d = np.cos(theta_3d)
    y_circle_3d = np.sin(theta_3d)
    z_circle_3d = np.zeros_like(theta_3d)
    
    fig.add_trace(
        go.Scatter3d(
            x=x_circle_3d,
            y=y_circle_3d,
            z=z_circle_3d,
            mode='lines',
            line=dict(color='black', width=2),
            name='Reference Circle',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Add node points in 3D
    node_z = [z_grid[i, -1] for i in node_indices]  # Use the outermost ring
    
    fig.add_trace(
        go.Scatter3d(
            x=[node_x[i] for i in range(len(node_indices))],
            y=[node_y[i] for i in range(len(node_indices))],
            z=node_z,
            mode='markers',
            marker=dict(size=5, color='red'),
            name='Nodes',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Add rotation axis
    fig.add_trace(
        go.Scatter3d(
            x=[0, 0],
            y=[0, 0],
            z=[-1, 1],
            mode='lines',
            line=dict(color='green', width=3, dash='dash'),
            name='Rotation Axis',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Update 3D layout
    fig.update_scenes(
        camera=dict(
            eye=dict(x=1.5, y=1.5, z=1),
            up=dict(x=0, y=0, z=1)
        ),
        xaxis=dict(range=[-1.5, 1.5], title='X'),
        yaxis=dict(range=[-1.5, 1.5], title='Y'),
        zaxis=dict(range=[-1, 1], title='Z'),
        aspectmode='cube',
        row=1, col=2
    )
    
    # Add title and adjust size
    fig.update_layout(
        title="Hemispherical Resonator Gyroscope Mode Shapes",
        height=500,
        width=1000,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_plots_figure(results):
    """Create Plotly figure for analytical plots.
    
    Args:
        results: Simulation results dictionary
        
    Returns:
        go.FigureWidget: Plotly figure with analytical plots
    """
    fig = go.FigureWidget(make_subplots(rows=2, cols=2,
                    subplot_titles=('Phase Space (X vs Y)', 'Mode Displacements',
                                    'Vibration Pattern Phase', 'Rotation Rate Measurement')))
    
    t = results['t']
    
    # Add phase space plot (top left)
    fig.add_trace(
        go.Scatter(x=results['x'], y=results['y'],
                  name='Phase Space', line=dict(color='blue', width=2)),
        row=1, col=1
    )
    
    # Add current state marker for phase space
    fig.add_trace(
        go.Scatter(x=[results['x'][0]], y=[results['y'][0]],
                  mode='markers',
                  marker=dict(size=10, color='red', symbol='circle'),
                  name='Current State',
                  showlegend=False),
        row=1, col=1
    )
    
    # Add mode displacements plot (top right)
    fig.add_trace(
        go.Scatter(x=t, y=results['x'],
                  name='X Mode', line=dict(color='blue')),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=t, y=results['y'],
                  name='Y Mode', line=dict(color='red')),
        row=1, col=2
    )
    
    # Add current state markers for mode displacements
    fig.add_trace(
        go.Scatter(x=[t[0]], y=[results['x'][0]],
                  mode='markers',
                  marker=dict(size=10, color='blue', symbol='circle'),
                  name='Current X',
                  showlegend=False),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=[t[0]], y=[results['y'][0]],
                  mode='markers',
                  marker=dict(size=10, color='red', symbol='circle'),
                  name='Current Y',
                  showlegend=False),
        row=1, col=2
    )
    
    # Set up time indicator line
    time_line_modes = fig.add_vline(x=t[0], line=dict(color='black', width=1, dash='dash'), 
                                   row=1, col=2)
    
    # Add phase plot (bottom left)
    fig.add_trace(
        go.Scatter(x=t, y=results['phase_unwrapped'],
                  name='Phase', line=dict(color='purple')),
        row=2, col=1
    )
    
    # Add current state marker for phase
    fig.add_trace(
        go.Scatter(x=[t[0]], y=[results['phase_unwrapped'][0]],
                  mode='markers',
                  marker=dict(size=10, color='purple', symbol='circle'),
                  name='Current Phase',
                  showlegend=False),
        row=2, col=1
    )
    
    # Set up time indicator line
    time_line_phase = fig.add_vline(x=t[0], line=dict(color='black', width=1, dash='dash'), 
                                   row=2, col=1)
    
    # Add rotation rate plot (bottom right)
    fig.add_trace(
        go.Scatter(x=t, y=results['measured_rotation_rate'],
                  name='Measured', line=dict(color='blue')),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=t, y=results['actual_rotation_rate'],
                  name='Actual', line=dict(color='green')),
        row=2, col=2
    )
    
    # Add current state markers for rotation rates
    fig.add_trace(
        go.Scatter(x=[t[0]], y=[results['measured_rotation_rate'][0]],
                  mode='markers',
                  marker=dict(size=10, color='blue', symbol='circle'),
                  name='Current Measured',
                  showlegend=False),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=[t[0]], y=[results['actual_rotation_rate'][0]],
                  mode='markers',
                  marker=dict(size=10, color='green', symbol='circle'),
                  name='Current Actual',
                  showlegend=False),
        row=2, col=2
    )
    
    # Set up time indicator line
    time_line_rates = fig.add_vline(x=t[0], line=dict(color='black', width=1, dash='dash'), 
                                   row=2, col=2)
    
    # Add subplot labels and settings
    fig.update_xaxes(title_text='X Displacement', row=1, col=1)
    fig.update_yaxes(title_text='Y Displacement', row=1, col=1)
    
    fig.update_xaxes(title_text='Time (s)', row=1, col=2)
    fig.update_yaxes(title_text='Displacement', row=1, col=2)
    
    fig.update_xaxes(title_text='Time (s)', row=2, col=1)
    fig.update_yaxes(title_text='Phase (rad)', row=2, col=1)
    
    fig.update_xaxes(title_text='Time (s)', row=2, col=2)
    fig.update_yaxes(title_text='Rotation Rate (rad/s)', row=2, col=2)
    
    # Add time text at the bottom
    time_text = fig.add_annotation(
        text=f"Time: {t[0]:.3f}s",
        x=0.5, y=0.01,
        xref='paper', yref='paper',
        showarrow=False,
        font=dict(size=12)
    )
    
    # Set axis limits
    fig.update_xaxes(range=[-1.5, 1.5], row=1, col=1)
    fig.update_yaxes(range=[-1.5, 1.5], row=1, col=1)
    
    # Make the axis equal for the phase space plot
    fig.update_xaxes(scaleanchor="y", scaleratio=1, row=1, col=1)
    
    # Add layout options
    fig.update_layout(
        height=600,
        width=1000,
        showlegend=True,
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center")
    )
    
    return fig

def update_animation_frame(anim_fig, plots_fig, results, frame):
    """Update animation and plot figures to current frame.
    
    Args:
        anim_fig: 3D mode shape animation figure
        plots_fig: Analytical plots figure
        results: Simulation results dictionary
        frame: Current frame index
    """
    t = results['t']
    current_t = t[frame]
    
    # 1. Update 2D mode shape visualization
    current_shape = results['mode_shapes']['combined_shapes'][frame]
    
    with anim_fig.batch_update():
        # Update combined mode shape (2D)
        anim_fig.data[0].x = current_shape[:, 0]
        anim_fig.data[0].y = current_shape[:, 1]
        
        # Update node points (2D)
        theta = results['mode_shapes']['theta']
        node_indices = [0, len(theta)//4, len(theta)//2, 3*len(theta)//4]
        node_x = [current_shape[i, 0] for i in node_indices]
        node_y = [current_shape[i, 1] for i in node_indices]
        anim_fig.data[2].x = node_x
        anim_fig.data[2].y = node_y
        
        # Update antinode points (2D)
        antinode_indices = [len(theta)//8, 3*len(theta)//8, 5*len(theta)//8, 7*len(theta)//8]
        antinode_x = [current_shape[i, 0] for i in antinode_indices]
        antinode_y = [current_shape[i, 1] for i in antinode_indices]
        anim_fig.data[3].x = antinode_x
        anim_fig.data[3].y = antinode_y
        
        # Update 3D surface
        # Create a meshgrid for 3D surface
        r = np.linspace(0, 1, 10)  # Radial distance from center
        theta_3d = results['mode_shapes']['theta']  # Angular coordinates
        
        r_grid, theta_grid = np.meshgrid(r, theta_3d)
        
        # Calculate base shape (circular disk)
        x_grid = r_grid * np.cos(theta_grid)
        y_grid = r_grid * np.sin(theta_grid)
        
        # Add displacement in z direction based on current mode shape
        z_factor = 0.5  # Scale factor for z displacement
        
        # Get normalized displacement (distance from unit circle)
        current_r = np.sqrt(current_shape[:, 0]**2 + current_shape[:, 1]**2)
        displacement = current_r - 1.0
        
        # Create z displacement field
        z_grid = np.zeros_like(r_grid)
        for i, disp in enumerate(displacement):
            z_grid[i, :] = disp * z_factor * r_grid[i, :]
        
        # Update 3D surface plot
        anim_fig.data[5].z = z_grid
        
        # Update node points in 3D
        node_z = [z_grid[i, -1] for i in node_indices]  # Use the outermost ring
        anim_fig.data[7].z = node_z
        
        # Add title with current time
        anim_fig.layout.title.text = f"Hemispherical Resonator Gyroscope Mode Shapes (Time: {current_t:.3f}s)"
        
    # 2. Update analytical plots
    with plots_fig.batch_update():
        # Update current state marker for phase space
        plots_fig.data[1].x = [results['x'][frame]]
        plots_fig.data[1].y = [results['y'][frame]]
        
        # Update mode displacement current markers
        plots_fig.data[4].x = [current_t]
        plots_fig.data[4].y = [results['x'][frame]]
        plots_fig.data[5].x = [current_t]
        plots_fig.data[5].y = [results['y'][frame]]
        
        # Update phase plot current marker
        plots_fig.data[7].x = [current_t]
        plots_fig.data[7].y = [results['phase_unwrapped'][frame]]
        
        # Update rotation rate current markers
        plots_fig.data[10].x = [current_t]
        plots_fig.data[10].y = [results['measured_rotation_rate'][frame]]
        plots_fig.data[11].x = [current_t]
        plots_fig.data[11].y = [results['actual_rotation_rate'][frame]]
        
        # Update time indicators in all plots
        for shape in plots_fig.layout.shapes:
            if shape.type == 'line' and hasattr(shape, 'x0'):
                shape.x0 = current_t
                shape.x1 = current_t
        
        # Update time text annotation
        for anno in plots_fig.layout.annotations:
            if "Time:" in anno.text:
                anno.text = f"Time: {current_t:.3f}s"
                break
