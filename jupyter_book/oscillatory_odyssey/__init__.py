"""
Oscillatory Odyssey - A package for simulating and visualizing pendulum physics.
"""

from .pendulum import ParametricPendulum
from .interactive import create_interactive_pendulum, InteractivePendulum
from .foucault import FoucaultPendulum
from .foucault_interactive import create_interactive_foucault_pendulum, InteractiveFoucaultPendulum
from .gyroscope import GyroscopeSimulation
from .gyroscope_interactive import create_interactive_gyroscope, InteractiveGyroscope
from .ring_laser_gyro import RingLaserGyroSimulation
from .ring_laser_gyro_interactive import create_interactive_ring_laser_gyro, InteractiveRingLaserGyro
from .hemispherical_resonator_gyro import HemisphericalResonatorGyroSimulation
from .hemispherical_resonator_gyro_interactive import create_interactive_hemispherical_resonator_gyro, InteractiveHemisphericalResonatorGyro

__version__ = '0.1.0'
__all__ = [
    'ParametricPendulum',
    'create_interactive_pendulum',
    'InteractivePendulum',
    'FoucaultPendulum',
    'create_interactive_foucault_pendulum',
    'InteractiveFoucaultPendulum',
    'GyroscopeSimulation',
    'create_interactive_gyroscope',
    'InteractiveGyroscope',
    'RingLaserGyroSimulation',
    'create_interactive_ring_laser_gyro',
    'InteractiveRingLaserGyro',
    'HemisphericalResonatorGyroSimulation',
    'create_interactive_hemispherical_resonator_gyro',
    'InteractiveHemisphericalResonatorGyro'
]