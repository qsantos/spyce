import vector
import physics


class RocketPart:
    """Rocket part

    Properties:
    name    identifier
    title   display name
    mass    empty mass (kg)
    drag    coefficient of drag (-)
    thrust  engine's thrust (N)
    isp     specific impulse (s)
    propel  stored propellant (kg)
    """

    def __init__(self, name, title, mass, drag):
        """Initiate a part with default properties"""
        self.name = name
        self.title = title
        self.mass = mass
        self.drag = drag
        self.make_engine(0., 1.)
        self.make_tank(0.)

    def __repr__(self):
        """Appear as part's name in a Python interpreter"""
        return self.name

    def __str__(self):
        """Cast to string using the part's title"""
        return self.title

    def make_engine(self, thrust, isp):
        self.thrust = thrust
        self.isp = isp
        self.exhaust_velocity = self.isp * physics.g0
        self.expulsion_rate = self.thrust / self.exhaust_velocity

    def make_tank(self, propel):
        self.propel = propel


class Rocket:
    def __init__(self):
        self.parts = set()
        self.mass = 0.

        self.position = vector.Vector([0, 0, 0])
        self.velocity = vector.Vector([0, 0, 0])
        self.acceleration = vector.Vector([0, 0, 0])

        self.orientation = vector.Matrix.identity()
        self.rotate_deg(90, 0, 1, 0)

    def simulate(self, dt):
        # propulsion
        self.acceleration = self.prograde * (self.thrust/self.mass)

        # update velocity and position
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt

    def update_parts(self):
        self.mass = sum(part.mass for part in self.parts)
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
