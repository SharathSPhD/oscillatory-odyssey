# Visualization Module API Reference

```{eval-rst}
.. automodule:: oscillatory_odyssey.visualization
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The visualization module provides functions for creating interactive visualizations of the parametric pendulum simulations. It uses Plotly for creating animated pendulum visualizations, time series plots, and interactive widgets.

## Key Functions

### `create_pendulum_animation`

Creates an animated visualization of the pendulum motion.

```python
from oscillatory_odyssey.pendulum import ParametricPendulum
from oscillatory_odyssey.visualization import create_pendulum_animation

# Create and run a simulation
pendulum = ParametricPendulum()
results = pendulum.simulate()

# Create the animation
fig = create_pendulum_animation(results, fps=30, show_trace=True)

# Display in a notebook
fig.show()
```

### `create_time_series_plots`

Creates time series plots of various aspects of the pendulum motion:
- Angle vs time
- Angular velocity vs time
- Length vs time
- Phase space (angle vs angular velocity)
- Energy vs time

```python
from oscillatory_odyssey.visualization import create_time_series_plots

# Create the plots using simulation results
fig = create_time_series_plots(results)

# Display in a notebook
fig.show()
```

### `create_interactive_simulation_widget`

Creates interactive widgets to control the pendulum simulation parameters. This is particularly useful in Jupyter notebooks, allowing users to experiment with different parameters and see the effects in real-time.

```python
from oscillatory_odyssey.visualization import create_interactive_simulation_widget
from oscillatory_odyssey.pendulum import ParametricPendulum

# Create the interactive widget
widget = create_interactive_simulation_widget(ParametricPendulum)

# Display in a notebook
from IPython.display import display
display(widget)
```

## Customization Options

### Animation Options

- `fps`: Frames per second for the animation
- `show_trace`: Whether to show a trace of the pendulum's path
- `max_trace_points`: Maximum number of points to show in the trace

### Time Series Plot Options

The time series plots include:
- Angle vs Time
- Angular Velocity vs Time
- Length vs Time
- Phase Space (angle vs angular velocity)
- Energy vs Time (kinetic, potential, and total)

### Interactive Widget Controls

The interactive simulation widget provides controls for:
- Base length
- Length variation amplitude
- Damping coefficient
- Initial angle
- Pumping frequency
- Pumping strategy
- Simulation time
- Resonant tuning toggle
