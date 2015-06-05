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
