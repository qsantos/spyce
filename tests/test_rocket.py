import unittest

import spyce.orbit
import spyce.ksp_cfg
import spyce.rocket
import spyce.load


class TestRocket(unittest.TestCase):
    def do_simulation(self, eccentricity):
        primary = spyce.load.kerbol['Kerbin']
        ship = spyce.rocket.Rocket(primary)
        ship |= spyce.ksp_cfg.PartSet().make(
            'Size3LargeTank', 'Size3LargeTank', 'Size3EngineCluster',
        )

        # enable physics simulation with no actual thrust
        ship.throttle = 1.
        ship.propellant = 0.

        # disable simulation of encounter with other satellites for performance
        satellites = primary.satellites
        primary.satellites = set()

        # set ship on orbit
        o = spyce.orbit.Orbit(primary, 700e3, eccentricity)
        ship.position = o.position_at_true_anomaly(0.)
        ship.velocity = o.velocity_at_true_anomaly(0.)

        # ship simulation
        n = 1000
        dt = .1
        for i in range(n):
            ship.simulate(i * dt, dt)

        # check consistency of simulation with Kepler orbits
        self.assertAlmostEqual(o.position_at_time(n * dt), ship.position)
        self.assertAlmostEqual(o.velocity_at_time(n * dt), ship.velocity)

        # restore satellites
        primary.satellites = satellites

    def test_simulation(self):
        self.do_simulation(0.)
        self.do_simulation(.5)
        self.do_simulation(1.)
        self.do_simulation(2.)


if __name__ == '__main__':
    unittest.main()
