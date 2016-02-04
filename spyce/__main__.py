import code

import interact


try:
    import readline
except ImportError:  # Windows
    pass
else:
    import os
    import rlcompleter

    completer = rlcompleter.Completer(interact.namespace)
    readline.set_completer(completer.complete)
    readline.parse_and_bind("tab: complete")

    histfile = os.path.join(os.path.expanduser("~"), ".spyce_history")
    try:
        readline.read_history_file(histfile)
    except:  # FileNotFoundError in Python 3, IOError in Python 2
        pass


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

code.interact(banner=banner, local=interact.namespace)

try:
    readline.write_history_file(histfile)
except NameError:  # Windows
    pass
