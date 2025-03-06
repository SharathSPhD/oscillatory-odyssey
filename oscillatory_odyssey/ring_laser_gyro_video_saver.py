"""Video creation utilities specifically for Ring Laser Gyroscope visualization."""

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

def save_ring_laser_gyro_video(anim_fig, results, filename='ring_laser_gyro_video.mp4', fps=30, dpi=100, width=1200, height=900):
    """Save Ring Laser Gyroscope animation as an MP4 video file using matplotlib.
    
    Layout:
    - Top left: 3D RLG animation
    - Bottom left: Lissajous figure (photodiode signals)
    - Top right: Phase difference and rotation rate
    - Bottom right: Photodiode signals
    
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
            print(f"Creating Ring Laser Gyroscope video with custom layout")
        
        # Check if required data is available
        if 't' not in results:
            raise ValueError(f"Time data not found in results. Available keys: {list(results.keys())}")
        
        # Extract data from results
        t_vals = results['t']
        phase_difference = results['phase_difference']
        theoretical_rotation_rate = results['theoretical_rotation_rate']
        measured_rotation_rate = results['measured_rotation_rate']
        photodiode1 = results['photodiode1']
        photodiode2 = results['photodiode2']
        interference_intensity = results['interference_intensity']
        
        # 3D visualization data
        cavity_vertices = results['cavity_vertices']
        mirror_positions = results['mirror_positions']
        cavity_shape = results['cavity_shape']
        
        # Beam positions for animation
        cw_beam_positions = results['cw_beam_positions']
        ccw_beam_positions = results['ccw_beam_positions']
        
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
        ax_3d = fig.add_subplot(gs[0, 0], projection='3d')
        ax_rates = fig.add_subplot(gs[0, 1])  # Phase difference and rotation rate (top right)
        ax_lissajous = fig.add_subplot(gs[1, 0])  # Lissajous figure (bottom left)
        ax_signals = fig.add_subplot(gs[1, 1])  # Photodiode signals (bottom right)
        
        # Standard tight layout
        fig.tight_layout(pad=3.0)
        
        # Setup for 3D RLG animation (top left)
        # Calculate axis limits
        radius = results['cavity_radius']
        max_dim = radius * 1.5
        
        # Set 3D plot limits
        ax_3d.set_xlim(-max_dim, max_dim)
        ax_3d.set_ylim(-max_dim, max_dim)
        ax_3d.set_zlim(-max_dim, max_dim)
        ax_3d.set_title('Ring Laser Gyroscope')
        ax_3d.set_xlabel('X')
        ax_3d.set_ylabel('Y')
        ax_3d.set_zlabel('Z')
        
        # Setup better viewpoint for 3D
        ax_3d.view_init(elev=30, azim=45)
        
        # Initialize cavity plot
        if cavity_shape == 'circle':
            # For circle, draw a circle patch on the xy plane
            cavity_line, = ax_3d.plot(cavity_vertices[:, 0], cavity_vertices[:, 1], cavity_vertices[:, 2], 'k-', lw=2)
        else:
            # For polygons, close the loop
            vertices_closed = np.vstack([cavity_vertices, cavity_vertices[0]])
            cavity_line, = ax_3d.plot(vertices_closed[:, 0], vertices_closed[:, 1], vertices_closed[:, 2], 'k-', lw=2)
        
        # Initialize mirrors
        mirror_points = []
        for mirror in mirror_positions:
            point, = ax_3d.plot([mirror[0]], [mirror[1]], [mirror[2]], 'o', ms=6, color='silver')
            mirror_points.append(point)
        
        # Initialize rotation axis
        axis_line, = ax_3d.plot([0, 0], [0, 0], [-max_dim, max_dim], 'g--', lw=2, label='Rotation Axis')
        
        # Initialize photodetector
        # Place it at the first mirror position
        pd_pos = mirror_positions[0]
        pd_point, = ax_3d.plot([pd_pos[0]], [pd_pos[1]], [pd_pos[2]], 'D', ms=8, color='purple', label='Photodetector')
        
        # Initialize beams with larger marker size for better visibility
        cw_beam, = ax_3d.plot([], [], [], 'ro', ms=6, label='CW Beam')
        ccw_beam, = ax_3d.plot([], [], [], 'bo', ms=6, label='CCW Beam')
        
        # Set legend for 3D plot
        ax_3d.legend(loc='upper right', fontsize=8)
        
        # Setup for rates plot (top right)
        # Line for phase difference
        phase_line, = ax_rates.plot([], [], 'b-', lw=2, label='Phase Difference (rad)')
        
        # Lines for rotation rates - renamed Theoretical to Actual
        theo_line, = ax_rates.plot([], [], 'g-', lw=2, label='Actual Rate (rad/s)')
        meas_line, = ax_rates.plot([], [], 'r-', lw=2, label='Measured Rate (rad/s)')
        
        # Setup current position indicators
        phase_point, = ax_rates.plot([], [], 'bo', ms=6)
        theo_point, = ax_rates.plot([], [], 'go', ms=6)
        meas_point, = ax_rates.plot([], [], 'ro', ms=6)
        
        # Set up time indicator line
        time_line_rates = ax_rates.axvline(x=0, color='k', linestyle='--', alpha=0.5)
        
        # Setup rates plot
        ax_rates.set_xlim(t_vals[0], t_vals[-1])
        # Calculate y-axis limits with some padding
        max_phase = max(abs(np.max(phase_difference)), abs(np.min(phase_difference)))
        max_rate = max(
            abs(np.max(theoretical_rotation_rate)), 
            abs(np.min(theoretical_rotation_rate)),
            abs(np.max(measured_rotation_rate)),
            abs(np.min(measured_rotation_rate))
        )
        
        # Create two y-axis scales (one for phase, one for rates)
        ax_rates.set_ylabel('Phase Difference (rad)', color='blue')
        ax_rates.tick_params(axis='y', labelcolor='blue')
        
        # Calculate appropriate limits for phase difference with generous padding
        # Add significant padding to ensure values are visible
        phase_padding = max(1.0, max_phase * 0.3)  # At least 1.0 or 30% padding
        ax_rates.set_ylim(-max_phase - phase_padding, max_phase + phase_padding)
        
        ax_rates_twin = ax_rates.twinx()
        ax_rates_twin.set_ylabel('Rotation Rate (rad/s)', color='green')
        ax_rates_twin.tick_params(axis='y', labelcolor='green')
        
        # More generous padding for rotation rates to ensure all content is visible
        rate_padding = max(1.0, max_rate * 0.3)  # At least 1.0 or 30% padding 
        ax_rates_twin.set_ylim(-max_rate - rate_padding, max_rate + rate_padding)
        
        # Create in-plot legend with only relevant labels
        handles = [theo_line, meas_line]
        labels = ['Actual Rate (rad/s)', 'Measured Rate (rad/s)']
        
        # Place legend inside the plot
        ax_rates_twin.legend(handles, labels, loc='upper right', fontsize=9, framealpha=0.8)
        
        # Remove phase difference from legend since it's on a different axis
        ax_rates.get_legend().remove() if ax_rates.get_legend() else None
        
        # Add clear titles
        ax_rates.set_title('Phase Difference & Rotation Rate')
        ax_rates.set_xlabel('Time (s)')
        ax_rates.grid(True)
        
        # Setup for Lissajous figure (bottom left)
        # Create a unit circle for reference
        theta = np.linspace(0, 2*np.pi, 100)
        circle = plt.Circle((0, 0), 1, fill=False, color='gray', linestyle='--', alpha=0.5)
        ax_lissajous.add_patch(circle)
        
        # Lissajous plot (PD1 vs PD2) - increase line width and opacity for better visibility
        lissajous_line, = ax_lissajous.plot([], [], 'purple', lw=2, alpha=0.8)
        lissajous_point, = ax_lissajous.plot([], [], 'ro', ms=10)
        
        # Setup Lissajous plot
        ax_lissajous.set_xlim(-1.2, 1.2)
        ax_lissajous.set_ylim(-1.2, 1.2)
        ax_lissajous.set_title('Lissajous Figure (PD1 vs PD2)')
        ax_lissajous.set_xlabel('PD1 (cos)')
        ax_lissajous.set_ylabel('PD2 (sin)')
        ax_lissajous.grid(True)
        ax_lissajous.set_aspect('equal')
        
        # Add phase difference annotation
        phase_text = ax_lissajous.text(0.05, 0.95, '', transform=ax_lissajous.transAxes, fontsize=10,
                                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Setup for photodiode signals plot (bottom right)
        pd1_line, = ax_signals.plot([], [], 'r-', lw=2, label='PD1 (cos)')
        pd2_line, = ax_signals.plot([], [], 'b-', lw=2, label='PD2 (sin)')
        interference_line, = ax_signals.plot([], [], 'purple', lw=1, alpha=0.5, label='Interference')
        
        # Setup current position indicators
        pd1_point, = ax_signals.plot([], [], 'ro', ms=6)
        pd2_point, = ax_signals.plot([], [], 'bo', ms=6)
        
        # Set up time indicator line
        time_line_signals = ax_signals.axvline(x=0, color='k', linestyle='--', alpha=0.5)
        
        # Setup signals plot
        ax_signals.set_xlim(t_vals[0], t_vals[-1])
        ax_signals.set_ylim(-1.2, 2.5)  # Range covers photodiode signals [-1,1] and interference [0,2] with extra padding
        ax_signals.set_title('Photodiode Signals')
        ax_signals.set_xlabel('Time (s)')
        ax_signals.set_ylabel('Signal Amplitude')
        ax_signals.grid(True)
        ax_signals.legend(loc='upper right', fontsize=8)
        
        # Add time text in its original position
        time_text = fig.text(0.5, 0.01, '', ha='center', fontsize=10)
        
        # Function to update the plots for each frame
        def update(frame_idx):
            i = indices[frame_idx]
            
            # Update time text
            time_text.set_text(f'Time: {t_vals[i]:.3f}s')
            
            # 1. Update 3D RLG visualization
            # Add rotation to make motion more visible
            angle = frame_idx * results['rotation_rate'] * 0.1  # Faster rotation for visibility
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)
            
            # Rotate cavity vertices for visualization
            original_vertices = results['cavity_vertices']
            rotated_vertices = np.zeros_like(original_vertices)
            for i_vertex, vertex in enumerate(original_vertices):
                rotated_vertices[i_vertex, 0] = vertex[0] * cos_a - vertex[1] * sin_a
                rotated_vertices[i_vertex, 1] = vertex[0] * sin_a + vertex[1] * cos_a
                rotated_vertices[i_vertex, 2] = vertex[2]
            
            # Update cavity outline
            if cavity_shape == 'circle':
                vertices_closed = np.vstack([rotated_vertices, rotated_vertices[0]])
            else:
                vertices_closed = np.vstack([rotated_vertices, rotated_vertices[0]])
                
            cavity_line.set_data(vertices_closed[:, 0], vertices_closed[:, 1])
            cavity_line.set_3d_properties(vertices_closed[:, 2])
            
            # Update mirrors
            for i_mirror, mirror_point in enumerate(mirror_points):
                original_mirror = mirror_positions[i_mirror]
                rotated_mirror_x = original_mirror[0] * cos_a - original_mirror[1] * sin_a
                rotated_mirror_y = original_mirror[0] * sin_a + original_mirror[1] * cos_a
                rotated_mirror_z = original_mirror[2]
                
                mirror_point.set_data([rotated_mirror_x], [rotated_mirror_y])
                mirror_point.set_3d_properties([rotated_mirror_z])
                
            # Rotate photodetector too
            original_pd = mirror_positions[0]
            rotated_pd_x = original_pd[0] * cos_a - original_pd[1] * sin_a
            rotated_pd_y = original_pd[0] * sin_a + original_pd[1] * cos_a
            rotated_pd_z = original_pd[2]
            pd_point.set_data([rotated_pd_x], [rotated_pd_y])
            pd_point.set_3d_properties([rotated_pd_z])
            
            # Update clockwise beam
            cw_pos = cw_beam_positions[i]
            # Apply rotation to beam positions for visualization
            rotated_cw_pos = np.zeros_like(cw_pos)
            for j, pos in enumerate(cw_pos):
                rotated_cw_pos[j, 0] = pos[0] * cos_a - pos[1] * sin_a
                rotated_cw_pos[j, 1] = pos[0] * sin_a + pos[1] * cos_a
                rotated_cw_pos[j, 2] = pos[2]
                
            cw_beam.set_data(rotated_cw_pos[:, 0], rotated_cw_pos[:, 1])
            cw_beam.set_3d_properties(rotated_cw_pos[:, 2])
            
            # Update counter-clockwise beam
            ccw_pos = ccw_beam_positions[i]
            # Apply rotation to beam positions for visualization
            rotated_ccw_pos = np.zeros_like(ccw_pos)
            for j, pos in enumerate(ccw_pos):
                rotated_ccw_pos[j, 0] = pos[0] * cos_a - pos[1] * sin_a
                rotated_ccw_pos[j, 1] = pos[0] * sin_a + pos[1] * cos_a
                rotated_ccw_pos[j, 2] = pos[2]
                
            ccw_beam.set_data(rotated_ccw_pos[:, 0], rotated_ccw_pos[:, 1])
            ccw_beam.set_3d_properties(rotated_ccw_pos[:, 2])
            
            # 2. Update phase & rotation rate plots
            # Calculate the indices to show up to the current frame
            visible_indices = indices[:frame_idx+1]
            visible_t = t_vals[visible_indices]
            
            # Update phase difference line
            visible_phase = phase_difference[visible_indices]
            phase_line.set_data(visible_t, visible_phase)
            phase_point.set_data([t_vals[i]], [phase_difference[i]])
            
            # Update actual rotation rate line
            visible_theo = theoretical_rotation_rate[visible_indices]
            theo_line.set_data(visible_t, visible_theo)
            theo_point.set_data([t_vals[i]], [theoretical_rotation_rate[i]])
            
            # Update measured rotation rate line
            visible_meas = measured_rotation_rate[visible_indices]
            meas_line.set_data(visible_t, visible_meas)
            meas_point.set_data([t_vals[i]], [measured_rotation_rate[i]])
            
            # Update time indicator
            time_line_rates.set_xdata([t_vals[i], t_vals[i]])
            
            # 3. Update Lissajous figure
            # Calculate points for the Lissajous figure
            pd1_all = photodiode1[visible_indices]
            pd2_all = photodiode2[visible_indices]
            lissajous_line.set_data(pd1_all, pd2_all)
            lissajous_point.set_data([photodiode1[i]], [photodiode2[i]])
            
            # Add a trail for the Lissajous figure
            trail_length = 20
            if frame_idx >= trail_length:
                # Get recent photodiode signals to form a visible trail
                trail_indices = [indices[max(0, frame_idx-k)] for k in range(trail_length)]
                pd1_trail = [photodiode1[idx] for idx in trail_indices]
                pd2_trail = [photodiode2[idx] for idx in trail_indices]
                
                # Create a Lissajous trail line if it doesn't exist yet
                if not hasattr(update, 'lissajous_trail_created'):
                    update.lissajous_trail, = ax_lissajous.plot(pd1_trail, pd2_trail, '-', 
                                                              color='purple', linewidth=3, alpha=1.0)
                    update.lissajous_trail_created = True
                else:
                    update.lissajous_trail.set_data(pd1_trail, pd2_trail)
            
            # Update phase text
            phase_text.set_text(f'Phase: {phase_difference[i]:.2f} rad')
            
            # 4. Update photodiode signals plot
            pd1_line.set_data(visible_t, pd1_all)
            pd2_line.set_data(visible_t, pd2_all)
            
            # Update interference intensity
            visible_interf = interference_intensity[visible_indices]
            interference_line.set_data(visible_t, visible_interf)
            
            # Update current point indicators
            pd1_point.set_data([t_vals[i]], [photodiode1[i]])
            pd2_point.set_data([t_vals[i]], [photodiode2[i]])
            
            # Update time indicator
            time_line_signals.set_xdata([t_vals[i], t_vals[i]])
            
            # Return all artists that were updated
            return (cw_beam, ccw_beam, phase_line, theo_line, meas_line, 
                    phase_point, theo_point, meas_point, lissajous_line, lissajous_point,
                    pd1_line, pd2_line, interference_line, pd1_point, pd2_point,
                    time_line_rates, time_line_signals, time_text, phase_text)
        
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
                metadata=dict(title='Ring Laser Gyroscope Animation'),
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
                metadata=dict(title='Ring Laser Gyroscope Animation'),
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
