import time

import gspyce.simulation
import gspyce.textures
from gspyce.graphics import *


class MissionGUI(gspyce.simulation.SimulationGUI):
    def __init__(self, *args, **kwargs):
        super(MissionGUI, self).__init__(*args, **kwargs)

        self.texture_rocket_on = gspyce.textures.load("rocket_on.png")
        self.texture_rocket_off = gspyce.textures.load("rocket_off.png")

        # texture transparency
        glAlphaFunc(GL_GREATER, 0.)
        glEnable(GL_ALPHA_TEST)

    def draw_rocket(self):
        """Draw the rocket"""

        self.add_pick_object(self.rocket)

        glPushMatrix()
        glTranslatef(*self.rocket._relative_position)
        glScalef(1e4, 1e4, 1e4)

        # follow rocket orientation
        (a, b, c), (d, e, f), (g, h, i) = self.rocket.orientation
        # glMultMatrixf() excepts a column-major matrix
        mat44 = [a, d, g, 0, b, e, h, 0, c, f, i, 0, 0, 0, 0, 1]
        glMultMatrixf(mat44)

        # pick correct texture
        if self.rocket.throttle == 0:
            gspyce.textures.bind(self.texture_rocket_off)
        else:
            gspyce.textures.bind(self.texture_rocket_on)

        # draw texture
        glDisable(GL_CULL_FACE)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0) or glVertex3f(-1, 0, -1)
        glTexCoord2f(0, 1) or glVertex3f(-1, 0, +1)
        glTexCoord2f(1, 1) or glVertex3f(+1, 0, +1)
        glTexCoord2f(1, 0) or glVertex3f(+1, 0, -1)
        glEnd()
        glEnable(GL_CULL_FACE)

        # all done
        gspyce.textures.unbind()
        glPopMatrix()

    def draw_body(self, body):
        """Draw a CelestialBody (or a Rocket)"""

        if body == self.rocket:
            return

        super(MissionGUI, self).draw_body(body)

    def draw(self):
        super(MissionGUI, self).draw()

        self.draw_rocket()

    def main(self):
        """Main loop"""
        last = time.time()
        accumulated_time = 0.
        while self.is_running:
            glutMainLoopEvent()

            # passage of time
            now = time.time()
            elapsed = now - last
            last = now
            accumulated_time += elapsed * self.timewarp

            dt = 2.**-5

            # avoid wasting cycles
            if accumulated_time < dt:
                pause = 1./60 - elapsed
                if pause > 0.:
                    time.sleep(pause)
                continue

            # physics simulation
            while accumulated_time > dt:
                if self.rocket.throttle:
                    # physical simulation (integration)
                    delta_t = dt
                else:
                    # logical simulation (just following Kepler orbits)
                    resume_delay = self.rocket.resume_time - self.time
                    next_activity = max(dt, resume_delay)
                    delta_t = (min(accumulated_time, next_activity) // dt) * dt
                accumulated_time -= delta_t
                self.rocket.simulate(self.time, delta_t)
                self.time += delta_t

            self.update()

        glutCloseFunc(None)


def main():
    import spyce.ksp_cfg
    import spyce.rocket

    sim = MissionGUI.from_cli_args()

    def launchpad_to_orbit(rocket):
        # vertical ascent with progressive gravity turn
        sim.log("Phase 1 (vertical take-off)")
        yield lambda: rocket.position[0] > 610e3
        sim.log("Phase 2 (start of gravity turn)")
        rocket.rotate_deg(-45, 1, 0, 0)
        yield lambda: rocket.orbit.apoapsis > 675e3
        sim.log("Phase 3 (end of gravity turn)")
        rocket.rotate_deg(-45, 1, 0, 0)
        yield lambda: rocket.orbit.apoapsis > 700e3
        sim.log("Phase 4 (coasting)")
        rocket.throttle = 0.

        # circularizing
        yield lambda: rocket.position.norm() > 699e3
        sim.log("Phase 5 (circularizing)")
        rocket.rotate_deg(-20, 1, 0, 0)
        rocket.throttle = 1.0
        yield lambda: rocket.orbit.periapsis > 695e3
        sim.log("In orbit")
        rocket.throttle = 0.0

    def program(rocket):
        for c in launchpad_to_orbit(rocket):
            yield c

        sim.log("Onto the Mun!")
        rocket.throttle = 1.0
        rocket.rotate_deg(58.0515, 1, 0, 0)

        yield lambda: rocket.propellant <= 0.
        sim.log("Out of propellant!")
        rocket.throttle = 0

    body = sim.focus
    rocket = spyce.rocket.Rocket(body, program)
    rocket |= spyce.ksp_cfg.PartSet().make(
        'Size3LargeTank', 'Size3LargeTank', 'Size3EngineCluster',
    )
    rocket.orbit.primary.satellites.append(rocket)

    sim.rocket = rocket
    sim.focus = rocket
    sim.main()


if __name__ == '__main__':
    main()