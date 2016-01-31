import unittest
import math
import random

import orbit


# isclose() from PEP 485
try:
    from math import isclose
except ImportError:
    def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
        return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


# dummy primary object
primary = type('Object', (), {'gravitational_parameter': 1e20})()


def random_angle():
    if random.randrange(2):
        return random.choice([-1, 1]) * random.choice(
            [0, math.pi/4, math.pi/2, math.pi])
    else:
        return random.uniform(-math.pi, math.pi)


def random_eccentricity():
    return random.choice([
        0.0,
        random.uniform(0.0, 1.0),
        1.0,
        1.0 + random.expovariate(0.25),
    ])


def random_orbit():
    periapsis = random.expovariate(1e-9)
    eccentricity = random_eccentricity()
    inclination = abs(random_angle())
    longitude_of_ascending_node = random_angle()
    argument_of_periapsis = random_angle()

    return orbit.Orbit(
        primary, periapsis, eccentricity,
        inclination, longitude_of_ascending_node, argument_of_periapsis,
    )


class TestOrbit(unittest.TestCase):
    def assertIsClose(self, first, second, rel_tol=1e-9, msg=None, abs_tol=0.):
        ok = isclose(first, second, rel_tol=rel_tol, abs_tol=abs_tol)
        self.assertTrue(ok, msg=msg)

    def assertAlmostEqualAngle(self, first, second, places=7, msg=None,
                               delta=None):
        angle_diff = (first-second + math.pi) % (2*math.pi) - math.pi
        self.assertAlmostEqual(angle_diff, 0, places, msg, delta)

    def assertAlmostEqualOrbits(self, a, b):
        self.assertIsClose(a.periapsis, b.periapsis)
        self.assertAlmostEqual(a.eccentricity, b.eccentricity)
        self.assertAlmostEqualAngle(a.inclination, b.inclination)

        # longitude of ascending node
        if a.inclination not in (0., math.pi):
            self.assertAlmostEqualAngle(a.longitude_of_ascending_node,
                                        b.longitude_of_ascending_node)

        # argument of periapsis
        if a.eccentricity != 0:
            argument_of_periapsis_a = a.argument_of_periapsis
            argument_of_periapsis_b = b.argument_of_periapsis
            if a.inclination == 0:
                argument_of_periapsis_a += a.longitude_of_ascending_node
                argument_of_periapsis_b += b.longitude_of_ascending_node
            elif a.inclination == math.pi:
                argument_of_periapsis_a -= a.longitude_of_ascending_node
                argument_of_periapsis_b -= b.longitude_of_ascending_node
            self.assertAlmostEqualAngle(argument_of_periapsis_a,
                                        argument_of_periapsis_b)

        # mean anomaly
        if 0 < a.eccentricity < 1:
            instant = random.uniform(-1e6, 1e6)
            self.assertAlmostEqualAngle(a.mean_anomaly(instant),
                                        b.mean_anomaly(instant))

    def orbit(self, o):
        # check true anomaly at periapsis and apoapsis
        self.assertAlmostEqual(o.true_anomaly(0), 0)
        if o.eccentricity < 1:
            apoapsis_time = (math.pi - o.mean_anomaly_at_epoch) / o.mean_motion
            self.assertAlmostEqual(o.true_anomaly(apoapsis_time), math.pi)

        # gather orbit characteristics
        args = o.__dict__
        args["apsis"] = o.periapsis if random.randrange(2) else o.apoapsis
        if random.randrange(2):
            args["apsis1"], args["apsis2"] = o.periapsis, o.apoapsis
        else:
            args["apsis1"], args["apsis2"] = o.apoapsis, o.periapsis

        # re-generate from semi-major axis
        if o.eccentricity != 1:  # semi-major axis is infinite
            new_orbit = orbit.Orbit.from_semi_major_axis(**args)
            self.assertAlmostEqualOrbits(o, new_orbit)

        # re-generate from apses
        self.assertAlmostEqualOrbits(o, orbit.Orbit.from_apses(**args))

        # re-generate from orbital period
        if o.eccentricity != 1:  # no period
            self.assertAlmostEqualOrbits(o, orbit.Orbit.from_period(**args))

        # re-generate from orbital period and apsis
        if o.eccentricity < 1:  # can't tell hyperbolic from elliptic
            new_orbit = orbit.Orbit.from_period_apsis(**args)
            self.assertAlmostEqualOrbits(o, new_orbit)

        # re-generate from state point
        instant = random.expovariate(1e-6) * random.choice([-1, 1])
        p, v = o.position_t(instant), o.velocity_t(instant)
        new_orbit = orbit.Orbit.from_state(primary, p, v, instant)
        self.assertAlmostEqualOrbits(o, new_orbit)

    def test_random(self):
        for _ in range(400):
            self.orbit(random_orbit())


if __name__ == '__main__':
    unittest.main()
