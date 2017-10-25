import unittest

import math
import random

from spyce.vector import Vec3, Mat3


class TestVector(unittest.TestCase):
    def test_vector(self):

        # shorthands
        def norm(u): return Vec3(u).norm()

        def dot(u, v): return Vec3(u).dot(Vec3(v))

        def cross(u, v): return Vec3(u).cross(Vec3(v))

        def angle(u, v): return Vec3(u).angle(Vec3(v))

        def oriented_angle(u, v): return Vec3(u).oriented_angle(Vec3(v))

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

        v = 0.3861364787976416
        self.assertEqual(angle([4, 7, 5], [3, 5, 8]), v)
        self.assertEqual(angle([4, 7, 5], [3, 5, 8]), v)
        self.assertEqual(oriented_angle([4, 7, 5], [3, 5, 8]), -v)
        self.assertEqual(oriented_angle([4, 5, 7], [3, 8, 5]), +v)

    def test_matrix(self):
        # easily verified
        i = Mat3()
        m = Mat3([[2, 0, 0], [0, 2, 0], [0, 0, 2]])
        r = Mat3.rotation(math.pi/2, 1, 0, 0)
        self.assertEqual(i * [1, 2, 3], [1, 2, 3])
        self.assertEqual(m * [1, 2, 3], [2, 4, 6])
        self.assertEqual(i * i, i)
        self.assertEqual(m * m, [[4, 0, 0], [0, 4, 0], [0, 0, 4]])
        self.assertAlmostEqual([[1, 0, 0], [0, 0, -1], [0, 1, 0]], r)

        # initial results
        A = Mat3([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        B = Mat3([[3, 2, 1], [6, 5, 4], [9, 8, 7]])
        self.assertEqual(A * B, [[42, 36, 30], [96, 81, 66], [150, 126, 102]])
        self.assertEqual(B * A, [[18, 24, 30], [54, 69, 84], [90, 114, 138]])

    def test_rotation(self):
        for _ in range(10):
            a = random.uniform(0, math.pi)
            x = random.uniform(0, 1)
            y = random.uniform(0, 1)
            r = Mat3.rotation(a, 0, 0, 1)
            u = Vec3([x, y, 0])
            v = r * u
            self.assertAlmostEqual(a, u.angle(v))

        m = Mat3([
            [0.33482917221585295, 0.8711838511445769, -0.3590656248350022],
            [-0.66651590413407, 0.4883301324737331, 0.5632852130622015],
            [0.6660675453507625, 0.050718627969319086, 0.7441650662368666],
        ])
        r = Mat3.rotation(5, 1, 2, 3)
        self.assertAlmostEqual(r, m)


if __name__ == '__main__':
    unittest.main()
