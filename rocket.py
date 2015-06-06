import vector
import physics


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
    def __init__(self):
        self.parts = set()
        self.dry_mass = 0.

        self.position = vector.Vector([0, 0, 0])
        self.velocity = vector.Vector([0, 0, 0])
        self.acceleration = vector.Vector([0, 0, 0])

        self.orientation = vector.Matrix.identity()
        self.rotate_deg(90, 0, 1, 0)

    def simulate(self, dt):
        # propulsion
        self.acceleration = self.prograde * (self.thrust/self.dry_mass)

        # update velocity and position
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt

    def update_parts(self):
        self.dry_mass = sum(part.dry_mass for part in self.parts)
        self.thrust = sum(part.thrust for part in self.parts)
        self.expulsion_rate = sum(part.expulsion_rate for part in self.parts)

    def __ior__(self, parts):
        self.parts |= parts
        self.update_parts()
        return self

    def __isub__(self, parts):
        self.parts -= parts
        self.update_parts()
        return self

    def rotate_deg(self, angle, x, y, z):
        self.orientation *= vector.Matrix.rotation_deg(angle, x, y, z)
        self.prograde = self.orientation * [0, 0, 1]


if __name__ == "__main__":
    import copy

    import ksp_cfg
    parts = ksp_cfg.get_parts()

    def make_parts(*names):
        return {copy.copy(parts[name]) for name in names}

    rocket = Rocket()

    stage = make_parts('probeCoreOcto', 'fuelTankSmallFlat', 'liquidEngine3')
    rocket |= stage

    print(rocket.position[0], rocket.velocity[0], rocket.acceleration[0])
    for _ in range(10):
        rocket.simulate(1)
        print(rocket.position[0], rocket.velocity[0], rocket.acceleration[0])
