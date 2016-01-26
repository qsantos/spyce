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

        # rotational period
        if rotational_period == 0 and orbit is not None:
            self.rotational_period = self.orbit.period
        else:
            self.rotational_period = float(rotational_period)

        # sphere of influence
        if self.orbit is None:
            self.sphere_of_influence = float("inf")
        else:
            a = self.orbit.semi_major_axis
            mu_p = self.orbit.primary.gravitational_parameter
            mu_b = self.gravitational_parameter
            self.sphere_of_influence = a * (mu_b / mu_p)**0.4

        # solar day
        if self.orbit is not None:
            sidereal_day = self.rotational_period
            sidereal_year = self.orbit.period
            solar_year = sidereal_year - sidereal_day
            if solar_year == 0:
                self.solar_day = float("inf")
            else:
                self.solar_day = sidereal_day * sidereal_year/solar_year
        else:
            self.solar_day = 0

        # surface velocity
        if self.rotational_period == 0:
            self.surface_velocity = float("inf")
        else:
            R = self.radius
            self.surface_velocity = 2*math.pi * R / self.rotational_period

    def __repr__(self):
        """Appear as <Name> in a Python interpreter"""
        return "<%s>" % (self.name)

    def __str__(self):
        """Cast to string using the name"""
        return self.name

    def gravity(self, distance=None):
        """Gravity at given distance from center

        Defaults to surface gravity
        """
        if distance is None:
            distance = self.radius
        mu = self.gravitational_parameter
        if distance < self.radius:
            # see https://en.wikipedia.org/wiki/Shell_theorem
            mu *= distance**3/self.radius**3
        return mu / distance**2

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
        return sign + "%.5gy,%4ud,%3u:%02u:%04.1f" % (y, d, h, m, seconds)

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
