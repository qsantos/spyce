import math


""" Vector manipulation functions

We only care 3D: vectors are lists of length 3
"""

def dot(u, v):
    """ Dot product of vectors """
    u1, u2, u3 = u
    v1, v2, v3 = v
    return u1*v1 + u2*v2 + u3*v3

def norm(u):
    """ Norm of a vector """
    u1, u2, u3 = u
    return math.sqrt(u1*u1 + u2*u2 + u3*u3)

def cross(u, v):
    """ Cross product of vectors """
    u1, u2, u3 = u
    v1, v2, v3 = v
    return [
        u2*v3 - u3*v2,
        u3*v1 - u1*v3,
        u1*v2 - u2*v1,
    ]

def angle(u, v):
    """ Angle formed by two vectors """
    angle = math.acos(dot(u,v)/norm(u)/norm(v))
    # we need to check the orientation of the cross-product
    # relatively to (0,0,1), i.e. dot([0,0,1],cross(u,v)), or:
    if cross(u, v)[2] < 0:
        return -angle
    else:
        return angle
