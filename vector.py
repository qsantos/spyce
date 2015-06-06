"""
Utilities for linear algebra

We only care 3D:
  * vectors are lists of length 3
  * matrices are 3-by-3 lists of lists
"""

import math


class Vector(list):
    def __mul__(self, s):
        return Vector(x*s for x in self)

    def __div__(self, s):
        return Vector(x/s for x in self)

    def __add__(self, v):
        return Vector(x+y for x, y in zip(self, v))

    def __iadd__(self, v):
        return self + v

    def __sub__(self, v):
        return Vector(x-y for x, y in zip(self, v))

    def __isub__(self, v):
        return self - v


def dot(u, v):
    """Dot product of vectors"""
    u1, u2, u3 = u
    v1, v2, v3 = v
    return math.fsum([u1*v1, u2*v2, u3*v3])


def norm(u):
    """Norm of a vector"""
    return math.sqrt(dot(u, u))


def cross(u, v):
    """Cross product of vectors"""
    u1, u2, u3 = u
    v1, v2, v3 = v
    return [
        u2*v3 - u3*v2,
        u3*v1 - u1*v3,
        u1*v2 - u2*v1,
    ]


def angle(u, v):
    """Angle formed by two vectors"""
    r = dot(u, v)/norm(u)/norm(v)
    r = max(-1, min(1, r))
    return math.acos(r)


def oriented_angle(u, v, normal=[0, 0, 1]):
    """Angle formed by two vectors"""
    geometric_angle = angle(u, v)
    if dot(normal, cross(u, v)) < 0:
        return -geometric_angle
    else:
        return geometric_angle


class Matrix(list):
    def __mul__(self, x):
        if type(x) == Matrix:
            # matrix-matrix multiplication
            m = Matrix(zip(*x))
            return Matrix(m*row for row in self)
        else:
            # matrix-vector multiplication
            return Vector(sum(a*b for a, b in zip(row, x)) for row in self)

    @classmethod
    def identity(cls):
        return cls([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

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
