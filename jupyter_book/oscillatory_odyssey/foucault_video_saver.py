"""Video creation utilities specifically for Foucault pendulum visualization."""

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

# Force matplotlib to use Agg backend for headless rendering
matplotlib.use('Agg')

def save_foucault_video(anim_fig, results, filename='foucault_pendulum_video.mp4', fps=30, dpi=100, width=1200, height=900):
    """Save animation as an MP4 video file using matplotlib with custom layout for Foucault pendulum.
    
    Layout:
    - Top left: 3D pendulum animation
    - Bottom left: Phase space projection (x-y)
    - Top right: Angle vs Time (to match the notebook plots)
    - Bottom right: Energy plots
    
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
            print(f"Creating Foucault pendulum video with custom layout")
        
        # Check if required data is available
        if 't' not in results:
            raise ValueError(f"Time data not found in results. Available keys: {list(results.keys())}")
        
        # Extract data from results
        t_vals = results['t']
        x_vals = results['x']
        y_vals = results['y']
        theta_vals = results['theta']
        
        # Get unwrapped phi values and convert to modular degrees (between -180° and 180°)
        phi_unwrapped = results['phi_unwrapped']
        phi_vals = np.degrees(np.mod(phi_unwrapped + np.pi, 2*np.pi) - np.pi)  # Keep between -180 and 180
        
        # 3D visualization data - original coordinates from simulation
        original_bob_x = results['bob_x']
        original_bob_y = results['bob_y']
        original_bob_z = results['bob_z']
        
        # Get the demo factor for precession enhancement
        demo_factor = results.get('rotation_demo_factor', 100)  # Default to 100
        
        # Get the real precession rate (in radians/sec)
        if 'real_precession_rate' in results:
            # Convert from degrees/sec to radians/sec
            real_precession_rate = results['real_precession_rate'] * np.pi / 180
        else:
            # Default value if not available
            real_precession_rate = 7.292e-5 * np.sin(np.radians(45))  # At 45° latitude
        
        # Reduce number of frames for speed
        total_frames = len(t_vals)
        with status_output:
            print(f"Total frames: {total_frames}")
        
        # Use every nth frame - aim for 120 frames max
        target_frames = min(120, total_frames)
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
        ax_3d = fig.add_subplot(gs[0, 0], projection='3d')
        ax_angle_time = fig.add_subplot(gs[0, 1])  # Angle vs Time (top right)
        ax_phase = fig.add_subplot(gs[1, 0])
        ax_energy = fig.add_subplot(gs[1, 1])
        
        fig.tight_layout(pad=3.0)
        
        # Setup for 3D pendulum animation (top left)
        # Initialize empty lines and points that will be updated
        pendulum_line, = ax_3d.plot([], [], [], 'gray', lw=2)  # pendulum rod
        pendulum_point, = ax_3d.plot([], [], [], 'ro', ms=10, markeredgecolor='black')  # pendulum bob
        
        # For ground trace and pendulum path, we'll use scatter plots updated each frame
        ground_scatter = ax_3d.scatter([], [], [], c='k', alpha=0.2, s=5)
        
        # For pendulum path, use a simple red scatter
        path_scatter = ax_3d.scatter([], [], [], c='red', alpha=0.5, s=4)
        
        # Add oscillation plane visualization
        theta_circle = np.linspace(0, 2*np.pi, 100)
        plane_scatter = ax_3d.scatter([], [], [], c='blue', alpha=0.3, s=5)
        
        # Set reasonable 3D limits based on original coordinates
        max_val = max(np.max(np.abs(original_bob_x)), np.max(np.abs(original_bob_y)), np.max(np.abs(original_bob_z)))
        ax_3d.set_xlim(-max_val*1.2, max_val*1.2)
        ax_3d.set_ylim(-max_val*1.2, max_val*1.2)
        ax_3d.set_zlim(-max_val*1.2, max_val*0.2)  # Bottom-heavy z range
        ax_3d.set_title('Foucault Pendulum 3D')
        ax_3d.set_xlabel('X')
        ax_3d.set_ylabel('Y')
        ax_3d.set_zlabel('Z')
        
        # Setup axis for better viewpoint - restore original view
        ax_3d.view_init(elev=30, azim=45)
        
        # Draw a subtle grid at z=0 to represent the ground
        xx, yy = np.meshgrid(
            np.linspace(-max_val, max_val, 5),
            np.linspace(-max_val, max_val, 5)
        )
        ax_3d.plot_surface(xx, yy, np.zeros_like(xx), alpha=0.1, color='gray')
        
        # Add a subtle circle on the ground to show the maximum amplitude
        ground_circle_theta = np.linspace(0, 2*np.pi, 100)
        ground_circle_r = max_val * 0.8
        ax_3d.plot(
            ground_circle_r * np.cos(ground_circle_theta),
            ground_circle_r * np.sin(ground_circle_theta),
            np.zeros_like(ground_circle_theta) - max_val*0.01,  # Just slightly below ground
            'k--', alpha=0.3, linewidth=1
        )
        
        # Setup for phase plot (bottom left)
        phase_point, = ax_phase.plot([], [], 'r*', ms=10)  # current state
        phase_trace, = ax_phase.plot([], [], 'purple', lw=1)  # phase space trajectory
        ax_phase.set_xlim(np.min(x_vals)*1.2, np.max(x_vals)*1.2)
        ax_phase.set_ylim(np.min(y_vals)*1.2, np.max(y_vals)*1.2)
        ax_phase.set_title('Phase Space (X-Y Projection)')
        ax_phase.set_xlabel('X-angle')
        ax_phase.set_ylabel('Y-angle')
        ax_phase.grid(True)
        
        # Setup for Angle vs Time plot (top right)
        angle_line, = ax_angle_time.plot([], [], 'g-', lw=2)  # phi vs time
        current_angle_point, = ax_angle_time.plot([], [], 'ro', ms=8)  # current state marker
        
        # Set time range for x-axis
        ax_angle_time.set_xlim(t_vals[0], t_vals[-1])
        
        # Set y-axis range with buffer
        max_phi = np.max(phi_vals)
        min_phi = np.min(phi_vals)
        phi_buffer = (max_phi - min_phi) * 0.1  # 10% buffer
        ax_angle_time.set_ylim(min_phi - phi_buffer, max_phi + phi_buffer)
        
        ax_angle_time.set_title('Angle vs Time')
        ax_angle_time.set_xlabel('Time (s)')
        ax_angle_time.set_ylabel('Angle φ (deg)')
        ax_angle_time.grid(True)
        
        # Energy plot (bottom right)
        ke_line, = ax_energy.plot([], [], 'g-', lw=1.5, label='Kinetic')  # kinetic energy
        pe_line, = ax_energy.plot([], [], 'orange', lw=1.5, label='Potential')  # potential energy
        total_line, = ax_energy.plot([], [], 'k-', lw=2, label='Total')  # total energy
        ax_energy.set_xlim(t_vals[0], t_vals[-1])
        ax_energy.set_ylim(0, max(max(results['total_energy']), max(results['kinetic_energy']), max(results['potential_energy'])) * 1.1)
        ax_energy.set_title('Energy vs Time')
        ax_energy.set_xlabel('Time (s)')
        ax_energy.set_ylabel('Energy (J)')
        ax_energy.legend(loc='upper right')
        ax_energy.grid(True)
        
        # Add time text
        time_text = fig.text(0.5, 0.01, '', ha='center', fontsize=10)
        
        # Function to update the plots for each frame
        def update(frame_idx):
            i = indices[frame_idx]
            
            # Get the original bob position (unenhanced, to preserve physics)
            bob_x = original_bob_x[i]
            bob_y = original_bob_y[i]
            bob_z = original_bob_z[i]
            
            # Update pendulum rod with original position
            pendulum_line.set_data_3d([0, bob_x], [0, bob_y], [0, bob_z])
            pendulum_point.set_data_3d([bob_x], [bob_y], [bob_z])
            
            # Update ground trace - showing all points up to current frame
            trace_x = original_bob_x[:i+1:step]
            trace_y = original_bob_y[:i+1:step]
            trace_z = np.full_like(trace_x, -max_val*0.01)  # Slightly below ground
            
            # Update the ground scatter
            ground_scatter._offsets3d = (trace_x, trace_y, trace_z)
            
            # Update phase plot - using all points up to current frame
            phase_x_trace = x_vals[:i+1:step]
            phase_y_trace = y_vals[:i+1:step]
            phase_point.set_data([x_vals[i]], [y_vals[i]])
            phase_trace.set_data(phase_x_trace, phase_y_trace)
            
            # Update angle vs time plot
            visible_t = t_vals[:i+1:step]  # Show all points up to current time
            visible_phi = phi_vals[:i+1:step]
            angle_line.set_data(visible_t, visible_phi)
            current_angle_point.set_data([t_vals[i]], [phi_vals[i]])
            
            # Update energy plot
            ke_line.set_data(visible_t, results['kinetic_energy'][:i+1:step])
            pe_line.set_data(visible_t, results['potential_energy'][:i+1:step])
            total_line.set_data(visible_t, results['total_energy'][:i+1:step])
            
            # Update time text
            time_text.set_text(f'Time: {t_vals[i]:.2f}s')
            
            # Update 3D pendulum path with original coordinates
            path_x = original_bob_x[:i+1:step]
            path_y = original_bob_y[:i+1:step]
            path_z = original_bob_z[:i+1:step]
            
            # Update path scatter plot
            path_scatter._offsets3d = (path_x, path_y, path_z)
            
            # Enhance only the oscillation plane visualization (not the physics)
            # Get base phi from original simulation
            phi_base = results['phi'][i]
            
            # Calculate elapsed time
            elapsed_time = t_vals[i] - t_vals[0]
            
            # Calculate enhanced phi that includes the visualization demo factor
            additional_rotation = real_precession_rate * (demo_factor - 1) * elapsed_time
            phi_enhanced = phi_base + additional_rotation
            
            # Calculate the oscillation plane circle
            r = np.max(np.sqrt(np.square(path_x) + np.square(path_y)))
            if r < 0.1:  # Use a minimum radius if current path is too small
                r = max_val * 0.8
            
            x_circle = r * np.cos(theta_circle)
            y_circle = r * np.sin(theta_circle)
            z_circle = np.ones_like(x_circle) * (-max_val*0.5)  # Position it midway in z
            
            # Rotate the circle based on enhanced phi
            rotated_x = x_circle * np.cos(phi_enhanced) - y_circle * np.sin(phi_enhanced)
            rotated_y = x_circle * np.sin(phi_enhanced) + y_circle * np.cos(phi_enhanced)
            
            # Update oscillation plane
            plane_scatter._offsets3d = (rotated_x, rotated_y, z_circle)
            
            # Return all updated artists
            return (pendulum_line, pendulum_point, ground_scatter, path_scatter, plane_scatter,
                    phase_point, phase_trace,
                    angle_line, current_angle_point,
                    ke_line, pe_line, total_line, time_text)
        
        # Create the animation
        with status_output:
            print(f"Creating animation with {len(indices)} frames")
        
        animation = FuncAnimation(
            fig, update, frames=len(indices), 
            interval=1000/fps, blit=True, repeat=False
        )
        
        # Set up FFmpeg writer
        if os.path.exists("C:\\ffmpeg\\bin\\ffmpeg.exe"):
            # Set the FFmpeg path in matplotlib's rcParams
            with status_output:
                print(f"Using system FFmpeg at C:\\ffmpeg\\bin\\ffmpeg.exe")
            
            # Set the path in matplotlib configuration
            matplotlib.rcParams['animation.ffmpeg_path'] = "C:\\ffmpeg\\bin\\ffmpeg.exe"
        else:
            with status_output:
                print(f"Using default FFmpeg path")
        
        # Create FFmpeg writer with appropriate settings
        writer = FFMpegWriter(
            fps=fps,
            metadata=dict(title='Foucault Pendulum Animation'),
            bitrate=2000,  # Higher bitrate for better quality
            codec='libx264',
            extra_args=['-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '22']
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
