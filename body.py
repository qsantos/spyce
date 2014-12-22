import math

import constants


class CelestialBody:
    """Celestial Body

    Minimalistic model of celestial bodies (stars, planets, moons)
    It includes a few handy methods to plan orbital travel.
    """

    def __init__(self, name, mass, radius=0, rot_period=0, orbit=None):
        """Definition of a celestial body

        Arguments:
        name       (string):          used for easy identification
        mass       (float):           total mass (kg)
        radius     (float, optional): mean radius (m)
        rot_period (float, optional): rotational period (s), 0 for tidal lock
        orbit      (Orbit, optional): trajectory around a more massive body
        """
        self.name = name
        self.radius = float(radius)
        self.mass = float(mass)
        self.orbit = orbit

        self.satellites = []
        if self.orbit is not None:
            l = self.orbit.primary.satellites
            self.label = len(l)
            l.append(self)
        else:
            self.label = 0

        if rot_period == 0 and orbit is not None:
            self.rot_period = self.orbit.period
        else:
            self.rot_period = float(rot_period)

    def __repr__(self):
        """Appear as <Name> in a Python interpreter"""
        return "<%s>" % (self.name)

    def __str__(self):
        """Cast to string using the name"""
        return self.name

    def gravity(self, a=0):
        """Gravity at given altitude

        Defaults to surface gravity
        """
        R = self.radius
        r = self.radius+a
        M = self.mass
        if a < 0:
            M *= r**3/R**3
        return constants.G*M / r**2

    def SoI(self):
        """Radius of the sphere of influence"""
        p = self.orbit.primary
        if p is None:
            return float("inf")
        else:
            return self.orbit.semimajor * (self.mass / p.mass)**0.4

    def primary_day(self):
        """Duration of the solar day"""
        d = self.rot_period
        y = self.orbit.period
        return d * y/(y-d)

    def time2str(self, s):
        """Convert a duration to a string

        The string will use conventional minutes and hours,
        as well as local days (based on rotational period)
        and local years (based on orbital period)

        See str2time()
        """
        n = s < 0
        s = abs(float(s))
        y, s = divmod(s, self.orbit.period)
        d, s = divmod(s, self.rot_period)
        h, s = divmod(s, 3600)
        m, s = divmod(s, 60)
        return "%s%uy, %ud, %u:%u:%.1f" % ("-" if n else "+", y, d, h, m, s)

    def str2time(self, t):
        """Convert a string to a duration

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
        s += d * self.rot_period
        s += h * 3600
        s += m * 60
        return s

    def escape_velocity(self, r):
        """Escape velocity at a given distance"""
        return math.sqrt(2*constants.G*self.mass/r)

    def angular_diameter(self, d):
        """Angular diameter / apparent size"""
        return math.atan(self.radius/d)
