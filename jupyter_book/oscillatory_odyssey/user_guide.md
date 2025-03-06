# Interactive Parametric Pendulum Simulation Guide

## Parameter Controls

### Initial Conditions
- **Initial angle (rad)**: Starting angle of the pendulum (0 = vertical down, π/2 = horizontal)
- **Base length (m)**: Length of the pendulum from pivot to equilibrium position
- **Length change (m)**: How much the length varies during pumping motion
- **Damping**: Energy loss in the system (0 = no damping, higher values = more damping)

### Pumping Parameters
- **Pump freq (Hz)**: Frequency of length oscillation
- **Pump strategy**: How the length changes
  - `sinusoidal`: Smooth length variation
  - `square`: Sharp transitions between long and short
  - `adaptive`: Length changes based on pendulum state

### Resonance Selection
- **Off**: Manual frequency selection
- **1st (2ω₀)**: Principal parametric resonance - strongest amplitude growth
- **2nd (ω₀)**: Secondary resonance - smaller but noticeable effect

## Simulation Controls

### Buttons
- **Simulate**: Run simulation with current parameters
- **Play/Pause**: Start/stop animation
- **Reset**: Return to initial state
- **Save Animation**: Save interactive visualization as HTML

### Animation Speed
- Slider controls playback speed of animation
- Higher values = faster playback

## Understanding the Plots

### Pendulum Animation (Top Left)
- Red dot = pendulum bob
- Gray line = pendulum rod
- Shows actual motion in real space

### Phase Plot (Top Right)
- X-axis: Angle
- Y-axis: Angular velocity
- Purple curve shows system trajectory
- Red star tracks current state
- Closed curves indicate energy conservation
- Spiraling indicates energy gain/loss

### Time Series (Bottom Left)
- Shows angle vs time
- Blue line tracks pendulum's angular position
- Red vertical line shows current time

### Energy Plot (Bottom Right)
- Green = Kinetic energy
- Orange = Potential energy
- Black = Total energy
- Shows energy exchange and conservation

## Tips for Understanding Parametric Resonance

1. Start with no damping and try the resonance settings:
   - Use 1st resonance to see strong amplitude growth
   - Compare with 2nd resonance or off-resonance behavior

2. Observe how different parameters affect motion:
   - Length change affects pumping strength
   - Damping limits maximum amplitude
   - Base length determines natural frequency

3. Watch phase plot behavior:
   - Expanding spirals = gaining energy
   - Shrinking spirals = losing energy
   - Stable orbit = balanced energy

4. Energy plot shows:
   - Energy transfer between kinetic and potential
   - Total energy growth during resonant pumping
   - Energy loss due to damping

## Common Experiments

1. **Find Natural Frequency**:
   - Set small initial angle
   - No pumping or damping
   - Observe oscillation period

2. **Parametric Resonance**:
   - Start with small angle
   - Turn on 1st resonance
   - Watch amplitude grow

3. **Damping Effects**:
   - Start with large angle
   - Add damping
   - Watch energy dissipate

4. **Pumping Strategies**:
   - Compare different strategies
   - Observe energy input differences
   - Look for most effective timing