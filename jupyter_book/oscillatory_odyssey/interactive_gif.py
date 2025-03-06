"""Interactive pendulum simulation with GIF export functionality."""

import numpy as np
from IPython.display import display
import ipywidgets as widgets
import os
from .pendulum import ParametricPendulum
from .widgets import create_parameter_widgets, create_control_buttons, create_control_panel
from .figures import create_animation_figure, create_plots_figure, update_animation_frame
from .animation import AnimationController
from .gif_saver import save_animation_as_gif

class InteractivePendulumWithGif:
    """Interactive interface for pendulum simulation with GIF export capability."""
    
    def __init__(self):
        """Initialize the interactive pendulum interface."""
        self.pendulum = ParametricPendulum()
        self.setup_interface()
        
        # Show resonance info immediately
        self.update_resonance_info()
        
    def setup_interface(self):
        """Set up the interactive interface components."""
        # Create widgets and buttons
        self.controls = create_parameter_widgets()
        self.buttons = create_control_buttons()
        
        # Add GIF button
        self.buttons['gif'] = widgets.Button(
            description='Save GIF',
            button_style='success',
            tooltip='Save animation as GIF'
        )
        
        # Set up button callbacks
        self.buttons['simulate'].on_click(self.update_simulation)
        self.buttons['play'].on_click(self.toggle_animation)
        self.buttons['reset'].on_click(self.reset_animation)
        self.buttons['save'].on_click(self.save_animation)
        self.buttons['gif'].on_click(self.save_gif)
        
        # Set up parameter callbacks
        self.controls['L0'].observe(self.update_resonance_info, names='value')
        self.controls['resonance'].observe(self.update_resonance, names='value')
        self.controls['animation_speed'].observe(self.update_animation_speed, names='value')
        
        # Create output area
        self.output = widgets.Output()
        
        # Set up animation controller
        self.animation = AnimationController(self.update_frame)
        
        # Apply initial resonance setting
        current_resonance = self.controls['resonance'].value
        if current_resonance != 'Off':
            self.controls['pumping_freq'].disabled = True
        
    def calculate_resonance(self):
        """Calculate resonant frequencies based on current parameters."""
        L0 = self.controls['L0'].value
        g = self.pendulum.params['g']
        
        # Natural frequency
        omega_n = np.sqrt(g/L0)  # rad/s
        
        # First parametric resonance (2ω₀)
        freq_1st = omega_n/(np.pi)  # Hz
        
        # Second parametric resonance (ω₀)
        freq_2nd = omega_n/(2*np.pi)  # Hz
        
        return freq_1st, freq_2nd
        
    def update_resonance_info(self, change=None):
        """Update resonance information display."""
        freq_1st, freq_2nd = self.calculate_resonance()
        self.controls['resonance_info'].value = (
            f"Resonant frequencies:<br>"
            f"1st (2ω₀): {freq_1st:.3f} Hz (Principal)<br>"
            f"2nd (ω₀): {freq_2nd:.3f} Hz (Secondary)"
        )
        
        # Update frequency if resonance is selected
        current_resonance = self.controls['resonance'].value
        if current_resonance == '1st (2ω₀)':
            self.controls['pumping_freq'].value = freq_1st
            self.controls['pumping_freq'].disabled = True
        elif current_resonance == '2nd (ω₀)':
            self.controls['pumping_freq'].value = freq_2nd
            self.controls['pumping_freq'].disabled = True
        else:
            self.controls['pumping_freq'].disabled = False
            
    def update_resonance(self, change):
        """Update pumping frequency based on resonance selection."""
        freq_1st, freq_2nd = self.calculate_resonance()
        
        # First enable/disable the frequency slider based on selection
        if change['new'] == 'Off':
            self.controls['pumping_freq'].disabled = False
        else:
            self.controls['pumping_freq'].disabled = True
            
            # Then set appropriate frequency
            if change['new'] == '1st (2ω₀)':
                self.controls['pumping_freq'].value = freq_1st
            elif change['new'] == '2nd (ω₀)':
                self.controls['pumping_freq'].value = freq_2nd
            
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
    
    def reset_animation(self, _=None):
        """Reset animation to initial frame and controls to defaults."""
        if hasattr(self, 'results'):
            # Reset animation
            self.animation.reset()
            self.buttons['play'].description = 'Play'
            
            # Reset control values to defaults
            default_pendulum = ParametricPendulum()
            
            # Reset parameters to the specific requested values
            specific_values = {
                'theta0': 0.1,
                'L0': 2.0,
                'delta_L': 0.15,
                'pumping_freq': 0.705,
                'damping': 0.1,
                'T': 30.0,
                'dt': 0.03,
                'pumping_strategy': 'sinusoidal'
            }
            
            for param, value in specific_values.items():
                if param in self.controls:
                    self.controls[param].value = value
            
            # Reset resonance to 1st
            self.controls['resonance'].value = '1st (2ω₀)'
            
            # Make sure frequency is disabled with resonance set
            self.controls['pumping_freq'].disabled = True
            
            # Update UI after reset
            self.update_resonance_info()
    
    def save_animation(self, _=None):
        """Save animation to HTML file and provide download link."""
        # Implementation retained but not used in this version
        pass
    
    def save_gif(self, _=None):
        """Save animation as GIF file."""
        if hasattr(self, 'results'):
            # Stop animation if running
            if self.animation.running:
                self.toggle_animation()
            
            # Reset to start
            self.animation.reset()
            
            # Create save status display
            if not hasattr(self, 'save_status'):
                self.save_status = widgets.HTML('')
                display(self.save_status)
            
            # Create output path
            output_path = "pendulum_animation.gif"
            
            # Save as GIF
            result = save_animation_as_gif(self.anim_fig, self.results, output_path)
            self.save_status.value = result.value
            
    def update_simulation(self, _=None):
        """Update simulation with current widget values."""
        # Update pendulum parameters
        for param, widget in self.controls.items():
            if param in ['resonance', 'resonance_info', 'animation_speed']:
                continue
            self.pendulum.params[param] = widget.value
            
        # Stop any running animation
        if self.animation.running:
            self.toggle_animation()
            
        # Run simulation
        self.results = self.pendulum.simulate()
        
        # Create new figures
        self.anim_fig = create_animation_figure(self.results)
        self.plots_fig = create_plots_figure(self.results)
        
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
        control_panel = create_control_panel(self.controls, self.buttons)
        
        # Display interface
        display(control_panel)
        display(self.output)
        
        # Run initial simulation
        if not hasattr(self, 'results'):
            self.update_simulation()

def create_interactive_pendulum_with_gif():
    """Create and display an interactive pendulum simulation with GIF export."""
    sim = InteractivePendulumWithGif()
    sim.display()
    return sim