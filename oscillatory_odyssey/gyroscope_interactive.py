"""Interactive gyroscope simulation interface with dynamic visualization."""

import os
import numpy as np
from IPython.display import display
import ipywidgets as widgets
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .gyroscope import GyroscopeSimulation
from .animation import AnimationController
from .gyroscope_video_saver import save_gyroscope_video


class InteractiveGyroscope:
    """Interactive interface for gyroscope simulation visualization."""
    
    def __init__(self):
        """Initialize the interactive gyroscope interface."""
        self.gyroscope = GyroscopeSimulation()
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
        self.controls['wheel_radius'].observe(self.update_inertia_display, names='value')
        self.controls['wheel_mass'].observe(self.update_inertia_display, names='value')
        self.controls['wheel_thickness'].observe(self.update_inertia_display, names='value')
        self.controls['moment_of_inertia_type'].observe(self.update_inertia_display, names='value')
        self.controls['initial_spin_rate'].observe(self.update_precession_rate, names='value')
        self.controls['animation_speed'].observe(self.update_animation_speed, names='value')
        
        # Create output area
        self.output = widgets.Output()
        
        # Set up animation controller
        self.animation = AnimationController(self.update_frame)
        
        # Initialize information displays
        self.update_inertia_display()
        self.update_precession_rate()
        
    def create_parameter_widgets(self):
        """Create all parameter control widgets."""
        controls = {}
        
        # Wheel properties
        controls['wheel_radius'] = widgets.FloatSlider(
            value=0.3,
            min=0.1,
            max=0.5,
            step=0.02,
            description='Wheel radius (m)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        controls['wheel_mass'] = widgets.FloatSlider(
            value=1.0,
            min=0.1,
            max=5.0,
            step=0.1,
            description='Wheel mass (kg)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        controls['wheel_thickness'] = widgets.FloatSlider(
            value=0.05,
            min=0.01,
            max=0.2,
            step=0.01,
            description='Wheel thickness (m)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        # Rod properties
        controls['rod_length'] = widgets.FloatSlider(
            value=0.5,
            min=0.2,
            max=1.0,
            step=0.05,
            description='Rod length (m)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        controls['rod_mass'] = widgets.FloatSlider(
            value=0.2,
            min=0.05,
            max=1.0,
            step=0.05,
            description='Rod mass (kg)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        # Rotation properties
        controls['initial_spin_rate'] = widgets.FloatLogSlider(
            value=20.0,
            base=10,
            min=0.0,  # 10^0 = 1
            max=2.0,  # 10^2 = 100
            step=0.1,
            description='Spin rate (rad/s)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        controls['theta0'] = widgets.FloatSlider(
            value=0.3,
            min=0.0,
            max=np.pi/2,
            step=0.05,
            description='Initial tilt (rad)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        controls['phi0'] = widgets.FloatSlider(
            value=0.0,
            min=-np.pi,
            max=np.pi,
            step=0.1,
            description='Initial azimuth (rad)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        # Physical properties
        controls['damping'] = widgets.FloatSlider(
            value=0.05,
            min=0.0,
            max=0.3,
            step=0.01,
            description='Damping',
            continuous_update=False
        )
        
        controls['g'] = widgets.FloatSlider(
            value=9.81,
            min=0.0,
            max=20.0,
            step=1.0,
            description='Gravity (m/s²)',
            continuous_update=False
        )
        
        controls['moment_of_inertia_type'] = widgets.RadioButtons(
            options=['rim', 'solid'],
            value='rim',
            description='Wheel type:',
            disabled=False
        )
        
        # Simulation controls
        controls['T'] = widgets.FloatSlider(
            value=10.0,
            min=2.0,
            max=30.0,
            step=1.0,
            description='Sim time (s)',
            continuous_update=False
        )
        
        controls['dt'] = widgets.FloatSlider(
            value=0.01,
            min=0.001,
            max=0.05,
            step=0.001,
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
        controls['inertia_display'] = widgets.HTML(
            value='Loading...',
            description='Moment of Inertia:',
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
            widgets.HBox([self.controls['wheel_radius'], self.controls['wheel_mass']]),
            widgets.HBox([self.controls['rod_length'], self.controls['initial_spin_rate']]),
            widgets.HBox([self.controls['theta0'], self.controls['damping']]),
            widgets.HBox([self.controls['inertia_display'], self.controls['precession_rate']])
        ])
        
        # Advanced parameters tab
        advanced_tab = widgets.VBox([
            widgets.HBox([self.controls['wheel_thickness'], self.controls['rod_mass']]),
            widgets.HBox([self.controls['phi0'], self.controls['g']]),
            widgets.HBox([self.controls['moment_of_inertia_type']]),
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
        
    def update_inertia_display(self, change=None):
        """Update moment of inertia information display."""
        # Update gyroscope parameters from controls
        self.gyroscope.params['wheel_radius'] = self.controls['wheel_radius'].value
        self.gyroscope.params['wheel_mass'] = self.controls['wheel_mass'].value
        self.gyroscope.params['wheel_thickness'] = self.controls['wheel_thickness'].value
        self.gyroscope.params['moment_of_inertia_type'] = self.controls['moment_of_inertia_type'].value
        
        # Update inertia
        self.gyroscope.update_inertia()
        
        # Get inertia values
        Ix = self.gyroscope.Ix
        Iz = self.gyroscope.Iz
        
        # Update display with formatted values
        self.controls['inertia_display'].value = (
            f"<b>Ix = {Ix:.3f} kg·m²</b><br>"
            f"Iz = {Iz:.3f} kg·m²<br>"
            f"Ratio Iz/Ix = {Iz/Ix:.2f}"
        )
        
        # Also update precession rate since inertia affects it
        self.update_precession_rate()
            
    def update_precession_rate(self, change=None):
        """Update precession rate information display."""
        # Update gyroscope parameters
        self.gyroscope.params['initial_spin_rate'] = self.controls['initial_spin_rate'].value
        
        # Calculate theoretical precession rate
        precession_rate = self.gyroscope.calculate_theoretical_precession_rate()
        
        # Convert to degrees per second and per minute
        rate_deg_per_s = np.degrees(precession_rate)
        rate_deg_per_min = rate_deg_per_s * 60
        
        # Calculate time for full rotation (360°)
        if abs(rate_deg_per_s) > 1e-6:
            full_rotation_s = 360 / abs(rate_deg_per_s)
            minutes = int(full_rotation_s / 60)
            seconds = full_rotation_s % 60
            time_str = f"{minutes} min {seconds:.1f} s"
        else:
            time_str = "∞"
        
        # Update display with formatted values
        self.controls['precession_rate'].value = (
            f"<b>{rate_deg_per_s:.3f}°/s</b><br>"
            f"{rate_deg_per_min:.2f}°/min<br>"
            f"Full rotation: {time_str}"
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
            
            # Clear history
            if hasattr(self, 'wheel_center_history'):
                self.wheel_center_history = []
                self.rod_history = []
            
            # Reset parameters to defaults
            default_gyro = GyroscopeSimulation()
            
            # Reset parameters to specific requested values
            default_values = {
                'wheel_radius': 0.3,
                'wheel_mass': 1.0,
                'wheel_thickness': 0.05, 
                'rod_length': 0.5,
                'rod_mass': 0.2,
                'initial_spin_rate': 20.0,
                'damping': 0.05,
                'theta0': 0.3,
                'phi0': 0.0,
                'g': 9.81,
                'moment_of_inertia_type': 'rim',
                'T': 10.0,
                'dt': 0.01,
                'animation_speed': 1.0
            }
            
            for param, value in default_values.items():
                if param in self.controls:
                    self.controls[param].value = value
            
            # Update displays
            self.update_inertia_display()
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
            output_path = "gyroscope_animation.mp4"
            
            # Clear output and show status
            self.output.clear_output(wait=True)
            
            # Save as video and display result in output area
            with self.output:
                # Create a dedicated HTML widget for save status
                save_status = widgets.HTML('Starting video save process...')
                display(save_status)
                
                # Save the animation using custom gyroscope video saver
                try:
                    result = save_gyroscope_video(self.anim_fig, self.results, output_path)
                    display(result)
                except Exception as e:
                    save_status.value = f"<div style='color: red; font-weight: bold;'>Error saving video:</div><div>{str(e)}</div>"
                    
                    # Redisplay the figures
                    self.display_figures()
    
    def create_animation_figure(self, results):
        """Create Plotly figure for gyroscope animation."""
        # Create a 3D figure for the gyroscope
        fig = go.FigureWidget()
        
        # Add rod trace
        pivot = results['pivot'][0]
        wheel_center = results['wheel_center'][0]
        
        fig.add_trace(
            go.Scatter3d(
                x=[pivot[0], wheel_center[0]], 
                y=[pivot[1], wheel_center[1]],
                z=[pivot[2], wheel_center[2]],
                mode='lines',
                line=dict(color='gray', width=6),
                name='Rod',
                showlegend=False
            )
        )
        
        # Add wheel center trace
        fig.add_trace(
            go.Scatter3d(
                x=[wheel_center[0]],
                y=[wheel_center[1]],
                z=[wheel_center[2]],
                mode='markers',
                marker=dict(size=5, color='red'),
                name='Wheel Center',
                showlegend=False
            )
        )
        
        # Add wheel rim trace
        rim_points = results['rim_points'][0]
        x_rim = rim_points[:, 0]
        y_rim = rim_points[:, 1]
        z_rim = rim_points[:, 2]
        
        # Close the loop by repeating the first point
        x_rim = np.append(x_rim, x_rim[0])
        y_rim = np.append(y_rim, y_rim[0])
        z_rim = np.append(z_rim, z_rim[0])
        
        fig.add_trace(
            go.Scatter3d(
                x=x_rim,
                y=y_rim,
                z=z_rim,
                mode='lines',
                line=dict(color='blue', width=3),
                name='Wheel Rim',
                showlegend=False
            )
        )
        
        # Add spin axis trace
        spin_axis = results['spin_axis'][0]
        axis_scale = results['wheel_radius'] * 1.5  # Scale to make axis visible
        
        fig.add_trace(
            go.Scatter3d(
                x=[wheel_center[0], wheel_center[0] + spin_axis[0] * axis_scale],
                y=[wheel_center[1], wheel_center[1] + spin_axis[1] * axis_scale],
                z=[wheel_center[2], wheel_center[2] + spin_axis[2] * axis_scale],
                mode='lines',
                line=dict(color='red', width=3),
                name='Spin Axis',
                showlegend=False
            )
        )
        
        # Add reference frame axes
        axis_length = results['rod_length'] * 1.5
        
        # X-axis (red)
        fig.add_trace(
            go.Scatter3d(
                x=[0, axis_length],
                y=[0, 0],
                z=[0, 0],
                mode='lines',
                line=dict(color='red', width=1),
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
                line=dict(color='green', width=1),
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
                line=dict(color='blue', width=1),
                name='Z-axis',
                showlegend=False
            )
        )
        
        # Add angular momentum vector trace
        # Angular momentum should be plotted from the wheel center along the spin axis
        # This ensures it's collinear with the spin axis as physically expected
        
        # Get the wheel center and spin axis
        wheel_center_pos = results['wheel_center'][0]
        spin_axis_dir = results['spin_axis'][0]
        
        # Scale the spin axis for visualization
        L_magnitude = results['L_magnitude'][0]
        if L_magnitude > 1e-6:
            L_scale = axis_length / L_magnitude * 0.8  # Scale proportional to magnitude
        else:
            L_scale = axis_length * 0.5  # Default scale if magnitude is very small
            
        # Calculate end point - angular momentum should be parallel to spin axis
        L_end_x = wheel_center_pos[0] + spin_axis_dir[0] * L_scale
        L_end_y = wheel_center_pos[1] + spin_axis_dir[1] * L_scale
        L_end_z = wheel_center_pos[2] + spin_axis_dir[2] * L_scale
        
        fig.add_trace(
            go.Scatter3d(
                x=[wheel_center_pos[0], L_end_x],
                y=[wheel_center_pos[1], L_end_y],
                z=[wheel_center_pos[2], L_end_z],
                mode='lines+markers',
                line=dict(color='purple', width=4),
                marker=dict(size=[0, 8], color='purple'),
                name='Angular Momentum',
                showlegend=False
            )
        )
        
        # Add trace for wheel center path history
        fig.add_trace(
            go.Scatter3d(
                x=[],
                y=[],
                z=[],
                mode='lines',
                line=dict(color='rgba(200, 0, 0, 0.5)', width=2),
                name='Path',
                showlegend=False
            )
        )
        
        # Update layout
        fig.update_layout(
            title='Gyroscope Animation',
            height=500,
            scene=dict(
                xaxis=dict(range=[-axis_length, axis_length], title='X'),
                yaxis=dict(range=[-axis_length, axis_length], title='Y'),
                zaxis=dict(range=[-0.2*axis_length, axis_length], title='Z'),
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
                        subplot_titles=('Angles vs Time', 'Angular Velocity vs Time',
                                        'Phase Space (θ-dθ/dt)', 'Energy & Angular Momentum')))
        
        t = results['t']
        
        # Add angles plot (top left)
        # Convert to degrees for easier interpretation
        theta_deg = np.degrees(results['theta'])
        phi_deg = np.degrees(results['phi_unwrapped'])
        
        fig.add_trace(
            go.Scatter(x=t, y=theta_deg,
                      name='Tilt (θ)', line=dict(color='blue')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=t, y=phi_deg,
                      name='Azimuth (φ)', line=dict(color='green')),
            row=1, col=1
        )
        
        # Add current state marker for angles
        fig.add_trace(
            go.Scatter(x=[t[0]], y=[theta_deg[0]],
                      mode='markers',
                      marker=dict(size=10, color='blue', symbol='circle'),
                      name='Current θ',
                      showlegend=False),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=[t[0]], y=[phi_deg[0]],
                      mode='markers',
                      marker=dict(size=10, color='green', symbol='circle'),
                      name='Current φ',
                      showlegend=False),
            row=1, col=1
        )
        
        # Add angular velocity plot (top right)
        # Convert to degrees/second for easier interpretation
        theta_dot_deg = np.degrees(results['theta_dot'])
        phi_dot_deg = np.degrees(results['phi_dot'])
        psi_dot_deg = np.degrees(results['psi_dot'])
        
        fig.add_trace(
            go.Scatter(x=t, y=theta_dot_deg,
                      name='dθ/dt', line=dict(color='blue', dash='dash')),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=t, y=phi_dot_deg,
                      name='dφ/dt', line=dict(color='green', dash='dash')),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=t, y=psi_dot_deg,
                      name='dψ/dt', line=dict(color='red', dash='dash')),
            row=1, col=2
        )
        
        # Add current state markers for angular velocities
        fig.add_trace(
            go.Scatter(x=[t[0]], y=[theta_dot_deg[0]],
                      mode='markers',
                      marker=dict(size=10, color='blue', symbol='circle'),
                      name='Current dθ/dt',
                      showlegend=False),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=[t[0]], y=[phi_dot_deg[0]],
                      mode='markers',
                      marker=dict(size=10, color='green', symbol='circle'),
                      name='Current dφ/dt',
                      showlegend=False),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=[t[0]], y=[psi_dot_deg[0]],
                      mode='markers',
                      marker=dict(size=10, color='red', symbol='circle'),
                      name='Current dψ/dt',
                      showlegend=False),
            row=1, col=2
        )
        
        # Add phase space plot (bottom left)
        fig.add_trace(
            go.Scatter(x=theta_deg, y=theta_dot_deg,
                      name='Phase Space', mode='lines',
                      line=dict(color='purple', width=2)),
            row=2, col=1
        )
        
        # Add current state marker on phase space
        fig.add_trace(
            go.Scatter(x=[theta_deg[0]], y=[theta_dot_deg[0]],
                      mode='markers',
                      marker=dict(size=10, color='red', symbol='star'),
                      name='Current State',
                      showlegend=False),
            row=2, col=1
        )
        
        # Add energy plots (bottom right)
        fig.add_trace(
            go.Scatter(x=t, y=results['kinetic_energy'],
                      name='Kinetic Energy', line=dict(color='green')),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=t, y=results['potential_energy'],
                      name='Potential Energy', line=dict(color='orange')),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=t, y=results['total_energy'],
                      name='Total Energy', line=dict(color='black')),
            row=2, col=2
        )
        
        # Add angular momentum magnitude to show conservation
        # Scale the angular momentum to fit on the same plot as energy
        L_magnitude = results['L_magnitude']
        max_energy = max(np.max(results['total_energy']), 1e-6)
        max_L_magnitude = max(np.max(L_magnitude), 1e-6)
        scale_factor = max_energy / max_L_magnitude
        scaled_L_magnitude = L_magnitude * scale_factor
        
        fig.add_trace(
            go.Scatter(x=t, y=scaled_L_magnitude,
                      name='Angular Momentum (scaled)', line=dict(color='purple', dash='dot', width=2)),
            row=2, col=2
        )
        
        # Add time indicator vertical lines
        shapes = []
        
        # Add time indicator for angles plot (top left)
        shapes.append(dict(
            type='line',
            x0=0, x1=0,
            y0=min(min(theta_deg), min(phi_deg)),
            y1=max(max(theta_deg), max(phi_deg)),
            xref='x1', yref='y1',
            line=dict(color='red', width=2, dash='dot')
        ))
        
        # Add time indicator for angular velocity plot (top right)
        y_min_vel = min(min(theta_dot_deg), min(phi_dot_deg), min(psi_dot_deg))
        y_max_vel = max(max(theta_dot_deg), max(phi_dot_deg), max(psi_dot_deg))
        shapes.append(dict(
            type='line',
            x0=0, x1=0,
            y0=y_min_vel, y1=y_max_vel,
            xref='x2', yref='y2',
            line=dict(color='red', width=2, dash='dot')
        ))
        
        # Add time indicator for energy plot (bottom right)
        max_y_value = max(max(results['total_energy']), max(scaled_L_magnitude))
        shapes.append(dict(
            type='line',
            x0=0, x1=0,
            y0=0, y1=max_y_value * 1.05,
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
        fig.update_xaxes(title_text='Tilt Angle θ (deg)', row=2, col=1)
        fig.update_xaxes(title_text='Time (s)', row=2, col=2)
        
        fig.update_yaxes(title_text='Angle (deg)', row=1, col=1)
        fig.update_yaxes(title_text='Angular Velocity (deg/s)', row=1, col=2)
        fig.update_yaxes(title_text='dθ/dt (deg/s)', row=2, col=1)
        fig.update_yaxes(title_text='Energy (J)<br>and Scaled Angular<br>Momentum (kg·m²/s)', title_font=dict(size=10), row=2, col=2)
        
        # Set reasonable axis ranges
        fig.update_yaxes(autorange=True, row=1, col=1)
        fig.update_yaxes(autorange=True, row=1, col=2)
        
        return fig

    def update_animation_frame(self, fig_anim, fig_plots, results, frame):
        """Update animation and plot figures to current frame."""
        t = results['t']
        current_t = t[frame]
        
        # Update 3D animation
        with fig_anim.batch_update():
            # Get current positions
            pivot = results['pivot'][frame]
            wheel_center = results['wheel_center'][frame]
            rim_points = results['rim_points'][frame]
            spin_axis = results['spin_axis'][frame]
            axis_scale = results['wheel_radius'] * 1.5
            
            # Update rod
            fig_anim.data[0].x = [pivot[0], wheel_center[0]]
            fig_anim.data[0].y = [pivot[1], wheel_center[1]]
            fig_anim.data[0].z = [pivot[2], wheel_center[2]]
            
            # Update wheel center
            fig_anim.data[1].x = [wheel_center[0]]
            fig_anim.data[1].y = [wheel_center[1]]
            fig_anim.data[1].z = [wheel_center[2]]
            
            # Update wheel rim
            x_rim = rim_points[:, 0]
            y_rim = rim_points[:, 1]
            z_rim = rim_points[:, 2]
            
            # Close the loop by repeating the first point
            x_rim = np.append(x_rim, x_rim[0])
            y_rim = np.append(y_rim, y_rim[0])
            z_rim = np.append(z_rim, z_rim[0])
            
            fig_anim.data[2].x = x_rim
            fig_anim.data[2].y = y_rim
            fig_anim.data[2].z = z_rim
            
            # Update spin axis
            fig_anim.data[3].x = [wheel_center[0], wheel_center[0] + spin_axis[0] * axis_scale]
            fig_anim.data[3].y = [wheel_center[1], wheel_center[1] + spin_axis[1] * axis_scale]
            fig_anim.data[3].z = [wheel_center[2], wheel_center[2] + spin_axis[2] * axis_scale]
            
            # Update angular momentum vector - align with spin axis
            # Get current wheel center and spin axis direction
            current_wheel_center = wheel_center
            current_spin_axis = spin_axis
            
            # Calculate angular momentum magnitude
            L_magnitude = results['L_magnitude'][frame]
            
            # Scale for visualization
            if L_magnitude > 1e-6:
                axis_length = results['rod_length'] * 1.5
                L_scale = axis_length / L_magnitude * 0.8
            else:
                L_scale = axis_length * 0.5  # Default scale if magnitude is very small
            
            # Calculate endpoint - angular momentum should align with spin axis
            L_end_x = current_wheel_center[0] + current_spin_axis[0] * L_scale
            L_end_y = current_wheel_center[1] + current_spin_axis[1] * L_scale
            L_end_z = current_wheel_center[2] + current_spin_axis[2] * L_scale
            
            # Update angular momentum vector visualization
            fig_anim.data[7].x = [current_wheel_center[0], L_end_x]
            fig_anim.data[7].y = [current_wheel_center[1], L_end_y]
            fig_anim.data[7].z = [current_wheel_center[2], L_end_z]
            
            # Store wheel center position history
            if not hasattr(self, 'wheel_center_history'):
                self.wheel_center_history = []
                self.rod_history = []
            
            # Add current position to history
            if frame >= len(self.wheel_center_history):
                self.wheel_center_history.append(wheel_center)
            
            # Update wheel center path history
            if len(self.wheel_center_history) > 0:
                wheel_centers = np.array(self.wheel_center_history)
                fig_anim.data[8].x = wheel_centers[:, 0]
                fig_anim.data[8].y = wheel_centers[:, 1]
                fig_anim.data[8].z = wheel_centers[:, 2]
        
        # Update plots
        with fig_plots.batch_update():
            # Get current values in degrees
            theta_deg = np.degrees(results['theta'][frame])
            phi_deg = np.degrees(results['phi_unwrapped'][frame])
            theta_dot_deg = np.degrees(results['theta_dot'][frame])
            phi_dot_deg = np.degrees(results['phi_dot'][frame])
            psi_dot_deg = np.degrees(results['psi_dot'][frame])
            
            # Update time indicators in all plots
            for shape in fig_plots.layout.shapes:
                shape.x0 = current_t
                shape.x1 = current_t
            
            # Update current state markers
            # Angles plot markers
            fig_plots.data[2].x = [current_t]
            fig_plots.data[2].y = [theta_deg]
            fig_plots.data[3].x = [current_t]
            fig_plots.data[3].y = [phi_deg]
            
            # Angular velocity plot markers
            fig_plots.data[7].x = [current_t]
            fig_plots.data[7].y = [theta_dot_deg]
            fig_plots.data[8].x = [current_t]
            fig_plots.data[8].y = [phi_dot_deg]
            fig_plots.data[9].x = [current_t]
            fig_plots.data[9].y = [psi_dot_deg]
            
            # Phase space plot marker
            fig_plots.data[11].x = [theta_deg]
            fig_plots.data[11].y = [theta_dot_deg]
            
    def update_simulation(self, _=None):
        """Update simulation with current widget values."""
        # Update gyroscope parameters
        for param, widget in self.controls.items():
            if param in ['inertia_display', 'precession_rate', 'animation_speed']:
                continue
            self.gyroscope.params[param] = widget.value
            
        # Store parameters for animation
        self.params = self.gyroscope.params.copy()
        
        # Clear history when starting a new simulation
        if hasattr(self, 'wheel_center_history'):
            self.wheel_center_history = []
            self.rod_history = []
        
        # Stop any running animation
        if self.animation.running:
            self.toggle_animation()
            
        # Run simulation
        self.results = self.gyroscope.simulate()
        
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

def create_interactive_gyroscope():
    """Create and display an interactive gyroscope simulation."""
    sim = InteractiveGyroscope()
    sim.display()
    return sim
