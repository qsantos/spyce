import math

import matrix
import vector
import constants


class Orbit:
    """Kepler orbit

    Allow to define an orbit in a number of way (see class methods)
    and to retrieve the position and velocity from various parameters.
    """
    def __init__(self, primary,
                 semimajor, eccentricity=0, anomaly0=0,    # 2D shape
                 inclination=0, ascending=0, argument=0):  # plane
        """Definition of an orbit from the usual orbital parameters

        Arguments:
        primary:                        object with a 'mass' attribute (kg)
        semimajor    (float):           semi-major axis (m)
        eccentricity (float, optional): ellipse eccentricity (-)
        anomaly0     (float, optional): mean anomaly at epoch (rad)
        inclination  (float, optional): inclination (rad)
        ascending    (float, optional): longitude of ascending node (rad)
        argument     (float, optional): argument of periapsis (rad)
        """

        self.primary = primary
        self.semimajor = float(semimajor)
        self.eccentricity = float(eccentricity)
        self.anomaly0 = float(anomaly0)
        self.inclination = float(inclination)
        self.ascending = float(ascending)
        self.argument = float(argument)

        self.periapsis = self.semimajor * (1-self.eccentricity)
        self.apoapsis = self.semimajor * (1+self.eccentricity)
        self.semilatus = self.semimajor * (1-self.eccentricity**2)
#        self.semiminor = self.semimajor * math.sqrt(1 - self.eccentricity**2)
#        self.focus = self.semimajor * self.eccentricity

        mu = constants.G * self.primary.mass
        self.mean_motion = math.sqrt(mu / self.semimajor**3)
        self.period = 2*math.pi / self.mean_motion

        m = matrix.identity()
        m = matrix.dot_m(matrix.rotation_rad(self.argument,    0, 0, 1), m)
        m = matrix.dot_m(matrix.rotation_rad(self.inclination, 1, 0, 0), m)
        m = matrix.dot_m(matrix.rotation_rad(self.ascending,   0, 0, 1), m)
        self.transform = m

    @classmethod
    def from_deg(cls, primary,
                 semimajor, eccentricity=0, anomaly0=0,    # 2D shape
                 inclination=0, ascending=0, argument=0):  # plane
        """Defines an orbit using degress for angles"""

        anomaly0 *= math.pi / 180
        inclination *= math.pi / 180
        ascending *= math.pi / 180
        argument *= math.pi / 180

        return cls(primary,
                   semimajor, eccentricity, anomaly0,
                   inclination, ascending, argument)

    @classmethod
    def from_apses(cls, primary,
                   apsis1, apsis2, anomaly0=0,               # 2D shape
                   inclination=0, ascending=0, argument=0):  # plane
        """Defines an orbit from periapsis (m) and apoapsis (m)"""

        apsis1 = float(apsis1)
        apsis2 = float(apsis2)
        semimajor = (apsis1 + apsis2) / 2
        eccentricity = abs(apsis1 - apsis2) / (apsis1 + apsis2)

        return cls(primary,
                   semimajor, eccentricity, anomaly0,
                   inclination, ascending, argument)

    @classmethod
    def from_period(cls, primary,
                    period, eccentricity=0, anomaly0=0,       # 2D shape
                    inclination=0, ascending=0, argument=0):  # plane
        """Defines an orbit from orbital period (s)"""

        period = float(period)
        mu = constants.G * primary.mass
        mean_motion = period / (2*math.pi)
        semimajor = (mean_motion**2 * mu)**(1./3)

        return cls(primary,
                   semimajor, eccentricity, anomaly0,
                   inclination, ascending, argument)

    @classmethod
    def from_period_apsis(cls, primary,
                          period, apsis, anomaly0=0,                # 2D shape
                          inclination=0, ascending=0, argument=0):  # plane
        """Defines an orbit from orbital period (s) and one apsis (m)"""

        period = float(period)
        mu = constants.G * primary.mass
        mean_motion = period / (2*math.pi)
        semimajor = (mean_motion**2 * mu)**(1./3)
        eccentricity = abs(apsis/semimajor - 1)

        return cls(primary,
                   semimajor, eccentricity, anomaly0,
                   inclination, ascending, argument)

    # inspired from https://space.stackexchange.com/questions/1904/#1919
    @classmethod
    def from_state(cls, primary, r, v):
        """Defines an orbit from position and velocity

        The state is given in a referential centered on the primary.

        Arguments:
        primary: orbited body, object with a 'mass' attribute (kg)
        r:       position vector of the vessel (m)
        v:       velocity vector of the vessel (m/s)
        """

        # normal vector to the orbital plane
        h = vector.cross(r, v)
        h[0] += 0.0001
        # inclination
        inclination = vector.angle(h, [0, 0, 1])

        # intersection of the equatorial and orbital planes
        n = vector.cross([0, 0, 1], h)
        # longitude of the ascending node
        ascending = vector.angle([1, 0, 0], n)

        # from the vis-viva equation
        mu = constants.G * primary.mass
        semimajor = 1 / abs(2/vector.norm(r) - vector.dot(v, v)/mu)

        # https://en.wikipedia.org/wiki/Eccentricity_vector
        vh = vector.cross(v, h)
        d = vector.norm(r)
        e = [vh[i]/mu-r[i]/d for i in range(3)]
        eccentricity = vector.norm(e)

        argument = vector.angle(n, e)
        anomaly0 = vector.angle(e, r)

        return cls(primary,
                   semimajor, eccentricity, anomaly0,
                   inclination, ascending, argument)

    def visviva(self, r=None):
        """Computes the orbital speed at a given distance from the focus

        This is an implementation of the vis-viva equation:
        v**2 / (GM) = 2/r - 1/a

        Arguments:
        r (float, optional): distance from the focus (m), default is periapsis

        Returns:
        float: orbital speed (m/s)
        """

        if r is None:
            r = self.periapsis
        mu = constants.G * self.primary.mass
        return math.sqrt(mu * (2./r - 1./self.semimajor))

    def visviva_peri(self):
        """Computes the orbital speed at periapsis"""
        return self.visviva(self.periapsis)

    def visviva_apo(self):
        """Computes the orbital speed at apoapsis"""
        return self.visviva(self.apoapsis)

    def r(self, theta):
        """Computes the distance from focus (m) at given true anomaly (rad)"""
        return self.semilatus / (1 + self.eccentricity * math.cos(theta))

    def v(self, theta):
        """Computes the orbital speed (m/s) at a given true anomaly (rad)"""
        r = self.r(theta)
        return self.visviva(r)

    def position(self, theta):
        """Computes the position vector at a given true anomaly (rad)"""
        r = self.r(theta)
        x = [r*math.cos(theta), r*math.sin(theta), 0.0]
        x = matrix.dot_v(self.transform, x)
        return x

    def velocity(self, theta):
        """Computes the velocity vector at a given true anomaly (rad)"""
        r = self.r(theta)
        c = math.cos(theta)
        s = math.sin(theta)
        x = self.semilatus*self.eccentricity*s/(1+self.eccentricity*c)**2
        v = [-r*s + x*c, r*c + x*s, 0]
        n = vector.norm(v)
        V = self.v(theta)
        v = [x/n*V for x in v]
        v = matrix.dot_v(self.transform, v)
        return v

    def mean_anomaly(self, t):
        """Computes the mean anomaly at a given time since epoch (s)"""
        return self.anomaly0 + self.mean_motion * t

    def eccentric_anomaly(self, t):
        """Computes the eccentric anomaly at a given time since epoch (s)"""
        M = self.mean_anomaly(t)
        e = self.eccentricity
        E = M if e < 0.8 else math.pi
        while True:
            oldE = E
            E -= (E - e*math.sin(E) - M) / (1 - e*math.cos(E))
            if (oldE - E)/2 <= 2**-51:
                break
        return E

    def true_anomaly(self, t):
        """Computes the true anomaly at a given time since epoch (s)"""
        E = self.eccentric_anomaly(t)
        e = self.eccentricity
        x = math.sqrt(1+e)*math.sin(E/2)
        y = math.sqrt(1-e)*math.cos(E/2)
        v = 2 * math.atan2(x, y)
        return v

    def position_t(self, t):
        """Computes the position vector at a given time since epoch (s)"""
        return self.position(self.true_anomaly(t))

    def velocity_t(self, t):
        """Computes the velocity vector at a given time since epoch (s)"""
        return self.velocity(self.true_anomaly(t))
