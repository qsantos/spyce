import re
import math

import physics


class CelestialBody:
    """Celestial Body

    Minimalistic model of celestial bodies (stars, planets, moons)
    It includes a few handy methods to plan orbital travel.
    """

    def __init__(self, name, gravitational_parameter=0, radius=0,
                 rotational_period=0, orbit=None, **_):
        """Definition of a celestial body

        Arguments:
        name
        gravitational_parameter  m^3/s^2
        radius                   m, optional
        rotational_period        s, optional, 0 for tidal lock
        orbit                    Orbit, optional
        """
        self.name = name
        self.radius = float(radius)
        self.gravitational_parameter = float(gravitational_parameter)
        self.orbit = orbit

        self.mass = self.gravitational_parameter/physics.G

        self.satellites = []
        if self.orbit is not None:
            self.orbit.primary.satellites.append(self)

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

    def gravity(self, altitude=0):
        """Gravity at given altitude (m/s^2)

        Defaults to surface gravity
        """
        # see https://en.wikipedia.org/wiki/Shell_theorem
        distance = self.radius + altitude
        mu = self.gravitational_parameter
        if altitude < 0:
            mu *= distance**3/self.radius**3
        return mu / distance**2

    def sphere_of_influence(self):
        """Radius of the sphere of influence (m)"""
        if self.orbit is None:
            return float("inf")

        mu_p = self.orbit.primary.gravitational_parameter
        mu_b = self.gravitational_parameter
        return self.orbit.semi_major_axis * (mu_b / mu_p)**0.4

    def solar_day(self):
        """Duration of the solar day (s)"""
        sidereal_day = self.rotational_period
        sidereal_year = self.orbit.period
        solar_year = sidereal_year - sidereal_day
        return sidereal_day * sidereal_year/solar_year

    def time2str(self, seconds):
        """Convert a duration (s) to a human-readable string

        The string will use conventional minutes and hours,
        as well as local days (based on rotational period)
        and local years (based on orbital period)

        See str2time()
        """
        sign = "-" if seconds < 0 else "+"
        seconds = abs(float(seconds))
        y, seconds = divmod(seconds, self.orbit.period)
        d, seconds = divmod(seconds, self.rotational_period)
        h, seconds = divmod(seconds, 3600)
        m, seconds = divmod(seconds, 60)
        return sign + "%uy, %ud, %u:%u:%.1f" % (y, d, h, m, seconds)

    def str2time(self, formatted_time):
        """Extract a duration (s) from formated time

        See time2str()
        """
        x = re.search("([0-9]*)y", formatted_time)
        y = 0 if x is None else int(x.group(1))

        x = re.search("([0-9]*)d", formatted_time)
        d = 0 if x is None else int(x.group(1))

        time_re = "((([0-9]{1,2}):)?([0-9]{1,2}):)?([0-9]{1,2}(\.[0-9]*)?)$"
        x = re.search(time_re, formatted_time)
        h = 0 if x is None else int(x.group(3))
        m = 0 if x is None else int(x.group(4))
        s = 0 if x is None else float(x.group(5))

        s += y * self.orbit.period
        s += d * self.rotational_period
        s += h * 3600
        s += m * 60

        if formatted_time[0] == "-":
            s = -s

        return s

    def escape_velocity(self, distance):
        """Escape velocity at a given distance (m)"""
        return math.sqrt(2 * self.gravitational_parameter / distance)

    def angular_diameter(self, distance):
        """Angular diameter / apparent size at a given distance (m)"""
        return math.atan(self.radius/distance)
