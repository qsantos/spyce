"""Parsing utilities for Kerbal Space Program's configuration files"""

import re


def parse(f):
    """Main parsing function

    Parse a configuration file from a file handler and structure it
    as a Python object.
    """
    r = {}
    while True:
        line = f.readline()
        if not line:
            break
        s = re.split('(\w+|//|[{}=])', line.strip())

        if len(s) <= 1:
            continue

        key = s[1]
        if key == '' or key == '//':
            continue
        if key == '}':
            break

        if len(s) > 5 and s[3] == '=':
            val = ''.join(s[5:])
        elif (len(s) >= 4 and s[3] == '{') or f.readline().strip() == '{':
            val = parse(f)
        else:
            s = re.split('\W', line)
            for key in s:
                if key != '':
                    r[key] = True
            continue

        if key in r:
            p = r[key]
            if not isinstance(p, list):
                r[key] = [p]
            r[key].append(val)
        else:
            r[key] = val

    return r

def dic_get_float(dic, key):
    """Get float a a given key (default: 0.)"""
    if key in dic:
        return float(dic[key])
    else:
        return 0.

def dic_get_string(dic, key):
    """Get string at a given key (default: "")"""
    if key in dic:
        return dic[key]
    else:
        return ""

def dic_get_group(dic, group, name):
    """Get element of a given name in a given group.

    For example, find the MODULE named ModuleEngine in the
    dictionary. If none is found, None is returned.
    """
    if not group in dic:
        return None
    g = dic[group]
    if isinstance(g, list):
        for _,v in enumerate(g):
            if 'name' in v and v['name'] == name:
                return v
    elif 'name' in g and g['name'] == name:
        return g
    return None
