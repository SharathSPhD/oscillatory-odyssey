# Pendulum Module API Reference

```{eval-rst}
.. automodule:: oscillatory_odyssey.pendulum
   :members:
   :undoc-members:
   :show-inheritance:
```

## `ParametricPendulum` Class

The `ParametricPendulum` class is the core of the Oscillatory Odyssey package. It models a pendulum with a time-varying length, similar to a playground swing being pumped by a child.

### Key Features

- Configurable physical parameters (length, mass, damping, etc.)
- Multiple pumping strategies (sinusoidal, square wave, adaptive)
- Energy calculation and analysis
- Integration with visualization tools

### Usage Example

```python
from oscillatory_odyssey.pendulum import ParametricPendulum

# Create a pendulum with default parameters
pendulum = ParametricPendulum()

# Customize parameters
pendulum.params["L0"] = 2.5  # Base length (m)
pendulum.params["delta_L"] = 0.5  # Length variation (m)
pendulum.params["pumping_strategy"] = "sinusoidal"
pendulum.params["resonant_tuning"] = True  # Use optimal frequency

# Run simulation
results = pendulum.simulate()

# Access results
time = results["time"]
theta = results["theta"]
energy = results["total_energy"]
```

### Configuration Parameters

The `ParametricPendulum` class accepts the following parameters:

#### Physical Parameters

- `g`: Gravitational acceleration (m/s²)
- `L0`: Base pendulum length (m)
- `delta_L`: Change in length during pumping (m)
- `m`: Mass (kg)
- `damping`: Damping coefficient

#### Pumping Parameters

- `pumping_freq`: Frequency of length change (Hz)
- `pumping_phase`: Phase offset for pumping (radians)
- `pumping_strategy`: Strategy for length variation (sinusoidal, square, adaptive)
- `standing_time`: Fraction of half-period to stand (for square wave)
- `pumping_amp_factor`: Amplitude factor for pumping
- `resonant_tuning`: Whether to tune pumping to resonant frequency
- `adaptive_threshold`: Threshold for adaptive pumping (radians)

#### Initial Conditions

- `theta0`: Initial angle (radians)
- `omega0`: Initial angular velocity (radians/s)

#### Simulation Parameters

- `T`: Total simulation time (s)
- `dt`: Time step for output (s)
- `method`: Integration method
- `rtol`: Relative tolerance for solver
- `atol`: Absolute tolerance for solver
