import os
import atexit
import readline
import rlcompleter
import code
import math

import load
import orbit
import physics

namespace = {
    "Orbit": orbit.Orbit,
    "math": math,
    "physics": physics,
    "kerbol": load.kerbol,
    "solar": load.solar,
}
namespace.update(math.__dict__)
namespace.update(physics.__dict__)
namespace.update(load.kerbol)
namespace.update(load.solar)

completer = rlcompleter.Completer(namespace)
readline.set_completer(completer.complete)
readline.parse_and_bind("tab: complete")

histfile = os.path.expanduser("~/.spyce_history")
try:
    readline.read_history_file(histfile)
except Exception:
    pass
atexit.register(readline.write_history_file, histfile)

banner = """===== Welcome to Spyce! =====
Session example:
    >>> help(math)
    >>> pi
    3.141592653589793
    >>> help(physics)
    >>> G
    6.67384e-11
    >>> kerbol
    >>> Kerbin.orbit.period
    9203544.617501413
    >>> solar
    >>> Sun.radius
    6960000000.0
    >>> help(Orbit)
"""
code.interact(banner=banner, local=namespace)
