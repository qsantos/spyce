import os
import json
import pkgutil

import spyce.body
import spyce.human
import spyce.orbit
import spyce.coordinates


def load_body(bodies, data, name):
    """Load body `name` from `data` to `bodies` and return it

    `data` maps names of celestial bodies to physical and orbital data
    `bodies` maps names to CelestialBody instances
    """
    if name in bodies:
        return bodies[name]

    body_data = data[name]

    # load orbit
    try:
        orbit_data = body_data["orbit"]
    except KeyError:
        pass
    else:
        orbit_data["primary"] = load_body(bodies, data, orbit_data["primary"])
        body_data["orbit"] = spyce.orbit.Orbit.from_semi_major_axis(**orbit_data)

    try:
        north_pole = body_data["north_pole"]
    except KeyError:
        pass
    else:
        coords = spyce.coordinates.CelestialCoordinates.from_equatorial(**north_pole)
        body_data["north_pole"] = coords

    bodies[name] = spyce.body.CelestialBody(name, **body_data)
    return bodies[name]


def load_bodies(filename):
    """Load celestial body physical and orbital data from a JSON file"""

    content = pkgutil.get_data("spyce", filename)
    data = json.loads(content.decode())

    bodies = {}
    for name in data:
        load_body(bodies, data, name)
    return bodies

kerbol = load_bodies("data/kerbol.json")
solar = load_bodies("data/solar.json")


def from_name(name):
    """Locate celestial body in any system by name"""
    for system in (kerbol, solar):
        try:
            return system[name]
        except KeyError:
            pass
    else:
        raise KeyError(name)


kerbol['Kerbol']._texture_directory = 'kerbol'
kerbol['Kerbol'].format_date = spyce.human.to_kerbal_date
solar['Sun']._texture_directory = 'solar'
solar['Sun'].format_date = spyce.human.to_human_date
