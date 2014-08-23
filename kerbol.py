import body
import orbit



""" Kerbol system

Definition of the major celestial bodies from Kerbal Space Program
"""

# data from http://wiki.kerbalspaceprogram.com/wiki/Kerbol_System and sublinks
# the information seems to be hard-coded in the game

# star
Kerbol = body.CelestialBody("Kerbol", 1.7565670e28,  261600e3,  432000)

# planets
Moho   = body.CelestialBody("Moho",   2.5263617e21,     250e3, 1210000,     orbit.Orbit.from_deg(Kerbol,  5263138304, 0.20, 180,  7.000,  70.0,  15))
Eve    = body.CelestialBody("Eve",    1.2244127e23,     700e3,   80500,     orbit.Orbit.from_deg(Kerbol,  9832684544, 0.01, 180,  2.100,  15.0,   0))
Kerbin = body.CelestialBody("Kerbin", 5.2915793e22,     600e3,   21600,     orbit.Orbit.from_deg(Kerbol, 13599840256, 0.00, 180,  0.000,   0.0,   0))
Duna   = body.CelestialBody("Duna",   4.5154812e21,     320e3,   65517.859, orbit.Orbit.from_deg(Kerbol, 20726155264, 0.05, 180,  0.060, 135.5,   0))
Dres   = body.CelestialBody("Dres",   3.2191322e20,     138e3,   34800,     orbit.Orbit.from_deg(Kerbol, 40839348203, 0.14, 180,  5.000, 280.0,  90))
Jool   = body.CelestialBody("Jool",   4.2332635e24,    6000e3,   36000,     orbit.Orbit.from_deg(Kerbol, 68773560320, 0.05,   6,  1.304,  52.0,   0))
Eeloo  = body.CelestialBody("Eeloo",  1.1149358e21,     210e3,   19460,     orbit.Orbit.from_deg(Kerbol, 90118820000, 0.26, 180,  6.150,  50.0, 260))

# moons
Gilly  = body.CelestialBody("Gilly",  1.2420512e17,      13e3,   28255,     orbit.Orbit.from_deg(Eve,       31500000, 0.55,  52, 12.000,  80.0,  10))
Mun    = body.CelestialBody("Mun",    9.7600236e20,     200e3,  138984.38,  orbit.Orbit.from_deg(Kerbin,    12000000, 0.00,  97,  0.000,   0.0,   0))
Minmus = body.CelestialBody("Minmus", 2.6457897e19,      60e3,   40400,     orbit.Orbit.from_deg(Kerbin,    47000000, 0.00,  52,  6.000,  78.0,  38))
Ike    = body.CelestialBody("Ike",    2.7821949e20,     130e3,   65517.862, orbit.Orbit.from_deg(Duna,       3200000, 0.03,  97,  0.200,   0.0,   0))
Laythe = body.CelestialBody("Laythe", 2.9397663e22,     500e3,   52980.879, orbit.Orbit.from_deg(Jool,      27184000, 0.00, 180,  0.000,   0.0,   0))
Vall   = body.CelestialBody("Vall",   3.1088028e21,     300e3,  105962.09,  orbit.Orbit.from_deg(Jool,      43152000, 0.00,  52,  0.000,   0.0,   0))
Tylo   = body.CelestialBody("Tylo",   4.2332635e22,     600e3,  211926.36,  orbit.Orbit.from_deg(Jool,      68500000, 0.00, 180,  0.025,   0.0,   0))
Bop    = body.CelestialBody("Bop",    3.7261536e19,      65e3,  544507.40,  orbit.Orbit.from_deg(Jool,     128500000, 0.24,  52, 15.000,  10.0,  25))
Pol    = body.CelestialBody("Pol",    1.0813636e19,      44e3,  901902.62,  orbit.Orbit.from_deg(Jool,     179890000, 0.17,  52,  4.250,   2.0,  15))
