import unittest
import math
import itertools

import orbit


# isclose() from PEP 485
try:
    from math import isclose
except ImportError:
    def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
        return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


# dummy primary object
class DummyPrimary(object):
    gravitational_parameter = 1e20

    def __repr__(self):
        return 'X'
primary = DummyPrimary()


class TestOrbit(unittest.TestCase):
    longMessage = True

    def assertIsClose(self, first, second, rel_tol=1e-9, msg=None, abs_tol=0.):
        ok = isclose(first, second, rel_tol=rel_tol, abs_tol=abs_tol)
        self.assertTrue(ok, msg=msg)

    def assertAlmostEqualAngle(self, first, second, places=7, msg=None,
                               delta=None):
        angle_diff = (first-second + math.pi) % (2*math.pi) - math.pi
        self.assertAlmostEqual(angle_diff, 0, places, msg, delta)

    def assertAlmostEqualOrbits(self, a, b):
        msg = '\n' + str(a) + ' != ' + str(b)

        self.assertIsClose(a.periapsis, b.periapsis, msg=msg)
        self.assertAlmostEqual(a.eccentricity, b.eccentricity, msg=msg)
        self.assertAlmostEqualAngle(a.inclination, b.inclination, msg=msg)

        # longitude of ascending node
        if a.inclination not in (0., math.pi):
            self.assertAlmostEqualAngle(a.longitude_of_ascending_node,
                                        b.longitude_of_ascending_node, msg=msg)

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
                                        argument_of_periapsis_b, msg=msg)

        # mean anomaly
        if a.eccentricity != 0:
            self.assertAlmostEqualAngle(a.mean_anomaly(0), b.mean_anomaly(0),
                                        msg=msg)

    def orbit(self, o):
        # check true anomaly at periapsis and apoapsis
        self.assertAlmostEqual(o.true_anomaly(0), 0)
        if o.eccentricity < 1:
            apoapsis_time = (math.pi - o.mean_anomaly_at_epoch) / o.mean_motion
            self.assertAlmostEqual(o.true_anomaly(apoapsis_time), math.pi)

        # gather orbit characteristics
        args = o.__dict__

        # re-generate from semi-major axis
        if o.eccentricity != 1:  # semi-major axis is infinite
            new_orbit = orbit.Orbit.from_semi_major_axis(**args)
            self.assertAlmostEqualOrbits(o, new_orbit)

        # re-generate from apses
        self.assertAlmostEqualOrbits(o, orbit.Orbit.from_apses(
            apsis1=o.periapsis, apsis2=o.apoapsis, **args))
        # also try with inverted apses
        self.assertAlmostEqualOrbits(o, orbit.Orbit.from_apses(
            apsis1=o.apoapsis, apsis2=o.periapsis, **args))

        # re-generate from orbital period
        if o.eccentricity != 1:  # no period
            self.assertAlmostEqualOrbits(o, orbit.Orbit.from_period(**args))

        # re-generate from orbital period and apsis
        if o.eccentricity < 1:  # can't tell hyperbolic from elliptic
            self.assertAlmostEqualOrbits(o, orbit.Orbit.from_period_apsis(
                apsis=o.periapsis, **args))
            # also try with apoapsis
            self.assertAlmostEqualOrbits(o, orbit.Orbit.from_period_apsis(
                apsis=o.apoapsis, **args))

        # re-generate from state point at arbitrary time
        time = 1e4
        position, velocity = o.position_t(time), o.velocity_t(time)
        new_orbit = orbit.Orbit.from_state(primary, position, velocity, time)
        self.assertAlmostEqualOrbits(o, new_orbit)

    def test_all(self):
        periapsis = (1e9, 1e13)
        eccentricity = (0.0, 0.00001, 0.5, 0.99999, 1.0, 1.00001, 10.0)
        angle = (-math.pi/2, 0, math.pi/4, math.pi/2, math.pi)
        for elements in itertools.product(periapsis, eccentricity, angle,
                                          angle, angle):
            self.orbit(orbit.Orbit(primary, *elements))

if __name__ == '__main__':
    unittest.main()
