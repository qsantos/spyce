import os
import atexit
import readline
import rlcompleter
import code
import textwrap

import load
import orbit


def spyce_help(object=None):
    if object is not None:
        help(object)
        return

    print("The Sun, Kerbol and others bodies are available in global scope:")
    print("* `Sun.radius` shows the Sun's radius (in meters)")
    print("* `Kerbin.orbit.period` shows Kerbin's orbital period (in seconds)")
    print("")
    print("List of defined bodies from the Kerbol System:")
    print("\n".join(textwrap.wrap(", ".join(load.kerbol))))
    print("")
    print("List of defined bodies from the Solar System:")
    print("\n".join(textwrap.wrap(", ".join(load.solar))))

namespace = {"help2": spyce_help, "Orbit": orbit.Orbit}
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
This is a Python interpretter with autocompletion enabled
Run "help()" for help about Python, "help2()" for help about Spyce"""
code.interact(banner=banner, local=namespace)
