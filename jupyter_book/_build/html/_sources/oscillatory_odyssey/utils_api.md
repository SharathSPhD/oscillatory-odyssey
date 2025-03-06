# Utilities Module API Reference

```{eval-rst}
.. automodule:: oscillatory_odyssey.utils
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The utils module provides helper functions for configuration management, data processing, and other common tasks used throughout the Oscillatory Odyssey package.

## Configuration Management

### `load_config`

Loads a configuration dictionary from a file. Supports YAML and JSON formats.

```python
from oscillatory_odyssey.utils import load_config

# Load a configuration from a YAML file
config = load_config('config/example_config.yaml')

# Use the configuration
print(f"Base length: {config['L0']} m")
print(f"Pumping strategy: {config['pumping_strategy']}")
```

### `save_config`

Saves a configuration dictionary to a file. Supports YAML and JSON formats.

```python
from oscillatory_odyssey.utils import save_config

# Create a configuration dictionary
config = {
    "L0": 2.5,
    "delta_L": 0.6,
    "pumping_strategy": "adaptive",
    "damping": 0.1
}

# Save to a YAML file
save_config(config, 'my_config.yaml')
```

### `generate_example_configs`

Generates example configuration files for different scenarios.

```python
from oscillatory_odyssey.utils import generate_example_configs

# Generate example configuration files in the specified directory
saved_files = generate_example_configs('my_configs')
print(f"Generated {len(saved_files)} configuration files")
```

## Data Management

### `export_results`

Exports simulation results to a NumPy compressed file.

```python
from oscillatory_odyssey.utils import export_results
from oscillatory_odyssey.pendulum import ParametricPendulum

# Run a simulation
pendulum = ParametricPendulum()
results = pendulum.simulate()

# Export the results
export_results(results, 'my_simulation.npz')
```

### `import_results`

Imports simulation results from a NumPy compressed file.

```python
from oscillatory_odyssey.utils import import_results

# Import previously saved results
results = import_results('my_simulation.npz')

# Use the results
import matplotlib.pyplot as plt
plt.plot(results['time'], results['theta'])
plt.xlabel('Time (s)')
plt.ylabel('Angle (rad)')
plt.show()
```

## Physics Calculations

### `calculate_parametric_resonance_frequency`

Calculates the parametric resonance frequency for a pendulum based on its length.

```python
from oscillatory_odyssey.utils import calculate_parametric_resonance_frequency

# Calculate the optimal pumping frequency for a 2.5m pendulum
freq = calculate_parametric_resonance_frequency(L0=2.5)
print(f"Optimal pumping frequency: {freq:.3f} Hz")
```

## Example Configurations

The utils module includes several predefined configurations:

- `default_config.yaml`: Basic parametric pendulum
- `resonant_config.yaml`: Pendulum pumped at the resonant frequency
- `damped_config.yaml`: Heavily damped pendulum
- `square_config.yaml`: Pendulum with square wave pumping
- `adaptive_config.yaml`: Pendulum with adaptive pumping strategy
- `playground_config.yaml`: Realistic playground swing parameters
- `foucault_config.yaml`: Long pendulum with minimal damping
