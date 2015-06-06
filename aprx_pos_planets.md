---
title: "Keplerian Elements for Approximate Positions of the Major Planets"
date: 2014-12-30
---

**Note:** This document is a transcript of a section from the *Explanatory
Supplement to the Astronomical Almanac* (1992). This section was authored by
Erland Myles Standish, from the Solar System Dynamics Groups of the Jet
Propulsion lab at Caltech. The original document is available at
<http://ssd.jpl.nasa.gov/txt/aprx_pos_planets.pdf>.

Lower accuracy formulae for planetary positions have a number of important
applications when one doesn't need the full accuracy of an integrated
ephemeris. They are often used in observation scheduling, telescope pointing,
and prediction of certain phenomena as well as in the planning and design of
spacecraft missions.

Approximate positions of the nine major planets may be found by using
Keplerian formulae with their associated elements and rates. Such
elements are not intended to represent any sort of mean; they are simply
the result of being adjusted for a best fit. As such, it must be noted
that the elements are not valid outside the given time-interval over
which they fit.

The elements are given below in Table 1 or in Tables 2a and 2b, depending upon
the time-interval over which they are fit and within which they are to be used.

Formulae for using them are given here.

Formulae for using the Keplerian elements
-----------------------------------------

Keplerian elements given in the tables below are:

Symbols          Description                     Units
---------------- ------------------------------- ------------------------
$a_0$, $\dot a$  semi-major axis                 au, au/century
$e_0$, $\dot e$  eccentricity                    -, -/century
$I_0$, $\dot I$  inclination                     degrees, degrees/century
$L_0$, $\dot L$  mean longitude                  degrees, degrees/century
$ϖ_0$, $\dot ϖ$  longitude of perihelion¹        degrees, degrees/century
$Ω_0$, $\dot Ω$  longitude of the ascending node degrees, degrees/century

¹ $ϖ = ω + Ω$

In order to obtain the coordinates of one of the planets at a given Julian
Ephemeris Date, $T_{eph}$:

 1. Compute the value of each of that planet's six elements: $a = a_0 + \dot a
    T$, etc., where T, the number of centuries pas J2000.0, is $T =
    (T_{eph} - 2451545.0)/36525$.

 2. Compute the argument of perihelion, $ω$, and the mean anomaly, $M$:

    * $ω = ϖ - Ω$
    * $M = L - ϖ + b T^2 + c \cos(f T) + s \sin(f T)$

    where the last three terms must be added to $M$ for Jupiter through Pluto
    when using the formulae for 3000 BC to 3000 AD.

 3. Modulus the mean anomaly so that $-180° \leq M \leq +180°$. and then obtain
    the eccentric anomaly, $E$, from the solution of Kepler's equation (see
    below):

    $M = E - e^{\star} \sin E$,

    where $e^{\star} = 180/\pi ~ e = 57.29578 e$.

 4. Compute the planet's heliocentric coordinates in its orbital plane,
    $\mathbf{r'}$, with the x'-axis aligned from the focus to the perihelion:

    * $x' = a(\cos E - e)$
    * $y' = a \sqrt{1 - e^2} \sin E$
    * $z' = 0$

 5. Compute the coordinates, $\mathbf{r_{ecl}}$, in the J2000 ecliptic
    plane, with the x-axis aligned toward the equinox:

    $\mathbf{r_{ecl}} = \mathcal M \mathbf{r'} \equiv \mathcal R_z(-Ω)
    R_x(-I) R_z(-ω) \mathbf{r'}$

    so that

    $$
    \begin{alignat}{4} x_{ecl} &= (\cos ω \cos Ω - \sin ω \sin Ω \cos I)
    &x'&& + (-\sin ω \cos Ω - \cos ω \sin Ω \cos I) &y'
    \\
    y_{ecl} &= (\cos ω \cos Ω + \sin ω \sin Ω \cos I) &x'&& + (-\sin ω
    \sin Ω - \cos ω \cos Ω \cos I) &y'
    \\
    z_{ecl} &= (\sin ω \sin I)  &x'&& + (\cos ω \sin I) &y'
    \end{alignat}
    $$

 6. If desired, obtain the equatorial coordinates in the “ICRF” or “J2000
    frame”, $\mathbf{r_{eq}}$:

    $$\begin{alignat}{3}
    x_{eq} &= x_{ecl} &                                       \\
    y_{eq} &=         & + \cos ε ~ y_{ecl} - \sin ε ~ z_{ecl} \\
    z_{eq} &=         & + \sin ε ~ y_{ecl} + \cos ε ~ z_{ecl} \\
    \end{alignat}$$

    where the obliquity at J2000 is $ε = 23.43928°$.

Solution of Kepler's Equation, $M = E - e^{\star} \sin E$
---------------------------------------------------------

Given the mean anomaly, $M$, and the ecentriciy, $e^{\star}$, both in degrees,
start with

$E_0 = M + e^{\star} \sin M$

and iterate the following three equations, with n = 0, 1, 2, …, until $|\Delta
E| \leq tol$ (noting that $e^{star}$ is in degrees; $e$ is in radians):

* $\Delta M = M - (E_n - e^{\star} \sin E_n)$
* $\Delta E = \Delta M / (1 - e \cos E_n)$
* $E_{n+1} = E_n + \Delta E$

For the approximate formulae in this present context, $tol = 10^{-6}°$ is
sufficient.

Table 1
-------

              a (au)           e (-)           I (°)             L (°)           ϖ (°)           Ω (°)
-------- ----------- --------------- --------------- ----------------- --------------- ---------------
Mercury   0.38709927      0.20563593      7.00497902      252.25032350     77.45779628     48.33076593
          0.00000037      0.00001906     -0.00594749   149472.67411175      0.16047689     -0.12534081
Venus     0.72333566      0.00677672      3.39467605      181.97909950    131.60246718     76.67984255
          0.00000390     -0.00004107     -0.00078890    58517.81538729      0.00268329     -0.27769418
EM Bary   1.00000261      0.01671123     -0.00001531      100.46457166    102.93768193      0.0
          0.00000562     -0.00004392     -0.01294668    35999.37244981      0.32327364      0.0
Mars      1.52371034      0.09339410      1.84969142       -4.55343205    -23.94362959     49.55953891
          0.00001847      0.00007882     -0.00813131    19140.30268499      0.44441088     -0.29257343
Jupiter   5.20288700      0.04838624      1.30439695       34.39644051     14.72847983    100.47390909
         -0.00011607     -0.00013253     -0.00183714     3034.74612775      0.21252668      0.20469106
Saturn    9.53667594      0.05386179      2.48599187       49.95424423     92.59887831    113.66242448
         -0.00125060     -0.00050991      0.00193609     1222.49362201     -0.41897216     -0.28867794
Uranus   19.18916464      0.04725744      0.77263783      313.23810451    170.95427630     74.01692503
         -0.00196176     -0.00004397     -0.00242939      428.48202785      0.40805281      0.04240589
Neptune  30.06992276      0.00859048      1.77004347      -55.12002969     44.96476227    131.78422574
          0.00026291      0.00005105      0.00035372      218.45945325     -0.32241464     -0.00508664
Pluto    39.48211675      0.24882730     17.14001206      238.92903833    224.06891629    110.30393684
         -0.00031596      0.00005170      0.00004818      145.20780515     -0.04062942     -0.01183482

Table: Keplerian elements and their rates, with respect to the mean ecliptic
and equinox of J2000, valid for the time-interval 1800 AD — 2050 AD.


Table 2a
--------

              a (au)           e (-)           I (°)             L (°)           ϖ (°)           Ω (°)
-------- ----------- --------------- --------------- ----------------- --------------- ---------------
Mercury   0.38709843      0.20563661      7.00559432      252.25166724     77.45771895     48.33961819
          0.00000000      0.00002123     -0.00590158   149472.67486623      0.15940013     -0.12214182
Venus     0.72332102      0.00676399      3.39777545      181.97970850    131.76755713     76.67261496
         -0.00000026     -0.00005107      0.00043494    58517.81560260      0.05679648     -0.27274174
EM Bary   1.00000018      0.01673163     -0.00054346      100.46691572    102.93005885     -5.11260389
         -0.00000003     -0.00003661     -0.01337178    35999.37306329      0.31795260     -0.24123856
Mars      1.52371243      0.09336511      1.85181869       -4.56813164    -23.91744784     49.71320984
          0.00000097      0.00009149     -0.00724757    19140.29934243      0.45223625     -0.26852431
Jupiter   5.20248019      0.04853590      1.29861416       34.33479152     14.27495244    100.29282654
         -0.00002864      0.00018026     -0.00322699     3034.90371757      0.18199196      0.13024619
Saturn    9.54149883      0.05550825      2.49424102       50.07571329     92.86136063    113.63998702
         -0.00003065     -0.00032044      0.00451969     1222.11494724      0.54179478     -0.25015002
Uranus   19.18797948      0.04685740      0.77298127      314.20276625    172.43404441     73.96250215
         -0.00020455     -0.00001550     -0.00180155      428.49512595      0.09266985      0.05739699
Neptune  30.06952752      0.00895439      1.77005520      304.22289287     46.68158724    131.78635853
          0.00006447      0.00000818      0.00022400      218.46515314      0.01009938     -0.00606302
Pluto    39.48686035      0.24885238     17.14104260      238.96535011    224.09702598    110.30167986
          0.00449751      0.00006016      0.00000501      145.18042903     -0.00968827     -0.00809981

Table: Keplerian elements and their rates, with respect to the mean ecliptic
and equinox of J2000, valid for the time-interval 3000 BC -- 3000 AD.
**NOTE:** the computation of M for Jupiter through Pluto **must** be augmented
by the additional terms given in Table 2b (below).


Table 2b
--------

                    b             c             s             f
-------- ------------ ------------- ------------- -------------
Jupiter   -0.00012452    0.06064060   -0.35635438   38.35125000
Saturn     0.00025899   -0.13434469    0.87320147   38.35125000
Uranus     0.00058331   -0.97731848    0.17689245    7.67025000
Neptune   -0.00041348    0.68346318   -0.10162547    7.67025000
Pluto     -0.01262724

Table: Additional terms which must be added to the computation of M for Jupiter
through Pluto, 3000 BC to 3000 AD, as described in the related document.
