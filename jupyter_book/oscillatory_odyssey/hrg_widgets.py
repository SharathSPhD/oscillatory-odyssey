"""Widget creation and management for Hemispherical Resonator Gyroscope simulation."""

import ipywidgets as widgets

def create_parameter_widgets():
    """Create all parameter control widgets for the HRG simulation.
    
    Returns:
        dict: Dictionary containing all control widgets
    """
    controls = {}
    
    # Oscillation parameters
    controls['natural_frequency'] = widgets.IntSlider(
        value=10000,
        min=5000,
        max=20000,
        step=100,
        description='Natural frequency (Hz)',
        style={'description_width': 'initial'},
        continuous_update=False
    )
    
    controls['damping_ratio'] = widgets.FloatLogSlider(
        value=1e-4,
        base=10,
        min=-6,  # 10^-6
        max=-2,  # 10^-2
        step=0.1,
        description='Damping ratio',
        style={'description_width': 'initial'},
        continuous_update=False
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
    
    controls['bryan_factor'] = widgets.FloatSlider(
        value=0.3,
        min=0.1,
        max=0.5,
        step=0.01,
        description='Bryan factor',
        style={'description_width': 'initial'},
        continuous_update=False
    )
    
    # Frequency mismatch (anisotropy)
    controls['frequency_mismatch'] = widgets.FloatSlider(
        value=0.0,
        min=-0.01,
        max=0.01,
        step=0.0001,
        description='Frequency mismatch',
        style={'description_width': 'initial'},
        continuous_update=False
    )
    
    # Excitation parameters
    controls['parametric_excitation_enabled'] = widgets.Checkbox(
        value=True,
        description='Enable parametric excitation',
        style={'description_width': 'initial'},
        disabled=False
    )
    
    controls['parametric_excitation_amp'] = widgets.FloatLogSlider(
        value=0.001,
        base=10,
        min=-4,  # 10^-4
        max=-1,  # 10^-1
        step=0.1,
        description='Excitation amplitude',
        style={'description_width': 'initial'},
        continuous_update=False
    )
    
    controls['cubic_stiffness'] = widgets.FloatLogSlider(
        value=0.01,
        base=10,
        min=-3,  # 10^-3
        max=0,  # 10^0
        step=0.1,
        description='Cubic stiffness',
        style={'description_width': 'initial'},
        continuous_update=False
    )
    
    # Initial conditions
    controls['x0'] = widgets.FloatSlider(
        value=1.0,
        min=0.0,
        max=2.0,
        step=0.1,
        description='Initial x',
        style={'description_width': 'initial'},
        continuous_update=False
    )
    
    controls['y0'] = widgets.FloatSlider(
        value=0.0,
        min=-2.0,
        max=2.0,
        step=0.1,
        description='Initial y',
        style={'description_width': 'initial'},
        continuous_update=False
    )
    
    # Error and noise modeling
    controls['noise_enabled'] = widgets.Checkbox(
        value=True,
        description='Enable noise',
        style={'description_width': 'initial'},
        disabled=False
    )
    
    controls['bias_drift_enabled'] = widgets.Checkbox(
        value=True,
        description='Enable bias drift',
        style={'description_width': 'initial'},
        disabled=False
    )
    
    controls['bias_drift_sigma'] = widgets.FloatLogSlider(
        value=1e-6,
        base=10,
        min=-8,  # 10^-8
        max=-4,   # 10^-4
        step=0.5,
        description='Drift coefficient',
        style={'description_width': 'initial'},
        continuous_update=False
    )
    
    # Simulation controls
    controls['T'] = widgets.FloatSlider(
        value=5.0,
        min=1.0,
        max=20.0,
        step=1.0,
        description='Sim time (s)',
        continuous_update=False
    )
    
    controls['output_dt'] = widgets.FloatLogSlider(
        value=5e-4,
        base=10,
        min=-4,  # 10^-4
        max=-2,  # 10^-2
        step=0.2,
        description='Output step (s)',
        continuous_update=False
    )
    
    controls['animation_speed'] = widgets.FloatSlider(
        value=5.0,
        min=1.0,
        max=20.0,
        step=1.0,
        description='Animation speed',
        continuous_update=False
    )
    
    # Visualization parameters
    controls['mode_shape_amplitude'] = widgets.FloatSlider(
        value=0.3,
        min=0.1,
        max=1.0,
        step=0.1,
        description='Mode amplitude',
        style={'description_width': 'initial'},
        continuous_update=False
    )
    
    # Information displays
    controls['gyro_display'] = widgets.HTML(
        value='Loading...',
        description='HRG info:',
        style={'description_width': 'initial'}
    )
    
    return controls

def create_control_buttons():
    """Create simulation control buttons.
    
    Returns:
        dict: Dictionary containing all control buttons
    """
    buttons = {}
    
    buttons['simulate'] = widgets.Button(description='Simulate')
    buttons['play'] = widgets.Button(description='Play')
    buttons['reset'] = widgets.Button(description='Reset')
    buttons['save'] = widgets.Button(description='Save Video')
    
    return buttons

def create_control_panel(controls, buttons):
    """Create the main control panel layout combining controls and buttons.
    
    Args:
        controls: Dictionary of control widgets
        buttons: Dictionary of control buttons
        
    Returns:
        widgets.VBox: Complete control panel
    """
    # Basic parameters tab
    basic_tab = widgets.VBox([
        widgets.HBox([controls['rotation_rate'], controls['bryan_factor']]),
        widgets.HBox([controls['frequency_mismatch'], controls['damping_ratio']]),
        widgets.HBox([controls['parametric_excitation_enabled'], controls['parametric_excitation_amp']]),
        widgets.HBox([controls['x0'], controls['y0']]),
        widgets.HBox([controls['gyro_display']])
    ])
    
    # Advanced parameters tab
    advanced_tab = widgets.VBox([
        widgets.HBox([controls['natural_frequency'], controls['cubic_stiffness']]),
        widgets.HBox([controls['noise_enabled'], controls['bias_drift_enabled']]),
        widgets.HBox([controls['bias_drift_sigma']]),
        widgets.HBox([controls['T'], controls['output_dt']]),
        widgets.HBox([controls['animation_speed'], controls['mode_shape_amplitude']])
    ])
    
    # Tab layout
    tab = widgets.Tab()
    tab.children = [basic_tab, advanced_tab]
    tab.set_title(0, 'Basic Settings')
    tab.set_title(1, 'Advanced Settings')
    
    # Button controls
    button_controls = widgets.HBox([
        buttons['simulate'],
        buttons['play'],
        buttons['reset'],
        buttons['save']
    ])
    
    return widgets.VBox([tab, button_controls])
