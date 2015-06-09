import time

from OpenGL.GL import *
from OpenGL.GLUT import *

import gui


class Simulation(gui.GUI):
    def __init__(self, rocket, *args, **kwargs):
        gui.GUI.__init__(self, *args, **kwargs)
        self.rocket = rocket
        self.path = [self.rocket.position]
        self.timewarp = 1.

    def draw(self):
        gui.GUI.draw(self)

        body = self.rocket.primary
        while body.orbit:
            glTranslate(*body.orbit.position_t(self.time))
            body = body.orbit.primary

        glColor4f(1, 0, 0, 1)
        glBegin(GL_LINE_STRIP)
        for position in self.path:
            glVertex3f(*position)
        glEnd()

    def draw_hud(self):
        gui.GUI.draw_hud(self)
        self.hud_print("Time x%g\n" % self.timewarp)
        self.hud_print(self.rocket.primary.time2str(self.time))

    def keyboardFunc(self, k, x, y):
        """Handle key presses (GLUT callback)"""
        gui.GUI.keyboardFunc(self, k, x, y)

        if k == b',':
            self.timewarp /= 10.
            print("Time x%g" % self.timewarp)
        elif k == b';':
            self.timewarp *= 10.
            print("Time x%g" % self.timewarp)

    def main(self, program):
        condition = next(program)

        last = time.time()
        while self.is_running:
            glutMainLoopEvent()

            # passage of time
            now = time.time()
            dt, last = (now - last) * self.timewarp, now

            # rocket simulation
            n = 256
            for _ in range(n):
                self.rocket.simulate(self.time, dt / n)
                if condition():
                    condition = next(program)
            self.path.append(self.rocket.position)  # save rocket path

            self.time += dt
            self.update()
        glutCloseFunc(None)


if __name__ == "__main__":
    import copy

    from load import kerbol
    import ksp_cfg
    import rocket

    def make_parts(*names):
        return {copy.copy(parts[name]) for name in names}

    parts = ksp_cfg.get_parts()
    body = kerbol['Kerbin']
    rocket = rocket.Rocket(body)
    rocket |= make_parts(
        'Size3LargeTank', 'Size3LargeTank', 'Size3EngineCluster',
    )

    def program():
        # vertical ascent with progressive gravity turn
        yield lambda: rocket.position[0] > 610e3
        rocket.rotate_deg(-45, 1, 0, 0)
        yield lambda: rocket.orbit.apoapsis > 675e3
        rocket.rotate_deg(-45, 1, 0, 0)
        yield lambda: rocket.orbit.apoapsis > 700e3
        rocket.throttle = 0.

        # circularizing
        yield lambda: rocket.position.norm() > 699e3
        rocket.rotate_deg(-20, 1, 0, 0)
        rocket.throttle = 1.0
        yield lambda: rocket.orbit.periapsis > 695e3
        rocket.throttle = 0.0
        yield lambda: False

    sim = Simulation(rocket, body, 'textures/kerbol')
    sim.main(program())
