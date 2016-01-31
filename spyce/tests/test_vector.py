import unittest

import math
import random

from vector import *


class TestVector(unittest.TestCase):
    def test_vector(self):
        # easily verified
        self.assertEqual(dot([1, 0, 0], [0, 1, 1]), 0)
        self.assertEqual(norm([8, 9, 12]), 17)
        self.assertEqual(cross([0, 1, 0], [1, 0, 0]), [0, 0, -1])
        self.assertEqual(angle([0, 1, 0], [1, 0, 0]), math.pi/2)
        self.assertEqual(oriented_angle([0, 1, 0], [1, 0, 0]), -math.pi/2)

        # initial results
        self.assertEqual(dot([1, 4, 7], [2, 5, 8]), 78)
        self.assertEqual(norm([4, 5, 6]), 8.774964387392123)
        self.assertEqual(cross([9, 8, 7], [2, 3, 1]), [-13, 5, 11])
        self.assertEqual(angle([4, 7, 5], [3, 5, 8]), 0.3861364787976416)
        self.assertEqual(angle([4, 7, 5], [3, 5, 8]), 0.3861364787976416)

        v = 0.3861364787976416
        self.assertEqual(oriented_angle([4, 7, 5], [3, 5, 8]), -v)
        self.assertEqual(oriented_angle([4, 5, 7], [3, 8, 5]), +v)

    def test_matrix(self):
        # easily verified
        i = Matrix.identity()
        m = Matrix([[2, 0, 0], [0, 2, 0], [0, 0, 2]])
        r = Matrix.rotation(math.pi/2, 1, 0, 0)
        self.assertEqual(i * [1, 2, 3], [1, 2, 3])
        self.assertEqual(m * [1, 2, 3], [2, 4, 6])
        self.assertEqual(i * i, i)
        self.assertEqual(m * m, [[4, 0, 0], [0, 4, 0], [0, 0, 4]])
        self.assertAlmostEqual([[1, 0, 0], [0, 0, -1], [0, 1, 0]], r)

        # initial results
        A = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        B = Matrix([[3, 2, 1], [6, 5, 4], [9, 8, 7]])
        self.assertEqual(A * B, [[42, 36, 30], [96, 81, 66], [150, 126, 102]])
        self.assertEqual(B * A, [[18, 24, 30], [54, 69, 84], [90, 114, 138]])

    def test_rotation(self):
        for _ in range(10):
            a = random.uniform(0, math.pi)
            x = random.uniform(0, 1)
            y = random.uniform(0, 1)
            r = Matrix.rotation(a, 0, 0, 1)
            u = [x, y, 0]
            v = r * u
            self.assertAlmostEqual(a, angle(u, v))

        m = Matrix([
            [0.33482917221585295, 0.8711838511445769, -0.3590656248350022],
            [-0.66651590413407, 0.4883301324737331, 0.5632852130622015],
            [0.6660675453507625, 0.050718627969319086, 0.7441650662368666],
        ])
        r = Matrix.rotation(5, 1, 2, 3)
        self.assertAlmostEqual(r, m)


if __name__ == '__main__':
    unittest.main()
