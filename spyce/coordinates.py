import math


class CelestialCoordinates(object):
    """Celestial coordinates of a point or a direction

    Celestial coordinates are spherical coordinates. The referential is thus
    given by an origin, a fundamental plane and a primary direction.

    * ecliptic coordinates: planet center, ecliptic, vernal equinox
    * equatorial coordinates: planet center, celestial equator, vernal equinox

    Note that the vernal equinox, the celestial equator and the ecliptic are
    respectively the northward equinox, the equatorial plane and the orbital
    plane *of the Earth*. It does mean that the direction of the north pole of
    Mars is given within a referential centered on Mars, oriented with Earth.
    """

    # the obliquity of the ecliptic is Earth's obliquity (tilt); that is, the
    # angle between the celestial equator (Earth's equatorial plane) and the
    # ecliptic (Earth's orbital plane)
    obliquity_of_the_ecliptic = 0.40910517666747087

    def __init__(self, right_ascension, declination, ecliptic_longitude,
                 ecliptic_latitude, distance):
        """Use from_equatorial() or from_ecliptic()"""
        self.right_ascension = right_ascension
        self.declination = declination
        self.ecliptic_longitude = ecliptic_longitude
        self.ecliptic_latitude = ecliptic_latitude
        self.distance = distance

    @classmethod
    def from_equatorial(cls, right_ascension, declination,
                        distance=float('inf')):
        """Locate an object from its equatorial coordinates (see class doc)

        If distance is omitted, it is assumed to be infinite; the coordinates
        then refer either to a point infinitely far away, or to a direction.
        """
        e = cls.obliquity_of_the_ecliptic
        ecliptic_longitude = math.atan(
            math.tan(right_ascension) * math.cos(e) +
            math.tan(declination) * math.sin(e) / math.cos(right_ascension)
        )
        ecliptic_latitude = math.asin(
            math.sin(declination) * math.cos(e) -
            math.cos(declination) * math.sin(e) * math.sin(right_ascension)
        )
        return cls(right_ascension, declination, ecliptic_longitude,
                   ecliptic_latitude, distance)

    @classmethod
    def from_ecliptic(cls, ecliptic_longitude, ecliptic_latitude,
                      distance=float('inf')):
        """Locate an object from its ecliptic coordinates (see class doc)

        If distance is omitted, it is assumed to be infinite; the coordinates
        then refer either to a point infinitely far away, or to a direction.
        """
        e = cls.obliquity_of_the_ecliptic
        right_ascension = math.atan(
            math.tan(ecliptic_longitude) * math.cos(e) -
            math.tan(ecliptic_latitude) * math.sin(e) /
            math.cos(ecliptic_longitude)
        )
        declination = math.asin(
            math.sin(ecliptic_latitude) * math.cos(e) +
            math.cos(ecliptic_latitude) * math.sin(e) *
            math.sin(ecliptic_longitude)
        )
        return cls(right_ascension, declination, ecliptic_longitude,
                   ecliptic_latitude, distance)
