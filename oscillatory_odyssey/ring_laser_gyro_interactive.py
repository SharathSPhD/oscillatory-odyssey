"""Interactive Ring Laser Gyroscope simulation interface with dynamic visualization."""

import os
import numpy as np
import json
import datetime
import matplotlib.pyplot as plt
import io
import base64
from IPython.display import display, HTML
import ipywidgets as widgets
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .ring_laser_gyro import RingLaserGyroSimulation
from .animation import AnimationController
from .ring_laser_gyro_video_saver import save_ring_laser_gyro_video


class InteractiveRingLaserGyro:
    """Interactive interface for Ring Laser Gyroscope simulation visualization."""
    
    def __init__(self):
        """Initialize the interactive RLG interface."""
        self.ring_laser_gyro = RingLaserGyroSimulation()
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
        self.controls['cavity_radius'].observe(self.update_cavity_display, names='value')
        self.controls['cavity_shape'].observe(self.update_cavity_display, names='value')
        self.controls['rotation_rate'].observe(self.update_sagnac_display, names='value')
        self.controls['dithering_enabled'].observe(self.toggle_dithering_controls, names='value')
        self.controls['animation_speed'].observe(self.update_animation_speed, names='value')
        
        # Create output area
        self.output = widgets.Output()
        
        # Set up animation controller
        self.animation = AnimationController(self.update_frame)
        
        # Initialize information displays
        self.update_cavity_display()
        self.update_sagnac_display()
        
    def create_parameter_widgets(self):
        """Create all parameter control widgets."""
        controls = {}
        
        # Cavity geometry
        controls['cavity_radius'] = widgets.FloatSlider(
            value=0.1,
            min=0.01,
            max=0.5,
            step=0.01,
            description='Cavity radius (m)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        controls['cavity_shape'] = widgets.Dropdown(
            options=['square', 'triangle', 'circle'],
            value='square',
            description='Cavity shape:',
            style={'description_width': 'initial'},
            disabled=False
        )
        
        # Rotation properties
        controls['rotation_rate'] = widgets.FloatSlider(
            value=1.0,
            min=-5.0,
            max=5.0,
            step=0.1,
            description='Rotation rate (rad/s)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        # Wavelength and optical properties
        controls['wavelength'] = widgets.FloatText(
            value=632.8e-9,
            description='Wavelength (m)',
            style={'description_width': 'initial'},
            disabled=False
        )
        
        controls['beam_power'] = widgets.FloatSlider(
            value=0.005,
            min=0.001,
            max=0.02,
            step=0.001,
            description='Beam power (W)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        # Lock-in and dithering
        controls['coupling_factor'] = widgets.FloatLogSlider(
            value=0.01,
            base=10,
            min=-4,  # 10^-4
            max=-1,  # 10^-1
            step=0.1,
            description='Coupling factor',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        controls['dithering_enabled'] = widgets.Checkbox(
            value=True,
            description='Enable dithering',
            style={'description_width': 'initial'},
            disabled=False
        )
        
        controls['dithering_amplitude'] = widgets.FloatSlider(
            value=0.5,
            min=0.0,
            max=2.0,
            step=0.1,
            description='Dithering amplitude (rad/s)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        controls['dithering_frequency'] = widgets.FloatSlider(
            value=400.0,
            min=10.0,
            max=1000.0,
            step=10.0,
            description='Dithering frequency (Hz)',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        # Error and noise modeling
        controls['shot_noise_enabled'] = widgets.Checkbox(
            value=True,
            description='Enable shot noise',
            style={'description_width': 'initial'},
            disabled=False
        )
        
        controls['random_walk_enabled'] = widgets.Checkbox(
            value=True,
            description='Enable bias drift',
            style={'description_width': 'initial'},
            disabled=False
        )
        
        controls['random_walk_sigma'] = widgets.FloatLogSlider(
            value=1e-7,
            base=10,
            min=-10,  # 10^-10
            max=-5,   # 10^-5
            step=0.5,
            description='Drift coefficient',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        # Simulation controls
        controls['T'] = widgets.FloatSlider(
            value=1.0,
            min=0.1,
            max=10.0,
            step=0.1,
            description='Sim time (s)',
            continuous_update=False
        )
        
        controls['output_dt'] = widgets.FloatLogSlider(
            value=1e-3,
            base=10,
            min=-4,  # 10^-4
            max=-2,  # 10^-2
            step=0.2,
            description='Output step (s)',
            continuous_update=False
        )
        
        controls['animation_speed'] = widgets.FloatSlider(
            value=10.0,
            min=1.0,
            max=30.0,
            step=1.0,
            description='Animation speed',
            continuous_update=False
        )
        
        # Information displays
        controls['cavity_display'] = widgets.HTML(
            value='Loading...',
            description='Cavity info:',
            style={'description_width': 'initial'}
        )
        
        controls['sagnac_display'] = widgets.HTML(
            value='Loading...',
            description='Sagnac effect:',
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
            widgets.HBox([self.controls['cavity_radius'], self.controls['cavity_shape']]),
            widgets.HBox([self.controls['rotation_rate'], self.controls['wavelength']]),
            widgets.HBox([self.controls['dithering_enabled'], self.controls['dithering_amplitude']]),
            widgets.HBox([self.controls['cavity_display'], self.controls['sagnac_display']])
        ])
        
        # Advanced parameters tab
        advanced_tab = widgets.VBox([
            widgets.HBox([self.controls['beam_power'], self.controls['coupling_factor']]),
            widgets.HBox([self.controls['dithering_frequency']]),
            widgets.HBox([self.controls['shot_noise_enabled'], self.controls['random_walk_enabled']]),
            widgets.HBox([self.controls['random_walk_sigma']]),
            widgets.HBox([self.controls['T'], self.controls['output_dt']]),
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
        
    def update_cavity_display(self, change=None):
        """Update cavity information display."""
        # Update RLG parameters from controls
        self.ring_laser_gyro.params['cavity_radius'] = self.controls['cavity_radius'].value
        self.ring_laser_gyro.params['cavity_shape'] = self.controls['cavity_shape'].value
        
        # Update derived parameters
        self.ring_laser_gyro.update_derived_parameters()
        
        # Get values
        perimeter = self.ring_laser_gyro.params['cavity_perimeter']
        area = self.ring_laser_gyro.params['cavity_area']
        
        # Update display with formatted values
        self.controls['cavity_display'].value = (
            f"<b>Perimeter = {perimeter:.3f} m</b><br>"
            f"Area = {area:.6f} m²<br>"
            f"Shape = {self.controls['cavity_shape'].value}"
        )
        
        # Also update Sagnac display since cavity affects it
        self.update_sagnac_display()
            
    def update_sagnac_display(self, change=None):
        """Update Sagnac effect information display."""
        # Update RLG parameters
        self.ring_laser_gyro.params['rotation_rate'] = self.controls['rotation_rate'].value
        self.ring_laser_gyro.params['wavelength'] = self.controls['wavelength'].value
        
        # Update derived parameters
        self.ring_laser_gyro.update_derived_parameters()
        
        # Calculate Sagnac effect
        scale_factor = self.ring_laser_gyro.params['scale_factor']
        rotation_rate = self.controls['rotation_rate'].value
        phase_diff = scale_factor * rotation_rate
        lock_in_threshold = self.ring_laser_gyro.params['lock_in_threshold']
        
        # Update display with formatted values
        self.controls['sagnac_display'].value = (
            f"<b>Scale factor = {scale_factor:.2e} rad/(rad/s)</b><br>"
            f"Phase diff = {phase_diff:.3f} rad<br>"
            f"Lock-in threshold = {lock_in_threshold:.3f} rad/s"
        )
            
    def toggle_dithering_controls(self, change=None):
        """Enable or disable dithering-related controls based on checkbox."""
        enabled = self.controls['dithering_enabled'].value
        self.controls['dithering_amplitude'].disabled = not enabled
        self.controls['dithering_frequency'].disabled = not enabled
        
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
            
            # Save diagnostic information when play is pressed
            self.save_diagnostics()
    
    def reset_animation(self, _=None):
        """Reset animation to initial frame and controls to defaults."""
        if hasattr(self, 'results'):
            # Reset animation
            self.animation.reset()
            self.buttons['play'].description = 'Play'
            
            # Reset parameters to defaults
            default_rlg = RingLaserGyroSimulation()
            
            # Reset parameters to specific requested values
            default_values = {
                'cavity_radius': 0.1,
                'cavity_shape': 'square',
                'rotation_rate': 1.0,
                'wavelength': 632.8e-9,
                'beam_power': 0.005,
                'coupling_factor': 0.01,
                'dithering_enabled': True,
                'dithering_amplitude': 0.5,
                'dithering_frequency': 400.0,
                'shot_noise_enabled': True,
                'random_walk_enabled': True,
                'random_walk_sigma': 1e-7,
                'T': 1.0,
                'output_dt': 1e-3,
                'animation_speed': 10.0
            }
            
            for param, value in default_values.items():
                if param in self.controls:
                    self.controls[param].value = value
            
            # Update displays
            self.update_cavity_display()
            self.update_sagnac_display()
            
    def save_animation(self, _=None):
        """Save animation as video file."""
        if hasattr(self, 'results'):
            # Stop animation if running
            if self.animation.running:
                self.toggle_animation()
            
            # Reset to start
            self.animation.reset()
            
            # Create timestamped output path for uniqueness
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"ring_laser_gyro_animation_{timestamp}.mp4"
            
            # Clear output and show status
            self.output.clear_output(wait=True)
            
            # Save as video and display result in output area
            with self.output:
                # Create a dedicated HTML widget for save status
                save_status = widgets.HTML('Starting video save process...')
                display(save_status)
                
                # Save the animation using custom RLG video saver
                try:
                    # First, make sure we've run a simulation
                    if 'phase_difference' not in self.results:
                        save_status.value = f"<div style='color: red; font-weight: bold;'>Error: Please run the simulation before saving video</div>"
                        self.display_figures()
                        return
                        
                    # Update status
                    save_status.value = f"<div>Creating video with {len(self.results['t'])} frames...</div>"
                    
                    # Call the video saver
                    result = save_ring_laser_gyro_video(self.anim_fig, self.results, output_path)
                    display(result)
                    
                    # Save a copy of the diagnostic data
                    self.save_diagnostics()
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    save_status.value = f"<div style='color: red; font-weight: bold;'>Error saving video:</div><div>{str(e)}</div><pre>{error_details}</pre>"
                    
                    # Redisplay the figures
                    self.display_figures()
    
    def create_animation_figure(self, results):
        """Create Plotly figure for RLG animation."""
        # Create a 3D figure for the RLG
        fig = go.FigureWidget()
        
        # Add cavity outline trace
        cavity_vertices = results['cavity_vertices']
        
        # For circle, close the loop
        if results['cavity_shape'] == 'circle':
            x_cavity = np.append(cavity_vertices[:, 0], cavity_vertices[0, 0])
            y_cavity = np.append(cavity_vertices[:, 1], cavity_vertices[0, 1])
            z_cavity = np.append(cavity_vertices[:, 2], cavity_vertices[0, 2])
        else:
            # For polygons, explicitly close the loop
            x_cavity = np.append(cavity_vertices[:, 0], cavity_vertices[0, 0])
            y_cavity = np.append(cavity_vertices[:, 1], cavity_vertices[0, 1])
            z_cavity = np.append(cavity_vertices[:, 2], cavity_vertices[0, 2])
        
        fig.add_trace(
            go.Scatter3d(
                x=x_cavity,
                y=y_cavity,
                z=z_cavity,
                mode='lines',
                line=dict(color='black', width=3),
                name='Cavity',
                showlegend=False
            )
        )
        
        # Add mirror traces
        mirror_positions = results['mirror_positions']
        for i, mirror in enumerate(mirror_positions):
            fig.add_trace(
                go.Scatter3d(
                    x=[mirror[0]],
                    y=[mirror[1]],
                    z=[mirror[2]],
                    mode='markers',
                    marker=dict(size=6, color='silver', symbol='square'),
                    name=f'Mirror {i+1}',
                    showlegend=False
                )
            )
        
        # Add clockwise beam trace
        cw_beam_positions = results['cw_beam_positions'][0]
        fig.add_trace(
            go.Scatter3d(
                x=cw_beam_positions[:, 0],
                y=cw_beam_positions[:, 1],
                z=cw_beam_positions[:, 2],
                mode='markers',
                marker=dict(size=3, color='red', symbol='circle'),
                name='CW Beam',
                showlegend=True
            )
        )
        
        # Add counter-clockwise beam trace
        ccw_beam_positions = results['ccw_beam_positions'][0]
        fig.add_trace(
            go.Scatter3d(
                x=ccw_beam_positions[:, 0],
                y=ccw_beam_positions[:, 1],
                z=ccw_beam_positions[:, 2],
                mode='markers',
                marker=dict(size=3, color='blue', symbol='circle'),
                name='CCW Beam',
                showlegend=True
            )
        )
        
        # Add rotation axis
        axis_length = results['cavity_radius'] * 2.0
        fig.add_trace(
            go.Scatter3d(
                x=[0, 0],
                y=[0, 0],
                z=[-axis_length, axis_length],
                mode='lines',
                line=dict(color='green', width=3, dash='dash'),
                name='Rotation Axis',
                showlegend=True
            )
        )
        
        # Add photodetector (where beams recombine)
        # Place it at the first mirror position
        pd_pos = mirror_positions[0]
        fig.add_trace(
            go.Scatter3d(
                x=[pd_pos[0]],
                y=[pd_pos[1]],
                z=[pd_pos[2]],
                mode='markers',
                marker=dict(size=8, color='purple', symbol='diamond'),
                name='Photodetector',
                showlegend=True
            )
        )
        
        # Update layout
        fig.update_layout(
            title='Ring Laser Gyroscope Animation',
            height=500,
            scene=dict(
                xaxis=dict(range=[-axis_length, axis_length], title='X'),
                yaxis=dict(range=[-axis_length, axis_length], title='Y'),
                zaxis=dict(range=[-axis_length, axis_length], title='Z'),
                aspectmode='cube'
            ),
            legend=dict(x=0, y=1),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig

    def create_plots_figure(self, results):
        """Create Plotly figure for time series plots."""
        fig = go.FigureWidget(make_subplots(rows=2, cols=2,
                        subplot_titles=('Phase Difference', 'Rotation Rate Measurement',
                                        'Interference Pattern', 'Photodiode Signals')))
        
        t = results['t']
        
        # Add phase difference plot (top left)
        fig.add_trace(
            go.Scatter(x=t, y=results['phase_difference'],
                      name='Phase Difference', line=dict(color='blue')),
            row=1, col=1
        )
        
        # Add current state marker for phase difference
        fig.add_trace(
            go.Scatter(x=[t[0]], y=[results['phase_difference'][0]],
                      mode='markers',
                      marker=dict(size=10, color='blue', symbol='circle'),
                      name='Current Phase',
                      showlegend=False),
            row=1, col=1
        )
        
        # Add rotation rate plot (top right)
        fig.add_trace(
            go.Scatter(x=t, y=results['theoretical_rotation_rate'],
                      name='Theoretical', line=dict(color='green')),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=t, y=results['measured_rotation_rate'],
                      name='Measured', line=dict(color='red')),
            row=1, col=2
        )
        
        # Add current state markers for rotation rates
        fig.add_trace(
            go.Scatter(x=[t[0]], y=[results['theoretical_rotation_rate'][0]],
                      mode='markers',
                      marker=dict(size=10, color='green', symbol='circle'),
                      name='Current Theoretical',
                      showlegend=False),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=[t[0]], y=[results['measured_rotation_rate'][0]],
                      mode='markers',
                      marker=dict(size=10, color='red', symbol='circle'),
                      name='Current Measured',
                      showlegend=False),
            row=1, col=2
        )
        
        # Add interference pattern plot (bottom left)
        fig.add_trace(
            go.Scatter(x=t, y=results['interference_intensity'],
                      name='Interference', line=dict(color='purple')),
            row=2, col=1
        )
        
        # Add current state marker for interference pattern
        fig.add_trace(
            go.Scatter(x=[t[0]], y=[results['interference_intensity'][0]],
                      mode='markers',
                      marker=dict(size=10, color='purple', symbol='circle'),
                      name='Current Interference',
                      showlegend=False),
            row=2, col=1
        )
        
        # Add photodiode signals plot (bottom right)
        fig.add_trace(
            go.Scatter(x=t, y=results['photodiode1'],
                      name='PD1 (cos)', line=dict(color='red')),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=t, y=results['photodiode2'],
                      name='PD2 (sin)', line=dict(color='blue')),
            row=2, col=2
        )
        
        # Add current state markers for photodiode signals
        fig.add_trace(
            go.Scatter(x=[t[0]], y=[results['photodiode1'][0]],
                      mode='markers',
                      marker=dict(size=10, color='red', symbol='circle'),
                      name='Current PD1',
                      showlegend=False),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=[t[0]], y=[results['photodiode2'][0]],
                      mode='markers',
                      marker=dict(size=10, color='blue', symbol='circle'),
                      name='Current PD2',
                      showlegend=False),
            row=2, col=2
        )
        
        # Add time indicator vertical lines
        shapes = []
        
        # Add time indicator for phase difference plot (top left)
        shapes.append(dict(
            type='line',
            x0=0, x1=0,
            y0=min(results['phase_difference']),
            y1=max(results['phase_difference']),
            xref='x1', yref='y1',
            line=dict(color='red', width=2, dash='dot')
        ))
        
        # Add time indicator for rotation rate plot (top right)
        min_rot = min(min(results['theoretical_rotation_rate']), min(results['measured_rotation_rate']))
        max_rot = max(max(results['theoretical_rotation_rate']), max(results['measured_rotation_rate']))
        shapes.append(dict(
            type='line',
            x0=0, x1=0,
            y0=min_rot, y1=max_rot,
            xref='x2', yref='y2',
            line=dict(color='red', width=2, dash='dot')
        ))
        
        # Add time indicator for interference plot (bottom left)
        shapes.append(dict(
            type='line',
            x0=0, x1=0,
            y0=min(results['interference_intensity']),
            y1=max(results['interference_intensity']),
            xref='x3', yref='y3',
            line=dict(color='red', width=2, dash='dot')
        ))
        
        # Add time indicator for photodiode signals plot (bottom right)
        min_pd = min(min(results['photodiode1']), min(results['photodiode2']))
        max_pd = max(max(results['photodiode1']), max(results['photodiode2']))
        shapes.append(dict(
            type='line',
            x0=0, x1=0,
            y0=min_pd, y1=max_pd,
            xref='x4', yref='y4',
            line=dict(color='red', width=2, dash='dot')
        ))
        
        # Create separate distinct legends for each plot to avoid duplication
        # Add necessary layout settings
        fig.update_layout(
            height=700,
            margin=dict(l=20, r=20, t=40, b=20),
            shapes=shapes
        )
        
        # Clear existing legends
        fig.update_layout(showlegend=False)
        
        # Add custom titles with more descriptive information
        fig.layout.annotations[0].text = "Phase Difference (rad)"
        fig.layout.annotations[1].text = "Rotation Rate (rad/s)"
        
        # Use trace groups with different coordinates for legends
        for i, trace in enumerate(fig.data):
            # Phase difference plot (first subplot)
            if i == 0:
                trace.showlegend = True
                trace.name = "Phase Difference"
                trace.legendgroup = "group1"
                trace.legendgrouptitle = {"text": "Phase Plot"}
            # Rotation rate traces (second subplot)
            elif i == 2:
                trace.showlegend = True
                trace.name = "Theoretical Rate"
                trace.legendgroup = "group2"
                trace.legendgrouptitle = {"text": "Rotation Rates"}
            elif i == 3:
                trace.showlegend = True
                trace.name = "Measured Rate"
                trace.legendgroup = "group2"
                
        # Add organized legend at the bottom
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,  # Position below the plots
                xanchor="center",
                x=0.5,
                font=dict(size=10),
                groupclick="toggleitem"
            )
        )
        
        # Add subplot labels
        fig.update_xaxes(title_text='Time (s)', row=1, col=1)
        fig.update_xaxes(title_text='Time (s)', row=1, col=2)
        fig.update_xaxes(title_text='Time (s)', row=2, col=1)
        fig.update_xaxes(title_text='Time (s)', row=2, col=2)
        
        fig.update_yaxes(title_text='Phase Difference (rad)', row=1, col=1)
        fig.update_yaxes(title_text='Rotation Rate (rad/s)', row=1, col=2)
        fig.update_yaxes(title_text='Intensity (a.u.)', row=2, col=1)
        fig.update_yaxes(title_text='Signal (a.u.)', row=2, col=2)
        
        # Set reasonable axis ranges
        fig.update_yaxes(autorange=True, row=1, col=1)
        fig.update_yaxes(autorange=True, row=1, col=2)
        fig.update_yaxes(range=[-0.1, 2.1], row=2, col=1)  # Interference pattern range with padding
        fig.update_yaxes(range=[-1.2, 1.2], row=2, col=2)  # Photodiode signals range
        
        return fig

    def check_lock_in_condition(self):
        """Check if the RLG is in a lock-in condition and display a warning if needed."""
        rotation_rate = self.results['rotation_rate']
        lock_in_threshold = self.results['lock_in_threshold']
        dithering_enabled = self.results['dithering_enabled']
        
        # Check if we are below the lock-in threshold
        if abs(rotation_rate) < lock_in_threshold and not dithering_enabled:
            self.output.clear_output(wait=True)
            with self.output:
                self.display_figures()
                display(HTML(f"<div style='background-color: #fff3cd; color: #856404; "
                             f"padding: 10px; border-radius: 5px; margin-top: 10px;'>"
                             f"<strong>Warning:</strong> Current rotation rate ({rotation_rate:.3e} rad/s) is below "
                             f"the lock-in threshold ({lock_in_threshold:.3e} rad/s) and dithering is disabled. "
                             f"The RLG may be in lock-in condition, causing reduced measurement accuracy and "
                             f"minimal animation movement. Consider enabling dithering or increasing the rotation rate."
                             f"</div>"))
                
                # Display statistics
                stats_html = f"""
                <div style="margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                    <h3>Simulation Statistics</h3>
                    <table style="width: 100%;">
                        <tr>
                            <td style="width: 50%;"><b>Mean Error:</b> {self.results['mean_error']:.3e} rad/s</td>
                            <td><b>Std Deviation:</b> {self.results['std_error']:.3e} rad/s</td>
                        </tr>
                        <tr>
                            <td><b>Max Error:</b> {self.results['max_error']:.3e} rad/s</td>
                            <td><b>Lock-in Threshold:</b> {self.results['lock_in_threshold']:.3e} rad/s</td>
                        </tr>
                        <tr>
                            <td><b>Dithering:</b> {'Enabled' if self.results['dithering_enabled'] else 'Disabled'}</td>
                            <td><b>Cavity Shape:</b> {self.results['cavity_shape']}</td>
                        </tr>
                    </table>
                </div>
                """
                display(HTML(stats_html))
    
    def update_animation_frame(self, fig_anim, fig_plots, results, frame):
        """Update animation and plot figures to current frame."""
        t = results['t']
        current_t = t[frame]
        
        # Update 3D animation
        with fig_anim.batch_update():
            # Update clockwise beam
            cw_beam_positions = results['cw_beam_positions'][frame]
            fig_anim.data[len(results['mirror_positions']) + 0].x = cw_beam_positions[:, 0]
            fig_anim.data[len(results['mirror_positions']) + 0].y = cw_beam_positions[:, 1]
            fig_anim.data[len(results['mirror_positions']) + 0].z = cw_beam_positions[:, 2]
            
            # Update counter-clockwise beam
            ccw_beam_positions = results['ccw_beam_positions'][frame]
            fig_anim.data[len(results['mirror_positions']) + 1].x = ccw_beam_positions[:, 0]
            fig_anim.data[len(results['mirror_positions']) + 1].y = ccw_beam_positions[:, 1]
            fig_anim.data[len(results['mirror_positions']) + 1].z = ccw_beam_positions[:, 2]
            
            # Rotate the cavity based on current rotation
            # This is a visual effect to show rotation - not physically accurate for an RLG
            # The actual RLG cavity would not visibly rotate in operation
            # For visualization purposes only, we show a slow rotation
            if hasattr(self, 'cavity_rotation_angle'):
                # Use much larger angle change to make rotation visible
                self.cavity_rotation_angle += self.ring_laser_gyro.params['rotation_rate'] * 0.1  # Faster rotation for visibility
            else:
                self.cavity_rotation_angle = 0.0
                
            # Enable cavity rotation to make movement more visible
            if True:  # Enable for better visualization
                # Create rotation matrix around z-axis
                angle = self.cavity_rotation_angle
                cos_a = np.cos(angle)
                sin_a = np.sin(angle)
                
                # Rotate cavity vertices
                original_vertices = results['cavity_vertices']
                rotated_vertices = np.zeros_like(original_vertices)
                
                for i, vertex in enumerate(original_vertices):
                    rotated_vertices[i, 0] = vertex[0] * cos_a - vertex[1] * sin_a
                    rotated_vertices[i, 1] = vertex[0] * sin_a + vertex[1] * cos_a
                    rotated_vertices[i, 2] = vertex[2]
                
                # For circle, close the loop
                if results['cavity_shape'] == 'circle':
                    x_cavity = np.append(rotated_vertices[:, 0], rotated_vertices[0, 0])
                    y_cavity = np.append(rotated_vertices[:, 1], rotated_vertices[0, 1])
                    z_cavity = np.append(rotated_vertices[:, 2], rotated_vertices[0, 2])
                else:
                    # For polygons, explicitly close the loop
                    x_cavity = np.append(rotated_vertices[:, 0], rotated_vertices[0, 0])
                    y_cavity = np.append(rotated_vertices[:, 1], rotated_vertices[0, 1])
                    z_cavity = np.append(rotated_vertices[:, 2], rotated_vertices[0, 2])
                
                # Update cavity outline trace
                fig_anim.data[0].x = x_cavity
                fig_anim.data[0].y = y_cavity
                fig_anim.data[0].z = z_cavity
                
                # Update mirror positions
                for i, mirror in enumerate(results['mirror_positions']):
                    rotated_mirror_x = mirror[0] * cos_a - mirror[1] * sin_a
                    rotated_mirror_y = mirror[0] * sin_a + mirror[1] * cos_a
                    rotated_mirror_z = mirror[2]
                    
                    # Updates mirrors (index 1 to len(mirror_positions))
                    fig_anim.data[i+1].x = [rotated_mirror_x]
                    fig_anim.data[i+1].y = [rotated_mirror_y]
                    fig_anim.data[i+1].z = [rotated_mirror_z]
        
        # Update plots
        with fig_plots.batch_update():
            # Update time indicators in all plots
            for shape in fig_plots.layout.shapes:
                shape.x0 = current_t
                shape.x1 = current_t
            
            # Update current state markers
            # Phase difference plot marker
            fig_plots.data[1].x = [current_t]
            fig_plots.data[1].y = [results['phase_difference'][frame]]
            
            # Rotation rate plot markers
            fig_plots.data[4].x = [current_t]
            fig_plots.data[4].y = [results['theoretical_rotation_rate'][frame]]
            fig_plots.data[5].x = [current_t]
            fig_plots.data[5].y = [results['measured_rotation_rate'][frame]]
            
            # Interference pattern plot marker
            fig_plots.data[7].x = [current_t]
            fig_plots.data[7].y = [results['interference_intensity'][frame]]
            
            # Photodiode signals plot markers
            fig_plots.data[10].x = [current_t]
            fig_plots.data[10].y = [results['photodiode1'][frame]]
            fig_plots.data[11].x = [current_t]
            fig_plots.data[11].y = [results['photodiode2'][frame]]
            
            # Create a trail of photodiode signals for better visualization of Lissajous pattern
            # If we're far enough into the animation, show a trail of the last 20 points
            trail_length = 20
            if frame >= trail_length:
                # Get recent photodiode signals to form a visible trail
                trail_indices = range(max(0, frame-trail_length), frame+1)
                pd1_trail = [results['photodiode1'][i] for i in trail_indices]
                pd2_trail = [results['photodiode2'][i] for i in trail_indices]
                
                # Create a Lissajous figure trace if it doesn't exist
                if len(fig_plots.data) <= 12:
                    # Add a new trace for the Lissajous trail
                    fig_plots.add_trace(
                        go.Scatter(x=pd1_trail, y=pd2_trail,
                                  mode='lines', line=dict(color='purple', width=2),
                                  name='Lissajous Trail', showlegend=False),
                        row=2, col=1
                    )
                else:
                    # Update existing trace
                    fig_plots.data[12].x = pd1_trail
                    fig_plots.data[12].y = pd2_trail
            
    def update_simulation(self, _=None):
        """Update simulation with current widget values."""
        # Update RLG parameters
        for param, widget in self.controls.items():
            if param in ['cavity_display', 'sagnac_display', 'animation_speed']:
                continue
            if param in self.ring_laser_gyro.params:
                self.ring_laser_gyro.params[param] = widget.value
            
        # Store parameters for animation
        self.params = self.ring_laser_gyro.params.copy()
        
        # Reset cavity rotation angle
        self.cavity_rotation_angle = 0.0
        
        # Stop any running animation
        if self.animation.running:
            self.toggle_animation()
            
        # Run simulation
        self.results = self.ring_laser_gyro.simulate()
        
        # Create new figures
        self.anim_fig = self.create_animation_figure(self.results)
        self.plots_fig = self.create_plots_figure(self.results)
        
        # Check if we are in a lock-in situation and warn the user
        self.check_lock_in_condition()
        
        # Reset animation state
        self.animation.reset()
        
        # Clear output and redisplay
        self.output.clear_output(wait=True)
        with self.output:
            self.display_figures()
            
            # Display statistics
            stats_html = f"""
            <div style="margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                <h3>Simulation Statistics</h3>
                <table style="width: 100%;">
                    <tr>
                        <td style="width: 50%;"><b>Mean Error:</b> {self.results['mean_error']:.3e} rad/s</td>
                        <td><b>Std Deviation:</b> {self.results['std_error']:.3e} rad/s</td>
                    </tr>
                    <tr>
                        <td><b>Max Error:</b> {self.results['max_error']:.3e} rad/s</td>
                        <td><b>Lock-in Threshold:</b> {self.results['lock_in_threshold']:.3e} rad/s</td>
                    </tr>
                    <tr>
                        <td><b>Dithering:</b> {'Enabled' if self.results['dithering_enabled'] else 'Disabled'}</td>
                        <td><b>Cavity Shape:</b> {self.results['cavity_shape']}</td>
                    </tr>
                </table>
            </div>
            """
            display(widgets.HTML(stats_html))
            
    def display_figures(self):
        """Display the figures."""
        display(self.anim_fig)
        display(self.plots_fig)
        
    def save_diagnostics(self):
        """Save diagnostic information to a file."""
        try:
            # Create diagnostics directory if it doesn't exist
            diag_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'notebooks', 'diagnostics')
            os.makedirs(diag_dir, exist_ok=True)
            
            # Create a timestamp for the filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"rlg_diagnostics_{timestamp}"
            
            # Save parameters and results to JSON file
            diag_data = {
                "parameters": self.ring_laser_gyro.params,
                "statistics": {
                    "mean_error": float(self.results.get('mean_error', 0)),
                    "std_error": float(self.results.get('std_error', 0)),
                    "max_error": float(self.results.get('max_error', 0)),
                    "lock_in_threshold": float(self.results.get('lock_in_threshold', 0))
                },
                "simulation_info": {
                    "time_points": len(self.results['t']),
                    "total_simulation_time": float(self.results['t'][-1]),
                    "cavity_shape": self.results['cavity_shape'],
                    "cavity_area": float(self.results['cavity_area']),
                    "scale_factor": float(self.results['scale_factor'])
                }
            }
            
            # Write to JSON file
            json_path = os.path.join(diag_dir, f"{base_filename}.json")
            with open(json_path, 'w') as f:
                json.dump(diag_data, f, indent=2)
                
            # Save key time series data to CSV for analysis
            csv_path = os.path.join(diag_dir, f"{base_filename}.csv")
            with open(csv_path, 'w') as f:
                # Write header
                f.write("time,phase_difference,theoretical_rotation_rate,measured_rotation_rate,error,photodiode1,photodiode2\n")
                
                # Write data rows
                for i in range(len(self.results['t'])):
                    f.write(f"{self.results['t'][i]},{self.results['phase_difference'][i]},{self.results['theoretical_rotation_rate'][i]},")
                    f.write(f"{self.results['measured_rotation_rate'][i]},{self.results['error'][i]},")
                    f.write(f"{self.results['photodiode1'][i]},{self.results['photodiode2'][i]}\n")
            
            # Save diagnostic plots
            plt_path = os.path.join(diag_dir, f"{base_filename}_plots.png")
            self.save_diagnostic_plots(plt_path)
            
            # Log information about the animation update
            log_path = os.path.join(diag_dir, f"{base_filename}_log.txt")
            with open(log_path, 'w') as f:
                f.write(f"Ring Laser Gyroscope Simulation Diagnostic Log\n")
                f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"Animation Information:\n")
                f.write(f"  - Current Frame: {self.animation.current_frame}\n")
                f.write(f"  - Total Frames: {len(self.results['t'])}\n")
                f.write(f"  - Animation Speed: {self.controls['animation_speed'].value}\n\n")
                
                f.write(f"3D Visualization Status:\n")
                if hasattr(self, 'anim_fig'):
                    f.write(f"  - 3D Figure initialized: Yes\n")
                    f.write(f"  - Number of traces: {len(self.anim_fig.data)}\n")
                    
                    # Log beam position data for first and last frame
                    f.write(f"\nBeam Position Data (First Frame):\n")
                    f.write(f"  - CW Beam: {self.results['cw_beam_positions'][0][0]}\n")
                    f.write(f"  - CCW Beam: {self.results['ccw_beam_positions'][0][0]}\n")
                    
                    f.write(f"\nBeam Position Data (Last Frame):\n")
                    last_idx = len(self.results['t']) - 1
                    f.write(f"  - CW Beam: {self.results['cw_beam_positions'][last_idx][0]}\n")
                    f.write(f"  - CCW Beam: {self.results['ccw_beam_positions'][last_idx][0]}\n")
                else:
                    f.write(f"  - 3D Figure initialized: No\n")
                
                f.write(f"\nLissajous Analysis:\n")
                # Check if there's movement in the Lissajous figure
                pd1 = self.results['photodiode1']
                pd2 = self.results['photodiode2']
                
                # Calculate the range of the Lissajous pattern
                pd1_range = np.max(pd1) - np.min(pd1)
                pd2_range = np.max(pd2) - np.min(pd2)
                
                f.write(f"  - PD1 range: {pd1_range:.6f}\n")
                f.write(f"  - PD2 range: {pd2_range:.6f}\n")
                
                if pd1_range < 0.01 or pd2_range < 0.01:
                    f.write(f"  - WARNING: Very small range in Lissajous figure. May be in lock-in state.\n")
                    f.write(f"  - Rotation rate: {self.results['rotation_rate']}\n")
                    f.write(f"  - Lock-in threshold: {self.results['lock_in_threshold']}\n")
                    f.write(f"  - Dithering enabled: {self.results['dithering_enabled']}\n")
                    
            # Display confirmation to user
            self.output.clear_output(wait=True)
            with self.output:
                self.display_figures()
                display(HTML(f"<div style='background-color: #d4edda; color: #155724; "
                             f"padding: 10px; border-radius: 5px; margin-top: 10px;'>"
                             f"Diagnostic data saved to:<br>"
                             f"<code>{json_path}</code><br>"
                             f"<code>{csv_path}</code><br>"
                             f"<code>{plt_path}</code><br>"
                             f"<code>{log_path}</code>"
                             f"</div>"))
                
                # Display statistics
                stats_html = f"""
                <div style="margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                    <h3>Simulation Statistics</h3>
                    <table style="width: 100%;">
                        <tr>
                            <td style="width: 50%;"><b>Mean Error:</b> {self.results['mean_error']:.3e} rad/s</td>
                            <td><b>Std Deviation:</b> {self.results['std_error']:.3e} rad/s</td>
                        </tr>
                        <tr>
                            <td><b>Max Error:</b> {self.results['max_error']:.3e} rad/s</td>
                            <td><b>Lock-in Threshold:</b> {self.results['lock_in_threshold']:.3e} rad/s</td>
                        </tr>
                        <tr>
                            <td><b>Dithering:</b> {'Enabled' if self.results['dithering_enabled'] else 'Disabled'}</td>
                            <td><b>Cavity Shape:</b> {self.results['cavity_shape']}</td>
                        </tr>
                    </table>
                </div>
                """
                display(HTML(stats_html))
                
        except Exception as e:
            # Display error message
            self.output.clear_output(wait=True)
            with self.output:
                self.display_figures()
                display(HTML(f"<div style='background-color: #f8d7da; color: #721c24; "
                             f"padding: 10px; border-radius: 5px; margin-top: 10px;'>"
                             f"Error saving diagnostic data: {str(e)}</div>"))
                
                import traceback
                print(f"Error details:\n{traceback.format_exc()}")
    
    def save_diagnostic_plots(self, filepath):
        """Save diagnostic plots to a file."""
        # Create a figure with subplots
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot 1: Phase difference and rotation rates
        axs[0, 0].plot(self.results['t'], self.results['phase_difference'], 'b-', label='Phase Difference')
        axs[0, 0].set_xlabel('Time (s)')
        axs[0, 0].set_ylabel('Phase Difference (rad)', color='blue')
        axs[0, 0].tick_params(axis='y', labelcolor='blue')
        axs[0, 0].grid(True)
        
        # Add twin axis for rotation rates
        ax2 = axs[0, 0].twinx()
        ax2.plot(self.results['t'], self.results['theoretical_rotation_rate'], 'g-', label='Theoretical Rate')
        ax2.plot(self.results['t'], self.results['measured_rotation_rate'], 'r-', label='Measured Rate')
        ax2.set_ylabel('Rotation Rate (rad/s)', color='green')
        ax2.tick_params(axis='y', labelcolor='green')
        
        # Combine legends
        lines1, labels1 = axs[0, 0].get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        axs[0, 0].legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        axs[0, 0].set_title('Phase Difference and Rotation Rates')
        
        # Plot 2: Error
        axs[0, 1].plot(self.results['t'], self.results['error'], 'r-')
        axs[0, 1].set_xlabel('Time (s)')
        axs[0, 1].set_ylabel('Error (rad/s)')
        axs[0, 1].grid(True)
        axs[0, 1].set_title('Measurement Error')
        
        # Plot 3: Lissajous figure
        axs[1, 0].plot(self.results['photodiode1'], self.results['photodiode2'], 'b-')
        axs[1, 0].set_xlabel('PD1 Signal (cos)')
        axs[1, 0].set_ylabel('PD2 Signal (sin)')
        axs[1, 0].set_aspect('equal')
        axs[1, 0].grid(True)
        axs[1, 0].set_title('Lissajous Figure')
        
        # Add unit circle reference
        theta = np.linspace(0, 2*np.pi, 100)
        axs[1, 0].plot(np.cos(theta), np.sin(theta), 'k--', alpha=0.3)
        
        # Plot 4: Photodiode signals
        axs[1, 1].plot(self.results['t'], self.results['photodiode1'], 'r-', label='PD1 (cos)')
        axs[1, 1].plot(self.results['t'], self.results['photodiode2'], 'b-', label='PD2 (sin)')
        axs[1, 1].plot(self.results['t'], self.results['interference_intensity'], 'purple', alpha=0.5, label='Interference')
        axs[1, 1].set_xlabel('Time (s)')
        axs[1, 1].set_ylabel('Signal')
        axs[1, 1].grid(True)
        axs[1, 1].legend()
        axs[1, 1].set_title('Photodiode Signals')
        
        # Add title with key parameters
        fig.suptitle(f"Ring Laser Gyro Diagnostics\n" 
                   f"Rot. Rate: {self.results['rotation_rate']:.3f} rad/s, " 
                   f"Dithering: {'On' if self.results['dithering_enabled'] else 'Off'}, " 
                   f"Shape: {self.results['cavity_shape']}")
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(filepath, dpi=150)
        plt.close(fig)
    
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

def create_interactive_ring_laser_gyro():
    """Create and display an interactive ring laser gyroscope simulation."""
    sim = InteractiveRingLaserGyro()
    sim.display()
    return sim
