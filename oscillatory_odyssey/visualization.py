"""
Visualization module for the parametric pendulum simulation.

This module provides functions to visualize the pendulum motion,
create animations, and generate interactive plots.
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display


def create_pendulum_animation(results, fps=30, show_trace=True, max_trace_points=100):
    """
    Create an animated visualization of the pendulum motion.
    
    Parameters:
    -----------
    results : dict
        Simulation results from ParametricPendulum.simulate()
    fps : int, optional
        Frames per second for the animation
    show_trace : bool, optional
        Whether to show a trace of the pendulum's path
    max_trace_points : int, optional
        Maximum number of points to show in the trace
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Animation figure that can be displayed in a notebook
    """
    # Extract data
    t = results["time"]
    theta = results["theta"]
    length = results["length"]
    
    # Calculate pendulum bob position at each time
    x = length * np.sin(theta)
    y = -length * np.cos(theta)
    
    # Create figure
    fig = go.Figure()
    
    # Determine the maximum dimensions for the plot
    max_length = np.max(length)
    max_x = np.max(np.abs(x)) * 1.1
    max_y = max_length * 1.1
    
    # Add initial pendulum (will be updated in frames)
    # The pendulum rod
    fig.add_trace(go.Scatter(
        x=[0, x[0]],
        y=[0, y[0]],
        mode='lines',
        line=dict(color='black', width=2),
        showlegend=False
    ))
    
    # The pendulum bob
    fig.add_trace(go.Scatter(
        x=[x[0]],
        y=[y[0]],
        mode='markers',
        marker=dict(color='red', size=12),
        showlegend=False
    ))
    
    # Add trace of the pendulum's path if requested
    if show_trace:
        fig.add_trace(go.Scatter(
            x=[],
            y=[],
            mode='lines',
            line=dict(color='rgba(200, 200, 200, 0.5)', width=1),
            showlegend=False
        ))
    
    # Create frames for animation
    frames = []
    for i in range(len(t)):
        frame_data = []
        
        # Pendulum rod for this frame
        frame_data.append(go.Scatter(
            x=[0, x[i]],
            y=[0, y[i]]
        ))
        
        # Pendulum bob for this frame
        frame_data.append(go.Scatter(
            x=[x[i]],
            y=[y[i]]
        ))
        
        # Trace for this frame (if enabled)
        if show_trace:
            # Calculate the start index to keep only max_trace_points
            start_idx = max(0, i - max_trace_points) if max_trace_points > 0 else 0
            frame_data.append(go.Scatter(
                x=x[start_idx:(i+1)],
                y=y[start_idx:(i+1)]
            ))
        
        frames.append(go.Frame(data=frame_data, name=f"frame{i}"))
    
    fig.frames = frames
    
    # Configure animation settings
    animation_settings = dict(
        frame=dict(duration=1000/fps, redraw=True),
        fromcurrent=True
    )
    
    # Add play and pause buttons
    fig.update_layout(
        updatemenus=[dict(
            type="buttons",
            buttons=[
                dict(label="Play",
                     method="animate",
                     args=[None, animation_settings]),
                dict(label="Pause",
                     method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=True), mode="immediate")])
            ],
            direction="left",
            pad=dict(r=10, t=10),
            showactive=False,
            x=0.1,
            xanchor="right",
            y=0,
            yanchor="top"
        )]
    )
    
    # Add slider for manual frame selection
    sliders = [dict(
        active=0,
        yanchor="top",
        xanchor="left",
        currentvalue=dict(
            font=dict(size=12),
            prefix="Time: ",
            suffix=" s",
            visible=True,
            xanchor="right"
        ),
        transition=dict(duration=300, easing="cubic-in-out"),
        pad=dict(b=10, t=50),
        len=0.9,
        x=0.1,
        y=0,
        steps=[dict(
            args=[[f"frame{i}"], dict(frame=dict(duration=0, redraw=True), mode="immediate")],
            label=f"{t[i]:.1f}",
            method="animate"
        ) for i in range(0, len(t), max(1, len(t)//20))]  # Only show ~20 steps on slider
    )]
    
    # Update layout
    fig.update_layout(
        sliders=sliders,
        title="Parametric Pendulum Animation",
        xaxis=dict(range=[-max_x, max_x], title="x position (m)"),
        yaxis=dict(range=[-max_y, 0.1], title="y position (m)"),
        width=700,
        height=500,
        showlegend=False,
        autosize=True,
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        hovermode="closest",
    )
    
    return fig


def create_time_series_plots(results):
    """
    Create time series plots of the pendulum motion.
    
    Parameters:
    -----------
    results : dict
        Simulation results from ParametricPendulum.simulate()
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Figure with time series plots
    """
    # Extract data
    t = results["time"]
    theta = results["theta"]
    omega = results["omega"]
    length = results["length"]
    ke = results["kinetic_energy"]
    pe = results["potential_energy"]
    te = results["total_energy"]
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=("Angle vs Time", "Angular Velocity vs Time", 
                        "Length vs Time", "Phase Space",
                        "Energy vs Time", "")
    )
    
    # Angle vs Time
    fig.add_trace(
        go.Scatter(x=t, y=theta, mode='lines', name='Angle'),
        row=1, col=1
    )
    
    # Angular Velocity vs Time
    fig.add_trace(
        go.Scatter(x=t, y=omega, mode='lines', name='Angular Velocity'),
        row=1, col=2
    )
    
    # Length vs Time
    fig.add_trace(
        go.Scatter(x=t, y=length, mode='lines', name='Length'),
        row=2, col=1
    )
    
    # Phase Space (theta vs omega)
    fig.add_trace(
        go.Scatter(x=theta, y=omega, mode='lines', name='Phase Space'),
        row=2, col=2
    )
    
    # Energy vs Time
    fig.add_trace(
        go.Scatter(x=t, y=ke, mode='lines', name='Kinetic Energy'),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=t, y=pe, mode='lines', name='Potential Energy'),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=t, y=te, mode='lines', name='Total Energy'),
        row=3, col=1
    )
    
    # Update layout
    fig.update_layout(
        title="Parametric Pendulum Time Series",
        height=800,
        width=1000,
        showlegend=True,
        legend=dict(x=1.0, y=0.5),
        autosize=True
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Time (s)", row=1, col=1)
    fig.update_yaxes(title_text="Angle (rad)", row=1, col=1)
    
    fig.update_xaxes(title_text="Time (s)", row=1, col=2)
    fig.update_yaxes(title_text="Angular Velocity (rad/s)", row=1, col=2)
    
    fig.update_xaxes(title_text="Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="Length (m)", row=2, col=1)
    
    fig.update_xaxes(title_text="Angle (rad)", row=2, col=2)
    fig.update_yaxes(title_text="Angular Velocity (rad/s)", row=2, col=2)
    
    fig.update_xaxes(title_text="Time (s)", row=3, col=1)
    fig.update_yaxes(title_text="Energy (J)", row=3, col=1)
    
    return fig


def create_interactive_simulation_widget(pendulum_class):
    """
    Create interactive widgets to control the pendulum simulation.
    
    Parameters:
    -----------
    pendulum_class : class
        The ParametricPendulum class
        
    Returns:
    --------
    ipywidgets.Widget
        Interactive widget for simulation control
    """
    # Create a pendulum instance to get default parameters
    pendulum = pendulum_class()
    
    # Create widgets for the main parameters
    L0_widget = widgets.FloatSlider(
        value=pendulum.params["L0"],
        min=0.5,
        max=5.0,
        step=0.1,
        description='Base Length (m):',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='.1f',
    )
    
    delta_L_widget = widgets.FloatSlider(
        value=pendulum.params["delta_L"],
        min=0.0,
        max=2.0,
        step=0.05,
        description='ΔL (m):',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='.2f',
    )
    
    damping_widget = widgets.FloatSlider(
        value=pendulum.params["damping"],
        min=0.0,
        max=1.0,
        step=0.01,
        description='Damping:',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='.2f',
    )
    
    theta0_widget = widgets.FloatSlider(
        value=pendulum.params["theta0"],
        min=-np.pi/2,
        max=np.pi/2,
        step=0.01,
        description='Initial Angle (rad):',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='.2f',
    )
    
    freq_widget = widgets.FloatSlider(
        value=pendulum.params["pumping_freq"],
        min=0.1,
        max=5.0,
        step=0.1,
        description='Pumping Freq (Hz):',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='.1f',
    )
    
    strategy_widget = widgets.Dropdown(
        options=['sinusoidal', 'square', 'adaptive'],
        value=pendulum.params["pumping_strategy"],
        description='Pumping Strategy:',
        disabled=False,
    )
    
    time_widget = widgets.FloatSlider(
        value=pendulum.params["T"],
        min=5.0,
        max=60.0,
        step=5.0,
        description='Simulation Time (s):',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='.1f',
    )
    
    resonant_widget = widgets.Checkbox(
        value=pendulum.params["resonant_tuning"],
        description='Use Resonant Frequency',
        disabled=False
    )
    
    # Animation controls
    play_button = widgets.Button(
        description='Play',
        button_style='success',
        tooltip='Play the animation',
        icon='play'
    )
    
    pause_button = widgets.Button(
        description='Pause',
        button_style='warning',
        tooltip='Pause the animation',
        icon='pause'
    )
    
    reset_button = widgets.Button(
        description='Reset',
        button_style='',
        tooltip='Reset the animation',
        icon='refresh'
    )
    
    # Create output areas
    info_output = widgets.Output(layout={'border': '1px solid #ddd', 'padding': '10px', 'height': '60px'})
    animation_output = widgets.Output(layout={'border': '1px solid #ddd', 'height': '550px'})
    plots_output = widgets.Output(layout={'border': '1px solid #ddd', 'height': '800px'})
    
    # Run button
    run_button = widgets.Button(
        description='Run Simulation',
        button_style='primary',
        tooltip='Run the simulation with current parameters',
        icon='play'
    )
    
    # Create a state management class to maintain simulation state
    class SimulationState:
        def __init__(self):
            self.results = None
            self.pendulum = None
            self.animation = None
            self.current_frame = 0
            self.is_playing = False
            self.timer = None
            self.fps = 30
        
        def run_simulation(self):
            # Get current parameter values
            L0 = L0_widget.value
            delta_L = delta_L_widget.value
            damping = damping_widget.value
            theta0 = theta0_widget.value
            freq = freq_widget.value
            strategy = strategy_widget.value
            time = time_widget.value
            resonant = resonant_widget.value
            
            # Create pendulum instance
            self.pendulum = pendulum_class()
            self.pendulum.params["L0"] = L0
            self.pendulum.params["delta_L"] = delta_L
            self.pendulum.params["damping"] = damping
            self.pendulum.params["theta0"] = theta0
            self.pendulum.params["pumping_freq"] = freq
            self.pendulum.params["pumping_strategy"] = strategy
            self.pendulum.params["T"] = time
            self.pendulum.params["resonant_tuning"] = resonant
            
            # If resonant tuning is enabled, calculate natural frequency
            if resonant:
                self.pendulum.omega_n = np.sqrt(self.pendulum.params["g"] / L0)
                self.pendulum.params["pumping_freq"] = self.pendulum.omega_n / np.pi
                with info_output:
                    info_output.clear_output(wait=True)
                    print(f"Resonant pumping frequency: {self.pendulum.params['pumping_freq']:.3f} Hz")
                # Update the freq widget without triggering callbacks
                freq_widget.value = self.pendulum.params["pumping_freq"]
            
            # Run simulation
            self.results = self.pendulum.simulate()
            self.current_frame = 0
            return self.results
        
        def create_animation_data(self):
            if self.results is None:
                return None
                
            # Extract data
            t = self.results["time"]
            theta = self.results["theta"]
            length = self.results["length"]
            
            # Calculate pendulum bob position at each time
            x = length * np.sin(theta)
            y = -length * np.cos(theta)
            
            # Create frames data
            frames_data = []
            for i in range(len(t)):
                frame = {
                    'time': t[i],
                    'x': x[i],
                    'y': y[i],
                    'rod_x': [0, x[i]],
                    'rod_y': [0, y[i]],
                    'trace_x': x[max(0, i-100):i+1],
                    'trace_y': y[max(0, i-100):i+1]
                }
                frames_data.append(frame)
            
            return frames_data
        
        def create_custom_animation(self):
            # Get animation data
            frames_data = self.create_animation_data()
            if frames_data is None:
                return
                
            # Get max dimensions for plot
            x_values = [frame['x'] for frame in frames_data]
            y_values = [frame['y'] for frame in frames_data]
            max_x = max(abs(min(x_values)), abs(max(x_values))) * 1.1
            max_y = abs(min(y_values)) * 1.1
            
            # Create figure
            fig = go.Figure()
            
            # Initial frame
            initial_frame = frames_data[0]
            
            # Add pendulum rod
            fig.add_trace(go.Scatter(
                x=initial_frame['rod_x'],
                y=initial_frame['rod_y'],
                mode='lines',
                line=dict(color='black', width=2),
                name='Rod'
            ))
            
            # Add pendulum bob
            fig.add_trace(go.Scatter(
                x=[initial_frame['x']],
                y=[initial_frame['y']],
                mode='markers',
                marker=dict(color='red', size=12),
                name='Bob'
            ))
            
            # Add trace
            fig.add_trace(go.Scatter(
                x=initial_frame['trace_x'],
                y=initial_frame['trace_y'],
                mode='lines',
                line=dict(color='rgba(200, 200, 200, 0.5)', width=1),
                name='Trace'
            ))
            
            # Update layout
            fig.update_layout(
                title="Parametric Pendulum Animation",
                xaxis=dict(range=[-max_x, max_x], title="x position (m)"),
                yaxis=dict(range=[-max_y, 0.1], title="y position (m)"),
                width=700,
                height=500,
                showlegend=False,
                autosize=True,
                margin=dict(l=50, r=50, b=50, t=50, pad=4),
                hovermode="closest",
            )
            
            self.animation_data = frames_data
            self.animation_figure = fig
            return fig
        
        def update_animation_frame(self, frame_idx=None):
            if self.animation_figure is None or self.animation_data is None:
                return
                
            if frame_idx is not None:
                self.current_frame = frame_idx
            
            if self.current_frame >= len(self.animation_data):
                self.current_frame = 0
                
            frame = self.animation_data[self.current_frame]
            
            with animation_output:
                # Update rod trace
                self.animation_figure.data[0].x = frame['rod_x']
                self.animation_figure.data[0].y = frame['rod_y']
                
                # Update bob position
                self.animation_figure.data[1].x = [frame['x']]
                self.animation_figure.data[1].y = [frame['y']]
                
                # Update trace
                self.animation_figure.data[2].x = frame['trace_x']
                self.animation_figure.data[2].y = frame['trace_y']
                
                # Update title to show time
                self.animation_figure.layout.title.text = f"Parametric Pendulum Animation (Time: {frame['time']:.2f}s)"
                
                # This would update the figure in the output
                if hasattr(self.animation_figure, 'update_layout'):
                    self.animation_figure.update_layout()
        
        def play_animation(self):
            if self.is_playing or self.animation_data is None:
                return
                
            self.is_playing = True
            
            def update_frame():
                if not self.is_playing:
                    return
                    
                self.current_frame += 1
                if self.current_frame >= len(self.animation_data):
                    self.current_frame = 0
                    
                self.update_animation_frame()
                
                # Schedule next update
                self.timer = setTimeout(update_frame, 1000/self.fps)
            
            # Start animation loop
            update_frame()
        
        def pause_animation(self):
            self.is_playing = False
            if self.timer:
                clearTimeout(self.timer)
                self.timer = None
        
        def reset_animation(self):
            self.current_frame = 0
            self.update_animation_frame()
        
        def update_displays(self):
            if self.results is None:
                return
                
            with animation_output:
                animation_output.clear_output(wait=True)
                fig = self.create_custom_animation()
                display(fig)
            
            with plots_output:
                plots_output.clear_output(wait=True)
                fig = create_time_series_plots(self.results)
                display(fig)
    
    # Create state manager
    state = SimulationState()
    
    # Define callback for run button
    def on_run_button_clicked(b):
        with info_output:
            info_output.clear_output(wait=True)
            print("Running simulation...")
        
        # Run simulation
        state.run_simulation()
        
        # Update displays
        state.update_displays()
        
        with info_output:
            info_output.clear_output(wait=True)
            if state.pendulum.params["resonant_tuning"]:
                print(f"Simulation complete! Resonant frequency: {state.pendulum.params['pumping_freq']:.3f} Hz")
            else:
                print("Simulation complete!")
    
    # Connect the run button to its callback
    run_button.on_click(on_run_button_clicked)
    
    # Animation control callbacks
    def on_play_clicked(b):
        state.play_animation()
        
    def on_pause_clicked(b):
        state.pause_animation()
        
    def on_reset_clicked(b):
        state.reset_animation()
    
    play_button.on_click(on_play_clicked)
    pause_button.on_click(on_pause_clicked)
    reset_button.on_click(on_reset_clicked)
    
    # Handle resonant checkbox changes
    def on_resonant_changed(change):
        if change['new']:
            # Calculate natural frequency based on current L0
            natural_freq = np.sqrt(pendulum.params["g"] / L0_widget.value) / (2*np.pi)
            freq_widget.value = 2 * natural_freq
            freq_widget.disabled = True
        else:
            freq_widget.disabled = False
    
    resonant_widget.observe(on_resonant_changed, names='value')
    
    # Create tabs for animation and plots
    tab = widgets.Tab()
    tab.children = [animation_output, plots_output]
    tab.set_title(0, 'Animation')
    tab.set_title(1, 'Plots')
    
    # Create the main layout
    parameters = widgets.VBox([
        widgets.HTML("<h3>Simulation Parameters</h3>"),
        widgets.HBox([L0_widget, delta_L_widget]),
        widgets.HBox([damping_widget, theta0_widget]),
        widgets.HBox([freq_widget, strategy_widget]),
        widgets.HBox([time_widget, resonant_widget]),
        widgets.HBox([run_button])
    ])
    
    animation_controls = widgets.HBox([
        widgets.HTML("<h4>Animation Controls:</h4>"),
        play_button, pause_button, reset_button
    ], layout={'padding': '10px 0'})
    
    # Main layout with parameters at the top
    main_layout = widgets.VBox([
        parameters,
        info_output,
        animation_controls,
        tab
    ])
    
    # Run initial simulation
    on_run_button_clicked(None)
    
    return main_layout
