import math

from spyce.vector import Vec3


class OrbitState:
    def __init__(self):
        raise NotImplementedError

    def distance_at_true_anomaly(self, true_anomaly):
        """Distance from focus (m) at a given true anomaly (rad)"""
        c = math.cos(true_anomaly)
        return self.semi_latus_rectum / (1 + self.eccentricity*c)

    def speed_at_distance(self, distance):
        """Orbital speed at a given distance from the focus

        This is an implementation of the vis-viva equation:
        speed**2 / (GM) = 2/distance - 1/semi_major_axis

        Arguments:
        distance: distance from the focus (m)
        """

        mu = self.primary.gravitational_parameter
        return math.sqrt(mu * (2/distance - 1/self.semi_major_axis))

    def speed_at_true_anomaly(self, true_anomaly):
        """Orbital speed (m/s) at a given true anomaly (rad)"""
        distance = self.distance_at_true_anomaly(true_anomaly)
        return self.speed_at_distance(distance)

    def position_at_true_anomaly(self, true_anomaly):
        """Position vector at a given true anomaly (rad)"""
        distance = self.distance_at_true_anomaly(true_anomaly)
        c = math.cos(true_anomaly)
        s = math.sin(true_anomaly)
        x = [distance*c, distance*s, 0.0]
        x = self.transform * x
        return x

    def velocity_at_true_anomaly(self, true_anomaly):
        """Velocity vector at a given true anomaly (rad)"""
        distance = self.distance_at_true_anomaly(true_anomaly)

        c = math.cos(true_anomaly)
        s = math.sin(true_anomaly)
        e = self.eccentricity

        x = self.semi_latus_rectum*e*s/(1+e*c)**2
        v = Vec3([-distance*s + x*c, distance*c + x*s, 0])

        norm_v = v.norm()
        speed = self.speed_at_true_anomaly(true_anomaly)
        v = [x/norm_v*speed for x in v]
        v = self.transform * v
        return v

    def position_at_time(self, time):
        """Position vector at a given time (s)"""
        return self.position_at_true_anomaly(self.true_anomaly_at_time(time))

    def velocity_at_time(self, time):
        """The velocity vector at a given time (s)"""
        return self.velocity_at_true_anomaly(self.true_anomaly_at_time(time))
