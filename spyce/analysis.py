"""Numerical analysis methods"""


def newton_raphson(x_0, f, f_prime):
    """Newton-Raphson method

    Look around `x_0` for a root of `f`, of derivative `f_prime`
    """
    x = x_0
    previous_x = 0
    for _ in range(30):  # upper limit on iteration count
        previous_previous_x, previous_x = previous_x, x
        x -= f(x) / f_prime(x)
        if x in (previous_x, previous_previous_x):
            # best accuracy reached
            break
    return x


def euler(f, t, y, h):
    """Euler method

    Run a numerical integration step `h` on `y` of derivative `f` along `t`"""
    # list-equivalent of
    # return y + f(t, y) * h
    return [x+dx*h for x, dx in zip(y, f(t, y))]


def runge_kutta_4(f, t, y, h):
    """Runge-Kutta 4 method

    Run a numerical integration step `h` on `y` of derivative `f` along `t`"""
    # notations from https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods
    # list-equivalent of
    # k1 = f(t, y)
    # k2 = f(t + h*0.5, y + k1 * (h*0.5))
    # k3 = f(t + h*0.5, y + k2 * (h*0.5))
    # k4 = f(t + h*1.0, y + k3 * (h*1.0))
    # return y + (k1 + k2*2. + k3*2. + k4) * (h/6.)
    k1 = f(t, y)
    k2 = f(t + h/2., [a+b*h/2. for a, b in zip(y, k1)])
    k3 = f(t + h/2., [a+b*h/2. for a, b in zip(y, k2)])
    k4 = f(t + h,    [a+b*h for a, b in zip(y, k3)])
    return [x + (dx1+2.*(dx2+dx3)+dx4)*h/6.
            for x, dx1, dx2, dx3, dx4 in zip(y, k1, k2, k3, k4)]
