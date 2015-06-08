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

    def keyboardFunc(self, k, x, y):
        """Handle key presses (GLUT callback)"""
        gui.GUI.keyboardFunc(self, k, x, y)

        if k == b',':
            self.timewarp /= 10.
            print("Time x%g" % self.timewarp)
        elif k == b';':
            self.timewarp *= 10.
            print("Time x%g" % self.timewarp)

    def main(self):
        last = time.time()
        while self.is_running:
            glutMainLoopEvent()
            now = time.time()
            dt, last = (now - last) * self.timewarp, now
            self.rocket.simulate(dt)
            self.time += dt
            self.path.append(self.rocket.position)
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
    rocket |= make_parts('Size3LargeTank', 'Size3EngineCluster')

    Simulation(rocket, body, 'textures/kerbol').main()
