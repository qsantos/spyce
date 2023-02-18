Spyce
=====

Spyce intends to be used as a Python library to help compute information about
space travel or plan trajectories in Kerbal Space Program.

This program is distributed under the [GPL licence](LICENCE.md). The credits
for the markdown formatting of the licence file go to
[IQAndreas](https://github.com/IQAndreas/markdown-licenses).



Usage
-----


### Installing Spyce


```bash
$ git clone "https://github.com/qsantos/spyce"
```

The only dependency is the Python interpreter itself (either Python 2 or 3),
unless you intend to use the [graphical interface](#graphical-interface) or [C
extensions](#c-extensions).


### Starting an interactive session

```bash
$ PYTHONPATH=. python3 spyce
```


### Comparing the Kerbol System to the Solar System

Bodies of the Kerbol system are smaller and closer than those of the Solar
System:

```python
>>> Kerbol.radius / Sun.radius
0.3758620689655172
>>> Kerbin.radius / Earth.radius
0.09417673834562863
>>> Mun.radius / Moon.radius
0.11510791366906475
>>> Kerbin.orbit.periapsis / Earth.orbit.periapsis
0.09245340411755291
>>> Mun.orbit.periapsis / Moon.orbit.periapsis
0.03304836098856901
```

However, their surface gravities are similar:

```python
>>> Kerbin.gravity() / Earth.gravity()
0.9989555850252271
>>> Mun.gravity() / Moon.gravity()
1.0027263771794397
```

This is because they are denser:

```python
>>> (Kerbin.mass/Kerbin.radius**3) / (Earth.mass/Earth.radius**3)
10.60724338699287
>>> (Mun.mass/Mun.radius**3) / (Moon.mass/Moon.radius**3)
8.711185401746382
```

Also, real gas giants have lots of moons:

```python
>>> len(Jool.satellites)
5
>>> len(Jupiter.satellites)
67
```


### Getting information about orbits

```python
>>> Orbit(Kerbin, Kerbin.radius+80e3).speed(0)
2278.931638238564
>>> o = Orbit.ask()
Primary [Kerbin]: Mun
== Orbit shape ==
   1 Periapsis and eccentricity
   2 Semi-major axis and eccentricity
   3 Periapsis and apoapsis
   4 Period and eccentricity
   5 Period and an apsis
   6 Position and velocity
Choose a method [1]: 1
Periapsis: Mun.radius + 20e3
Eccentricity [0]: 0
== Orbital plane ==
To use degrees, enter `radians(45)` for example
Inclination [0]: radians(90)
Longitude of ascending node [0]:
Argument of periapsis [0]:
== Position ==
Epoch [0]:
Mean anomaly [0]:
>>> o
Orbit(Mun, 220000, 0, 1.5708, 0, 0, 0, 0)
>>> o.speed(0)
544.1356679123854
```

### Computing surface and orbital velocities

```python
>>> Kerbin.surface_velocity
174.5336361449068
>>> Orbit(Kerbin, Kerbin.radius+80e3).speed(0)
2278.931638238564
>>> Mun.surface_velocity
9.041570660012562
>>> Orbit(Mun, Mun.radius+10e3).speed(0)
556.9406120378104
>>> Earth.surface_velocity
464.5806481876878
>>> Orbit(Earth, Earth.radius+120e3).speed(0)
7836.338986369195
```


### Notes

* works similarly with either Python 2 or Python 3
* auto-completion is enabled
* command history is preserved
* only imports Sun, planets, dwarf planets and moons from NASA (no asteroids)
* most of the API is documented and the code is commented; should you find
  missing information, feel free to get in contact or send a pull request


### Graphical interface (Work-In-Progress)

The graphical interface requires the python package `OpenGL` and uses `PIL` if
available (for textures). To install both on Debian (Ubuntu), run the relevant
command:

```bash
$ sudo apt-get install python-opengl python-pil
$ sudo apt-get install python3-opengl python3-pil
```

You can visualize the Kerbol or Solar system with:

```bash
$ cd spyce
$ python -m gui.system
$ python -m gui.system Earth
```

It also works for stars (Sun and Kerbol), the other planets and the moons.
Similarly, you can run `gui.simulation` to look at a rocket get into orbit.


### C extensions

To improve performance, a small (but heavily used) part of the Python code also
has a C implementation in [cext/](cext/). To enable this optimization, you will
need `gcc`, `make` and `libpython-dev` (or `libpython3-dev`); then, run `make`
in the `cext/` directory.



Data
----

### Time

Time is measured in seconds and dates are given in the J2000 date scale. This
corresponds to the number of seconds since 2000-01-01T12:00:00 TT (Terrestrial
Time), or 2000-01-01T11:59:27.816 TAI, or 2000-01-01T11:58:55.816 UTC.

Note that Unix Time is **not** the number of seconds since 1970-01-01T00:00:00
because it skips leap seconds.


### Solar System

Information on the Solar System is publicly made available at [Solar System
Dynamics](http://www.jpl.nasa.gov/) by the Jet Propulsion Laboratory (NASA):

* [Physical data for planets](http://ssd.jpl.nasa.gov/?planet_phys_par)
* [More physical data for planets (tilt)](http://nssdc.gsfc.nasa.gov/planetary/planetfact.html)
* [Physical data for moons](http://ssd.jpl.nasa.gov/?sat_phys_par)
* [Proper orbital elements for planets](http://ssd.jpl.nasa.gov/?planet_pos)
([from 1800 to 2050](http://ssd.jpl.nasa.gov/txt/p_elem_t1.txt))
* [Proper orbital elements for moons](http://ssd.jpl.nasa.gov/?sat_elem)
* [Dwarf planets (and small bodies)](http://ssd.jpl.nasa.gov/sbdb.cgi)
* [Gravitational parameter of the Sun](http://ssd.jpl.nasa.gov/?constants)

This information is included in Spyce in the file [solar.json](solar.json). For
osculating orbits, use the [HORIZONS
system](http://ssd.jpl.nasa.gov/?horizons).


### Kerbol System

Information on the Kerbol System can be accessed on [KSP official
wiki](http://wiki.kerbalspaceprogram.com/wiki/Kerbol_System) or from the game
by using a [plugin](modump/) to dump data. The information is included in Spyce
as [kerbol.json](kerbol.json).


### KSP parts

The rocket simulation script requires importing parts from KSP. Those are not
included in this repository and will be fetched in the installation folder of
KSP, which should be detected automatically.
