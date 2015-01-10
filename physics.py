"""Main physical constants

All values but Planck charge and values from the "miscellaneous" section
comes from CODATA 2010 by NIST [1]. Those, as well as formulaes are from
various pages of Wikipedia such as [2]. All values are in SI units.

The function _() allows to have the value from CODATA 2010 along with its
absolute uncertainty as well as an explicit expression from previously
defined constants. The current implementation prefers locally computed
values but checks them against the tabulated ones.

[1] http://physics.nist.gov/cuu/Constants/
[2] https://en.wikipedia.org/wiki/Plank_units
"""

import math


def _(tabulated, uncertainty=None, computed=None):
    if computed is None:
        return tabulated

    if uncertainty is None:
        error = abs(tabulated-computed)/tabulated
        assert error < 1e-10, "relative error (%g) too important" % error
    else:
        error = abs(tabulated-computed)
        assert error < uncertainty, \
            "absolute error (%g) above threshold (%g)" % (error, uncertainty)
    return computed


# universal constants
c = _(299792458)               # speed of ligth in vacuum (m/s)
G = _(6.67384e-11, 80e-16)     # gravitational constant (N.(m/kg)^2)
h = _(6.62606957e-34, 29e-42)  # Planck constant (J.s)

# nuclear constants
alph = _(7.2973525698e-3, 24e-13)                     # fine-structure constant
R_inf = _(10973731.568539, 55e-6)                     # Rydberg constant (1/m)
m_e = _(9.10938291e-31, 40e-39, 2*R_inf*h/c/alph**2)  # electron rest mass (kg)
m_p = _(1.672621777e-27, 74e-36)                      # proton mass (kg)

A_r_e = _(5.4857990914e-4, 14e-10)  # electron relative atomic mass

# electromagnetic constants
mu_0 = _(1.2566370614e-6, None, 4*math.pi/1e7)  # magnetic constant (N/A^2)
eps_0 = _(8.854187817e-12, None, 1/mu_0/c**2)   # electric constant (F/m)
k_e = _(8.9875517873681764e9, None, c**2/1e7)   # Coulomb constant (N.m^2/C^2)

# adopted value
M_u = _(1e-3)  # molar mass constant

# physico-chemical constants
N_A = _(6.02214129e23, 27e15, A_r_e*M_u/m_e)  # Avogadro constant (1/mol)
R = _(8.3144621, 75e-7)                       # molar gas constant (J/mol/K)
k_B = _(1.3806488e-23, 13e-30, R / N_A)       # Bolzmann constant (J/K)

# universal constants: Planck units
bh = _(1.054571726e-34, 47e-43, h/2/math.pi)         # reduced Planck constant
l_P = _(1.616199e-35, 97e-41, math.sqrt(bh*G/c**3))  # Planck length (m)
m_P = _(2.17651e-8, 13e-13, math.sqrt(bh * c / G))   # Planck mass (kg)
t_P = _(5.39106e-44, 32e-49, l_P / c)                # Planck time (s)
T_P = _(1.416833e32, 85e26, m_P * c**2 / k_B)        # Planck temperature (K)

# Planck unit not in CODATA
q_P = _(1.875545956e-18, 41e-29, math.sqrt(bh*1e7/c))  # Planck charge (C)

# electromagnetic constants
q = _(1.602176565e-19, 35e-28, math.sqrt(alph)*q_P)  # elementary charge (C)

# physico-chemical constants
m_u = _(1.660538921e-27, 73e-36, m_e / A_r_e)  # atomic mass constant (kg)

# adopted values
g0 = _(9.80665)  # standard gravity (m/s^2)
T0 = _(288.15)   # standard temperature (K)
p0 = _(101325)   # standard pressure (Pa)
atm = p0

# miscellaneous (not CODATA)
M_air = _(0.0289644, 50e-9)                          # air mass (kg/mol)
L = _(0.0064, 10e-5)                                 # lapse rate (K/m)
ly = _(9460730472580800, None, 365.25*86400*c)       # light year (m)
au = _(149597870700)                                 # astronomical unit (m)
parsec = _(3.0856775815e16, None, 648e3/math.pi*au)  # parsec (m)
