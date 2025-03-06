"""Video creation utilities specifically for gyroscope visualization."""

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

def save_gyroscope_video(anim_fig, results, filename='gyroscope_video.mp4', fps=30, dpi=100, width=1200, height=900):
    """Save gyroscope animation as an MP4 video file using matplotlib.
    
    Layout:
    - Top left: 3D gyroscope animation
    - Bottom left: Phase space (θ vs dθ/dt)
    - Top right: Angles vs Time (θ, φ)
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
            print(f"Creating gyroscope video with custom layout")
        
        # Check if required data is available
        if 't' not in results:
            raise ValueError(f"Time data not found in results. Available keys: {list(results.keys())}")
        
        # Extract data from results
        t_vals = results['t']
        theta = results['theta']
        phi = results['phi_unwrapped']
        theta_dot = results['theta_dot']
        psi_dot = results['psi_dot']
        
        # 3D visualization data
        pivot = results['pivot']
        wheel_center = results['wheel_center']
        rim_points = results['rim_points']
        spin_axis = results['spin_axis']
        
        # Angular momentum data
        L_x = results['L_x']
        L_y = results['L_y']
        L_z = results['L_z']
        L_magnitude = results['L_magnitude']  # Add this line to extract magnitude
        
        # Energy data
        kinetic_energy = results['kinetic_energy']
        potential_energy = results['potential_energy']
        total_energy = results['total_energy']
        
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
        
        # Initialize path history arrays
        path_history_x = []
        path_history_y = []
        path_history_z = []
        
        # Create the four axes for the different plots
        ax_3d = fig.add_subplot(gs[0, 0], projection='3d')
        ax_angles = fig.add_subplot(gs[0, 1])  # Angles vs Time (top right)
        ax_phase = fig.add_subplot(gs[1, 0])  # Phase space (bottom left)
        ax_energy = fig.add_subplot(gs[1, 1])  # Energy plots (bottom right)
        
        fig.tight_layout(pad=3.0)
        
        # Setup for 3D gyroscope animation (top left)
        # Calculate maximum rod length for setting axis limits
        rod_length = results['rod_length']
        wheel_radius = results['wheel_radius']
        max_dim = max(rod_length, wheel_radius) * 1.5
        
        # Initialize empty lines and points that will be updated
        rod_line, = ax_3d.plot([], [], [], 'gray', lw=3, label='Rod')  # rod
        wheel_center_point, = ax_3d.plot([], [], [], 'ro', ms=5, label='Wheel Center')  # wheel center
        spin_axis_line, = ax_3d.plot([], [], [], 'r-', lw=2, label='Spin Axis')  # spin axis
        
        # Initialize empty wheel rim
        wheel_rim, = ax_3d.plot([], [], [], 'b-', lw=2, label='Wheel Rim')
        
        # Angular momentum vector
        wheel_center_0 = wheel_center[0]
        spin_axis_0 = spin_axis[0]
        
        # Scale for initial visualization
        L_scale = max_dim * 0.8
        
        # Calculate endpoint
        L_end_x = wheel_center_0[0] + spin_axis_0[0] * L_scale
        L_end_y = wheel_center_0[1] + spin_axis_0[1] * L_scale
        L_end_z = wheel_center_0[2] + spin_axis_0[2] * L_scale
        
        angular_momentum_line, = ax_3d.plot(
            [wheel_center_0[0], L_end_x],
            [wheel_center_0[1], L_end_y],
            [wheel_center_0[2], L_end_z],
            'purple', lw=3, label='Angular Momentum'
        )
        angular_momentum_point, = ax_3d.plot(
            [L_end_x], [L_end_y], [L_end_z], 'o', ms=5, color='purple'
        )
        
        # Path history
        path_line, = ax_3d.plot([], [], [], 'r--', lw=1, alpha=0.5, label='Path')
        
        # Set 3D plot limits
        ax_3d.set_xlim(-max_dim, max_dim)
        ax_3d.set_ylim(-max_dim, max_dim)
        ax_3d.set_zlim(-0.2*max_dim, max_dim)
        ax_3d.set_title('Gyroscope 3D Animation')
        ax_3d.set_xlabel('X')
        ax_3d.set_ylabel('Y')
        ax_3d.set_zlabel('Z')
        
        # Setup better viewpoint for 3D
        ax_3d.view_init(elev=30, azim=45)
        
        # Setup reference axes
        ax_3d.plot([0, max_dim], [0, 0], [0, 0], 'r-', lw=1, alpha=0.5)  # X-axis
        ax_3d.plot([0, 0], [0, max_dim], [0, 0], 'g-', lw=1, alpha=0.5)  # Y-axis
        ax_3d.plot([0, 0], [0, 0], [0, max_dim], 'b-', lw=1, alpha=0.5)  # Z-axis
        
        # Setup for angles plot (top right)
        theta_line, = ax_angles.plot([], [], 'b-', lw=2, label='θ (tilt)')
        phi_line, = ax_angles.plot([], [], 'g-', lw=2, label='φ (azimuth)')
        current_theta_point, = ax_angles.plot([], [], 'bo', ms=5)
        current_phi_point, = ax_angles.plot([], [], 'go', ms=5)
        
        # Setup angle plot
        ax_angles.set_xlim(t_vals[0], t_vals[-1])
        theta_deg = np.degrees(theta)
        phi_deg = np.degrees(phi)
        ax_angles.set_ylim(
            min(np.min(theta_deg), np.min(phi_deg)) - 5,
            max(np.max(theta_deg), np.max(phi_deg)) + 5
        )
        ax_angles.set_title('Angles vs Time')
        ax_angles.set_xlabel('Time (s)')
        ax_angles.set_ylabel('Angle (degrees)')
        ax_angles.grid(True)
        ax_angles.legend()
        
        # Setup for phase space plot (bottom left)
        phase_line, = ax_phase.plot([], [], 'purple', lw=2)
        current_phase_point, = ax_phase.plot([], [], 'ro', ms=6)
        
        # Calculate phase space limits
        theta_deg = np.degrees(theta)
        theta_dot_deg = np.degrees(theta_dot)
        
        # Set phase space plot limits with padding
        theta_range = max(theta_deg) - min(theta_deg)
        theta_dot_range = max(theta_dot_deg) - min(theta_dot_deg)
        
        ax_phase.set_xlim(
            min(theta_deg) - 0.1 * theta_range,
            max(theta_deg) + 0.1 * theta_range
        )
        ax_phase.set_ylim(
            min(theta_dot_deg) - 0.1 * theta_dot_range,
            max(theta_dot_deg) + 0.1 * theta_dot_range
        )
        
        ax_phase.set_title('Phase Space (θ vs dθ/dt)')
        ax_phase.set_xlabel('Tilt Angle θ (degrees)')
        ax_phase.set_ylabel('Angular Velocity dθ/dt (degrees/s)')
        ax_phase.grid(True)
        
        # Setup for energy plot (bottom right)
        kinetic_line, = ax_energy.plot([], [], 'g-', lw=2, label='Kinetic Energy')
        potential_line, = ax_energy.plot([], [], 'orange', lw=2, label='Potential Energy')
        total_line, = ax_energy.plot([], [], 'k-', lw=2, label='Total Energy')
        
        # Add angular momentum line to energy plot
        # Scale the angular momentum to fit on the same plot as energy
        max_energy = max(np.max(kinetic_energy), np.max(potential_energy), np.max(total_energy))
        max_L_magnitude = max(np.max(L_magnitude), 1e-6)
        scale_factor = max_energy / max_L_magnitude
        scaled_L_magnitude = L_magnitude * scale_factor
        
        # Initialize angular momentum line
        angular_mom_line, = ax_energy.plot([], [], 'purple', linestyle='dotted', lw=2, label='Angular Momentum (scaled)')
        
        # Setup energy plot
        ax_energy.set_xlim(t_vals[0], t_vals[-1])
        ax_energy.set_ylim(0, max(max_energy, np.max(scaled_L_magnitude)) * 1.1)
        ax_energy.set_title('Energy & Angular Momentum')
        ax_energy.set_xlabel('Time (s)')
        ax_energy.set_ylabel('Energy (J) and\nScaled Angular Momentum\n(kg·m²/s)', fontsize=9)
        ax_energy.grid(True)
        ax_energy.legend(loc='upper right', fontsize=8)
        
        # Add time text
        time_text = fig.text(0.5, 0.01, '', ha='center', fontsize=10)
        
        # Function to update the plots for each frame
        def update(frame_idx):
            i = indices[frame_idx]
            nonlocal path_history_x, path_history_y, path_history_z
            
            # Update time text
            time_text.set_text(f'Time: {t_vals[i]:.2f}s')
            
            # Update 3D gyroscope
            current_pivot = pivot[i]
            current_wheel_center = wheel_center[i]
            current_spin_axis = spin_axis[i]
            current_rim_points = rim_points[i]
            rod_line.set_data_3d(
                [current_pivot[0], current_wheel_center[0]],
                [current_pivot[1], current_wheel_center[1]],
                [current_pivot[2], current_wheel_center[2]]
            )
            
            # Update wheel center
            wheel_center_point.set_data_3d(
                [current_wheel_center[0]],
                [current_wheel_center[1]],
                [current_wheel_center[2]]
            )
            
            # Update spin axis
            axis_scale = wheel_radius * 1.5
            spin_axis_line.set_data_3d(
                [current_wheel_center[0], current_wheel_center[0] + current_spin_axis[0] * axis_scale],
                [current_wheel_center[1], current_wheel_center[1] + current_spin_axis[1] * axis_scale],
                [current_wheel_center[2], current_wheel_center[2] + current_spin_axis[2] * axis_scale]
            )
            
            # Update wheel rim
            rim_x = current_rim_points[:, 0]
            rim_y = current_rim_points[:, 1]
            rim_z = current_rim_points[:, 2]
            
            # Close the loop
            rim_x = np.append(rim_x, rim_x[0])
            rim_y = np.append(rim_y, rim_y[0])
            rim_z = np.append(rim_z, rim_z[0])
            
            wheel_rim.set_data_3d(rim_x, rim_y, rim_z)
            
            # Update angular momentum vector - align with spin axis
            
            # Extract current angular momentum magnitude from results
            current_magnitude = L_magnitude[i]  # Use the magnitude directly from results
            
            # Scale for visualization based on magnitude
            # Ensure we never use zero magnitude to avoid division errors
            current_magnitude = max(current_magnitude, 1e-6)
            L_scale = max_dim * 0.8
            
            # Calculate endpoint - angular momentum vector should align with spin axis
            L_end_x = current_wheel_center[0] + current_spin_axis[0] * L_scale
            L_end_y = current_wheel_center[1] + current_spin_axis[1] * L_scale
            L_end_z = current_wheel_center[2] + current_spin_axis[2] * L_scale
            
            # Update angular momentum vector visualization
            angular_momentum_line.set_data_3d(
                [current_wheel_center[0], L_end_x], 
                [current_wheel_center[1], L_end_y], 
                [current_wheel_center[2], L_end_z]
            )
            angular_momentum_point.set_data_3d([L_end_x], [L_end_y], [L_end_z])
            
            # Update path history
            # Initialize path history if it's the first frame
            if frame_idx == 0:
                path_history_x.clear()
                path_history_y.clear()
                path_history_z.clear()
                
            # Add current position to history
            path_history_x.append(current_wheel_center[0])
            path_history_y.append(current_wheel_center[1])
            path_history_z.append(current_wheel_center[2])
            
            # Limit history length for smoother visualization
            max_history = 200
            if len(path_history_x) > max_history:
                path_history_x = path_history_x[-max_history:]
                path_history_y = path_history_y[-max_history:]
                path_history_z = path_history_z[-max_history:]
                
            path_line.set_data_3d(path_history_x, path_history_y, path_history_z)
            
            # Update angles plot
            visible_t = t_vals[:i+1:step]
            visible_theta_deg = np.degrees(theta[:i+1:step])
            visible_phi_deg = np.degrees(phi[:i+1:step])
            
            theta_line.set_data(visible_t, visible_theta_deg)
            phi_line.set_data(visible_t, visible_phi_deg)
            
            current_theta_point.set_data([t_vals[i]], [np.degrees(theta[i])])
            current_phi_point.set_data([t_vals[i]], [np.degrees(phi[i])])
            
            # Update phase space plot
            visible_theta_deg = np.degrees(theta[:i+1:step])
            visible_theta_dot_deg = np.degrees(theta_dot[:i+1:step])
            
            phase_line.set_data(visible_theta_deg, visible_theta_dot_deg)
            current_phase_point.set_data([np.degrees(theta[i])], [np.degrees(theta_dot[i])])
            
            # Update energy plot
            visible_t = t_vals[:i+1:step]
            visible_ke = kinetic_energy[:i+1:step]
            visible_pe = potential_energy[:i+1:step]
            visible_te = total_energy[:i+1:step]
            visible_am = scaled_L_magnitude[:i+1:step]
            
            kinetic_line.set_data(visible_t, visible_ke)
            potential_line.set_data(visible_t, visible_pe)
            total_line.set_data(visible_t, visible_te)
            angular_mom_line.set_data(visible_t, visible_am)
            
            # Return all artists that were updated
            return (rod_line, wheel_center_point, spin_axis_line, wheel_rim, 
                    angular_momentum_line, angular_momentum_point, path_line,
                    theta_line, phi_line, current_theta_point, current_phi_point,
                    phase_line, current_phase_point,
                    kinetic_line, potential_line, total_line, angular_mom_line, time_text)
        
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
            metadata=dict(title='Gyroscope Animation'),
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
