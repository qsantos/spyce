import math


"""Matrix manipulation functions

We only care rotations in 3D: matrices are 3-by-3 arrays made with lists
"""

def identity():
    """Identity matrix"""
    return [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ]

def dot_v(m, v):
    """Matrix-vector multiplication"""
    # using sum and zip is pretty but slow
    return [sum(i*j for i,j in zip(u,v)) for u in m]

def dot_m(a, b):
    """Matrix-matrix multiplication"""
    return [dot_v(zip(*b), row) for row in a]

def rotation_rad(angle, x, y, z):
    """Rotation matrix of given angle (radians) around axis (x,y,z)"""
    s = math.sin(angle)
    c = math.cos(angle)
    d = math.sqrt(x*x + y*y + z*z)
    x, y, z = x/d, y/d, z/d
    return [
        [x*x*(1-c)+c,   x*y*(1-c)-z*s, x*z*(1-c)+y*s],
        [y*x*(1-c)+z*s, y*y*(1-c)+c,   y*z*(1-c)-x*s],
        [z*x*(1-c)-y*s, z*y*(1-c)+x*s, z*z*(1-c)+c],
    ]

def rotation(angle, x, y, z):
    """Rotation matrix of given angle (degrees) around axis (x,y,z)"""
    angle *= math.pi / 180
    return rotation_rad(angle, x, y, z)
