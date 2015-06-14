import time

import system
import textures
from graphics import *


class SimulationGUI(system.SystemGUI):
    def __init__(self, *args, **kwargs):
        system.SystemGUI.__init__(self, *args, **kwargs)

        self.path = []
        self.timewarp = 1.
        self.texture_rocket_on = textures.load("textures/rocket_on.png")
        self.texture_rocket_off = textures.load("textures/rocket_off.png")

        glAlphaFunc(GL_GREATER, 0.)
        glEnable(GL_ALPHA_TEST)

    def draw_body(self, body):
        if body == self.rocket:
            glPushMatrix()
            glScalef(1e4, 1e4, 1e4)
            (a, b, c), (d, e, f), (g, h, i) = body.orientation
            mat44 = [a, d, g, 0, b, e, h, 0, c, f, i, 0, 0, 0, 0, 1]
            glMultMatrixf(mat44)

            if self.rocket.throttle == 0:
                textures.bind(self.texture_rocket_off)
            else:
                textures.bind(self.texture_rocket_on)

            glBegin(GL_QUADS)
            glTexCoord2f(0, 0) or glVertex3f(-1, 0, -1)
            glTexCoord2f(0, 1) or glVertex3f(-1, 0, +1)
            glTexCoord2f(1, 1) or glVertex3f(+1, 0, +1)
            glTexCoord2f(1, 0) or glVertex3f(+1, 0, -1)
            glEnd()

            textures.unbind()
            glPopMatrix()
            return

        if body == self.rocket.primary:
            glColor4f(1, 0, 0, 1)
            glBegin(GL_LINE_STRIP)
            for position in self.path:
                glVertex3f(*position)
            glEnd()

        system.SystemGUI.draw_body(self, body)

    def draw_hud(self):
        system.SystemGUI.draw_hud(self)
        self.hud_print("Time x%g\n" % self.timewarp)
        self.hud_print("%s\n" % self.rocket.primary.time2str(self.time))

    def keyboardFunc(self, k, x, y):
        """Handle key presses (GLUT callback)"""
        if k == b'\x1b':  # escape
            self.is_running = False
        elif k == b',':
            self.timewarp /= 10.
        elif k == b';':
            self.timewarp *= 10.
        else:
            system.SystemGUI.keyboardFunc(self, k, x, y)

    def main(self):
        """Main loop"""
        last = time.time()
        while self.is_running:
            glutMainLoopEvent()

            # passage of time
            now = time.time()
            dt, last = (now - last) * self.timewarp, now

            # rocket simulation
            n = 32
            for _ in range(n):
                self.rocket.simulate(self.time, dt / n)
            self.path.append(self.rocket.position)  # save rocket path

            self.time += dt
            self.update()
        glutCloseFunc(None)

if __name__ == "__main__":
    from load import kerbol
    import ksp_cfg
    import rocket

    def program(rocket):
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

    body = kerbol['Kerbin']
    rocket = rocket.Rocket(body, program)
    rocket |= ksp_cfg.PartSet().make(
        'Size3LargeTank', 'Size3LargeTank', 'Size3EngineCluster',
    )
    rocket.orbit.primary.satellites.append(rocket)

    sim = SimulationGUI.from_cli_args()
    sim.rocket = rocket
    sim.focus = rocket
    sim.main()
