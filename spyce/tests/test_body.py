import unittest

import random

import orbit
import body


class TestBody(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
