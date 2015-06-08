import vector
import physics
import orbit


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
    def __init__(self, primary=None):
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

    def simulate(self, dt):
        """Run physics simulation"""
        mass = self.dry_mass + self.propellant
        self.acceleration = vector.Vector([0, 0, 0])

        # gravity
        if self.primary:
            distance = vector.norm(self.position)
            g = self.primary.gravity_from_center(distance)
            self.acceleration -= self.position * (g/distance)

        # propulsion
        if self.propellant > 0:
            self.acceleration += self.prograde*(self.thrust*self.throttle/mass)
            self.propellant -= self.expulsion_rate * dt * self.throttle

        # update velocity and position
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt

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

    def orbit(self):
        """Current orbital trajectory"""
        return orbit.Orbit.from_state(
            self.primary, self.position, self.velocity)
