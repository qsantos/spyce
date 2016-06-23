import unittest

import math
import random
import physics

import orbit
import body
from load import solar


class TestBody(unittest.TestCase):
    def test_gravity(self):
        Earth = solar['Earth']
        self.assertAlmostEqual(Earth.gravity(), physics.g0, places=1)

        self.assertEqual(Earth.gravity(0), 0)

        self.assertEqual(Earth.gravity(Earth.radius / 2), Earth.gravity() / 2)

    def test_local_time(self):
        star = body.CelestialBody("star", 1e20)
        planet = body.CelestialBody(
            name="planet",
            rotational_period=random.uniform(1e3, 1e5),
            orbit=orbit.Orbit(star, random.uniform(1e10, 1e11))
        )

        time = random.randint(1e6, 1e8)
        local_time = planet.time2str(time)
        self.assertAlmostEqual(planet.str2time(local_time), time, places=0)

        time = -random.randint(1e6, 1e8)
        local_time = planet.time2str(time)
        self.assertAlmostEqual(planet.str2time(local_time), time, places=0)

    def test_escape_velocity_at_distance(self):
        Earth = solar['Earth']
        escape_velocity = Earth.escape_velocity_at_distance(Earth.radius)
        self.assertAlmostEqual(escape_velocity, 11186, places=0)

    def test_angular_diameter(self):
        Sun = solar['Sun']
        Earth = solar['Earth']
        Moon = solar['Moon']

        computed = Sun.angular_diameter(Earth.orbit.periapsis)
        expected = math.radians(32./60 + 32./3600)
        self.assertAlmostEqual(computed, expected, places=5)

        computed = Moon.angular_diameter(Moon.orbit.apoapsis)
        expected = math.radians(29./60 + 26./3600)
        self.assertAlmostEqual(computed, expected, places=5)

    def test_name(self):
        Earth = solar['Earth']
        self.assertEqual(str(Earth), 'Earth')
        self.assertEqual(repr(Earth), '<Earth>')


if __name__ == '__main__':
    unittest.main()
