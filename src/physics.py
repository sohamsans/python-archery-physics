import numpy as np

# Constants
G = 9.81
RHO = 1.225 # Air density at sea level [kg/m^3]

class PhysicsEngine:
    def __init__(self, arrow):
        self.arrow = arrow
        # History updated for angular states
        # theta (pitch angle), alpha (angle of attack)
        self.history = {'x': [], 'h': [], 'vx': [], 'vh': [], 
                        'theta': [], 'alpha': [], 't': []}

    def reset(self):
         self.history = {'x': [], 'h': [], 'vx': [], 'vh': [], 
                        'theta': [], 'alpha': [], 't': []}

    def derivatives(self, t, state):
        """
        Calculate derivatives [dx, dh, dvx, dvh, dtheta, domega]
        State: [x, h, vx, vh, theta, omega]
        """
        x, h, vx, vh, theta, omega = state
        
        # Velocity
        v_sq = vx**2 + vh**2
        v = np.sqrt(v_sq)
        
        if v == 0:
            return np.zeros(6)
            
        # Flight Path Angle (gamma)
        gamma = np.arctan2(vh, vx)
        
        # Angle of Attack (alpha) = Pitch - FlightPath
        alpha = theta - gamma
        # Normalize -pi to pi?
        # Typically alpha is small, but if tumbling...
        
        # Dynamic Pressure
        q = 0.5 * RHO * v_sq
        S = self.arrow.area
        
        # Aerodynamics (Linear)
        # Drag: Cd = Cd0 + k * alpha^2 (Polar)
        Cd = self.arrow.Cd0 + 2.0 * alpha**2 # Simple induced drag
        Fd = q * S * Cd
        
        # Lift: Cl = CL_alpha * alpha
        Cl = self.arrow.CL_alpha * alpha
        # Stall? Keep linear for now, archery usually stays low alpha unless tumbling.
        Fl = q * S * Cl
        
        # Aerodynamics (Rotational / Moment)
        # Static Margin Moment (Stability)
        # M_static = -Lift * (Xcp - Xcg)
        # Lift acts at CP.
        moment_arm = self.arrow.xcp - self.arrow.xcg
        M_static = -Fl * moment_arm # Restoring moment if stable (Xcp > Xcg)
        
        # Damping Moment
        # M_damp = 0.5 * rho * v * S * L^2 * Cmq * omega / V ?? (non-dimensional form)
        # Simplified: M_damp = q * S * L * (Cmq * omega * L / (2V))
        ref_len = self.arrow.length
        M_damp = q * S * ref_len * (self.arrow.Cmq * (omega * ref_len) / (2*v))
        
        M_total = M_static + M_damp
        
        # Forces to Accelerations
        # Drag acts in -V direction
        # Lift acts in +Alpha direction (perp to V)
        
        cos_g = np.cos(gamma)
        sin_g = np.sin(gamma)
        
        fx_d = -Fd * cos_g
        fh_d = -Fd * sin_g
        
        fx_l = -Fl * sin_g
        fh_l = Fl * cos_g
        
        ax = (fx_d + fx_l) / self.arrow.mass
        ah = (fh_d + fh_l) / self.arrow.mass - G
        
        # Angular Acceleration
        alpha_acc = M_total / self.arrow.Iyy
        
        return np.array([vx, vh, ax, ah, omega, alpha_acc])

    def simulate(self, v0, angle_deg, dt=0.005, max_time=10.0):
        self.reset()
        
        theta0 = np.radians(angle_deg)
        vx0 = v0 * np.cos(theta0)
        vh0 = v0 * np.sin(theta0)
        
        # Initial State: [x, h, vx, vh, theta, omega]
        # Assume initial pitch aligns with velocity (alpha=0)
        # omega=0 (no initial tumble)
        state = np.array([0.0, 0.0, vx0, vh0, theta0, 0.0])
        
        t = 0.0
        while t < max_time:
            # Derived vals for logging
            vx, vh, theta = state[2], state[3], state[4]
            gamma = np.arctan2(vh, vx)
            alpha = theta - gamma
            
            self.history['t'].append(t)
            self.history['x'].append(state[0])
            self.history['h'].append(state[1])
            self.history['vx'].append(vx)
            self.history['vh'].append(vh)
            self.history['theta'].append(np.degrees(theta))
            self.history['alpha'].append(np.degrees(alpha))
            
            if t > 0 and state[1] < 0:
                break
                
            # RK4 Integration
            k1 = self.derivatives(t, state)
            k2 = self.derivatives(t + dt/2, state + k1*dt/2)
            k3 = self.derivatives(t + dt/2, state + k2*dt/2)
            k4 = self.derivatives(t + dt, state + k3*dt)
            
            state += (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
            t += dt
            
        return self.history
