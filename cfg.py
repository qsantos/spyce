"""Parsing utilities for Kerbal Space Program's configuration files"""


def unpack(a, *b):
    """Short work-around for Python 2 lack of support of a, *b = ..."""
    return a, b


def parse(f):
    """Main parsing function

    Parse a configuration file from a file handler and structure it
    as a Python object.
    """
    r = {}
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
        if key in r:
            p = r[key]
            if not isinstance(p, list):
                r[key] = [p]
            r[key].append(value)
        else:
            r[key] = value

    return r


def dic_get_group(dic, group, name):
    """Get element of a given name in a given group

    For example, find the MODULE named ModuleEngine.
    """

    try:
        g = dic[group]
    except KeyError:
        return None

    if isinstance(g, list):
        for v in g:
            if v.get("name") == name:
                return v
    elif g.get("name") == name:
        return g
    return None
