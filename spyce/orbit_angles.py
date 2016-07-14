import sys
import math

import analysis


class OrbitGeometry(object):
    def __init__(self, eccentricity):
        self.eccentricity = eccentricity

    def __repr__(self):
        return "%s(eccentricity=%f)" % (type(self).__name__, self.eccentricity)

    def ejection_angle(self):
        """"Ejection angle (true anomaly at infinity)

        Normally used for parabolic or hyperbolic trajectories
        """
        if self.eccentricity < 1:  # closed orbit
            return float('inf')
        else:
            # when inf = p / (1 + e cos theta),
            # 1 + e cos theta = 0
            return math.acos(-1. / self.eccentricity)

    def mean_anomaly_at_eccentric_anomaly(self, eccentric_anomaly):
        e = self.eccentricity
        E = eccentric_anomaly
        if e < 1:
            return E - e*math.sin(E)
        elif e == 1:
            return (E**3 + E*3) / 2
        else:
            return e*math.sinh(E) - E

    def mean_anomaly_at_true_anomaly(self, true_anomaly):
        E = self.eccentric_anomaly_at_true_anomaly(true_anomaly)
        return self.mean_anomaly_at_eccentric_anomaly(E)

    def eccentric_anomaly_at_mean_anomaly(self, mean_anomaly):
        M = mean_anomaly
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
        elif e == 1:
            z = (M + math.sqrt(M**2+1))**(1./3)
            return z - 1/z
        else:  # M = e sinh E - E
            # sinh(E) = E -> M = (e - 1) E
            if abs(M) < 2**-26:
                return M / (e - 1)

            return analysis.newton_raphson(
                x_0=1,
                f=lambda E: e*math.sinh(E) - E - M,
                f_prime=lambda E: e*math.cosh(E) - 1,
            )

    def eccentric_anomaly_at_true_anomaly(self, true_anomaly):
        """Eccentric anomaly at given time, mean anomaly, or true anomaly"""
        v = true_anomaly
        if self.eccentricity < 1:  # circular or elliptic orbit
            x = math.sqrt(1+self.eccentricity)*math.cos(v/2)
            y = math.sqrt(1-self.eccentricity)*math.sin(v/2)
            return 2 * math.atan2(y, x)
        elif self.eccentricity == 1:  # parabolic trajectory
            return math.tan(v / 2)
        else:  # hyperbolic trajectory
            e = self.eccentricity
            return 2 * math.atanh(math.sqrt((e-1)/(e+1)) * math.tan(v/2))

    def true_anomaly_at_mean_anomaly(self, mean_anomaly):
        E = self.eccentric_anomaly_at_mean_anomaly(mean_anomaly)
        return self.true_anomaly_at_eccentric_anomaly(E)

    def true_anomaly_at_eccentric_anomaly(self, eccentric_anomaly):
        E = eccentric_anomaly
        if self.eccentricity < 1:  # circular or elliptic orbit
            x = math.sqrt(1-self.eccentricity)*math.cos(E/2)
            y = math.sqrt(1+self.eccentricity)*math.sin(E/2)
            return 2 * math.atan2(y, x)
        elif self.eccentricity == 1:  # parabolic trajectory
            return 2 * math.atan(E)
        else:  # hyperbolic trajectory
            x = math.sqrt(self.eccentricity-1)*math.cosh(E/2)
            y = math.sqrt(self.eccentricity+1)*math.sinh(E/2)
            return 2 * math.atan2(y, x)


class OrbitAngles(OrbitGeometry):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    def time_at_mean_anomaly(self, mean_anomaly):
        return self.epoch + \
            (mean_anomaly - self.mean_anomaly_at_epoch) / self.mean_motion

    def time_at_eccentric_anomaly(self, eccentric_anomaly):
        M = self.mean_anomaly_at_eccentric_anomaly(eccentric_anomaly)
        return self.time_at_mean_anomaly(M)

    def time_at_true_anomaly(self, true_anomaly):
        M = self.mean_anomaly_at_true_anomaly(true_anomaly)
        return self.time_at_mean_anomaly(M)

    def mean_anomaly_at_time(self, time):
        return self.mean_anomaly_at_epoch + \
            self.mean_motion * (time - self.epoch)

    def eccentric_anomaly_at_time(self, time):
        M = self.mean_anomaly_at_time(time)
        return self.eccentric_anomaly_at_mean_anomaly(M)

    def true_anomaly_at_time(self, time):
        M = self.mean_anomaly_at_time(time)
        return self.true_anomaly_at_mean_anomaly(M)

    def true_anomaly_at_distance(self, distance):
        """Positive true anomaly when at the given distance from focus

        A non-circular orbit may reach a specific distance either once
        (periapsis and apoapsis), twice (anything in between) or never. Those
        two points always have opposite true anomalies. The positive one is
        returned if it exists; otherwise, None is returnd.

        A circular orbit is either always or never at the distance. For this
        reason, they always return None.
        """

        # circular orbit
        if self.eccentricity == 0:
            return None

        # too high a periapsis
        if distance < self.periapsis:
            return None

        # parabolic orbit with too low an apoapsis
        if 0 < self.apoapsis <= distance:
            return None

        return math.acos(
            (self.semi_latus_rectum / distance - 1) / self.eccentricity
        )

    def true_anomaly_at_escape(self):
        """True anomaly when escaping the primary's sphere of influence"""
        return self.true_anomaly_at_distance(self.primary.sphere_of_influence)


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
    def true_anomaly_at_mean_anomaly(self, mean_anomaly):
        e = self.eccentricity
        M = mean_anomaly
        return cext.true_anomaly_at_mean_anomaly(e, M)
    OrbitGeometry.true_anomaly_at_mean_anomaly = true_anomaly_at_mean_anomaly
