#!/usr/bin/env python
import sys
import math

import orbit
import load
import human
import analysis


if __name__ == '__main__':
    # parse orbited body
    if len(sys.argv) <= 1:
        sys.stderr.write('Usage: %s BODY\n' % sys.argv[0])
        sys.exit(1)
    primary = load.from_name(sys.argv[1])

    R = primary.radius
    mu = primary.gravitational_parameter

    def f(a):
        # note: a for semi-major axis
        return 2 * math.asin(R / a) * math.sqrt(a*a*a / mu)

    # f''(a) / f'(a)
    def ratio(a):
        r = R/a
        x = 1 - r*r
        s = math.asin(r)/r * math.sqrt(x)
        return a * (1.5*s - 1) / (.75*s - 2 + 1/x)

    # find a root of f'
    # i.e. a local extremum of f
    semi_major_axis = analysis.newton_raphson(primary.radius+1e-6, ratio=ratio)

    night_time = human.to_human_time(f(semi_major_axis))
    altitude = human.to_si_prefix(semi_major_axis - primary.radius, 'm')
    print('Consider a satellite in a circular orbit around %s' % primary)
    print('The time spent in the dark is at least %s' % night_time)
    print('This is achieved at altitude %s' % altitude)
    print('Note that this ignores possible eclipses from natural satellites')
