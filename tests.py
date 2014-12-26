import math
import random


import vector

# easily verified
assert vector.dot([1, 0, 0], [0, 1, 1]) == 0
assert vector.norm([8, 9, 12]) == 17
assert vector.cross([0, 1, 0], [1, 0, 0]) == [0, 0, -1]
assert vector.angle([0, 1, 0], [1, 0, 0]) == -math.pi/2

# initial results
assert vector.dot([1, 4, 7], [2, 5, 8]) == 78
assert vector.norm([4, 5, 6]) == 8.774964387392123
assert vector.cross([9, 8, 7], [2, 3, 1]) == [-13, 5, 11]
assert vector.angle([4, 7, 5], [3, 5, 8]) == -0.3861364787976416
assert vector.angle([4, 5, 7], [3, 8, 5]) == +0.3861364787976416


def checkdiff(A, B):
    for i in range(3):
        for j in range(3):
            a = A[i][j]
            b = B[i][j]
            if abs(a - b) > 1e-10:
                return False
    return True

# easily verified
i = vector.Matrix.identity()
m = vector.Matrix([[2, 0, 0], [0, 2, 0], [0, 0, 2]])
r = vector.Matrix.rotation(math.pi/2, 1, 0, 0)
assert i * [1, 2, 3] == [1, 2, 3]
assert m * [1, 2, 3] == [2, 4, 6]
assert i * i == i
assert m * m == [[4, 0, 0], [0, 4, 0], [0, 0, 4]]
assert checkdiff(r, [[1, 0, 0], [0, 0, -1], [0, 1, 0]])

for _ in range(10):
    angle = random.uniform(0, math.pi)
    x = random.uniform(0, 1)
    y = random.uniform(0, 1)
    r = vector.Matrix.rotation(angle, 0, 0, 1)
    u = [x, y, 0]
    v = r * u
    assert abs(angle - vector.angle(u, v)) < 1e-6

# initial results
A = vector.Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
B = vector.Matrix([[3, 2, 1], [6, 5, 4], [9, 8, 7]])
assert A * B == [[42, 36, 30], [96, 81, 66], [150, 126, 102]]
assert B * A == [[18, 24, 30], [54, 69, 84], [90, 114, 138]]

m = vector.Matrix([
    [0.33482917221585295, 0.8711838511445769, -0.3590656248350022],
    [-0.66651590413407, 0.4883301324737331, 0.5632852130622015],
    [0.6660675453507625, 0.050718627969319086, 0.7441650662368666],
])
r = vector.Matrix.rotation(5, 1, 2, 3)
assert checkdiff(r, m)


import orbit


class Object:
    pass
b = Object()
b.mass = 1e30


def check_val(a, b):
    if a == 0:
        return b < 1e-6
    else:
        return abs(a-b) / a < 1e-6


def check_orbit(o1, o2):
    return (
        check_val(o1.semimajor, o2.semimajor) and
        check_val(o1.eccentricity, o2.eccentricity) and
        check_val(o1.inclination, o2.inclination) and
        (o1.inclination == 0 or check_val(o1.ascending, o2.ascending)) and
        (o1.eccentricity == 0 or check_val(o1.argument, o2.argument)) and
        True
    )


def check_fromstate(o1):
    o2 = orbit.Orbit.from_state(b, o.position(7), o.velocity(7))
    return check_orbit(o1, o2)

for _ in range(10):
    a = random.uniform(1e07, 1e09)
    e = random.uniform(0.1,  0.9)
    inc = random.uniform(0, math.pi)
    lan = random.uniform(0, math.pi)
    aop = random.uniform(0, math.pi)
    o = orbit.Orbit(b, a, e, 0, inc, lan, aop)
    assert (o.apoapsis + o.periapsis) / 2 - a < 1e-3
    assert check_fromstate(o)

for _ in range(10):
    p = random.uniform(1e07, 1e10)
    a = random.uniform(1e07, 1e09)
    inc = random.uniform(0, math.pi)
    lan = random.uniform(0, math.pi)
    aop = random.uniform(0, math.pi)
    o = orbit.Orbit.from_period_apsis(b, p, a, 0, inc, lan, aop)
    assert o.period - p < 1e-5
    assert (o.apoapsis - a < 1e-3) or (o.periapsis - a) < 1e-3
    assert check_fromstate(o)


import body

A = body.CelestialBody("A", 1e30)
o = orbit.Orbit(A, random.uniform(1e10, 1e11))
b_mass = random.uniform(1e07, 1e09)
b_radius = random.uniform(1e7, 1e8)
b_rot_period = random.uniform(1e3, 1e5)
B = body.CelestialBody("B", b_mass, b_radius, b_rot_period, o)
t = random.randint(1e6, 1e8)
assert round(B.str2time(B.time2str(t))) == t


import solar
import kerbol


def check_mass(b):
    assert b.mass > 1e9
    for s in b.satellites:
        check_mass(s)
check_mass(solar .Sun)
check_mass(kerbol.Kerbol)


import cfg
try:  # Python 2
    from StringIO import StringIO
except ImportError:  # Python 3
    from io import StringIO

assert cfg.parse(StringIO("""
PART
{
name = somepart
}
""")) == {'PART': {'name': 'somepart'}}

assert cfg.parse(StringIO("""
PART
{
MODULE
{
name = somemodule
}
}""")) == {'PART': {'MODULE': {'name': 'somemodule'}}}

part = cfg.parse(StringIO("""
PART
{
MODULE
{
name = first
}
MODULE
{
name = second
}
}
"""))
assert part == {'PART': {'MODULE': [{'name': 'first'}, {'name': 'second'}]}}

part = part['PART']
assert cfg.dic_get_group(part, 'MODULE', 'first') == {'name': 'first'}
