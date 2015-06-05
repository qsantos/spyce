"""Parsing utilities for KSP"""

import os
import io

import rocket


def unpack(a, *b):
    """Short work-around for Python 2 lack of support of a, *b = ..."""
    return a, b


def locate(path="GameData"):
    """Locate path in KSP installation directory"""

    subpath = os.path.join("SteamApps", "common", "Kerbal Space Program", path)
    home = os.path.expanduser("~")
    candidates = (
        home + "/.steam/steam", home + "/.local/share/Steam",  # GNU/Linux
        "C:\Program Files\Steam", "C:\Program Files (x86)\Steam",  # Windows
        home + "/Library/Application Support/Steam",  # Mac
    )

    for directory in candidates:
        path = os.path.join(directory, subpath)
        if os.path.exists(path):
            return path
    else:
        raise IOError("cannot find KSP folder")


def files(directory="GameData", extension=".cfg"):
    """Iterate through KSP files"""

    directory = locate(directory)
    for root, dirs, files in os.walk(directory):
        for file_ in files:
            if not extension or file_.endswith(extension):
                yield os.path.join(root, file_)


def parse(f):
    """Parse a KSP .cfg file into Python dict"""

    cfg_dict = {}
    for line in f:
        line, _ = unpack(*line.split("//", 1))  # strip comments
        line = line.strip()

        if line == "}":  # end of block
            break

        if not line:
            continue

        if "=" in line:  # assignment
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
        else:  # start of block
            key, end = unpack(*line.split(None, 1))

            if end == ["{"] or next(f).strip() == "{":
                value = parse(f)  # parse recursively
            else:
                raise SyntaxError("Expected '{'")

        # save key/value
        if key in cfg_dict:
            p = cfg_dict[key]
            if not isinstance(p, list):
                cfg_dict[key] = [p]
            cfg_dict[key].append(value)
        else:
            cfg_dict[key] = value

    return cfg_dict


def dict_get_group(cfg_dict, group, name):
    """Get element of a given name in a given group

    For example, find the MODULE named ModuleEngine.
    """

    try:
        g = cfg_dict[group]
    except KeyError:
        return None

    if isinstance(g, list):
        for v in g:
            if v.get("name") == name:
                return v
    elif g.get("name") == name:
        return g
    return None


def part_from_cfg(cfg_dict):
    """Create a part out of a parsed .cfg file"""

    # general
    name = cfg_dict['name']
    title = cfg_dict.get('title', name)
    mass = float(cfg_dict.get('mass', 100.)) * 1e3  # given in tons
    drag = float(cfg_dict.get('maximum_drag', .2))
    part = rocket.RocketPart(name, title, mass, drag)

    # engine
    r = dict_get_group(cfg_dict, 'MODULE', 'ModuleEngines') or \
        dict_get_group(cfg_dict, 'MODULE', 'ModuleEnginesFX')
    if r is not None:
        thrust = float(r.get('maxThrust', 0.)) * 1e3  # given in kN
        a = r['atmosphereCurve']['key']
        a = a[1] if isinstance(a, list) else a
        isp = float(a.split(' ')[1])
        part.make_engine(thrust, isp)

    # tank
    r = dict_get_group(cfg_dict, 'RESOURCE', 'LiquidFuel')
    if r is not None:
        q_fuel = float(r.get('amount', 0.))
        q_prop = q_fuel / 0.9 * 2  # fuel + oxidizer (liters)
        m_prop = q_prop * 5  # (kg)
        part.make_tank(m_prop)

    return part


def get_parts():
    """Generate all rocket parts from a local KSP installation"""

    parts = {}
    for path in files(os.path.join("GameData", "Squad", "Parts")):
        # "utf-8-sig" gets rid of the Byte Order Mask
        # open() from Python 2 does not have an `encoding` parameter
        with io.open(path, encoding="utf-8-sig") as f:
            cfg_dict = parse(f)

        part = part_from_cfg(cfg_dict['PART'])
        parts[part.name] = part

    return parts


if __name__ == "__main__":
    parts = get_parts()
    print("%u parts loaded" % len(parts))
