import sys
import math

import vector
import analysis


class InvalidElements(Exception):
    pass


class Orbit(object):
    """Kepler orbit

    Two-body approximation of a body orbiting a mass-point.
    """
    def __init__(
        self, primary, periapsis, eccentricity=0,
        inclination=0, longitude_of_ascending_node=0, argument_of_periapsis=0,
        epoch=0, mean_anomaly_at_epoch=0, **_
    ):
        """Orbit from the orbital elements

        Arguments:
        primary                     object with a "gravitational_parameter"
        periapsis                   m
        eccentricity                -, optional
        inclination                 rad, optional
        longitude_of_ascending_node rad, optional
        argument_of_periapsis       rad, optional
        epoch                       s, optional
        mean_anomaly_at_epoch       rad, optional
        """

        self.primary = primary
        self.periapsis = float(periapsis)
        self.eccentricity = float(eccentricity)
        self.inclination = float(inclination)
        self.longitude_of_ascending_node = float(longitude_of_ascending_node)
        self.argument_of_periapsis = float(argument_of_periapsis)
        self.epoch = float(epoch)
        self.mean_anomaly_at_epoch = float(mean_anomaly_at_epoch)

        mu = self.primary.gravitational_parameter

        if self.eccentricity == 1:  # parabolic trajectory
            self.semi_major_axis = float("inf")
            self.mean_motion = 0
            self.period = float("inf")
        else:
            self.semi_major_axis = self.periapsis / (1 - self.eccentricity)
            self.mean_motion = math.sqrt(mu / abs(self.semi_major_axis)**3)
            self.period = 2*math.pi / self.mean_motion

        self.apoapsis = self.semi_major_axis * (1 + self.eccentricity)
        self.semi_latus_rectum = self.periapsis * (1 + self.eccentricity)
        e2 = 1-self.eccentricity**2
        self.semi_minor_axis = self.semi_major_axis * math.sqrt(abs(e2))
        self.focus = self.semi_major_axis * self.eccentricity

        self.transform = vector.Matrix.from_euler_angles(
            self.longitude_of_ascending_node,
            self.inclination,
            self.argument_of_periapsis,
        )

    def __repr__(self):
        return (
            "Orbit(%(primary)s, %(periapsis)g, %(eccentricity)g, "
            "%(inclination)g, %(longitude_of_ascending_node)g, "
            "%(argument_of_periapsis)g, %(epoch)g, %(mean_anomaly_at_epoch)g)"
            % self.__dict__
        )

    @classmethod
    def from_semi_major_axis(
        cls, primary, semi_major_axis, eccentricity,
        inclination=0, longitude_of_ascending_node=0, argument_of_periapsis=0,
        epoch=0, mean_anomaly_at_epoch=0, **_
    ):
        """Orbit from semi-major axis (m) and eccentricity (-)"""

        if eccentricity < 1 and semi_major_axis <= 0:
            raise InvalidElements("eccentricity < 1 but semi-major axis <= 0")
        if eccentricity > 1 and semi_major_axis >= 0:
            raise InvalidElements("eccentricity > 1 but semi-major axis >= 0")

        periapsis = semi_major_axis * (1 - eccentricity)

        return cls(
            primary, periapsis, eccentricity,
            inclination, longitude_of_ascending_node, argument_of_periapsis,
            epoch, mean_anomaly_at_epoch
        )

    @classmethod
    def from_apses(
        cls, primary, apsis1, apsis2,
        inclination=0, longitude_of_ascending_node=0, argument_of_periapsis=0,
        epoch=0, mean_anomaly_at_epoch=0, **_
    ):
        """Orbit from periapsis (m) and apoapsis (m)"""

        periapsis = min(abs(apsis1), abs(apsis2))

        if float("inf") in (apsis1, apsis2):  # parabolic trajectory
            eccentricity = 1
        else:
            eccentricity = abs(apsis1 - apsis2) / abs(apsis1 + apsis2)

        return cls(
            primary, periapsis, eccentricity,
            inclination, longitude_of_ascending_node, argument_of_periapsis,
            epoch, mean_anomaly_at_epoch
        )

    @classmethod
    def from_period(
        cls, primary, period, eccentricity=0,
        inclination=0, longitude_of_ascending_node=0, argument_of_periapsis=0,
        epoch=0, mean_anomaly_at_epoch=0, **_
    ):
        """Orbit from orbital period (s)"""

        period = float(period)
        mu = primary.gravitational_parameter
        mean_motion = period / (2*math.pi)
        semi_major_axis = (mean_motion**2 * mu)**(1./3)

        if eccentricity > 1:
            semi_major_axis = -semi_major_axis

        return cls.from_semi_major_axis(
            primary, semi_major_axis, eccentricity,
            inclination, longitude_of_ascending_node, argument_of_periapsis,
            epoch, mean_anomaly_at_epoch
        )

    @classmethod
    def from_period_apsis(
        cls, primary, period, apsis,
        inclination=0, longitude_of_ascending_node=0, argument_of_periapsis=0,
        epoch=0, mean_anomaly_at_epoch=0, **_
    ):
        """Orbit from orbital period (s) and one apsis (m)"""

        period = float(period)
        mu = primary.gravitational_parameter
        mean_motion = period / (2*math.pi)
        semi_major_axis = (mean_motion**2 * mu)**(1./3)
        eccentricity = abs(apsis/semi_major_axis - 1)

        return cls.from_semi_major_axis(
            primary, semi_major_axis, eccentricity,
            inclination, longitude_of_ascending_node, argument_of_periapsis,
            epoch, mean_anomaly_at_epoch
        )

    # inspired from https://space.stackexchange.com/questions/1904/#1919
    @classmethod
    def from_state(cls, primary, position, velocity, epoch=0):
        """Orbit from position and velocity

        The state is given in a referential centered on the primary.

        Arguments:
        primary:  orbited body, object with a "gravitational_parameter"
        position: position vector of the vessel (m)
        velocity: velocity vector of the vessel (m/s)
        epoch:    time of the position and velocity (s)
        """

        distance = position.norm()
        speed = velocity.norm()
        mu = primary.gravitational_parameter

        x_axis = vector.Vector([1, 0, 0])
        z_axis = vector.Vector([0, 0, 1])
        orbital_plane_normal_vector = position.cross(velocity)

        # eccentricity
        rv = position.dot(velocity)
        eccentricity_vector = vector.Vector([
            (speed**2 * p - rv*v)/mu - p/distance
            for p, v in zip(position, velocity)
        ])
        eccentricity = eccentricity_vector.norm()

        # periapsis
        # from r(t) = 1 / mu * h / (1 + e cos t)
        specific_angular_momentum = orbital_plane_normal_vector.norm()
        periapsis = specific_angular_momentum**2 / mu / (1 + eccentricity)
        periapsis_dir = eccentricity_vector if eccentricity else x_axis

        # inclination
        inclination = orbital_plane_normal_vector.angle(z_axis)

        # direction of the ascending node
        if inclination in (0, math.pi):
            ascend_node_dir = x_axis
        else:
            ascend_node_dir = z_axis.cross(orbital_plane_normal_vector)

        # longitude of ascending node
        longitude_of_ascending_node = x_axis.angle(ascend_node_dir)
        if orbital_plane_normal_vector[0] < 0:
            longitude_of_ascending_node = - longitude_of_ascending_node

        # argument of periapsis
        argument_of_periapsis = ascend_node_dir.oriented_angle(
            periapsis_dir, orbital_plane_normal_vector)

        # true anomaly at epoch
        true_anomaly_at_epoch = periapsis_dir.oriented_angle(
            position, orbital_plane_normal_vector)

        # mean anomaly from true anomaly
        v = true_anomaly_at_epoch
        if eccentricity < 1:  # circular or elliptic orbit
            x = math.sqrt(1+eccentricity)*math.cos(v/2)
            y = math.sqrt(1-eccentricity)*math.sin(v/2)
            E = 2 * math.atan2(y, x)
            M = E - eccentricity * math.sin(E)
        elif eccentricity == 1:  # parabolic trajectory
            M = 0
        else:  # hyperbolic trajectory
            x = math.sqrt(eccentricity+1)*math.cos(v/2)
            y = math.sqrt(eccentricity-1)*math.sin(v/2)
            ratio = y / x
            if abs(ratio) <= 1:
                E = 2 * math.atanh(ratio)
            else:
                E = math.copysign(float("-inf"), ratio)
            M = eccentricity * math.sinh(E) - E
        mean_anomaly_at_epoch = M

        return cls(
            primary, periapsis, eccentricity,
            inclination, longitude_of_ascending_node, argument_of_periapsis,
            epoch, mean_anomaly_at_epoch
        )

    def visviva(self, distance):
        """Orbital speed at a given distance from the focus

        This is an implementation of the vis-viva equation:
        speed**2 / (GM) = 2/distance - 1/semi_major_axis

        Arguments:
        distance: distance from the focus (m)
        """

        mu = self.primary.gravitational_parameter
        return math.sqrt(mu * (2./distance - 1./self.semi_major_axis))

    def visviva_peri(self):
        """Orbital speed at periapsis"""
        return self.visviva(self.periapsis)

    def visviva_apo(self):
        """Orbital speed at apoapsis"""
        return self.visviva(self.apoapsis)

    def distance(self, true_anomaly):
        """Distance from focus (m) at a given true anomaly (rad)"""
        c = math.cos(true_anomaly)
        return self.semi_latus_rectum / (1 + self.eccentricity*c)

    def speed(self, true_anomaly):
        """Orbital speed (m/s) at a given true anomaly (rad)"""
        distance = self.distance(true_anomaly)
        return self.visviva(distance)

    def position(self, true_anomaly):
        """Position vector at a given true anomaly (rad)"""
        distance = self.distance(true_anomaly)
        c = math.cos(true_anomaly)
        s = math.sin(true_anomaly)
        x = [distance*c, distance*s, 0.0]
        x = self.transform * x
        return x

    def velocity(self, true_anomaly):
        """Velocity vector at a given true anomaly (rad)"""
        distance = self.distance(true_anomaly)

        c = math.cos(true_anomaly)
        s = math.sin(true_anomaly)
        e = self.eccentricity

        x = self.semi_latus_rectum*e*s/(1+e*c)**2
        v = vector.Vector([-distance*s + x*c, distance*c + x*s, 0])

        norm_v = v.norm()
        speed = self.speed(true_anomaly)
        v = [x/norm_v*speed for x in v]
        v = self.transform * v
        return v

    def mean_anomaly(self, time):
        """Mean anomaly at a given time (s)"""
        time_since_epoch = time - self.epoch
        return self.mean_anomaly_at_epoch + self.mean_motion * time_since_epoch

    def eccentric_anomaly(self, time):
        """Eccentric anomaly at a given time (s)"""
        M = self.mean_anomaly(time)
        e = self.eccentricity

        if e < 1:  # M = E - e sin E
            M %= (2*math.pi)

            # sin(E) = E -> M = (1 - e) E
            if abs(M) < 2**-26:
                return M / (1 - e)

            return analysis.newton_raphson(
                x_0=math.pi,
                f=lambda E: E - e*math.sin(E) - M,
                f_prime=lambda E: 1 - e*math.cos(E),
            )
        else:  # M = e sinh E - E
            # sinh(E) = E -> M = (e - 1) E
            if abs(M) < 2**-26:
                return M / (e - 1)

            return analysis.newton_raphson(
                x_0=math.asinh(M),
                f=lambda E: e*math.sinh(E) - E - M,
                f_prime=lambda E: e*math.cosh(E) - 1,
            )

    def true_anomaly(self, time):
        """True anomaly at a given time (s)"""
        if self.eccentricity < 1:  # circular or elliptic orbit
            E = self.eccentric_anomaly(time)
            x = math.sqrt(1-self.eccentricity)*math.cos(E/2)
            y = math.sqrt(1+self.eccentricity)*math.sin(E/2)
            true_anomaly = 2 * math.atan2(y, x)
        elif self.eccentricity == 1:  # parabolic trajectory
            time_since_epoch = time - self.epoch
            mu = self.primary.gravitational_parameter
            W = math.sqrt(mu / (2*self.periapsis**3)) * 3/2 * time_since_epoch
            y = (W + math.sqrt(W**2+1))**(1./3)
            true_anomaly = 2 * math.atan(y - 1/y) if y else - math.pi/2
        else:  # hyperbolic trajectory
            E = self.eccentric_anomaly(time)
            x = math.sqrt(self.eccentricity-1)*math.cosh(E/2)
            y = math.sqrt(self.eccentricity+1)*math.sinh(E/2)
            true_anomaly = 2 * math.atan2(y, x)
        return true_anomaly

    def position_t(self, time):
        """Position vector at a given time (s)"""
        return self.position(self.true_anomaly(time))

    def velocity_t(self, time):
        """The velocity vector at a given time (s)"""
        return self.velocity(self.true_anomaly(time))


# if available, use a C version to compute orbital elements from state vectors

try:  # Python 3
    import cext.orbit_py3 as cext
except ImportError:
    try:  # Python 2
        import cext.orbit_py2 as cext
    except ImportError:
        sys.stderr.write("Note: to improve performances, run `make` in cext/")
        cext = None

if cext is not None:
    @classmethod
    def from_state(cls, primary, position, velocity, epoch=0):
        mu = primary.gravitational_parameter
        elements = cext.elements_from_state(mu, position, velocity, epoch)
        return cls(primary, *elements)
    Orbit.from_state = from_state

    def eccentric_anomaly(self, time):
        e = self.eccentricity
        M = self.mean_anomaly(time)
        return cext.eccentric_anomaly(e, M)
    Orbit.eccentric_anomaly = eccentric_anomaly

    def true_anomaly(self, time):
        e = self.eccentricity
        M = self.mean_anomaly(time)
        return cext.true_anomaly(e, M)
    Orbit.true_anomaly = true_anomaly
