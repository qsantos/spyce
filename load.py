import os
import json

import body
import orbit


def load_body(bodies, data, name):
    """Load body `name` from `data` to `bodies` and return it

    `data` maps names to physical and orbital data
    `bodies` maps names to CelestialBody instances
    """
    if name in bodies:
        return bodies[name]

    b = data[name]

    # load orbit
    try:
        o = b["orbit"]
    except KeyError:
        b["orbit"] = None
    else:
        o["primary"] = load_body(bodies, data, o["primary"])
        b["orbit"] = orbit.Orbit(**o)

    b = bodies[name] = body.CelestialBody(name, **b)
    return b


def load_bodies(filename):
    """Load celestial body physical and orbital data from a JSON file"""

    with open(filename) as f:
        data = json.load(f)

    bodies = {}
    for name in data:
        load_body(bodies, data, name)
    return bodies

dir = os.path.dirname(__file__)
kerbol = load_bodies(os.path.join(dir, "kerbol.json"))
solar = load_bodies(os.path.join(dir, "solar.json"))
