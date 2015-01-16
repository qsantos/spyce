import math

import vector


class InvalidElements(Exception):
    pass


class Orbit:
    """Kepler orbit

    Allow to define an orbit in a number of way (see class methods)
    and to retrieve the position and velocity from various parameters.
    """
    def __init__(
        self, primary, periapsis, eccentricity=0,
        inclination=0, longitude_of_ascending_node=0, argument_of_periapsis=0,
        epoch=0, mean_anomaly_at_epoch=0, **_
    ):
        """Definition of an orbit from the usual orbital parameters

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

        m = vector.Matrix.identity()
        m = vector.Matrix.rotation(self.argument_of_periapsis,       0, 0, 1)*m
        m = vector.Matrix.rotation(self.inclination,                 1, 0, 0)*m
        m = vector.Matrix.rotation(self.longitude_of_ascending_node, 0, 0, 1)*m
        self.transform = m

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
        """Defines an orbit from semi-major axis (m) and eccentricity (-)"""

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
        """Defines an orbit from periapsis (m) and apoapsis (m)"""

        periapsis = min(apsis1, apsis2)
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
        """Defines an orbit from orbital period (s)"""

        period = float(period)
        mu = primary.gravitational_parameter
        mean_motion = period / (2*math.pi)
        semi_major_axis = (mean_motion**2 * mu)**(1./3)

        return cls(
            primary, periapsis, eccentricity,
            inclination, longitude_of_ascending_node, argument_of_periapsis,
            epoch, mean_anomaly_at_epoch
        )

    @classmethod
    def from_period_apsis(
        cls, primary, period, apsis,
        inclination=0, longitude_of_ascending_node=0, argument_of_periapsis=0,
        epoch=0, mean_anomaly_at_epoch=0, **_
    ):
        """Defines an orbit from orbital period (s) and one apsis (m)"""

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
        """Defines an orbit from position and velocity

        The state is given in a referential centered on the primary.

        Arguments:
        primary:  orbited body, object with a "gravitational_parameter"
        position: position vector of the vessel (m)
        velocity: velocity vector of the vessel (m/s)
        """

        distance = vector.norm(position)
        speed = vector.norm(velocity)
        mu = primary.gravitational_parameter

        orbital_plane_normal_vector = vector.cross(position, velocity)

        # https://en.wikipedia.org/wiki/Eccentricity_vector
        v_cross_h = vector.cross(velocity, orbital_plane_normal_vector)
        eccentricity_vector = [
            v_cross_h[i]/mu - position[i]/distance for i in range(3)
        ]

        eccentricity = vector.norm(eccentricity_vector)

        # from r(t) = 1 / mu * h / (1 + e cos t)
        specific_angular_momentum = vector.norm(orbital_plane_normal_vector)
        periapsis = specific_angular_momentum**2 / mu / (1 + eccentricity)

        # the eccentricity vector points to the periapsis
        mean_anomaly_at_epoch = vector.angle(eccentricity_vector, position)

        x_axis = [1, 0, 0]
        z_axis = [0, 0, 1]

        # orbital plane
        inclination = vector.angle(orbital_plane_normal_vector, z_axis)
        if inclination == 0:
            longitude_of_ascending_node = 0
            argument_of_periapsis = vector.angle(x_axis, eccentricity_vector)
        else:
            line_of_nodes = vector.cross(z_axis, orbital_plane_normal_vector)
            longitude_of_ascending_node = vector.angle(x_axis, line_of_nodes)
            argument_of_periapsis = vector.angle(line_of_nodes,
                                                 eccentricity_vector)

            # picking right orientation
            if orbital_plane_normal_vector[2] < 0:
                argument_of_periapsis = -argument_of_periapsis

        return cls(
            primary, periapsis, eccentricity,
            inclination, longitude_of_ascending_node, argument_of_periapsis,
            epoch, mean_anomaly_at_epoch
        )

    def visviva(self, distance):
        """Computes the orbital speed at a given distance from the focus

        This is an implementation of the vis-viva equation:
        speed**2 / (GM) = 2/distance - 1/semi_major_axis

        Arguments:
        distance: distance from the focus (m)
        """

        mu = self.primary.gravitational_parameter
        return math.sqrt(mu * (2./distance - 1./self.semi_major_axis))

    def visviva_peri(self):
        """Computes the orbital speed at periapsis"""
        return self.visviva(self.periapsis)

    def visviva_apo(self):
        """Computes the orbital speed at apoapsis"""
        return self.visviva(self.apoapsis)

    def distance(self, true_anomaly):
        """Computes the distance from focus (m) at given true anomaly (rad)"""
        c = math.cos(true_anomaly)
        return self.semi_latus_rectum / (1 + self.eccentricity*c)

    def speed(self, true_anomaly):
        """Computes the orbital speed (m/s) at a given true anomaly (rad)"""
        distance = self.distance(true_anomaly)
        return self.visviva(distance)

    def position(self, true_anomaly):
        """Computes the position vector at a given true anomaly (rad)"""
        distance = self.distance(true_anomaly)
        c = math.cos(true_anomaly)
        s = math.sin(true_anomaly)
        x = [distance*c, distance*s, 0.0]
        x = self.transform * x
        return x

    def velocity(self, true_anomaly):
        """Computes the velocity vector at a given true anomaly (rad)"""
        distance = self.distance(true_anomaly)

        c = math.cos(true_anomaly)
        s = math.sin(true_anomaly)
        e = self.eccentricity

        x = self.semi_latus_rectum*e*s/(1+e*c)**2
        v = [-distance*s + x*c, distance*c + x*s, 0]

        norm_v = vector.norm(v)
        speed = self.speed(true_anomaly)
        v = [x/norm_v*speed for x in v]
        v = self.transform * v
        return v

    def mean_anomaly(self, time):
        """Computes the mean anomaly at a given time (s)"""
        time_since_epoch = time - self.epoch
        return self.mean_anomaly_at_epoch + self.mean_motion * time_since_epoch

    def eccentric_anomaly(self, time):
        """Computes the eccentric anomaly at a given time (s)"""
        M = self.mean_anomaly(time) % (2*math.pi)
        e = self.eccentricity
        E = M if e < 0.8 else math.pi
        while True:
            if e < 1:
                # M = E - e sin E
                # Newton's method on f(x) = x - e sin x - M
                # f'(x) = 1 - e cos x
                delta = (E - e*math.sin(E) - M) / (1 - e*math.cos(E))
            else:
                # M = e sinh E - E
                # Newton's method on f(x) = e sinh x - x - M
                # f'(x) = e cosh x - 1
                delta = (e*math.sinh(E) - E - M) / (e*math.cosh(E) - 1)
            E -= delta
            if delta <= 2**-52:
                break
        return E

    def true_anomaly(self, time):
        """Computes the true anomaly at a given time (s)"""
        if self.eccentricity < 1:  # circular or elliptic orbit
            E = self.eccentric_anomaly(time)
            x = math.sqrt(1+self.eccentricity)*math.sin(E/2)
            y = math.sqrt(1-self.eccentricity)*math.cos(E/2)
            true_anomaly = 2 * math.atan2(x, y)
        elif self.eccentricity == 1:  # parabolic trajectory
            time_since_epoch = time - self.epoch
            mu = self.primary.gravitational_parameter
            W = math.sqrt(mu / (2*self.periapsis**3)) * 3/2 * time_since_epoch
            y = (W + math.sqrt(W**2+1))**(1./3)
            true_anomaly = 2 * math.atan(y - 1/y)
        else:  # hyperbolic trajectory
            E = self.eccentric_anomaly(time)
            x = math.sqrt(self.eccentricity+1)*math.sinh(E/2)
            y = math.sqrt(self.eccentricity-1)*math.cosh(E/2)
            true_anomaly = 2 * math.atan2(x, y)
        return true_anomaly

    def position_t(self, time):
        """Computes the position vector at a given time (s)"""
        return self.position(self.true_anomaly(time))

    def velocity_t(self, time):
        """Computes the velocity vector at a given time (s)"""
        return self.velocity(self.true_anomaly(time))
