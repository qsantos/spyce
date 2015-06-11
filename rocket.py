import vector
import physics
import orbit
import integration


class RocketPart:
    """Rocket part

    Properties:
    name
    title
    dry_mass             kg
    coefficient_of_drag  -
    thrust               N
    specific_impulse     s
    propellant           kg
    exhaust_velocity     m/s
    expulsion_rate       kg/s
    """

    def __init__(self, name, title, dry_mass, coefficient_of_drag):
        """Initiate a part with default properties"""
        self.name = name
        self.title = title
        self.dry_mass = dry_mass
        self.coefficient_of_drag = coefficient_of_drag
        self.make_engine(0., 1.)
        self.make_tank(0.)

    def __repr__(self):
        """Appear as part's name in a Python interpreter"""
        return self.name

    def __str__(self):
        """Cast to string using the part's title"""
        return self.title

    def make_engine(self, thrust, specific_impulse):
        self.thrust = thrust
        self.specific_impulse = specific_impulse
        self.exhaust_velocity = self.specific_impulse * physics.g0
        self.expulsion_rate = self.thrust / self.exhaust_velocity

    def make_tank(self, propellant):
        self.propellant = propellant


class Rocket:
    """A rocket, or a spaceship, or a duck"""
    def __init__(self, primary=None, program=None):
        self.parts = set()
        self.dry_mass = 0.
        self.throttle = 1.

        self.acceleration = vector.Vector([0, 0, 0])
        if primary is None:
            self.velocity = vector.Vector([0, 0, 0])
            self.position = vector.Vector([0, 0, 0])
        else:
            self.velocity = vector.Vector([0, primary.surface_velocity(), 0])
            self.position = vector.Vector([primary.radius, 0, 0])
        self.primary = primary

        self.orientation = vector.Matrix.identity()
        self.rotate_deg(90, 0, 1, 0)

        self.update_orbit(0.)

        if program is None:
            self.program = None
            self.resume_condition = lambda: False
        else:
            self.program = program(self)
            self.resume_condition = next(self.program)

    def simulate(self, t, dt):
        """Run physics simulation"""

        if self.resume_condition():
            self.resume_condition = next(self.program)

        if self.throttle == 0.:
            self.position = self.orbit.position_t(t + dt)
            self.velocity = self.orbit.velocity_t(t + dt)
            return

        # propulsion
        if self.propellant > 0:
            self.propellant -= self.expulsion_rate * dt * self.throttle

        def f(t, y):
            position, velocity = vector.Vector(y[:3]), y[3:]
            acceleration = vector.Vector([0, 0, 0])

            # gravity
            if self.primary:
                distance = position.norm()
                g = self.primary.gravity_from_center(distance)
                acceleration -= position * (g/distance)

            # propulsion
            if self.propellant > 0:
                mass = self.dry_mass + self.propellant
                acceleration += self.prograde*(self.thrust*self.throttle/mass)
            return vector.Vector(velocity + acceleration)

        # update velocity and position
        y = self.position[:] + self.velocity
        y = integration.rk4(f, t, y, dt)
        self.position = vector.Vector(y[:3])
        self.velocity = vector.Vector(y[3:])

        self.update_orbit(t)

    def update_orbit(self, epoch):
        """Update current orbital trajectory"""
        self.orbit = orbit.Orbit.from_state(
            self.primary, self.position, self.velocity, epoch)

    def update_parts(self):
        """Update information about parts"""
        self.dry_mass = sum(part.dry_mass for part in self.parts)
        self.thrust = sum(part.thrust for part in self.parts)
        self.expulsion_rate = sum(part.expulsion_rate for part in self.parts)
        self.propellant = sum(part.propellant for part in self.parts)

    def __ior__(self, parts):
        """Add parts"""
        self.parts |= parts
        self.update_parts()
        return self

    def __isub__(self, parts):
        """Remove parts"""
        self.parts -= parts
        self.update_parts()
        return self

    def rotate_deg(self, angle, x, y, z):
        """Rotate `angle` degrees along axis (x,y,z)"""
        self.orientation *= vector.Matrix.rotation_deg(angle, x, y, z)
        self.prograde = self.orientation * [0, 0, 1]
