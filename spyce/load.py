import os
import json

import body
import human
import orbit
import coordinates


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
        body_data["orbit"] = orbit.Orbit.from_semi_major_axis(**orbit_data)

    try:
        north_pole = body_data["north_pole"]
    except KeyError:
        pass
    else:
        coords = coordinates.CelestialCoordinates.from_equatorial(**north_pole)
        body_data["north_pole"] = coords

    bodies[name] = body.CelestialBody(name, **body_data)
    return bodies[name]


def load_bodies(filename):
    """Load celestial body physical and orbital data from a JSON file"""

    with open(filename) as f:
        data = json.load(f)

    bodies = {}
    for name in data:
        load_body(bodies, data, name)
    return bodies

relative_path = os.path.dirname(__file__)
kerbol = load_bodies(os.path.join(relative_path, "data", "kerbol.json"))
solar = load_bodies(os.path.join(relative_path, "data", "solar.json"))


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
kerbol['Kerbol'].format_date = human.to_kerbal_date
solar['Sun']._texture_directory = 'solar'
solar['Sun'].format_date = human.to_human_date
