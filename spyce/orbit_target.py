import math

from spyce.analysis import golden_section_search, bisection_method


class OrbitTarget:
    def __init__(self):
        raise NotImplementedError

    def position_to_target(self, target, time):
        return target.position_at_time(time) - self.position_at_time(time)

    def distance_to_target(self, target, time):
        return self.position_to_target(target, time).norm()

    def velocity_to_target(self, target, time):
        return target.velocity_at_time(time) - self.velocity_at_time(time)

    def speed_to_target(self, target, time):
        return self.velocity_to_target(target, time).norm()

    def time_at_next_approach(self, target, t, tolerance=0):
        """Search for a near approach for half a period"""
        if self.eccentricity >= 1:
            # open orbit, use target's orbit
            if target.eccentricity >= 1:
                raise NotImplementedError
            return target.time_at_next_approach(self, t, tolerance)

        # basic pruning
        if self.eccentricity < 1:  # True
            if target.periapsis - self.apoapsis > tolerance:
                return None
        if target.eccentricity < 1:
            if self.periapsis - target.apoapsis > tolerance:
                return None

        def f(t):
            """Distance between the two objects at given time"""
            return (target.position_at_time(t)-self.position_at_time(t)).norm()
        # Although the distance is not strictly unimodal on a half-period,
        # golden section search works because f has at most one real local
        # minimum on a half-period.
        time = golden_section_search(f, t, t+self.period/2, tolerance)
        if time is None or f(time) > tolerance:
            return None
        return time

    def time_at_next_encounter(self, target, t, encounter_radius):
        """Search for an encounter for half a period"""
        # first, find near approach with just enough precision
        next_approach = self.time_at_next_approach(target, t, encounter_radius)
        if next_approach is None:
            return math.inf

        # second, search for time of encounter
        def f(t):
            """Distance before encounter"""
            # distance between the two objects at given time
            d = (target.position_at_time(t)-self.position_at_time(t)).norm()
            # distance to encounter
            return d - encounter_radius
        return bisection_method(f, t, next_approach)
