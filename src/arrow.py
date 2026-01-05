import numpy as np

class Arrow:
    def __init__(self, mass=0.024, length=0.75, diameter=0.0055, cg_pos=0.45, cp_pos=None, Cd0=1.2):
        """
        Initialize Rigid Body Arrow.
        
        Args:
            mass (float): Mass [kg].
            length (float): Length [m].
            diameter (float): Shaft Diameter [m] (used for Area).
            cg_pos (float): Center of Gravity from Tip [m].
            cp_pos (float): Center of Pressure from Tip [m] (Default: 90% of length).
            Cd0 (float): Zero-lift drag coefficient.
        """
        self.mass = mass
        self.length = length
        self.diameter = diameter
        self.area = np.pi * (diameter/2)**2 # Cross section
        self.Cd0 = Cd0
        
        # CG and CP
        self.xcg = cg_pos
        
        # CP Position
        if cp_pos is not None:
             self.xcp = cp_pos
        else:
             # Assume CP is near the fletching (rear 10%)
             self.xcp = length * 0.9 
        
        # Moment of Inertia (Iyy)
        # Approximation: Slender rod around end -> Shift to CG
        # I_end = mL^2/3. I_cg = I_end - m(xg)^2 ??
        # Better: Uniform rod I = mL^2/12 around center.
        # Let's approximate as thin rod around CG.
        # Dist from center of rod (L/2) to CG (xcg) -> d = xcg - L/2
        # I_cg = (1/12)*m*L^2 + m*d^2
        d = self.xcg - (self.length / 2.0)
        self.Iyy = (1.0/12.0) * self.mass * self.length**2 + self.mass * d**2
        
        # Aerodynamic Derivatives
        # C_L_alpha: Lift slope. Slender body + Fletching.
        # Fletching is main lift generator. 
        # Estimate: ~2.0 to 4.0 per radian? (Typical wing is 6.28 aka 2pi).
        # Fletches are small wings. Let's use conservative 3.0.
        self.CL_alpha = 3.0
        
        # Damping derivative (Cmq)
        self.Cmq = -5.0 # Resistant to rotation rate
