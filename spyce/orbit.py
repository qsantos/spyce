import math

import vector
import orbit_determination
import orbit_angles
import orbit_state
import orbit_target


# NOTE: to ease reading, Orbit is split into three base classes
#       OrbitDetermination contains alternate constructors
#       OrbitAngles contains methods to convert anomalies and times
#       OrbitState contains methods to predict position and velocity
#       OrbitTarget contains methods to predict near approaches and encounters
class Orbit(
        orbit_determination.OrbitDetermination,
        orbit_angles.OrbitAngles,
        orbit_state.OrbitState,
        orbit_target.OrbitTarget,
        ):
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

        # normalize inclination within [0, math.pi]
        # a retrograde orbit has an inclination of exactly math.pi
        inclination %= 2*math.pi
        if inclination > math.pi:
            inclination -= math.pi
            longitude_of_ascending_node -= math.pi
            argument_of_periapsis -= math.pi
        longitude_of_ascending_node %= 2*math.pi
        argument_of_periapsis %= 2*math.pi

        self.primary = primary
        self.periapsis = float(periapsis)
        self.eccentricity = float(eccentricity)
        self.inclination = float(inclination)
        self.longitude_of_ascending_node = float(longitude_of_ascending_node)
        self.argument_of_periapsis = float(argument_of_periapsis)
        self.epoch = float(epoch)
        self.mean_anomaly_at_epoch = float(mean_anomaly_at_epoch)

        # semi-major axis
        if self.eccentricity == 1:  # parabolic trajectory
            self.semi_major_axis = float("inf")
        else:
            self.semi_major_axis = self.periapsis / (1 - self.eccentricity)

        # other distances
        self.apoapsis = self.semi_major_axis * (1 + self.eccentricity)
        self.semi_latus_rectum = self.periapsis * (1 + self.eccentricity)
        e2 = 1-self.eccentricity**2
        self.semi_minor_axis = self.semi_major_axis * math.sqrt(abs(e2))
        self.focus = self.semi_major_axis * self.eccentricity

        # mean motion
        mu = self.primary.gravitational_parameter
        if self.eccentricity == 1:  # parabolic trajectory
            self.mean_motion = 3 * math.sqrt(mu / (self.semi_latus_rectum)**3)
        else:
            self.mean_motion = math.sqrt(mu / abs(self.semi_major_axis)**3)

        # period
        if self.eccentricity >= 1:  # parabolic/hyperbolic trajectory
            self.period = float("inf")
        else:  # circular/elliptic orbit
            self.period = 2*math.pi / self.mean_motion

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
