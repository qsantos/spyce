#!/usr/bin/env python
import sys

import orbit
import load
import human


if __name__ == '__main__':
    # parse orbited body
    if len(sys.argv) <= 1:
        sys.stderr.write('Usage: %s BODY\n' % sys.argv[0])
        sys.exit(1)
    primary = load.from_name(sys.argv[1])

    # antennas from RemoteTech
    antennas = [
        ('Reflectron DP-10', 0.5e6),
        ('Communotron 16', 2.5e6),
        ('CommTech EXP-VR-2T', 3e6),
        ('Communotron 32', 5e6),
        ('Comms DTS-M1', 50e6),
        ('Reflectron KR-7', 90e6),
        ('Communotron 88-88', 40e9),
        ('Reflectron KR-14', 60e9),
        ('CommTech 1', 350e9),
        ('Reflectron GX-120', 400e9),
    ]

    for antenna, communication_range in antennas:
        # get characteristics of constellation
        size = primary.constellation_minimum_size(communication_range)
        min_a, max_a = primary.constellation_radius(communication_range, size)

        # compute period and altitude ranges
        min_period = human.to_human_time(orbit.Orbit(primary, min_a).period)
        max_period = human.to_human_time(orbit.Orbit(primary, max_a).period)
        min_a = human.si_prefix(min_a - primary.radius, 'm')
        max_a = human.si_prefix(max_a - primary.radius, 'm')

        # print everthing
        print(u'%-20s %i× %s (%s) -- %s (%s)' %
              (antenna+':', size, min_a, min_period, max_a, max_period))
