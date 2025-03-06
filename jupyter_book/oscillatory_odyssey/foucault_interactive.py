"""Interactive Foucault pendulum simulation interface with dynamic visualization."""

import os
import numpy as np
from IPython.display import display
import ipywidgets as widgets
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .foucault import FoucaultPendulum
from .animation import AnimationController
from .video_saver import save_animation_as_video
from .foucault_video_saver import save_foucault_video
import importlib.util

# Try to import the debug module if available
try:
    from .foucault_debug import save_debug_information
    DEBUG_MODULE_AVAILABLE = True
except ImportError:
    DEBUG_MODULE_AVAILABLE = False

class InteractiveFoucaultPendulum:
    """Interactive interface for Foucault pendulum simulation visualization."""
    
    def __init__(self):
        """Initialize the interactive Foucault pendulum interface."""
        self.pendulum = FoucaultPendulum()
        self.setup_interface()
        
    def setup_interface(self):
        """Set up the interactive interface components."""
        # Create widgets and buttons
        self.controls = self.create_parameter_widgets()
        self.buttons = self.create_control_buttons()
        
        # Set up button callbacks
        self.buttons['simulate'].on_click(self.update_simulation)
        self.buttons['play'].on_click(self.toggle_animation)
        self.buttons['reset'].on_click(self.reset_animation)
        self.buttons['save'].on_click(self.save_animation)
        
        # Set up parameter callbacks
        self.controls['L'].observe(self.update_natural_frequency, names='value')
        self.controls['latitude'].observe(self.update_precession_rate, names='value')
        self.controls['rotation_demo_factor'].observe(self.update_precession_rate, names='value')
        self.controls['animation_speed'].observe(self.update_animation_speed, names='value')
        
        # Create output area
        self.output = widgets.Output()
        
        # Set up animation controller
        self.animation = AnimationController(self.update_frame)
        
        # Initialize information displays
        self.update_natural_frequency()
        self.update_precession_rate()
        
    def create_parameter_widgets(self):
        """Create all parameter control widgets."""
        controls = {}
        
        # Initial conditions
        controls['theta0'] = widgets.FloatSlider(
            value=0.1,
            min=0.0,
            max=np.pi/2,
            step=0.01,
            description='Initial amplitude (rad)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        controls['phi0'] = widgets.FloatSlider(
            value=0.0,
            min=-np.pi,
            max=np.pi,
            step=0.1,
            description='Initial direction (rad)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        # System parameters
        controls['L'] = widgets.FloatSlider(
            value=10.0,
            min=1.0,
            max=20.0,
            step=0.5,
            description='Length (m)',
            continuous_update=False
        )
        
        controls['damping'] = widgets.FloatSlider(
            value=0.05,
            min=0.0,
            max=0.2,
            step=0.01,
            description='Damping',
            continuous_update=False
        )
        
        controls['latitude'] = widgets.FloatSlider(
            value=45.0,
            min=0.0,
            max=90.0,
            step=5.0,
            description='Latitude (°)',
            continuous_update=False
        )
        
        controls['rotation_demo_factor'] = widgets.FloatLogSlider(
            value=100,
            base=10,
            min=1,  # 10^1
            max=4,  # 10^4
            step=0.1,
            description='Demo speed factor',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        # No pendulum type selection - removed
        
        # Advanced parameters
        controls['quadrature'] = widgets.FloatSlider(
            value=0.0,
            min=0.0,
            max=5.0,
            step=0.2,
            description='Frequency split (Hz)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        controls['isotropy_defect'] = widgets.FloatSlider(
            value=0.0,
            min=0.0,
            max=3.0,
            step=0.1,
            description='Isotropy defect (%)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        controls['principal_axes_angle'] = widgets.FloatSlider(
            value=0.0,
            min=0.0,
            max=90.0,
            step=5.0,
            description='Principal axes angle (°)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        controls['use_charron_ring'] = widgets.Checkbox(
            value=False,
            description='Use Charron ring',
            style={'description_width': 'initial'}
        )
        
        controls['onnes_correction'] = widgets.Checkbox(
            value=False,
            description='Kamerlingh Onnes correction',
            style={'description_width': 'initial'}
        )
        
        # Simulation controls
        controls['T'] = widgets.FloatSlider(
            value=100.0,
            min=50.0,
            max=300.0,
            step=10.0,
            description='Sim time (s)',
            continuous_update=False
        )
        
        controls['dt'] = widgets.FloatSlider(
            value=0.05,
            min=0.01,
            max=0.1,
            step=0.01,
            description='Time step (s)',
            continuous_update=False
        )
        
        controls['animation_speed'] = widgets.FloatSlider(
            value=1.0,
            min=0.1,
            max=3.0,
            step=0.1,
            description='Animation speed',
            continuous_update=False
        )
        
        # Information displays
        controls['natural_frequency'] = widgets.HTML(
            value='Loading...',
            description='Natural frequency:',
            style={'description_width': 'initial'}
        )
        
        controls['precession_rate'] = widgets.HTML(
            value='Loading...',
            description='Precession rate:',
            style={'description_width': 'initial'}
        )
        
        return controls
    
    def create_control_buttons(self):
        """Create simulation control buttons."""
        buttons = {}
        
        buttons['simulate'] = widgets.Button(description='Simulate')
        buttons['play'] = widgets.Button(description='Play')
        buttons['reset'] = widgets.Button(description='Reset')
        buttons['save'] = widgets.Button(description='Save Video')
        
        return buttons
    
    def create_control_panel(self):
        """Create the main control panel layout."""
        # Basic parameters tab
        basic_tab = widgets.VBox([
            widgets.HBox([self.controls['theta0'], self.controls['phi0']]),
            widgets.HBox([self.controls['L'], self.controls['damping']]),
            widgets.HBox([self.controls['latitude'], self.controls['rotation_demo_factor']]),
            widgets.HBox([self.controls['natural_frequency'], self.controls['precession_rate']])
        ])
        
        # Advanced parameters tab
        advanced_tab = widgets.VBox([
            widgets.HBox([self.controls['quadrature'], self.controls['isotropy_defect']]),
            widgets.HBox([self.controls['principal_axes_angle']]),
            widgets.HBox([self.controls['use_charron_ring'], self.controls['onnes_correction']]),
            widgets.HBox([self.controls['T'], self.controls['dt']]),
            widgets.HBox([self.controls['animation_speed']])
        ])
        
        # Tab layout
        tab = widgets.Tab()
        tab.children = [basic_tab, advanced_tab]
        tab.set_title(0, 'Basic Settings')
        tab.set_title(1, 'Advanced Settings')
        
        # Button controls
        button_controls = widgets.HBox([
            self.buttons['simulate'],
            self.buttons['play'],
            self.buttons['reset'],
            self.buttons['save']
        ])
        
        return widgets.VBox([tab, button_controls])
        
    def update_natural_frequency(self, change=None):
        """Update natural frequency information display."""
        L = self.controls['L'].value
        g = self.pendulum.params['g']
        
        # Natural frequency in Hz
        freq = np.sqrt(g/L) / (2 * np.pi)
        period = 1 / freq
        
        self.controls['natural_frequency'].value = (
            f"<b>{freq:.3f} Hz</b><br>"
            f"Period: {period:.3f} s"
        )
            
    def update_precession_rate(self, change=None):
        """Update precession rate information display."""
        # Update pendulum parameters from controls
        self.pendulum.params['latitude'] = self.controls['latitude'].value
        self.pendulum.params['rotation_demo_factor'] = self.controls['rotation_demo_factor'].value
        
        # Calculate visualization rate (with demo factor)
        rate_rad_per_s = self.pendulum.calculate_effective_rotation_rate() 
        rate_deg_per_s = rate_rad_per_s * 180 / np.pi
        
        # Calculate real Earth rate (without demo factor)
        real_rate_rad_per_s = self.pendulum.calculate_real_rotation_rate()
            
        # Convert to degrees per hour
        real_rate_deg_per_h = real_rate_rad_per_s * 180 / np.pi * 3600
        
        # Calculate time for full rotation (360°)
        full_rotation_hours = 360 / real_rate_deg_per_h if real_rate_deg_per_h > 0 else float('inf')
        
        # Update display with formatted values
        self.controls['precession_rate'].value = (
            f"<b>{rate_deg_per_s:.5f}°/s</b> (in simulation)<br>"
            f"Real Earth: {real_rate_deg_per_h:.3f}°/hr<br>"
            f"Full rotation: {full_rotation_hours:.1f} hours"
        )
            
    def update_animation_speed(self, change):
        """Update animation speed."""
        self.animation.set_speed(change['new'])
        
    def update_frame(self, frame):
        """Update animation frame."""
        if hasattr(self, 'results') and hasattr(self, 'anim_fig') and hasattr(self, 'plots_fig'):
            self.update_animation_frame(self.anim_fig, self.plots_fig, self.results, frame)
            
    def toggle_animation(self, _=None):
        """Toggle animation play/pause."""
        if not hasattr(self, 'results'):
            return
            
        if self.animation.running:
            self.animation.stop()
            self.buttons['play'].description = 'Play'
        else:
            self.animation.start(len(self.results['t']))
            self.buttons['play'].description = 'Pause'
    
    def reset_animation(self, _=None):
        """Reset animation to initial frame and controls to defaults."""
        if hasattr(self, 'results'):
            # Reset animation
            self.animation.reset()
            self.buttons['play'].description = 'Play'
            
            # Clear acceleration history
            if hasattr(self, 'acc_history_x'):
                self.acc_history_x = []
                self.acc_history_y = []
                self.acc_history_z = []
            
            # Reset control values to defaults
            default_pendulum = FoucaultPendulum()
            
            # Reset parameters to the specific requested values
            default_values = {
                'theta0': 0.1,
                'phi0': 0.0,
                'L': 10.0,
                'damping': 0.05,
                'latitude': 45.0,
                'rotation_demo_factor': 100,
                'quadrature': 0.0,
                'isotropy_defect': 0.0,
                'principal_axes_angle': 0.0,
                'use_charron_ring': False,
                'onnes_correction': False,
                'T': 100.0,
                'dt': 0.05,
                'animation_speed': 1.0
            }
            
            for param, value in default_values.items():
                if param in self.controls:
                    self.controls[param].value = value
            
            # Update UI after reset
            self.update_natural_frequency()
            self.update_precession_rate()
            
    def save_animation(self, _=None):
        """Save animation as video file."""
        if hasattr(self, 'results'):
            # Stop animation if running
            if self.animation.running:
                self.toggle_animation()
            
            # Reset to start
            self.animation.reset()
            
            # Create output path
            output_path = "foucault_pendulum_animation.mp4"
            
            # Clear output and show status within output area
            self.output.clear_output(wait=True)
            
            # Save as video and display result in output area
            with self.output:
                # Create a dedicated HTML widget for save status
                save_status = widgets.HTML('Starting video save process...')
                display(save_status)
                
                # Save the animation using our custom Foucault video saver
                try:
                    result = save_foucault_video(self.anim_fig, self.results, output_path)
                    display(result)
                except Exception as e:
                    save_status.value = f"<div style='color: red; font-weight: bold;'>Error saving video:</div><div>{str(e)}</div>"
                    
                    # Redisplay the figures
                    self.display_figures()
    
    def create_animation_figure(self, results):
        """Create Plotly figure for pendulum animation."""
        # Create a 3D figure for the pendulum
        fig = go.FigureWidget()
        
        # Add pendulum rod trace
        fig.add_trace(
            go.Scatter3d(
                x=[0, results['bob_x'][0]], 
                y=[0, results['bob_y'][0]],
                z=[0, results['bob_z'][0]],
                mode='lines',
                line=dict(color='gray', width=6),
                name='Rod',
                showlegend=False
            )
        )
        
        # Add pendulum bob trace
        fig.add_trace(
            go.Scatter3d(
                x=[results['bob_x'][0]],
                y=[results['bob_y'][0]],
                z=[results['bob_z'][0]],
                mode='markers',
                marker=dict(size=10, color='red'),
                name='Bob',
                showlegend=False
            )
        )
        
        # Add line trace to show oscillation plane
        # First, calculate a circle in the xy plane
        theta_circle = np.linspace(0, 2*np.pi, 100)
        r = self.params["L"] * np.sin(results['theta'][0])
        x_circle = r * np.cos(theta_circle)
        y_circle = r * np.sin(theta_circle)
        z_circle = np.zeros_like(x_circle)
        
        # Then, rotate the circle according to the current oscillation direction
        phi = results['phi'][0]
        x_plane = x_circle * np.cos(phi) - y_circle * np.sin(phi)
        y_plane = x_circle * np.sin(phi) + y_circle * np.cos(phi)
        
        fig.add_trace(
            go.Scatter3d(
                x=x_plane,
                y=y_plane,
                z=z_circle,
                mode='lines',
                line=dict(color='blue', width=2, dash='dash'),
                name='Oscillation Plane',
                showlegend=False,
                opacity=0.7
            )
        )
        
        # Add reference frame axes
        axis_length = self.params["L"] * 1.2
        
        # X-axis (red)
        fig.add_trace(
            go.Scatter3d(
                x=[0, axis_length],
                y=[0, 0],
                z=[0, 0],
                mode='lines',
                line=dict(color='red', width=2),
                name='X-axis',
                showlegend=False
            )
        )
        
        # Y-axis (green)
        fig.add_trace(
            go.Scatter3d(
                x=[0, 0],
                y=[0, axis_length],
                z=[0, 0],
                mode='lines',
                line=dict(color='green', width=2),
                name='Y-axis',
                showlegend=False
            )
        )
        
        # Z-axis (blue)
        fig.add_trace(
            go.Scatter3d(
                x=[0, 0],
                y=[0, 0],
                z=[0, axis_length],
                mode='lines',
                line=dict(color='blue', width=2),
                name='Z-axis',
                showlegend=False
            )
        )
        
        # Add a trace for pendulum path history - full history from start to end
        fig.add_trace(
            go.Scatter3d(
                x=results['bob_x'],
                y=results['bob_y'],
                z=results['bob_z'],
                mode='lines',
                line=dict(color='rgba(200, 0, 0, 0.5)', width=4),
                name='Path',
                showlegend=False
            )
        )
        
        # Add trace for projected path on xy-plane (shadow) - full history
        fig.add_trace(
            go.Scatter3d(
                x=results['bob_x'],
                y=results['bob_y'],
                z=np.full(len(results['t']), -axis_length),  # Place at the bottom of the view
                mode='lines',
                line=dict(color='rgba(50, 50, 50, 0.8)', width=5),  # Darker, wider line
                name='Ground Trace',
                showlegend=False
            )
        )
        
        # Update layout
        fig.update_layout(
            title='Foucault Pendulum Animation',
            height=500,
            scene=dict(
                xaxis=dict(range=[-axis_length, axis_length], title='X'),
                yaxis=dict(range=[-axis_length, axis_length], title='Y'),
                zaxis=dict(range=[-axis_length, 0.2*axis_length], title='Z'),
                aspectmode='cube'
            ),
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(x=0, y=1)
        )
        
        return fig

    def create_plots_figure(self, results):
        """Create Plotly figure for time series plots."""
        fig = go.FigureWidget(make_subplots(rows=2, cols=2,
                        subplot_titles=('Amplitude vs Time', 'Angle vs Time',
                                        'Phase Space (x-y projection)', 'Energy')))
        
        t = results['t']
        
        # Add amplitude plot
        fig.add_trace(
            go.Scatter(x=t, y=results['theta'],
                      name='Amplitude', line=dict(color='blue', dash='solid')),
            row=1, col=1
        )
        
        # Add ellipticity evolution annotation in the first subplot
        ellipticity = results.get('ellipticity', 0)
        measured_defect = results.get('measured_isotropy_defect', 0)
        defect_text = f"Ellipticity: {ellipticity:.3f}<br>Measured defect: {measured_defect:.1f}%"
        
        fig.add_annotation(
            x=0.05, y=0.95,
            xref="paper", yref="paper",
            xanchor="left", yanchor="top",
            text=defect_text,
            showarrow=False,
            bgcolor="white",
            opacity=0.8,
            bordercolor="black",
            borderwidth=1
        )
        
        # Add angle vs time plot - use modular representation for clearer visualization
        phi_deg_modular = np.degrees(np.mod(results['phi_unwrapped'] + np.pi, 2*np.pi) - np.pi)  # Keep between -180 and 180
        fig.add_trace(
            go.Scatter(x=results['t'], y=phi_deg_modular,
                      name='Angle (deg)', mode='lines',
                      line=dict(color='green', dash='solid')),
            row=1, col=2
        )
        
        # Add current state marker to angle vs time plot
        current_phi_deg = phi_deg_modular[0]
        fig.add_trace(
            go.Scatter(x=[results['t'][0]], y=[current_phi_deg],
                      mode='markers',
                      marker=dict(size=10, color='red', symbol='circle'),
                      name='Current Angle',
                      showlegend=False),
            row=1, col=2
        )
        
        # No specific range for time axis needed - let it auto-scale
        # For angle axis, include some buffer space
        max_phi = np.max(np.degrees(results['phi_unwrapped']))
        min_phi = np.min(np.degrees(results['phi_unwrapped']))
        phi_buffer = (max_phi - min_phi) * 0.1  # 10% buffer
        
        # Set y-axis range with buffer
        fig.update_yaxes(range=[min_phi - phi_buffer, max_phi + phi_buffer], row=1, col=2)
        
        # Removed the measured/expected annotation
        
        # Add complete trace for the phase space plot to show how it evolves
        fig.add_trace(
            go.Scatter(x=results['x'], y=results['y'],
                      name='Phase Space Full', mode='lines',
                      line=dict(color='purple', width=2, dash='solid'),
                      opacity=0.7),
            row=2, col=1
        )
        
        # Current state marker on phase space plot
        fig.add_trace(
            go.Scatter(x=[results['x'][0]], y=[results['y'][0]],
                      mode='markers',
                      marker=dict(size=10, color='red', symbol='star'),
                      name='Current State'),
            row=2, col=1
        )
        
        # Add detected principal axes if available
        if 'major_axis_angle' in results and 'ellipticity' in results:
            angle_rad = np.radians(results['major_axis_angle'])
            max_radius = max(np.max(np.abs(results['x'])), np.max(np.abs(results['y'])))
            if max_radius > 0:
                # Major axis line
                x_major = [-max_radius * np.cos(angle_rad), max_radius * np.cos(angle_rad)]
                y_major = [-max_radius * np.sin(angle_rad), max_radius * np.sin(angle_rad)]
                
                # Minor axis line (perpendicular to major)
                minor_angle = angle_rad + np.pi/2
                minor_length = max_radius * results['ellipticity'] 
                x_minor = [-minor_length * np.cos(minor_angle), minor_length * np.cos(minor_angle)]
                y_minor = [-minor_length * np.sin(minor_angle), minor_length * np.sin(minor_angle)]
                
                # Add major axis
                fig.add_trace(
                    go.Scatter(x=x_major, y=y_major,
                              mode='lines',
                              line=dict(color='red', width=1, dash='dash'),
                              name='Major Axis',
                              showlegend=False),
                    row=2, col=1
                )
                
                # Add minor axis
                fig.add_trace(
                    go.Scatter(x=x_minor, y=y_minor,
                              mode='lines',
                              line=dict(color='green', width=1, dash='dash'),
                              name='Minor Axis',
                              showlegend=False),
                    row=2, col=1
                )
        
        # Add energy plots
        fig.add_trace(
            go.Scatter(x=t, y=results['kinetic_energy'],
                      name='Kinetic', line=dict(color='green')),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(x=t, y=results['potential_energy'],
                      name='Potential', line=dict(color='orange')),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(x=t, y=results['total_energy'],
                      name='Total', line=dict(color='black')),
            row=2, col=2
        )
        
        # Add vertical line shapes for time indicators
        shapes = []
        
        # Add time indicator line for amplitude plot (top left)
        shapes.append(dict(
            type='line',
            x0=0, x1=0,
            y0=min(results['theta']), y1=max(results['theta']),
            xref='x1', yref='y1',
            line=dict(color='red', width=2, dash='dot')
        ))
        
        # No time indicator line for the angular velocity vs angle plot as it's not time-based
        
        # Add time indicator line for energy plot (bottom right)
        shapes.append(dict(
            type='line',
            x0=0, x1=0,
            y0=0, y1=max(results['total_energy']),
            xref='x4', yref='y4',
            line=dict(color='red', width=2, dash='dot')
        ))
        
        # Update layout
        fig.update_layout(
            height=700,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=10)
            ),
            margin=dict(l=20, r=20, t=40, b=20),
            shapes=shapes
        )
        
        # Add subplot labels
        fig.update_xaxes(title_text='Time (s)', row=1, col=1)
        fig.update_xaxes(title_text='Time (s)', row=1, col=2)
        fig.update_xaxes(title_text='X-angle', row=2, col=1)
        fig.update_xaxes(title_text='Time (s)', row=2, col=2)
        
        fig.update_yaxes(title_text='Amplitude θ (rad)', row=1, col=1)
        fig.update_xaxes(title_text='Time (s)', row=1, col=2)
        fig.update_yaxes(title_text='Angle φ (deg)', row=1, col=2)
        fig.update_yaxes(title_text='Y-angle', row=2, col=1)
        fig.update_yaxes(title_text='Energy (J)', row=2, col=2)
        
        return fig

    def update_animation_frame(self, fig_anim, fig_plots, results, frame):
        """Update animation and plot figures to current frame."""
        # Get current time and demo factor
        current_t = results['t'][frame]
        demo_factor = self.params["rotation_demo_factor"]
        
        # Calculate effective rotation for enhanced visualization of oscillation plane only
        # Get real precession rate (in radians/sec)
        if 'real_precession_rate' in results:
            real_precession_rate = results['real_precession_rate'] * np.pi / 180  # Convert from deg/s to rad/s
        else:
            # Calculate it from the pendulum parameters
            latitude_rad = np.radians(self.pendulum.params["latitude"])
            rotation_rate = self.pendulum.params["rotation_rate"]
            if self.pendulum.params.get("pendulum_type", "foucault") == "spherical_oscillator":
                real_precession_rate = rotation_rate * np.sin(latitude_rad) / 2
            else:
                real_precession_rate = rotation_rate * np.sin(latitude_rad)
        
        # Calculate elapsed time
        elapsed_time = current_t - results['t'][0]
        
        # Apply visualization update to 3D animation
        with fig_anim.batch_update():
            # Get the base phi from the physics simulation
            base_phi = results['phi'][frame]
            
            # Get original bob position from simulation (with minimal physical precession)
            bob_x = results['bob_x'][frame]
            bob_y = results['bob_y'][frame]
            bob_z = results['bob_z'][frame]
            
            # Use original position without enhancement to preserve physics
            # Update pendulum rod with original position
            fig_anim.data[0].x = [0, bob_x]
            fig_anim.data[0].y = [0, bob_y]
            fig_anim.data[0].z = [0, bob_z]
            
            # Update pendulum bob with original position
            fig_anim.data[1].x = [bob_x]
            fig_anim.data[1].y = [bob_y]
            fig_anim.data[1].z = [bob_z]
            
            # Update oscillation plane - only enhance the plane visualization (not the physics)
            theta_circle = np.linspace(0, 2*np.pi, 100)
            r = self.params["L"] * np.sin(results['theta'][frame])
            x_circle = r * np.cos(theta_circle)
            y_circle = r * np.sin(theta_circle)
            z_circle = np.zeros_like(x_circle)
            
            # Calculate enhanced phi for visualization ONLY
            additional_rotation = real_precession_rate * (demo_factor - 1) * elapsed_time
            enhanced_phi = base_phi + additional_rotation
            
            # Rotate the plane based on enhanced phi - this shows the precession visually
            # without affecting the actual pendulum physics
            x_plane = x_circle * np.cos(enhanced_phi) - y_circle * np.sin(enhanced_phi)
            y_plane = x_circle * np.sin(enhanced_phi) + y_circle * np.cos(enhanced_phi)
            
            fig_anim.data[2].x = x_plane
            fig_anim.data[2].y = y_plane
            fig_anim.data[2].z = z_circle
            
            # Store original bob positions for history (preserve physics)
            if not hasattr(self, 'acc_history_x'):
                self.acc_history_x = []
                self.acc_history_y = []
                self.acc_history_z = []
            
            # Add current position to history (original coordinates)
            if frame >= len(self.acc_history_x):
                self.acc_history_x.append(bob_x)
                self.acc_history_y.append(bob_y)
                self.acc_history_z.append(bob_z)
            
            # Update path history with simulation positions - keep full history
            if len(self.acc_history_x) > 0:
                # Update with all history points
                fig_anim.data[6].x = self.acc_history_x
                fig_anim.data[6].y = self.acc_history_y
                fig_anim.data[6].z = self.acc_history_z
                
                # Update shadow with all positions
                fig_anim.data[7].x = self.acc_history_x
                fig_anim.data[7].y = self.acc_history_y
                fig_anim.data[7].z = np.full(len(self.acc_history_x), -self.params["L"] * 1.2)
        
        with fig_plots.batch_update():
            # Update time indicators
            current_t = results['t'][frame]
            # Update time indicators for all three plots with time axes
            for i, shape in enumerate(fig_plots.layout.shapes):
                shape.x0 = current_t
                shape.x1 = current_t
                
            # Update current state marker in phase space plot
            # The current state marker is the 5th trace (index 4) in our revised layout
            try:
                # Set current state marker to current position in phase space plot
                fig_plots.data[4].x = [results['x'][frame]]
                fig_plots.data[4].y = [results['y'][frame]]
                
                # Update marker in angle vs time plot - use modular angle
                current_phi_deg = np.degrees(np.mod(results['phi_unwrapped'][frame] + np.pi, 2*np.pi) - np.pi)
                fig_plots.data[2].x = [results['t'][frame]]
                fig_plots.data[2].y = [current_phi_deg]
            except Exception as e:
                print(f"Error updating phase space marker: {e} - Trace count: {len(fig_plots.data)}")
            
    def update_simulation(self, _=None):
        """Update simulation with current widget values."""
        # Update pendulum parameters
        for param, widget in self.controls.items():
            if param in ['natural_frequency', 'precession_rate', 'animation_speed']:
                continue
            self.pendulum.params[param] = widget.value
            
        # Store parameters for the animation
        self.params = self.pendulum.params.copy()
        
        # Clear acceleration history when starting a new simulation
        if hasattr(self, 'acc_history_x'):
            self.acc_history_x = []
            self.acc_history_y = []
            self.acc_history_z = []
        
        # Stop any running animation
        if self.animation.running:
            self.toggle_animation()
            
        # Run simulation
        self.results = self.pendulum.simulate()
        
        # Save debug info if available (silently)
        try:
            debug_folder = "debug_output"
            if not os.path.exists(debug_folder):
                os.makedirs(debug_folder)
            
            if DEBUG_MODULE_AVAILABLE:
                # Silently save debug information without printing
                save_debug_information(self.pendulum, self.results, debug_folder)
        except Exception:
            # Silently handle any errors
            pass
        
        # Create new figures
        self.anim_fig = self.create_animation_figure(self.results)
        self.plots_fig = self.create_plots_figure(self.results)
        
        # Reset animation state
        self.animation.reset()
        
        # Clear output and redisplay
        self.output.clear_output(wait=True)
        with self.output:
            self.display_figures()
            
    def display_figures(self):
        """Display the figures."""
        display(self.anim_fig)
        display(self.plots_fig)
    
    def display(self):
        """Display the interactive interface."""
        # Create control panel
        control_panel = self.create_control_panel()
        
        # Display interface
        display(control_panel)
        display(self.output)
        
        # Run initial simulation
        if not hasattr(self, 'results'):
            self.update_simulation()

def create_interactive_foucault_pendulum():
    """Create and display an interactive Foucault pendulum simulation."""
    sim = InteractiveFoucaultPendulum()
    sim.display()
    return sim