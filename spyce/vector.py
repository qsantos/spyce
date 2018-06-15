"""
Utilities for linear algebra

We only care about 3D:
  * vectors are lists of length 3
  * matrices are 3-by-3 lists of lists
"""

import math


class Vec3(list):
    def norm(u):
        return math.sqrt(u.dot(u))

    def dot(u, v):
        """Dot product"""
        u1, u2, u3 = u
        v1, v2, v3 = v
        return math.fsum([u1*v1, u2*v2, u3*v3])

    def cross(u, v):
        """Cross product"""
        u1, u2, u3 = u
        v1, v2, v3 = v
        return Vec3([
            u2*v3 - u3*v2,
            u3*v1 - u1*v3,
            u1*v2 - u2*v1,
        ])

    def angle(u, v):
        """Angle formed by two vectors"""
        r = u.dot(v)/u.norm()/v.norm()
        r = max(-1, min(1, r))
        return math.acos(r)

    def oriented_angle(u, v, normal=None):
        """Angle formed by two vectors"""
        if normal is None:
            normal = Vec3([0, 0, 1])
        geometric_angle = u.angle(v)
        if normal.dot(u.cross(v)) < 0:
            return -geometric_angle
        else:
            return geometric_angle

    def __mul__(u, s):
        x, y, z = u
        return Vec3([x*s, y*s, z*s])

    def __div__(u, s):
        x, y, z = u
        return Vec3([x/s, y/s, z/s])

    def __add__(u, v):
        x, y, z = u
        a, b, c = v
        return Vec3([x+a, y+b, z+c])

    def __iadd__(u, v):
        x, y, z = u
        a, b, c = v
        return Vec3([x+a, y+b, z+c])

    def __sub__(u, v):
        x, y, z = u
        a, b, c = v
        return Vec3([x-a, y-b, z-c])

    def __isub__(u, v):
        x, y, z = u
        a, b, c = v
        return Vec3([x-a, y-b, z-c])

    def __neg__(u):
        x, y, z = u
        return Vec3([-x, -y, -z])

    def __abs__(u):
        """Maximum metric (see Chebyshev distance)"""
        return max(abs(x) for x in u)


class Mat3(list):
    def __init__(cls, *args, **kwargs):
        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    def __sub__(A, B):
        # used by assertAlmostEqual()
        return Mat3([x-y for a, b in zip(A, B) for x, y in zip(a, b)])

    def __abs__(A):
        """Maximum metric (see Chebyshev distance)"""
        # used by assertAlmostEqual()
        return max(abs(a) for a in A)

    def __mul__(self, x):
        if isinstance(x, Mat3):  # matrix-matrix multiplication
            m = Mat3(zip(*x))
            return Mat3([m*row for row in self])
        else:  # matrix-vector multiplication
            return Vec3([sum(a*b for a, b in zip(row, x)) for row in self])

    @classmethod
    def rotation(cls, angle, x, y, z):
        """Rotation matrix of given angle (radians) around axis (x,y,z)"""
        s = math.sin(angle)
        c = math.cos(angle)
        d = math.sqrt(x*x + y*y + z*z)
        x, y, z = x/d, y/d, z/d
        return cls([
            [x*x*(1-c)+c,   x*y*(1-c)-z*s, x*z*(1-c)+y*s],
            [y*x*(1-c)+z*s, y*y*(1-c)+c,   y*z*(1-c)-x*s],
            [z*x*(1-c)-y*s, z*y*(1-c)+x*s, z*z*(1-c)+c],
        ])

    @classmethod
    def from_euler_angles(cls, alpha, beta, gamma):
        """Return the rotation matrix from the given Z1X2Z3 Euler angles"""
        # see https://en.wikipedia.org/wiki/Euler_angles#Rotation_matrix
        c1, s1 = math.cos(alpha), math.sin(alpha)
        c2, s2 = math.cos(beta),  math.sin(beta)
        c3, s3 = math.cos(gamma), math.sin(gamma)
        return cls([
            [c1*c3-c2*s1*s3, -c1*s3-c2*c3*s1, s1*s2],
            [c3*s1+c1*c2*s3, c1*c2*c3-s1*s3,  -c1*s2],
            [s2*s3,          c3*s2,           c2],
        ])


class Vec4(list):
    def __init__(cls, x=0, y=0, z=0, w=1):
        super().__init__([x, y, z, w])


class Mat4:
    def __init__(self, v=None):
        if v is None:
            self.v = [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ]
        else:
            self.v = v

    def __sub__(A, B):
        return Mat4([x - y for a, b in zip(A, B) for x, y in zip(a, b)])

    def __abs__(A):
        """Maximum metric (see Chebyshev distance)"""
        return max(abs(a) for a in A)

    def transpose(self):
        return Mat4(list(zip(*self.v)))

    def __matmul__(self, other):
        if isinstance(other, Mat4):  # matrix-matrix multiplication
            m = other.transpose()
            return Mat4([m @ row for row in self.v])
        else:  # matrix-vector multiplication
            return [sum(a * b for a, b in zip(row, other)) for row in self.v]

    def row_major(self):
        return [v for row in self.v for v in row]

    def column_major(self):
        return [v for col in zip(*self.v) for v in col]

    @classmethod
    def translate(cls, x, y, z):
        """Rotation matrix of given angle (radians) around axis (x,y,z)"""
        return cls([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1],
        ])

    @classmethod
    def scale(cls, x, y, z):
        """Rotation matrix of given angle (radians) around axis (x,y,z)"""
        return cls([
            [x, 0, 0, 0],
            [0, y, 0, 0],
            [0, 0, z, 0],
            [0, 0, 0, 1],
        ])

    @classmethod
    def rotate(cls, angle, x, y, z):
        """Rotation matrix of given angle (radians) around axis (x,y,z)"""
        s = math.sin(angle)
        c = math.cos(angle)
        d = math.sqrt(x*x + y*y + z*z)
        x, y, z = x/d, y/d, z/d
        return cls([
            [x*x*(1-c)+c,   x*y*(1-c)-z*s, x*z*(1-c)+y*s, 0],
            [y*x*(1-c)+z*s, y*y*(1-c)+c,   y*z*(1-c)-x*s, 0],
            [z*x*(1-c)-y*s, z*y*(1-c)+x*s, z*z*(1-c)+c,   0],
            [0, 0, 0, 1],
        ])

    @classmethod
    def frustrum(cls, left, right, bottom, top, near, far):
        A = (right + left) / (right - left)
        B = (top + bottom) / (top - bottom)
        C = - (far + near) / (far - near)
        D = - (2*far * near) / (far - near)
        return cls([
            [2 * near / (right - left), 0, A, 0],
            [0, 2 * near / (top - bottom), B, 0],
            [0, 0, C, D],
            [0, 0, -1, 0],
        ])

    @classmethod
    def ortho(cls, left, right, bottom, top, near, far):
        tx = - (right + left) / (right - left)
        ty = - (top + bottom) / (top - bottom)
        tz = - (far + near) / (far - near)
        return cls([
            [2 / (right - left), 0, 0, tx],
            [0, 2 / (top - bottom), 0, ty],
            [0, 0, -2 / (far - near), tz],
            [0, 0, 0, 1],
        ])
