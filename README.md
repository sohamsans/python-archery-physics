# Archery Aerodynamics Simulator

A Rigid Body physics simulation for archery ballistics, built with Python and Qt. This tool visualizes the flight trajectory and stability dynamics of an arrow, considering geometric and aerodynamic properties.

## Features

- **Rigid Body Physics**: Models the arrow as a physical object with Mass, Length, Diameter, and Moment of Inertia.
- **Stability Analysis**: proper simulation of the "Weathervane effect" (Static Margin) based on Center of Gravity (CG) vs Center of Pressure (CP).
- **Interactive GUI**:
  - Inputs for Launch Velocity, Angle, and Arrow Geometry.
  - Real-time tooltips explaining aerodynamic concepts.
  - **Graphs**:
    - **Trajectory**: Side-view altitude vs range.
    - **Orientation**: Pitch angle ($\theta$) and Angle of Attack ($\alpha$) over time (visualizes oscillation/damping).

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
   cd REPO_NAME
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the GUI application:
```bash
python src/gui.py
```

### Controls
- **Launch Parameters**: Set the initial velocity (m/s) and angle (degrees).
- **Arrow Geometry**:
  - **Mass**: Total weight of the arrow.
  - **Length/Diameter**: Shaft dimensions.
  - **CG Position**: Balance point (measured from the tip).
  - **CP Position**: Center of Pressure (aerodynamic center). **CP must be > CG** for stable flight.
- **Aerodynamics**: Adjust the Drag Coefficient ($C_d$).

## Physics Model
The core engine uses a **2D 3-DOF Rigid Body** formulation:
- **Forces**: Gravity, Drag, Lift.
- **Moments**: Pitching moment derived from the aerodynamic center offset ($CP - CG$) and damping derivatives ($C_{mq}$).
- **Integration**: 4th Order Runge-Kutta (RK4).

## License
MIT License
