import sys
import os

# Allow imports from current dir
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFormLayout, QLabel, QDoubleSpinBox, QPushButton, QGroupBox)
from PyQt6.QtCore import Qt

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from arrow import Arrow
from physics import PhysicsEngine

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class ArcheryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Archery Aerodynamics Simulator (Rigid Body)")
        self.resize(1200, 800)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # --- Subplot Canvas ---
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        main_layout.addWidget(self.canvas, stretch=2)
        
        # --- Controls ---
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        form_layout = QFormLayout()
        
        # Launch Parameters
        group_launch = QGroupBox("Launch Parameters")
        layout_launch = QFormLayout()
        self.speed_input = self.add_param(layout_launch, "Velocity (m/s)", 60.0, 1.0, 5000.0, 
                                          tooltip="Initial speed of the arrow (approx 200 fps = 60 m/s).")
        self.angle_input = self.add_param(layout_launch, "Angle (deg)", 10.0, -90.0, 90.0, 
                                          tooltip="Launch angle relative to horizontal.")
        group_launch.setLayout(layout_launch)
        control_layout.addWidget(group_launch)
        
        # Arrow Geometry
        group_geom = QGroupBox("Arrow Geometry")
        layout_geom = QFormLayout()
        self.mass_input = self.add_param(layout_geom, "Mass (kg)", 0.024, 0.001, 10.0, step=0.001,
                                         tooltip="Total mass of the arrow (shaft + point + fletching).")
        self.len_input = self.add_param(layout_geom, "Length (m)", 0.75, 0.05, 5.0, step=0.01,
                                        tooltip="Total length of the arrow shaft.")
        self.diam_input = self.add_param(layout_geom, "Diameter (mm)", 5.5, 0.5, 500.0, step=0.1,
                                         tooltip="Shaft diameter (used to calculate air resistance area).")
        self.cg_input = self.add_param(layout_geom, "CG Position (m from Tip)", 0.45, 0.0, 5.0, step=0.01,
                                       tooltip="Center of Gravity. Balance point of the arrow.")
        self.cp_input = self.add_param(layout_geom, "CP Position (m from Tip)", 0.675, 0.0, 5.0, step=0.01,
                                       tooltip="Center of Pressure. Aerodynamic center (where Lift/Drag act).\nMust be BEHIND CG for stability.")
        # Stability Note
        self.stability_label = QLabel("Stability Note: Ensure CP > CG for stable flight.")
        self.stability_label.setWordWrap(True)
        self.stability_label.setStyleSheet("color: gray; font-style: italic; font-size: 10px;")
        layout_geom.addRow(self.stability_label)
        
        group_geom.setLayout(layout_geom)
        control_layout.addWidget(group_geom)
        
        # Aerodynamics
        group_aero = QGroupBox("Aerodynamics")
        layout_aero = QFormLayout()
        self.cd_input = self.add_param(layout_aero, "Zero-Lift Drag (Cd0)", 1.2, 0.01, 20.0, step=0.1,
                                       tooltip="Base drag coefficient. Higher means more air resistance.")
        group_aero.setLayout(layout_aero)
        control_layout.addWidget(group_aero)
        
        # Run Button
        self.run_btn = QPushButton("Simulate Shot")
        self.run_btn.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        self.run_btn.clicked.connect(self.run_simulation)
        control_layout.addWidget(self.run_btn)
        
        control_layout.addStretch()
        main_layout.addWidget(control_panel, stretch=1)
        
        # Initial Plot
        self.run_simulation()

    def add_param(self, layout, label, val, min_v, max_v, step=1.0, tooltip=None):
        spin = QDoubleSpinBox()
        spin.setRange(min_v, max_v)
        spin.setValue(val)
        spin.setSingleStep(step)
        spin.setDecimals(4)
        if tooltip:
            spin.setToolTip(tooltip)
            # Also set on label?
        layout.addRow(label, spin)
        return spin
        
    def run_simulation(self):
        # 1. Setup Wrapper
        arrow = Arrow(
            mass=self.mass_input.value(),
            length=self.len_input.value(),
            diameter=self.diam_input.value() / 1000.0, # mm to m
            cg_pos=self.cg_input.value(),
            cp_pos=self.cp_input.value(),
            Cd0=self.cd_input.value()
        )
        engine = PhysicsEngine(arrow)
        
        v0 = self.speed_input.value()
        angle = self.angle_input.value()
        
        # 2. Run
        res = engine.simulate(v0, angle)
        
        # 3. Plot
        self.figure.clear()
        
        # Top Left: Trajectory (Auto Scale)
        ax1 = self.figure.add_subplot(221)
        ax1.plot(res['x'], res['h'], 'b-', linewidth=2)
        ax1.set_title("Trajectory (Side View - Auto Scaled)")
        ax1.set_xlabel("Range [m]")
        ax1.set_ylabel("Altitude [m]")
        ax1.grid(True)
        ax1.axhline(0, color='black', linewidth=1) 
        
        # Top Right: Trajectory (True Scale)
        ax_true = self.figure.add_subplot(222)
        ax_true.plot(res['x'], res['h'], 'b-', linewidth=2)
        ax_true.set_title("Trajectory (True Scale 1:1)")
        ax_true.set_xlabel("Range [m]")
        ax_true.set_ylabel("Altitude [m]")
        ax_true.grid(True)
        ax_true.axhline(0, color='black', linewidth=1)
        ax_true.set_aspect('equal', adjustable='datalim')
        
        # Bottom: Pitch and Alpha (Spans bottom)
        ax2 = self.figure.add_subplot(212)
        ax2.plot(res['t'], res['theta'], 'r-', label='Pitch (Theta) [deg]')
        ax2.plot(res['t'], res['alpha'], 'g--', label='AoA (Alpha) [deg]')
        
        ax2.set_title("Orientation vs Time")
        ax2.set_xlabel("Time [s]")
        ax2.set_ylabel("Angle [deg]")
        ax2.grid(True)
        ax2.legend()
        
        self.figure.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArcheryWindow()
    window.show()
    sys.exit(app.exec())
