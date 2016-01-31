import unittest

import random

import orbit
import ksp_cfg
import rocket
from load import kerbol


class TestRocket(unittest.TestCase):
    def test_simulation(self):
        primary = kerbol['Kerbin']
        ship = rocket.Rocket(primary)
        ship |= ksp_cfg.PartSet().make(
            'Size3LargeTank', 'Size3LargeTank', 'Size3EngineCluster',
        )

        # enable physics simulation with no actual thrust
        ship.throttle = 1.
        ship.propellant = 0.

        # set ship on orbit
        o = orbit.Orbit(primary, 700e3, random.uniform(0., 2.))
        ship.position = o.position(0.)
        ship.velocity = o.velocity(0.)

        # ship simulation
        n = 1000
        dt = .1
        for i in range(n):
            ship.simulate(i * dt, dt)

        self.assertAlmostEqual(o.position_t(n * dt), ship.position)
        self.assertAlmostEqual(o.velocity_t(n * dt), ship.velocity)


if __name__ == '__main__':
    unittest.main()
