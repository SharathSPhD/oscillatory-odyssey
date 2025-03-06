"""Video creation utilities specifically for Hemispherical Resonator Gyroscope visualization."""

import os
import tempfile
import shutil
import numpy as np
from IPython.display import display, HTML, Video
import ipywidgets as widgets
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import matplotlib.gridspec as gridspec
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as patches

# Force matplotlib to use Agg backend for headless rendering
matplotlib.use('Agg')

def save_hrg_video(anim_fig, results, filename='hrg_video.mp4', fps=30, dpi=100, width=1200, height=900):
    """Save Hemispherical Resonator Gyroscope animation as an MP4 video file using matplotlib.
    
    Layout:
    - Top left: 2D mode shape animation
    - Top right: 3D resonator visualization
    - Bottom left: Phase space plot (x vs y)
    - Bottom right: Rotation rate measurement
    
    Args:
        anim_fig: Original Plotly figure (not used in this implementation)
        results: Simulation results dictionary
        filename: Output filename (should end with .mp4)
        fps: Frames per second in the output video
        dpi: Resolution (dots per inch)
        width: Width of the output video in pixels (approximate)
        height: Height of the output video in pixels (approximate)
        
    Returns:
        widgets.HTML: HTML widget with status message and embedded video
    """
    # Display status
    status_output = widgets.Output()
    display(status_output)
    
    try:
        with status_output:
            print(f"Creating Hemispherical Resonator Gyroscope video with custom layout")
        
        # Check if required data is available
        if 't' not in results:
            raise ValueError(f"Time data not found in results. Available keys: {list(results.keys())}")
        
        # Extract data from results
        t_vals = results['t']
        x = results['x']
        y = results['y']
        phase = results['phase_unwrapped']
        measured_rotation_rate = results['measured_rotation_rate']
        actual_rotation_rate = results['actual_rotation_rate']
        
        # Mode shape data
        mode_shapes = results['mode_shapes']
        theta = mode_shapes['theta']
        circle_x = mode_shapes['circle_x']
        circle_y = mode_shapes['circle_y']
        combined_shapes = mode_shapes['combined_shapes']
        
        # Reduce number of frames for speed
        total_frames = len(t_vals)
        with status_output:
            print(f"Total frames: {total_frames}")
        
        # Use every nth frame - aim for 240 frames max (8 seconds at 30fps)
        target_frames = min(240, total_frames)
        step = max(1, total_frames // target_frames)
        with status_output:
            print(f"Using frame step: {step} (keeping approximately {total_frames//step} frames)")
        
        # Keep track of frames we'll use
        indices = list(range(0, total_frames, step))
        
        # Create figure with gridspec for custom layout
        fig_width = width / dpi
        fig_height = height / dpi
        
        with status_output:
            print(f"Creating matplotlib figure with custom layout ({fig_width:.1f}x{fig_height:.1f} inches at {dpi} DPI)")
        
        # Create figure with gridspec for layout
        fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi)
        gs = gridspec.GridSpec(2, 2, figure=fig, height_ratios=[1, 1], width_ratios=[1, 1])
        
        # Create the four axes for the different plots
        ax_2d = fig.add_subplot(gs[0, 0])  # 2D mode shape (top left)
        ax_3d = fig.add_subplot(gs[0, 1], projection='3d')  # 3D visualization (top right)
        ax_phase = fig.add_subplot(gs[1, 0])  # Phase space plot (bottom left)
        ax_rates = fig.add_subplot(gs[1, 1])  # Rotation rate (bottom right)
        
        # Standard tight layout
        fig.tight_layout(pad=3.0)
        
        # Setup for 2D mode shape (top left)
        # Plotting initial shape
        initial_shape = combined_shapes[0]
        
        # Plot reference circle
        circle_line, = ax_2d.plot(circle_x, circle_y, 'k--', lw=1, alpha=0.5)
        
        # Plot mode shape
        mode_line, = ax_2d.plot(initial_shape[:, 0], initial_shape[:, 1], 'b-', lw=2)
        
        # Add node and antinode markers
        node_indices = [0, len(theta)//4, len(theta)//2, 3*len(theta)//4]
        node_x = [initial_shape[i, 0] for i in node_indices]
        node_y = [initial_shape[i, 1] for i in node_indices]
        node_points, = ax_2d.plot(node_x, node_y, 'ro', ms=6)
        
        antinode_indices = [len(theta)//8, 3*len(theta)//8, 5*len(theta)//8, 7*len(theta)//8]
        antinode_x = [initial_shape[i, 0] for i in antinode_indices]
        antinode_y = [initial_shape[i, 1] for i in antinode_indices]
        antinode_points, = ax_2d.plot(antinode_x, antinode_y, 'go', ms=6)
        
        # Add reference axis to visualize rotation
        ax_2d.plot([0, 1.5], [0, 0], 'k:', lw=1)
        
        # Setup 2D plot
        ax_2d.set_xlim(-1.5, 1.5)
        ax_2d.set_ylim(-1.5, 1.5)
        ax_2d.set_aspect('equal')
        ax_2d.grid(True, alpha=0.3)
        ax_2d.set_title('Mode Shape')
        ax_2d.set_xlabel('X')
        ax_2d.set_ylabel('Y')
        
        # Setup 3D visualization (top right)
        # First setup the meshgrid for the 3D visualization
        r = np.linspace(0, 1, 10)  # Radial distance from center
        r_grid, theta_grid = np.meshgrid(r, theta)
        
        # Base shape (circular disk)
        x_grid = r_grid * np.cos(theta_grid)
        y_grid = r_grid * np.sin(theta_grid)
        
        # Initial z displacement based on mode shape
        z_factor = 0.5  # Scale factor for z displacement
        initial_r = np.sqrt(initial_shape[:, 0]**2 + initial_shape[:, 1]**2)
        displacement = initial_r - 1.0
        
        # Create z displacement field
        z_grid = np.zeros_like(r_grid)
        for i, disp in enumerate(displacement):
            z_grid[i, :] = disp * z_factor * r_grid[i, :]
        
        # Plot the 3D surface
        surf = ax_3d.plot_surface(x_grid, y_grid, z_grid, cmap='viridis', alpha=0.8, edgecolor='none')
        
        # Add reference circle (at z=0)
        ax_3d.plot(circle_x, circle_y, np.zeros_like(circle_x), 'k-', lw=1)
        
        # Add rotation axis
        ax_3d.plot([0, 0], [0, 0], [-1, 1], 'g--', lw=2, label='Rotation Axis')
        
        # Setup 3D plot
        ax_3d.set_xlim(-1.5, 1.5)
        ax_3d.set_ylim(-1.5, 1.5)
        ax_3d.set_zlim(-1, 1)
        ax_3d.set_title('3D Visualization')
        ax_3d.set_xlabel('X')
        ax_3d.set_ylabel('Y')
        ax_3d.set_zlabel('Z')
        ax_3d.view_init(elev=30, azim=45)
        
        # Setup phase space plot (bottom left)
        phase_line, = ax_phase.plot(x, y, 'b-', lw=2)
        phase_point, = ax_phase.plot([x[0]], [y[0]], 'ro', ms=8)
        
        # Setup phase space plot
        ax_phase.set_xlim(-1.5, 1.5)
        ax_phase.set_ylim(-1.5, 1.5)
        ax_phase.set_aspect('equal')
        ax_phase.grid(True)
        ax_phase.set_title('Phase Space (X vs Y)')
        ax_phase.set_xlabel('X Displacement')
        ax_phase.set_ylabel('Y Displacement')
        
        # Setup rotation rate plot (bottom right)
        measured_line, = ax_rates.plot(t_vals, measured_rotation_rate, 'b-', lw=2, label='Measured')
        actual_line, = ax_rates.plot(t_vals, actual_rotation_rate, 'g-', lw=2, label='Actual')
        
        # Current time marker
        time_marker_rates, = ax_rates.plot([t_vals[0]], [measured_rotation_rate[0]], 'ro', ms=8)
        
        # Current time line
        time_line = ax_rates.axvline(x=t_vals[0], color='k', linestyle='--', alpha=0.5)
        
        # Setup rotation rate plot
        ax_rates.set_xlim(t_vals[0], t_vals[-1])
        ax_rates.set_ylim(
            min(np.min(measured_rotation_rate), np.min(actual_rotation_rate)) * 1.2,
            max(np.max(measured_rotation_rate), np.max(actual_rotation_rate)) * 1.2
        )
        ax_rates.grid(True)
        ax_rates.set_title('Rotation Rate Measurement')
        ax_rates.set_xlabel('Time (s)')
        ax_rates.set_ylabel('Rotation Rate (rad/s)')
        ax_rates.legend()
        
        # Add main title
        plt.suptitle(
            f"Hemispherical Resonator Gyroscope Simulation\n"
            f"Rotation Rate: {results['rotation_rate']:.2f} rad/s, Bryan Factor: {results['bryan_factor']:.2f}",
            fontsize=14
        )
        
        # Add time display
        time_text = fig.text(0.5, 0.01, f"Time: {t_vals[0]:.3f} s", ha='center', fontsize=12)
        
        # Function to update the animation for each frame
        def update(frame_idx):
            i = indices[frame_idx]
            current_t = t_vals[i]
            
            # 1. Update 2D mode shape
            current_shape = combined_shapes[i]
            mode_line.set_data(current_shape[:, 0], current_shape[:, 1])
            
            # Update node markers
            node_x = [current_shape[j, 0] for j in node_indices]
            node_y = [current_shape[j, 1] for j in node_indices]
            node_points.set_data(node_x, node_y)
            
            # Update antinode markers
            antinode_x = [current_shape[j, 0] for j in antinode_indices]
            antinode_y = [current_shape[j, 1] for j in antinode_indices]
            antinode_points.set_data(antinode_x, antinode_y)
            
            # 2. Update 3D surface
            # First clear the old surface
            ax_3d.clear()
            
            # Get normalized displacement for the current shape
            current_r = np.sqrt(current_shape[:, 0]**2 + current_shape[:, 1]**2)
            displacement = current_r - 1.0
            
            # Create z displacement field
            z_grid = np.zeros_like(r_grid)
            for j, disp in enumerate(displacement):
                z_grid[j, :] = disp * z_factor * r_grid[j, :]
            
            # Plot the new 3D surface
            surf = ax_3d.plot_surface(x_grid, y_grid, z_grid, cmap='viridis', alpha=0.8, edgecolor='none')
            
            # Re-add reference circle and rotation axis
            ax_3d.plot(circle_x, circle_y, np.zeros_like(circle_x), 'k-', lw=1)
            ax_3d.plot([0, 0], [0, 0], [-1, 1], 'g--', lw=2)
            
            # Reset 3D view settings
            ax_3d.set_xlim(-1.5, 1.5)
            ax_3d.set_ylim(-1.5, 1.5)
            ax_3d.set_zlim(-1, 1)
            ax_3d.set_title('3D Visualization')
            ax_3d.set_xlabel('X')
            ax_3d.set_ylabel('Y')
            ax_3d.set_zlabel('Z')
            ax_3d.view_init(elev=30, azim=45)
            
            # 3. Update phase space plot
            # Calculate visible indices up to current frame
            visible_range = range(0, i+1)
            phase_line.set_data(x[visible_range], y[visible_range])
            phase_point.set_data([x[i]], [y[i]])
            
            # 4. Update rotation rate plot
            time_marker_rates.set_data([current_t], [measured_rotation_rate[i]])
            time_line.set_xdata([current_t, current_t])
            
            # 5. Update time text
            time_text.set_text(f"Time: {current_t:.3f} s")
            
            return (mode_line, node_points, antinode_points, phase_line, phase_point,
                    time_marker_rates, time_line, time_text, surf)
        
        # Create the animation
        with status_output:
            print(f"Creating animation with {len(indices)} frames")
        
        animation = FuncAnimation(
            fig, update, frames=len(indices), 
            interval=1000/fps, blit=True, repeat=False
        )
        
        # Set up FFmpeg writer
        # Try multiple common FFmpeg paths
        ffmpeg_paths = [
            "C:\\ffmpeg\\bin\\ffmpeg.exe",  # Common Windows installation
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",  # Another common Windows path
            "/usr/bin/ffmpeg",  # Linux path
            "/usr/local/bin/ffmpeg"  # macOS common path
        ]
        
        ffmpeg_found = False
        for ffmpeg_path in ffmpeg_paths:
            if os.path.exists(ffmpeg_path):
                # Set the FFmpeg path in matplotlib's rcParams
                with status_output:
                    print(f"Using FFmpeg at {ffmpeg_path}")
                
                # Set the path in matplotlib configuration
                matplotlib.rcParams['animation.ffmpeg_path'] = ffmpeg_path
                ffmpeg_found = True
                break
        
        if not ffmpeg_found:
            with status_output:
                print("FFmpeg not found in common locations. Using default matplotlib configuration.")
                print("If video saving fails, please install FFmpeg or specify its location.")
        
        # Create FFmpeg writer with appropriate settings
        try:
            writer = FFMpegWriter(
                fps=fps,
                metadata=dict(title='Hemispherical Resonator Gyroscope Animation'),
                bitrate=2000,  # Higher bitrate for better quality
                codec='libx264',
                extra_args=['-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '22']
            )
        except Exception as ffmpeg_error:
            with status_output:
                print(f"Error initializing FFMpegWriter: {str(ffmpeg_error)}")
                print("Trying with basic settings...")
            
            # Fallback to simpler writer configuration
            writer = FFMpegWriter(
                fps=fps,
                metadata=dict(title='Hemispherical Resonator Gyroscope Animation'),
                bitrate=1500
            )
        
        # Save the animation
        with status_output:
            print(f"Saving animation to {filename}...")
            print(f"This will take a moment, please wait...")
        
        animation.save(filename, writer=writer, dpi=dpi)
        
        # Close the figure to free memory
        plt.close(fig)
        
        with status_output:
            print(f"Animation saved successfully!")
        
        # Display the video
        video = Video(filename, embed=True, html_attributes="controls autoplay loop")
        
        return widgets.HTML(
            f"<div style='background-color: #d4edda; color: #155724; padding: 15px; border-radius: 4px; margin-bottom: 20px;'>"
            f"Animation saved successfully to <code>{filename}</code></div>"
            f"<div style='margin: 20px 0;'>{video._repr_html_()}</div>"
        )
        
    except Exception as e:
        with status_output:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return widgets.HTML(
            f"<div style='background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 4px; margin-bottom: 20px;'>"
            f"Error saving animation: {str(e)}</div>"
        )
