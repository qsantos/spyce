import unittest

import math
import time

import spyce.analysis


class TestAnalysis(unittest.TestCase):
    def test_newton_raphson(self):
        x = spyce.analysis.newton_raphson(
            x_0=1.4,
            f=lambda x: x**2 - 2,
            f_prime=lambda x: 2*x,
        )
        self.assertEqual(x, math.sqrt(2))

    def integration(self, method, n_iterations, step):
        # set problem: free fall on Earth surface
        def f(t, y):
            return [y[1], -9.81]  # velocity, acceleration
        y = [0, 0]  # position, velocity

        # integrate and measure computation time
        last = time.time()
        for iteration in range(n_iterations):
            y = method(f, iteration*step, y, step)
        elapsed = time.time() - last

        # relative error
        expected = - .5 * 9.81 * (n_iterations * step)**2
        error = abs(y[0] - expected) / max(abs(y[0]), abs(expected))

        return error, elapsed

    def test_euler(self):
        error, elapsed = self.integration(spyce.analysis.euler, 100000, 0.1)
        self.assertLess(error, 1e-4)
        self.assertLess(elapsed, 1.0)

    def test_rk4(self):
        error, elapsed = self.integration(spyce.analysis.runge_kutta_4, 100000, 0.1)
        self.assertLess(error, 1e-12)
        self.assertLess(elapsed, 1.0)


if __name__ == '__main__':
    unittest.main()
