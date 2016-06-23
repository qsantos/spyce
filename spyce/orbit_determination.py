import sys
import math

import vector
import orbit_angles


class InvalidElements(Exception):
    pass


class OrbitDetermination(object):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

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
        if eccentricity == 1:
            raise InvalidElements(
                "cannot define parabolic trajectory from semi-major axis")

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

        if eccentricity >= 1:
            raise InvalidElements(
                "cannot define parabolic/hyperbolic trajectory from period")

        period = float(period)
        mu = primary.gravitational_parameter
        mean_motion = period / (2*math.pi)
        semi_major_axis = (mean_motion**2 * mu)**(1./3)

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

        if math.isinf(period):
            raise InvalidElements(
                "cannot define parabolic/hyperbolic trajectory from period")

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

        o = orbit_angles.OrbitGeometry(eccentricity)
        v = true_anomaly_at_epoch
        M = o.mean_anomaly_at_true_anomaly(v)
        mean_anomaly_at_epoch = M

        return cls(
            primary, periapsis, eccentricity,
            inclination, longitude_of_ascending_node, argument_of_periapsis,
            epoch, mean_anomaly_at_epoch
        )


# if available, use a C versions

try:  # Python 3
    import cext.orbit_py3 as cext
except ImportError:
    try:  # Python 2
        import cext.orbit_py2 as cext
    except ImportError:
        sys.stderr.write("Note: to improve performance, run `make` in cext/\n")
        cext = None

if cext is not None:
    @classmethod
    def from_state(cls, primary, position, velocity, epoch=0):
        mu = primary.gravitational_parameter
        elements = cext.elements_from_state(mu, position, velocity, epoch)
        return cls(primary, *elements)
    OrbitDetermination.from_state = from_state
