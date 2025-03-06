"""Interactive Hemispherical Resonator Gyroscope simulation interface with dynamic visualization."""

import os
import numpy as np
from IPython.display import display, HTML
import ipywidgets as widgets

from .hemispherical_resonator_gyro import HemisphericalResonatorGyroSimulation
from .animation import AnimationController
from .hemispherical_resonator_gyro_video_saver import save_hrg_video

# Import modular components
from .hrg_widgets import create_parameter_widgets, create_control_buttons, create_control_panel
from .hrg_visualization import create_animation_figure, create_plots_figure, update_animation_frame
from .hrg_data_handler import (
    generate_statistics_html, 
    check_frequency_mismatch_warning,
    save_diagnostics, 
    update_gyro_display
)


class InteractiveHemisphericalResonatorGyro:
    """Interactive interface for Hemispherical Resonator Gyroscope simulation visualization."""
    
    def __init__(self):
        """Initialize the interactive HRG interface."""
        self.hrg = HemisphericalResonatorGyroSimulation()
        self.setup_interface()
        
    def setup_interface(self):
        """Set up the interactive interface components."""
        # Create widgets and buttons
        self.controls = create_parameter_widgets()
        self.buttons = create_control_buttons()
        
        # Set up button callbacks
        self.buttons['simulate'].on_click(self.update_simulation)
        self.buttons['play'].on_click(self.toggle_animation)
        self.buttons['reset'].on_click(self.reset_animation)
        self.buttons['save'].on_click(self.save_animation)
        
        # Set up parameter callbacks
        self.controls['rotation_rate'].observe(self.update_gyro_display, names='value')
        self.controls['bryan_factor'].observe(self.update_gyro_display, names='value')
        self.controls['parametric_excitation_enabled'].observe(self.toggle_excitation_controls, names='value')
        self.controls['animation_speed'].observe(self.update_animation_speed, names='value')
        
        # Create output area
        self.output = widgets.Output()
        
        # Set up animation controller
        self.animation = AnimationController(self.update_frame)
        
        # Initialize information displays
        self.update_gyro_display()
        
    def update_gyro_display(self, change=None):
        """Update HRG information display."""
        update_gyro_display(self.hrg, self.controls)
            
    def toggle_excitation_controls(self, change=None):
        """Enable or disable parametric excitation-related controls."""
        enabled = self.controls['parametric_excitation_enabled'].value
        self.controls['parametric_excitation_amp'].disabled = not enabled
        
    def update_animation_speed(self, change):
        """Update animation speed."""
        self.animation.set_speed(change['new'])
        
    def update_frame(self, frame):
        """Update animation frame."""
        if hasattr(self, 'results') and hasattr(self, 'anim_fig') and hasattr(self, 'plots_fig'):
            update_animation_frame(self.anim_fig, self.plots_fig, self.results, frame)
            
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
            success, message, file_paths = save_diagnostics(self.results, __file__)
            if not success:
                print(f"Warning: {message}")
    
    def reset_animation(self, _=None):
        """Reset animation to initial frame and controls to defaults."""
        if hasattr(self, 'results'):
            # Reset animation
            self.animation.reset()
            self.buttons['play'].description = 'Play'
            
            # Reset parameters to defaults
            default_hrg = HemisphericalResonatorGyroSimulation()
            
            # Reset parameters to specific requested values
            default_values = {
                'natural_frequency': 10000,
                'damping_ratio': 1e-4,
                'rotation_rate': 1.0,
                'bryan_factor': 0.3,
                'frequency_mismatch': 0.0,
                'parametric_excitation_enabled': True,
                'parametric_excitation_amp': 0.001,
                'cubic_stiffness': 0.01,
                'x0': 1.0,
                'y0': 0.0,
                'noise_enabled': True,
                'bias_drift_enabled': True,
                'bias_drift_sigma': 1e-6,
                'T': 5.0,
                'output_dt': 5e-4,
                'animation_speed': 5.0,
                'mode_shape_amplitude': 0.3
            }
            
            for param, value in default_values.items():
                if param in self.controls:
                    self.controls[param].value = value
            
            # Update displays
            self.update_gyro_display()
            
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
            output_path = f"hrg_animation_{timestamp}.mp4"
            
            # Clear output and show status
            self.output.clear_output(wait=True)
            
            # Save as video and display result in output area
            with self.output:
                # Create a dedicated HTML widget for save status
                save_status = widgets.HTML('Starting video save process...')
                display(save_status)
                
                # Save the animation using custom HRG video saver
                try:
                    # First, make sure we've run a simulation
                    if 'x' not in self.results:
                        save_status.value = f"<div style='color: red; font-weight: bold;'>Error: Please run the simulation before saving video</div>"
                        self.display_figures()
                        return
                        
                    # Update status
                    save_status.value = f"<div>Creating video with {len(self.results['t'])} frames...</div>"
                    
                    # Call the video saver
                    result = save_hrg_video(self.anim_fig, self.results, output_path)
                    display(result)
                    
                    # Save a copy of the diagnostic data
                    success, message, file_paths = save_diagnostics(self.results, __file__)
                    if not success:
                        print(f"Warning: {message}")
                    
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    save_status.value = f"<div style='color: red; font-weight: bold;'>Error saving video:</div><div>{str(e)}</div><pre>{error_details}</pre>"
                    
                    # Redisplay the figures
                    self.display_figures()
    
    def update_simulation(self, _=None):
        """Update simulation with current widget values."""
        # Update HRG parameters from controls
        for param, widget in self.controls.items():
            if param in ['gyro_display', 'animation_speed']:
                continue
            if param in self.hrg.params:
                self.hrg.params[param] = widget.value
            
        # Store parameters for animation
        self.params = self.hrg.params.copy()
        
        # Stop any running animation
        if self.animation.running:
            self.toggle_animation()
            
        # Run simulation and create figures with error handling
        try:
            self.results = self.hrg.simulate()
            
            # Create new figures
            self.anim_fig = create_animation_figure(self.results)
            self.plots_fig = create_plots_figure(self.results)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.output.clear_output(wait=True)
            with self.output:
                display(HTML(f"<div style='background-color: #f8d7da; color: #721c24; padding: 15px; "
                             f"border-radius: 4px; margin-bottom: 20px;'>"
                             f"<h3>Error in simulation:</h3><p>{str(e)}</p>"
                             f"<pre>{error_details}</pre></div>"))
            raise
        
        # Reset animation state
        self.animation.reset()
        
        # Clear output and redisplay
        self.output.clear_output(wait=True)
        with self.output:
            self.display_figures()
            
            # Check for warnings
            warning_html = check_frequency_mismatch_warning(self.results)
            if warning_html:
                display(HTML(warning_html))
            
            # Display statistics
            stats_html = generate_statistics_html(self.results)
            display(HTML(stats_html))
            
    def display_figures(self):
        """Display the figures."""
        display(self.anim_fig)
        display(self.plots_fig)
    
    def display(self):
        """Display the interactive interface."""
        # Create control panel
        control_panel = create_control_panel(self.controls, self.buttons)
        
        # Display interface
        display(control_panel)
        display(self.output)
        
        # Run initial simulation
        if not hasattr(self, 'results'):
            self.update_simulation()


def create_interactive_hemispherical_resonator_gyro():
    """Create and display an interactive hemispherical resonator gyroscope simulation."""
    sim = InteractiveHemisphericalResonatorGyro()
    sim.display()
    return sim
