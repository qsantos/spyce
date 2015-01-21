import math
import random


import vector

# easily verified
assert vector.dot([1, 0, 0], [0, 1, 1]) == 0
assert vector.norm([8, 9, 12]) == 17
assert vector.cross([0, 1, 0], [1, 0, 0]) == [0, 0, -1]
assert vector.angle([0, 1, 0], [1, 0, 0]) == math.pi/2
assert vector.oriented_angle([0, 1, 0], [1, 0, 0]) == -math.pi/2

# initial results
assert vector.dot([1, 4, 7], [2, 5, 8]) == 78
assert vector.norm([4, 5, 6]) == 8.774964387392123
assert vector.cross([9, 8, 7], [2, 3, 1]) == [-13, 5, 11]
assert vector.angle([4, 7, 5], [3, 5, 8]) == 0.3861364787976416
assert vector.angle([4, 7, 5], [3, 5, 8]) == 0.3861364787976416
assert vector.oriented_angle([4, 7, 5], [3, 5, 8]) == -0.3861364787976416
assert vector.oriented_angle([4, 5, 7], [3, 8, 5]) == +0.3861364787976416


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
    def __repr__(self):
        return "<TestBody>"

primary = Object()
primary.gravitational_parameter = 1e20


def check_error(orbit, value_name, precision, value1, value2, error):
    if abs(error) > 2**-precision:
        print("Failed at:  %s" % value_name)
        print("Orbit was:  %s" % orbit)
        print("Values are: %.17f != %.17f" % (value1, value2))
        print("Valid bits: %g" % math.floor(-math.log(abs(error), 2)))
        exit(1)


def check_values(orbit, value_name, precision, value1, value2):
    error = value2 - value1
    if abs(value1)/2 < abs(value2) < 2*abs(value1):
        error /= value1
    check_error(orbit, value_name, precision, value1, value2, error)


def check_angles(orbit, value_name, precision, value1, value2):
    error = (value1 - value2) % (2*math.pi)
    if error > math.pi:
        error -= 2*math.pi
    check_error(orbit, value_name, precision, value1, value2, error)


def check_orbit(a, b):
    check_values(a, "periapsis", 19, a.periapsis, b.periapsis)
    check_values(a, "eccentricity", 26, a.eccentricity, b.eccentricity)
    check_angles(a, "inclination", 29, a.inclination, b.inclination)

    # longitude of ascending node
    if a.inclination != 0:
        check_angles(
            a, "longitude of ascending node", 22,
            a.longitude_of_ascending_node, b.longitude_of_ascending_node
        )

    # argument of periapsis
    if a.eccentricity != 0:
        angle_a = a.argument_of_periapsis
        angle_b = b.argument_of_periapsis
        if a.inclination == 0:
            angle_a += a.longitude_of_ascending_node
            angle_b += b.longitude_of_ascending_node
        check_angles(a, "argument of periapsis", 22, angle_a, angle_b)

    # mean anomaly
    if 0 < a.eccentricity < 1:
        instant = random.uniform(-1e6, 1e6)
        check_angles(a, "mean anomaly", 27,
                     a.mean_anomaly(instant),  b.mean_anomaly(instant))


def random_angle():
    if random.randrange(2):
        return random.choice([-1, 1]) * random.choice(
            [0, math.pi/4, math.pi/2, math.pi])
    else:
        return random.uniform(-math.pi, math.pi)


def check_eccentricity(eccentricity):
    periapsis = random.expovariate(1e-9)
    inclination = abs(random_angle())
    longitude_of_ascending_node = random_angle()
    argument_of_periapsis = random_angle()

    o = orbit.Orbit(
        primary, periapsis, eccentricity,
        inclination, longitude_of_ascending_node, argument_of_periapsis,
    )

    # check true anomaly at periapsis and apoapsis
    assert abs(o.true_anomaly(0)) < 2**-95
    if o.eccentricity < 1:
        apoapsis_time = (math.pi - o.mean_anomaly_at_epoch) / o.mean_motion
        assert abs(o.true_anomaly(apoapsis_time) - math.pi) < 2**-44

    args = o.__dict__
    args["apsis"] = o.periapsis if random.randrange(2) else o.apoapsis
    if random.randrange(2):
        args["apsis1"], args["apsis2"] = o.periapsis, o.apoapsis
    else:
        args["apsis1"], args["apsis2"] = o.apoapsis, o.periapsis

    if o.eccentricity != 1:  # semi-major_axis is infinite
        check_orbit(o, orbit.Orbit.from_semi_major_axis(**args))

    check_orbit(o, orbit.Orbit.from_apses(**args))

    if o.eccentricity != 1:  # no period
        check_orbit(o, orbit.Orbit.from_period(**args))

    if o.eccentricity < 1:  # can't tell hyperbolic from elliptic
        check_orbit(o, orbit.Orbit.from_period_apsis(**args))

    instant = random.expovariate(1e-6) * random.choice([-1, 1])
    p, v = o.position_t(instant), o.velocity_t(instant)
    check_orbit(o, orbit.Orbit.from_state(primary, p, v, instant))

# circular orbits
for _ in range(100):
    check_eccentricity(0)

# elliptic orbits
for _ in range(100):
    check_eccentricity(random.uniform(0, 1))

# parabolic trajectories
for _ in range(100):
    check_eccentricity(1)

# hyperbolic trajectories
for _ in range(100):
    check_eccentricity(1 + random.expovariate(.25))


import body

A = body.CelestialBody("A", 1e20)
o = orbit.Orbit(A, random.uniform(1e10, 1e11))
b_mu = random.uniform(1e07, 1e09)
b_radius = random.uniform(1e7, 1e8)
b_rotational_period = random.uniform(1e3, 1e5)
B = body.CelestialBody("B", b_mu, b_radius, b_rotational_period, o)
t = random.randint(1e6, 1e8)
assert round(B.str2time(B.time2str(t))) == t


import physics
import load

Kerbol = load.kerbol['Kerbol']
Sun = load.solar['Sun']
assert len(Kerbol.satellites) == 7
assert sum(1 for x in Sun.satellites if x.mass > 1e23) == 8
assert max(b.orbit.semi_major_axis for b in Sun.satellites) < 100*physics.au
assert max(b.orbit.semi_major_axis for b in Kerbol.satellites) < physics.au

for system in (load.kerbol, load.solar):
    assert sum(1 for b in system if system[b].orbit is None) == 1
    for name in system:
        body = system[name]
        for b in body.satellites:
            assert b.mass < body.mass, "%s is not satellite of %s" % (b, body)
        if body.orbit is not None:
            assert body.orbit.period > 3600, "%s has a short orbit" % body


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
""")) == {"PART": {"name": "somepart"}}

assert cfg.parse(StringIO("""
PART
{
MODULE
{
name = somemodule
}
}""")) == {"PART": {"MODULE": {"name": "somemodule"}}}

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
assert part == {"PART": {"MODULE": [{"name": "first"}, {"name": "second"}]}}

part = part["PART"]
assert cfg.dic_get_group(part, "MODULE", "first") == {"name": "first"}
