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

# filter out symbols starting with "_"
for k in list(namespace):
    if k.startswith("_"):
        del namespace[k]

namespace["__name__"] = "spyce"


def ask(prompt, default=None):
    """Interactively ask for a value or evaluable expression"""
    try:  # Python 2
        line = raw_input(prompt)
    except NameError:  # Python 3
        line = input(prompt)
    return eval(line, namespace) if line else default


@classmethod
def ask_orbit(cls):
    """Interactively ask orbital elements"""
    args = {}
    args["primary"] = ask("Primary [Kerbin]: ", load.kerbol["Kerbin"])

    print("== Orbit shape ==")
    print("   1 Periapsis and eccentricity")
    print("   2 Semi-major axis and eccentricity")
    print("   3 Periapsis and apoapsis")
    print("   4 Period and eccentricity")
    print("   5 Period and an apsis")
    print("   6 Position and velocity")
    choice = ask("Choose a method [1]: ", 1)

    if choice == 1:
        constructor = cls
        args["periapsis"] = ask("Periapsis: ")
        args["eccentricity"] = ask("Eccentricity [0]: ", 0)
    if choice == 2:
        constructor = cls.from_semi_major_axis
        args["semi_major_axis"] = ask("Semi-major axis: ")
        args["eccentricity"] = ask("Eccentricity [0]: ", 0)
    elif choice == 3:
        constructor = cls.from_apses
        args["apsis1"] = ask("First apsis: ", 0)
        args["apsis2"] = ask("Second apsis: ", 0)
    elif choice == 4:
        constructor = cls.from_period
        args["period"] = ask("Period: ")
        args["eccentricity"] = ask("Eccentricity [0]: ", 0)
    elif choice == 5:
        constructor = cls.from_period
        args["period"] = ask("Period: ")
        args["apsis"] = ask("One apsis: ", 0)

    print("== Orbital plane ==")
    print("To use degrees, enter `radians(45)` for example")
    args["inclination"] = ask("Inclination [0]: ", 0)
    args["longitude_of_ascending_node"] = \
        ask("Longitude of ascending node [0]: ", 0)
    args["argument_of_periapsis"] = ask("Argument of periapsis [0]: ", 0)

    print("== Position ==")
    args["epoch"] = ask("Epoch [0]: ", 0)
    args["mean_anomaly_at_epoch"] = ask("Mean anomaly [0]: ", 0)

    return constructor(**args)

orbit.Orbit.ask = ask_orbit
