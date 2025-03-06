"""Video creation utilities for pendulum visualization."""

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

# Force matplotlib to use Agg backend for headless rendering
matplotlib.use('Agg')

def save_animation_as_video(anim_fig, results, filename='pendulum_animation.mp4', fps=30, dpi=100, width=1200, height=900):
    """Save animation as an MP4 video file using matplotlib (much faster).
    
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
            print(f"Creating pendulum animation with matplotlib (fast method)")
        
        # Check if 't' or 'time' is used in results
        time_key = 't' if 't' in results else 'time'
        if time_key not in results:
            raise ValueError(f"Time data not found in results. Available keys: {list(results.keys())}")
        
        # Extract data from results
        t_vals = results[time_key]
        x_vals = results['x']
        y_vals = results['y']
        theta_vals = results['theta']
        omega_vals = results['omega']
        
        # Check if energy data is available
        has_energy_data = 'kinetic_energy' in results and 'potential_energy' in results
        if has_energy_data:
            ke_vals = results['kinetic_energy']
            pe_vals = results['potential_energy']
            total_energy = results['total_energy'] if 'total_energy' in results else ke_vals + pe_vals
        elif 'mass' in results:
            # If energy data is not provided, try to calculate it
            mass = results['mass']
            g = 9.81  # gravitational acceleration
            L = results['L0'] if 'L0' in results else np.mean(results['L']) if 'L' in results else 1.0
            
            # Calculate kinetic and potential energy
            ke_vals = 0.5 * mass * ((omega_vals * L)**2)
            pe_vals = mass * g * L * (1 - np.cos(theta_vals))
            total_energy = ke_vals + pe_vals
            has_energy_data = True
        else:
            has_energy_data = False
        
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
        
        # Find axis limits for pendulum animation
        x_min, x_max = min(x_vals), max(x_vals)
        y_min, y_max = min(y_vals), max(y_vals)
        
        # Add 10% padding around the limits
        x_padding = 0.1 * (x_max - x_min)
        y_padding = 0.1 * (y_max - y_min)
        x_min, x_max = x_min - x_padding, x_max + x_padding
        y_min, y_max = y_min - y_padding, y_max + y_padding
        
        # Find limits for phase plot
        theta_min, theta_max = min(theta_vals), max(theta_vals)
        omega_min, omega_max = min(omega_vals), max(omega_vals)
        
        # Add padding for phase plot
        theta_padding = 0.1 * (theta_max - theta_min)
        omega_padding = 0.1 * (omega_max - omega_min)
        theta_min, theta_max = theta_min - theta_padding, theta_max + theta_padding
        omega_min, omega_max = omega_min - omega_padding, omega_max + omega_padding
        
        # Create figure and axis with figsize proportional to width/height
        fig_width = width / dpi
        fig_height = height / dpi
        
        with status_output:
            print(f"Creating matplotlib figure with grid layout ({fig_width:.1f}x{fig_height:.1f} inches at {dpi} DPI)")
        
        # Create figure with gridspec for layout
        fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi)
        gs = gridspec.GridSpec(2, 2, figure=fig, height_ratios=[1, 1], width_ratios=[1, 1])
        
        # Create the four axes for the different plots
        ax_pendulum = fig.add_subplot(gs[0, 0])
        ax_phase = fig.add_subplot(gs[0, 1])
        ax_time = fig.add_subplot(gs[1, 0])
        ax_energy = fig.add_subplot(gs[1, 1])
        
        fig.tight_layout(pad=3.0)
        
        # Setup for pendulum animation (top left)
        pendulum_line, = ax_pendulum.plot([], [], 'gray', lw=2)  # pendulum rod
        pendulum_point, = ax_pendulum.plot([], [], 'ro', ms=10)  # pendulum bob
        pendulum_trace, = ax_pendulum.plot([], [], 'b-', alpha=0.3, lw=1)  # trace of pendulum motion
        ax_pendulum.set_xlim(x_min, x_max)
        ax_pendulum.set_ylim(y_min, y_max)
        ax_pendulum.set_aspect('equal')
        ax_pendulum.set_title('Pendulum Animation')
        ax_pendulum.set_xlabel('x position')
        ax_pendulum.set_ylabel('y position')
        ax_pendulum.grid(True)
        
        # Setup for phase plot (top right)
        phase_point, = ax_phase.plot([], [], 'r*', ms=10)  # current state
        phase_trace, = ax_phase.plot([], [], 'purple', lw=1)  # phase space trajectory
        ax_phase.set_xlim(theta_min, theta_max)
        ax_phase.set_ylim(omega_min, omega_max)
        ax_phase.set_title('Phase Plot')
        ax_phase.set_xlabel('Angle (rad)')
        ax_phase.set_ylabel('Angular Velocity (rad/s)')
        ax_phase.grid(True)
        
        # Setup for time series (bottom left)
        time_line, = ax_time.plot([], [], 'b-', lw=2)  # angle vs time
        time_point, = ax_time.plot([], [], 'ro', ms=6)  # current time point
        ax_time.set_xlim(t_vals[0], t_vals[-1])
        ax_time.set_ylim(min(theta_vals), max(theta_vals))
        ax_time.set_title('Angle vs Time')
        ax_time.set_xlabel('Time (s)')
        ax_time.set_ylabel('Angle (rad)')
        ax_time.grid(True)
        
        # Setup for energy plot (bottom right)
        if has_energy_data:
            ke_line, = ax_energy.plot([], [], 'g-', lw=1.5, label='Kinetic')  # kinetic energy
            pe_line, = ax_energy.plot([], [], 'orange', lw=1.5, label='Potential')  # potential energy
            total_line, = ax_energy.plot([], [], 'k-', lw=2, label='Total')  # total energy
            ax_energy.set_xlim(t_vals[0], t_vals[-1])
            ax_energy.set_ylim(0, max(max(total_energy), max(ke_vals), max(pe_vals)) * 1.1)
            ax_energy.set_title('Energy vs Time')
            ax_energy.set_xlabel('Time (s)')
            ax_energy.set_ylabel('Energy (J)')
            ax_energy.legend(loc='upper right')
            ax_energy.grid(True)
        else:
            # If no energy data, just show empty plot with message
            ax_energy.text(0.5, 0.5, 'Energy data not available', 
                           ha='center', va='center', transform=ax_energy.transAxes)
            ax_energy.set_title('Energy vs Time')
            ax_energy.set_xlabel('Time (s)')
            ax_energy.set_ylabel('Energy (J)')
            ax_energy.grid(True)
        
        # Add time text
        time_text = fig.text(0.5, 0.01, '', ha='center', fontsize=10)
        
        # Initialize trace arrays
        x_trace, y_trace = [], []
        theta_trace, omega_trace = [], []
        
        # Process some frames first to build up trace data
        with status_output:
            print("Building up initial traces...")
        
        # Pre-compute a portion of the traces for better visualization
        trace_length = min(20, len(indices))  # Use first 20 frames or fewer
        for i in range(trace_length):
            frame_idx = indices[i]
            x_trace.append(x_vals[frame_idx])
            y_trace.append(y_vals[frame_idx])
            theta_trace.append(theta_vals[frame_idx])
            omega_trace.append(omega_vals[frame_idx])
        
        # Function to update the plots for each frame
        def update(frame_idx):
            i = indices[frame_idx]
            
            # Update pendulum animation
            pendulum_line.set_data([0, x_vals[i]], [0, y_vals[i]])
            pendulum_point.set_data([x_vals[i]], [y_vals[i]])
            
            # Update pendulum trace (last 100 points)
            x_trace.append(x_vals[i])
            y_trace.append(y_vals[i])
            trace_length = 50  # Keep the last 50 points for trace
            pendulum_trace.set_data(x_trace[-trace_length:], y_trace[-trace_length:])
            
            # Update phase plot
            theta_trace.append(theta_vals[i])
            omega_trace.append(omega_vals[i])
            phase_point.set_data([theta_vals[i]], [omega_vals[i]])
            phase_trace.set_data(theta_trace, omega_trace)
            
            # Update time series
            visible_t = t_vals[:i+1:step]  # Show all points up to current time
            visible_theta = theta_vals[:i+1:step]
            time_line.set_data(visible_t, visible_theta)
            time_point.set_data([t_vals[i]], [theta_vals[i]])
            
            # Update energy plot
            if has_energy_data:
                ke_line.set_data(visible_t, ke_vals[:i+1:step])
                pe_line.set_data(visible_t, pe_vals[:i+1:step])
                total_line.set_data(visible_t, total_energy[:i+1:step])
            
            # Update time text
            time_text.set_text(f'Time: {t_vals[i]:.2f}s')
            
            # Return all updated artists
            if has_energy_data:
                return (pendulum_line, pendulum_point, pendulum_trace,
                        phase_point, phase_trace,
                        time_line, time_point,
                        ke_line, pe_line, total_line, time_text)
            else:
                return (pendulum_line, pendulum_point, pendulum_trace,
                        phase_point, phase_trace,
                        time_line, time_point, time_text)
        
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
            metadata=dict(title='Pendulum Animation'),
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
