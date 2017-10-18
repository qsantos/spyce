import unittest

import spyce.physics
import spyce.load


class TestSystems(unittest.TestCase):
    def system(self, system):
        stars = [body for body in system.values() if body.orbit is None]

        # star count
        self.assertEqual(len(stars), 1)

        for body in system.values():
            for satellite in body.satellites:
                self.assertLess(satellite.mass, body.mass)
            if body.orbit is not None:
                self.assertGreater(body.orbit.period, 3600)

    def test_kerbol(self):
        self.system(spyce.load.kerbol)

        Kerbol = spyce.load.kerbol['Kerbol']

        # planet count
        n_planets = len(Kerbol.satellites)
        self.assertEqual(n_planets, 7)

        # system radius
        for satellite in Kerbol.satellites:
            self.assertLess(satellite.orbit.apoapsis, spyce.physics.au)

    def test_solar(self):
        self.system(spyce.load.solar)

        Sun = spyce.load.solar['Sun']

        # planet count
        n_planets = sum(1 for planet in Sun.satellites if planet.mass > 1e23)
        self.assertEqual(n_planets, 8)

        # system radius
        for satellite in Sun.satellites:
            self.assertLess(satellite.orbit.apoapsis, 1e3 * spyce.physics.au)


if __name__ == '__main__':
    unittest.main()
