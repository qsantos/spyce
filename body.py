import math

import constants


class CelestialBody:
    """Celestial Body

    Minimalistic model of celestial bodies (stars, planets, moons)
    It includes a few handy methods to plan orbital travel.
    """

    def __init__(self, name, mu, radius=0, rotational_period=0, orbit=None):
        """Definition of a celestial body

        Arguments:
        name
        mass       kg
        radius     m, optional
        rotational_period s, optional, 0 for tidal lock
        orbit      Orbit, optional
        """
        self.name = name
        self.radius = float(radius)
        self.mass = float(mu)/constants.G
        self.orbit = orbit

        self.satellites = []
        if self.orbit is not None:
            s = self.orbit.primary.satellites
            s.append(self)
            self.label = len(s)  # moon label convention
        else:
            self.label = 0

        if rotational_period == 0 and orbit is not None:
            self.rotational_period = self.orbit.period
        else:
            self.rotational_period = float(rotational_period)

    def __repr__(self):
        """Appear as <Name> in a Python interpreter"""
        return "<%s>" % (self.name)

    def __str__(self):
        """Cast to string using the name"""
        return self.name

    def gravity(self, a=0):
        """Gravity at given altitude (m/s^2)

        Defaults to surface gravity
        """
        # see https://en.wikipedia.org/wiki/Shell_theorem
        r = self.radius+a
        M = self.mass
        if a < 0:
            M *= r**3/self.radius**3
        return constants.G*M / r**2

    def sphere_of_influence(self):
        """Radius of the sphere of influence (m)"""
        p = self.orbit.primary
        if p is None:
            return float("inf")
        else:
            return self.orbit.semi_major_axis * (self.mass / p.mass)**0.4

    def solar_day(self):
        """Duration of the solar day (s)"""
        d = self.rotational_period
        y = self.orbit.period
        return d * y/(y-d)

    def time2str(self, s):
        """Convert a duration (s) to a human-readable string

        The string will use conventional minutes and hours,
        as well as local days (based on rotational period)
        and local years (based on orbital period)

        See str2time()
        """
        n = s < 0
        s = abs(float(s))
        y, s = divmod(s, self.orbit.period)
        d, s = divmod(s, self.rotational_period)
        h, s = divmod(s, 3600)
        m, s = divmod(s, 60)
        return "%s%uy, %ud, %u:%u:%.1f" % ("-" if n else "+", y, d, h, m, s)

    def str2time(self, t):
        """Convert a string formated time to a duration (s)

        See time2str()
        """
        n = t[0] == "-"
        import re

        x = re.search("([0-9]*)y", t)
        y = 0 if x is None else int(x.group(1))

        x = re.search("([0-9]*)d", t)
        d = 0 if x is None else int(x.group(1))

        time_re = "((([0-9]{1,2}):)?([0-9]{1,2}):)?([0-9]{1,2}(\.[0-9]*)?)$"
        x = re.search(time_re, t)
        h = 0 if x is None else int(x.group(3))
        m = 0 if x is None else int(x.group(4))
        s = 0 if x is None else float(x.group(5))

        s += y * self.orbit.period
        s += d * self.rotational_period
        s += h * 3600
        s += m * 60
        return s

    def escape_velocity(self, distance):
        """Escape velocity at a given distance (m)"""
        return math.sqrt(2*constants.G*self.mass/distance)

    def angular_diameter(self, distance):
        """Angular diameter / apparent size at a given distance (m)"""
        return math.atan(self.radius/distance)
