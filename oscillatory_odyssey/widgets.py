"""Widget creation and management for pendulum interface."""

import numpy as np
import ipywidgets as widgets

def create_parameter_widgets():
    """Create all parameter control widgets."""
    controls = {}
    
    # Initial conditions
    controls['theta0'] = widgets.FloatSlider(
        value=0.1,
        min=0.0,
        max=np.pi/2,
        step=0.05,
        description='Initial angle (rad)',
        continuous_update=False
    )
    
    # System parameters
    controls['L0'] = widgets.FloatSlider(
        value=2.0,
        min=0.5,
        max=5.0,
        step=0.1,
        description='Base length (m)',
        continuous_update=False
    )
    
    controls['delta_L'] = widgets.FloatSlider(
        value=0.15,
        min=0.0,
        max=1.0,
        step=0.05,
        description='Length change (m)',
        continuous_update=False
    )
    
    controls['pumping_freq'] = widgets.FloatSlider(
        value=0.705,
        min=0.1,
        max=3.0,
        step=0.1,
        description='Pump freq (Hz)',
        continuous_update=False,
        readout_format='.3f',
        disabled=True
    )
    
    controls['damping'] = widgets.FloatSlider(
        value=0.1,
        min=0.0,
        max=1.0,
        step=0.05,
        description='Damping',
        continuous_update=False
    )
    
    # Simulation controls
    controls['T'] = widgets.FloatSlider(
        value=30.0,
        min=5.0,
        max=30.0,
        step=1.0,
        description='Sim time (s)',
        continuous_update=False
    )
    
    controls['dt'] = widgets.FloatSlider(
        value=0.03,
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
    
    # Animation saving controls
    controls['save_fps'] = widgets.FloatSlider(
        value=30.0,
        min=5.0,
        max=60.0,
        step=5.0,
        description='Save FPS',
        style={'description_width': 'initial'},
        continuous_update=False
    )
    
    # Resonance selection
    controls['resonance'] = widgets.RadioButtons(
        options=['Off', '1st (2ω₀)', '2nd (ω₀)'],
        value='1st (2ω₀)',
        description='Resonance:',
        style={'description_width': 'initial'}
    )
    
    # Resonance info display
    controls['resonance_info'] = widgets.HTML(
        value='Loading resonance information...',
        description='Resonance Info:',
        style={'description_width': 'initial'}
    )
    
    # Pumping strategy
    controls['pumping_strategy'] = widgets.Dropdown(
        options=['sinusoidal', 'square', 'adaptive'],
        value='sinusoidal',
        description='Pump strategy'
    )
    
    return controls

def create_control_buttons():
    """Create simulation control buttons."""
    buttons = {}
    
    buttons['simulate'] = widgets.Button(description='Simulate')
    buttons['play'] = widgets.Button(description='Play')
    buttons['reset'] = widgets.Button(description='Reset')
    buttons['save'] = widgets.Button(description='Save Video')
    
    return buttons

def create_control_panel(controls, buttons):
    """Create the main control panel layout."""
    # Parameter controls
    param_controls = widgets.VBox([
        widgets.HBox([controls['theta0'], controls['L0']]),
        widgets.HBox([controls['delta_L'], controls['pumping_freq']]),
        widgets.HBox([controls['damping'], controls['T']]),
        widgets.HBox([controls['dt'], controls['animation_speed']]),
        widgets.HBox([controls['pumping_strategy'], controls['save_fps']]),
        widgets.HBox([controls['resonance'], controls['resonance_info']])
    ])
    
    # Button controls
    button_controls = widgets.HBox([
        buttons['simulate'],
        buttons['play'],
        buttons['reset'],
        buttons['save']
    ])
    
    return widgets.VBox([param_controls, button_controls])