Spyce
=====

Spyce intends to be used as a Python library to help compute information
about space travel or plan trajectories in Kerbal Space Program.

Licence
-------

This program is distributed under the GPL licence (see [LICENCE.md](LICENCE.md)
file). The credits for markdown formatting go to
[IQAndreas](https://github.com/IQAndreas/markdown-licenses).

Time
====

Time is measured in seconds and dates are given in the J2000 date scale. This
corresponds to the number of seconds since 2000-01-01T12:00:00 TT (Terrestrial
Time), or 2000-01-01T11:59:27.816 TAI, or 2000-01-01T11:58:55.816 UTC.

Note that Unix Time is **not** the number of seconds since 1970-01-01T00:00:00
because it skips leap seconds.

Data
====

Solar System
------------

Information on the Solar System is publicly made available at [Solar System
Dynamics](http://www.jpl.nasa.gov/) by the Jet Propulsion Laboratory (NASA):

* [Physical data for planets](http://ssd.jpl.nasa.gov/?planet_phys_par)
* [Physical data for moons](http://ssd.jpl.nasa.gov/?sat_phys_par)
* [Proper orbital elements for planets](http://ssd.jpl.nasa.gov/?planet_pos)
  ([from 1800 to 2050](http://ssd.jpl.nasa.gov/txt/p_elem_t1.txt))
* [Proper orbital elements for moons](http://ssd.jpl.nasa.gov/?sat_elem)
* [Dwarf planets (and small bodies)](http://ssd.jpl.nasa.gov/sbdb.cgi)
* [Gravitational parameter of the Sun](http://ssd.jpl.nasa.gov/?constants)

For osculating orbits, use the [HORIZONS
system](http://ssd.jpl.nasa.gov/?horizons).

Kerbol System
-------------

Information on the Kerbol System can be accessed on [KSP official
wiki](http://wiki.kerbalspaceprogram.com/wiki/Kerbol_System) or from the game
by using a [plugin](modump/) to dump data.
