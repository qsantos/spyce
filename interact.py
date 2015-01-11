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
