def euler(f, t, y, h):
    """Euler method

    Run a numerical integration step `h` on `y` of derivative `f` along `t`"""
    # equivalent of
    # return y + f(t, y) * h
    return [x+dx*h for x, dx in zip(y, f(t, y))]


def rk4(f, t, y, h):
    """Runge-Kutta method

    Run a numerical integration step `h` on `y` of derivative `f` along `t`"""
    # notations from https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods
    # equivalent of
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


if __name__ == "__main__":
    import time

    def test(name, method, duration, dt):
        n_iterations = int(duration / dt)
        duration = n_iterations * dt

        # set problem (derivative and inital values)
        def f(t, y):
            _, _, _, vx, vy, vz = y
            return [vx, vy, vz, -9.81, 0, 0]
        y = [0]*6  # position, velocity

        # integrate and measure computation time
        last = time.time()
        for iteration in range(n_iterations):
            y = method(f, iteration*dt, y, dt)
        elapsed = time.time() - last

        # compute and print accuracy
        expect = - .5 * 9.81 * duration**2
        error = abs(y[0] - expect)
        print("%-6s time = %.2fs, error = %.1e" % (name+":", elapsed, error))

    test("Euler", euler, 1e4, .1)
    test("RK4",   rk4,   1e4, .1)
