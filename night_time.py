#!/usr/bin/env python
import sys
import math

import spyce.orbit
import spyce.load
import spyce.human
import spyce.analysis


def main():
    # parse orbited body
    if len(sys.argv) <= 1:
        print(
            'Usage: %s BODY [ALTITUDE]\n'
            'Compute the time spent in the dark by a satellite\n'
            'If ALTITUDE is not given, the best one is computed\n'
            % sys.argv[0], file=sys.stderr)
        sys.exit(1)
    primary = spyce.load.from_name(sys.argv[1])

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

    if len(sys.argv) > 2:
        altitude = float(sys.argv[2])
        semi_major_axis = primary.radius + altitude
        altitude = spyce.human.to_si_prefix(altitude, 'm')
        night_time = spyce.human.to_human_time(f(semi_major_axis))
        print('Consider a satellite in a circular orbit around %s' % primary)
        print('Time in the dark at altitude %s: %s' % (altitude, night_time))
        print('This ignores possible eclipses from natural satellites')
        sys.exit(0)

    # find a root of f'
    # i.e. a local extremum of f
    semi_major_axis = spyce.analysis.newton_raphson(primary.radius+1e-6, ratio=ratio)

    night_time = spyce.human.to_human_time(f(semi_major_axis))
    altitude = spyce.human.to_si_prefix(semi_major_axis - primary.radius, 'm')
    print('Consider a satellite in a circular orbit around %s' % primary)
    print('The time spent in the dark is at least %s' % night_time)
    print('This is achieved at altitude %s' % altitude)
    print('Note that this ignores possible eclipses from natural satellites')


if __name__ == '__main__':
    main()
