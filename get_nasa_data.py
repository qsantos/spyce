#!/usr/bin/env python
import math
import re
import json
try:  # python 3
    from urllib.request import urlopen
except ImportError:  # python 2
    from urllib2 import urlopen

import spyce.physics
import spyce.coordinates


def tt_to_j2000(year, month=1, day=1, hour=0, minute=0, second=0):
    is_leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
    y = year - 2000
    leap_years = y // 4 - y // 100 + y // 400 + (0 if is_leap else 1)
    days = [31, 29 if is_leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    d = y*365 + leap_years + sum(days[:month-1]) + day-1
    return d * 86400 + (hour-12)*3600 + minute*60 + second


assert tt_to_j2000(2000,  1,  1, 12) == 0
assert tt_to_j2000(2000,  3,  3, 12) == 5356800
assert tt_to_j2000(2001,  3,  3, 12) == 36892800
assert tt_to_j2000(3919,  3,  3, 12) == 60563030400
assert tt_to_j2000(3920,  3,  3, 12) == 60594652800
assert tt_to_j2000(3925, 11, 14, 12) == 60774537600
assert tt_to_j2000(1961,  7, 14, 14, 30, 28.5) == -1213910971.5

assert tt_to_j2000(2010, 6, 2) == tt_to_j2000(2010, 1, 153)
assert tt_to_j2000(2004, 4, 4.25) == tt_to_j2000(2004, 4, 4, 6)


def get_sun_physics(bodies):
    """Get physical information of the Sun"""

    bodies["Sun"] = {
        "gravitational_parameter": 1.3271244018e20,
        "radius": 6.96e8,
        "rotational_period": 2192832.0
    }


def get_planets_physics(bodies):
    """Get physical information of planets of the Solar System"""

    # retrieve page for physical characteristics
    url_physics = "http://ssd.jpl.nasa.gov/?planet_phys_par"
    html = urlopen(url_physics).read().decode()

    # extract data from table
    pattern = '''
    <td align="left">(.*)<br>&nbsp;</td>
([\s\S]*?)
  </tr>
'''
    matches = re.findall(pattern, html)

    # this page use a value of 6.67428e-11 kg^-1 m^3 s^-2
    # from CODATA 2006 for the gravitational constant
    # to derive the mass from the gravitational parameter
    G = 6.67428e-11

    for name, data in matches:
        pattern = '<td align="right" nowrap>(.*)<br>'
        matches = re.findall(pattern, data)

        _, radius, mass, _, rotational_period, _, _, _, _, _ = matches
        bodies[name] = {
            "gravitational_parameter": G*float(mass)*1e24,
            "radius": float(radius)*1e3,
            "rotational_period": float(rotational_period)*86400,
        }


def get_more_physics(bodies, body):
    """Get more physical information on a body of the Solar System"""

    # retrieve page for physical characteristics
    url = "http://nssdc.gsfc.nasa.gov/planetary/factsheet/%sfact.html" \
        % body.lower()
    html = urlopen(url).read().decode()
    # in case it drives you crazy, uncomment this
    # html = html.replace('\r', '\r\n')

    # orientation of north pole (axial tilt)

    # extract right ascension
    matches = re.search(r'Right Ascension *: *([\-0-9\.]+)', html)
    right_ascension = math.radians(float(matches.group(1)))

    # extract declination
    matches = re.search(r'Declination *: *([\-0-9\.]+)', html)
    declination = math.radians(float(matches.group(1)))

    bodies[body]['north_pole'] = {
        'right_ascension': right_ascension,
        'declination': declination,
    }


def get_planets_orbits(bodies):
    """Get orbital information of planets of the Solar System"""

    # retrieve page for orbital elements
    url_orbits = "http://ssd.jpl.nasa.gov/txt/p_elem_t1.txt"
    html = urlopen(url_orbits).read().decode()

    # extract data from table
    lines = html.split("\n")
    lines = [re.split("\s{2,}", line) for line in lines[16:]]

    epoch = tt_to_j2000(2000, 1, 1, 12)

    for i in range(0, len(lines)-1, 2):
        name = lines[i][0]
        elements = lines[i][1:]
        changes = lines[i+1][1:]

        if name == "EM Bary":
            name = "Earth"

        # see aprx_pos_planets.md
        t = float(epoch) / 86400 / 36525
        elements = [float(x0) + float(dx)*t
                    for x0, dx in zip(elements, changes)]

        (semi_major_axis, eccentricity, inclination, mean_longitude,
            longitude_of_periapsis, longitude_of_ascending_node) = elements

        mean_anomaly = mean_longitude - longitude_of_periapsis
        argument_of_periapsis = \
            longitude_of_periapsis - longitude_of_ascending_node

        body = bodies.setdefault(name, {})
        body["orbit"] = {
            "primary": "Sun",
            "semi_major_axis": semi_major_axis * spyce.physics.au,
            "eccentricity": eccentricity,
            "inclination": math.radians(inclination % 360),
            "longitude_of_ascending_node":
                math.radians(longitude_of_ascending_node % 360),
            "argument_of_periapsis": math.radians(argument_of_periapsis % 360),
            "epoch": epoch,
            "mean_anomaly_at_epoch": math.radians(mean_anomaly % 360),
        }


def get_moons_physics(bodies):
    """Get physical information of moons of the Solar System"""

    # retrieve page for physical characteristics
    url_physics = "http://ssd.jpl.nasa.gov/?sat_phys_par"
    html = urlopen(url_physics).read().decode()

    # find moons
    pattern = '''<TR ALIGN=right><TD ALIGN=left>(.*?)\s*</TD>
<TD.*>(.*?)(&#177;.*)?</TD><TD>.*</TD>
<TD.*>(.*?)(&#177;.*)?</TD><TD>.*</TD>'''
    matches = re.findall(pattern, html)

    # save data
    for name, mu, _, radius, _ in matches:
        bodies[name] = {
            "gravitational_parameter": float(mu)*1e9,
            "radius": float(radius)*1e3,
        }


def get_moons_orbits(bodies):
    """Get orbital information of moons of the Solar System"""

    # retrieve page for orbital elements
    url_orbits = "http://ssd.jpl.nasa.gov/?sat_elem"
    html = urlopen(url_orbits).read().decode()

    # find planetary systems
    pattern = '''<table cellpadding="5" cellspacing="0" border="0" width="100%">
  <tr bgcolor="#CCCCCC">
    <td align="left" nowrap><b>Satellites of (.*)</b></td>
([\s\S]*?)
</table>'''
    matches = re.findall(pattern, html)

    for primary, data in matches:
        # find orbit sets
        pattern = '''(<td colspan="2">|<HR>)
<H3>([\s\S]*?)</H3>(
Epoch (.*) TD?T<BR>)?
([\s\S]*?)
</TABLE>'''
        matches = re.findall(pattern, data)

        for reference_plane, comment, _, epoch, data in matches:
            # missing epoch
            if not epoch and primary == "Pluto":
                epoch = "2013 Jan. 1.00"

            # convert epoch to J2000
            pattern = "^([0-9]{4})\s*([A-Z][a-z]{2})\.\s*([0-9]{1,2}\.[0-9]*)$"
            m = re.match(pattern, epoch)
            year, month, day = m.groups()
            month = 1 + "JanFebMarAprMayJunJulAugSepOctNovDec".find(month)//3
            epoch = tt_to_j2000(int(year), month, float(day))

            # find moons
            pattern = '''<TR ALIGN=right><TD ALIGN=left>(.*?)</TD>
?<TD>(.*?)</TD>
?<TD>(.*?)</TD>
?<TD>(.*?)</TD>
?<TD>(.*?)</TD>
?<TD>(.*?)</TD>
?<TD>(.*?)</TD>'''
            matches = re.findall(pattern, data)

            # save data
            for (name, semi_major_axis, eccentricity, argument_of_periapsis,
                 mean_anomaly_at_epoch, inclination,
                 longitude_of_ascending_node) in matches:

                # S/2003 J1 -> S/2003J1
                if re.match("^S/[0-9]{4} [A-Z] [0-9]*$", name):
                    name = "".join(name.rsplit(" ", 1))

                # convert to standard units
                semi_major_axis = float(semi_major_axis)*1e3
                eccentricity = float(eccentricity)
                inclination = math.radians(float(inclination))
                longitude_of_ascending_node = \
                    math.radians(float(longitude_of_ascending_node))
                argument_of_periapsis = \
                    math.radians(float(argument_of_periapsis))
                mean_anomaly_at_epoch = \
                    math.radians(float(mean_anomaly_at_epoch))

                # when given equatorial elements, convert to ecliptic elements
                # when given Laplacian elements, handle as equatorial elements
                if 'ecliptic' not in reference_plane.lower():
                    # inclination is given relative to the equatorial plane of
                    # the primary; longitude of the ascending node is given
                    # relative to the northward equinox

                    # recover ecliptic coordinates of the primary's north pole
                    north_pole = bodies[primary]['north_pole']
                    north_pole = spyce.coordinates.CelestialCoordinates. \
                        from_equatorial(north_pole['right_ascension'],
                                        north_pole['declination'])

                    # from http://www.krysstal.com/sphertrig.html
                    # the blue great circle is the ecliptic
                    # A is the normal of the ecliptic
                    # B is the primary's north pole
                    # C is the normal of the satellite's orbital plane
                    # a is the equatorial orbital inclination of the satellite
                    # b is the ecliptic orbital inclination of the satellite
                    # c is the orbital inclination of the primary
                    # B' is orthogonal to the line of nodes of the primary
                    # C' is orthogonal to the line of nodes of the satellite

                    # compute ecliptic inclination
                    a = inclination
                    c = math.pi/2 - north_pole.ecliptic_latitude
                    B = longitude_of_ascending_node + math.pi/2
                    cb = math.cos(a)*math.cos(c) + \
                        math.sin(a)*math.sin(c)*math.cos(B)
                    b = math.acos(cb)

                    # compute ecliptic longitude of the orbital normal
                    sA = math.sin(B) * math.sin(a) / math.sin(b)
                    A = math.asin(sA)
                    A += north_pole.ecliptic_longitude

                    # ecliptic elements
                    inclination = b  # relative to the ecliptic
                    longitude_of_ascending_node = A + math.pi/2

                # save orbit
                body = bodies.setdefault(name, {})
                body["orbit"] = {
                    "primary": primary,
                    "semi_major_axis": semi_major_axis,
                    "eccentricity": eccentricity,
                    "inclination": inclination,
                    "longitude_of_ascending_node": longitude_of_ascending_node,
                    "argument_of_periapsis": argument_of_periapsis,
                    "epoch": epoch,
                    "mean_anomaly_at_epoch": mean_anomaly_at_epoch,
                }


def get_dwarf_planet_data(bodies, name):
    """Get physical and orbital information of dwarf planets"""

    # retrieve relevant page
    url_search = "http://ssd.jpl.nasa.gov/sbdb.cgi?sstr=%s"
    html = urlopen(url_search % name).read().decode()

    body = bodies.setdefault(name, {})

    # extract physical information
    pattern = '''<tr>
  <td.*>(.*)</font></a></td>
.*
  <td.*>(.*)</font></td>'''
    matches = re.findall(pattern, html)

    for name, value in matches:
        if name == "diameter":
            body["radius"] = float(value)*500
        elif name == "GM":
            body["gravitational_parameter"] = float(value)*1e9
        elif name == "rotation period":
            body["rotational_period"] = float(value)*3600

    # extract epoch
    pattern = "<b>Orbital Elements at Epoch ([0-9]+(\.[0-9])?) "
    epoch = re.search(pattern, html).group(1)
    epoch = float(epoch) - 2451545.0  # shift from Julian Date to J2000
    epoch *= 86400  # convert from Julian days to seconds

    # extract orbital information
    pattern = "<tr.*>(.*)</a></font></td> <td.*?><font.*?>(.*?)</font></td>"
    matches = re.findall(pattern, html)
    elements = dict(matches)

    body["orbit"] = {
        "primary": "Sun",
        "semi_major_axis": float(elements["a"]) * spyce.physics.au,
        "eccentricity": float(elements["e"]),
        "inclination": math.radians(float(elements["i"])),
        "longitude_of_ascending_node": math.radians(float(elements["node"])),
        "argument_of_periapsis": math.radians(float(elements["peri"])),
        "epoch": epoch,
        "mean_anomaly_at_epoch": math.radians(float(elements["M"])),
    }


def main():
    bodies = {}

    get_sun_physics(bodies)
    get_planets_physics(bodies)
    for planet in [
        'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus',
        'Neptune', 'Pluto'
    ]:
        get_more_physics(bodies, planet)
    get_planets_orbits(bodies)
    get_moons_physics(bodies)
    get_more_physics(bodies, 'Moon')
    get_moons_orbits(bodies)

    dwarf_planets = ["Ceres", "Pluto", "Sedna", "Haumea", "Makemake", "Eris"]
    for dwarf_planet in dwarf_planets:
        get_dwarf_planet_data(bodies, dwarf_planet)

    with open("solar.json", "w") as f:
        json.dump(bodies, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.write('\n')


if __name__ == '__main__':
    main()
