import sys
import math

import spyce.human
import gspyce.textures
import gspyce.skybox
import gspyce.picking
import gspyce.terminal
import gspyce.mesh
from gspyce.graphics import *


def ancestors_descendants(body, max_depth=1):
    """Return the ancestors of a body and their descendants

    Return two lists: ancestors and descendants.
    ancestors are `body` itself, its primary, its primary's primary and so on
    descendants are the children of each ancestors, their children and so on

    `max_depth` limits the level of recursion when search for descendants.

    With max_depth=-1, it will return all the bodies, except that the ancestors
    will be in a separate list.
    """
    ancestors = []
    descendants = []

    def down(body, skip, max_depth):
        """Explore down the tree and collect other nodes"""
        if not max_depth:
            return
        for satellite in body.satellites:
            if satellite is skip:
                continue
            descendants.append(satellite)
            down(satellite, skip, max_depth-1)

    def up(body, skip=None):
        """Climb up the tree and collect ancestors"""
        ancestors.append(body)
        down(body, skip, max_depth)
        if body.orbit is not None:
            up(body.orbit.primary, body)

    up(body)
    return ancestors, descendants


class SystemGUI(gspyce.picking.PickingGUI, gspyce.terminal.TerminalGUI):
    """GUI for showing a planetary system"""
    def __init__(self, focus):
        title = b'Sp' + b'a'*42 + b'ce'
        super().__init__(title)

        self.time = 0
        self.zoom = 1e-7

        # detect current system
        self.focus = focus
        self.system = self.focus
        while self.system.orbit is not None:
            self.system = self.system.orbit.primary

        if self.system.name == 'Sun':
            self.time = spyce.human.now()

        glEnable(GL_POINT_SPRITE)
        self.shader_position_marker = main_program("circle_point")

        # lighting shader
        self.shader_lighting = main_program("lighting")
        # set up light
        glLightfv(GL_LIGHT0, GL_AMBIENT,  [1, 1, 1, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  [3, 3, 3, 1])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])
        # set up material for planets
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.3, 0.3, 0.3, 1])
        glMateriali(GL_FRONT, GL_SHININESS, 16)

        # sphere VBO for drawing bodies
        self.sphere = gspyce.mesh.Sphere(1, 64, 64)

        # meshes for drawing orbits
        self.circle = gspyce.mesh.Circle(1, 512)
        self.circle_through_origin = gspyce.mesh.CircleThroughOrigin(1, 256)
        self.parabola = gspyce.mesh.Parabola(256)

        # make call lists for orbits
        def make_orbit_call_list(body):
            if body.orbit:
                body.orbit.call_list = glGenLists(1)
                glNewList(body.orbit.call_list, GL_COMPILE)
                self.draw_orbit(body.orbit, use_vbo=False)
                glEndList()
            for satellite in body.satellites:
                make_orbit_call_list(satellite)
        make_orbit_call_list(self.system)

        # textures
        gspyce.textures.init()
        texture_directory = self.system._texture_directory

        def load_body(body):
            """Recursively load textures for celestial bodies"""
            filename = "%s.jpg" % body.name
            body.texture = gspyce.textures.load(texture_directory, filename)
            for satellite in body.satellites:
                load_body(satellite)
        load_body(self.system)

        # skybox
        self.skybox = gspyce.skybox.Skybox("skybox", "GalaxyTex_%s.jpg")

    @classmethod
    def from_cli_args(cls):
        """Load the system given in command-line arguments"""
        import spyce.load

        try:
            name = sys.argv[1]
        except IndexError:
            name = 'Kerbin'

        try:
            body = spyce.load.from_name(name)
        except KeyError:
            print("Unknwon body '%s'" % name, file=sys.stderr)
            sys.exit(1)

        return cls(body)

    def draw_orbit(self, orbit, use_vbo=True):
        """Draw an orbit using focus as origin"""
        glPushMatrix()

        # make tilted ellipse from a circle or tilted hyperbola from a parabola
        glRotatef(math.degrees(orbit.longitude_of_ascending_node), 0, 0, 1)
        glRotatef(math.degrees(orbit.inclination),                 1, 0, 0)
        glRotatef(math.degrees(orbit.argument_of_periapsis),       0, 0, 1)
        glTranslatef(-orbit.focus, 0, 0)
        glScalef(orbit.semi_major_axis, orbit.semi_minor_axis, 1.0)

        # draw circle or parabola
        mesh = self.circle if orbit.eccentricity < 1. else self.parabola
        if use_vbo:
            mesh.draw()
        else:
            # quick fix to allow drawing in display lists
            # TODO: not use display lists
            glBegin(mesh.mode)
            for v in mesh.vertices():
                glVertex(*v)
            glEnd()

        # apses
        glPointSize(5)
        glBegin(GL_POINTS)
        # periapsis
        glVertex3f(+1, 0, 0)
        if orbit.eccentricity < 1.:  # circular and elliptic orbits
            # apoapsis
            glVertex3f(-1, 0, 0)
        glEnd()

        glPopMatrix()

    def draw_orbit_focused(self, body):
        """Draw on orbit using current position as origin"""

        # issues when drawing the orbit a focused body:
        # 1. moving to system center and back close to camera induces
        #    loss of significance and produces jitter
        # 2. drawing the orbit as segments may put the body visibly out
        #    of the line when zooming in
        # 3. line breaks may be visible close to the camera

        # now, we fix the three issues mentioned above
        # draw the orbit from the body rather than from the orbit focus (1.)

        def corrected_orbit_position_at_true_anomaly(theta):
            return body.orbit.position_at_true_anomaly(theta) - focus_offset
        focus_offset = body.orbit.position_at_time(self.time)

        orbit = body.orbit

        if orbit.eccentricity >= 1.:  # open orbits
            # choose interpolation points
            def _():
                true_anomaly = orbit.true_anomaly_at_time(self.time)
                # decide when to stop drawing
                max_true_anomaly = orbit.true_anomaly_at_escape()
                if max_true_anomaly is None:
                    max_true_anomaly = orbit.ejection_angle() - 1e-2
                # normal hyperbola
                n = 128
                for i in range(n+1):
                    t = 2.*i/n - 1
                    yield max_true_anomaly * t
                # ensure the body will be on the line (2.)
                # more points close to the camera (3.)
                n = 64
                for i in range(n+1):
                    t = 2.*i/n - 1
                    theta = true_anomaly + t * abs(t)
                    if abs(theta) < max_true_anomaly:
                        yield theta
            angles = sorted(_())

            # draw trajectory
            glPointSize(2)
            glBegin(GL_LINE_STRIP)
            for angle in angles:
                glVertex3f(*corrected_orbit_position_at_true_anomaly(angle))
            glEnd()

            # periapsis
            glPointSize(5)
            glBegin(GL_POINTS)
            glVertex3f(*corrected_orbit_position_at_true_anomaly(0))
            glEnd()
        else:  # closed orbits
            # nice hack with circle symetry to draw the orbit from the body
            # while still using VBOs
            # unsure it can be adapted for parabolic and hyperbolic orbits

            glPushMatrix()

            # make tilted ellipse from a circle
            glRotatef(math.degrees(orbit.longitude_of_ascending_node), 0, 0, 1)
            glRotatef(math.degrees(orbit.inclination),                 1, 0, 0)
            glRotatef(math.degrees(orbit.argument_of_periapsis),       0, 0, 1)
            glScalef(orbit.semi_major_axis, orbit.semi_minor_axis, 1.0)

            # account for current position of the body (use circle symmetry)
            anomaly = orbit.eccentric_anomaly_at_time(self.time)
            glRotatef(math.degrees(anomaly) - 180., 0, 0, 1)

            # the first point of circle_through_origin is (0,0) (2.)
            # more points are located near the origin (3.)
            self.circle_through_origin.draw()

            glPopMatrix()

            # apses
            glPointSize(5)
            glBegin(GL_POINTS)
            glVertex3f(*corrected_orbit_position_at_true_anomaly(0))
            glVertex3f(*corrected_orbit_position_at_true_anomaly(math.pi))
            glEnd()

    def draw_body(self, body):
        """Draw a CelestialBody"""

        glPushMatrix()

        glTranslatef(*body._relative_position)
        self.add_pick_object(body)

        # axial tilt
        if body.north_pole is not None:
            z_angle = body.north_pole.ecliptic_longitude - math.pi/2
            glRotatef(math.degrees(z_angle), 0, 0, 1)
            x_angle = body.north_pole.ecliptic_latitude - math.pi/2
            glRotatef(math.degrees(x_angle), 1, 0, 0)

        # OpenGL use single precision while Python has double precision
        # reducing modulo 2 PI in Python reduces loss of significance
        turn_fraction, _ = math.modf(self.time / body.rotational_period)
        glRotatef(360. * turn_fraction, 0, 0, 1)

        # textured quadric (representation from close by)
        # sphere with radius proportional to that of the body
        gspyce.textures.bind(body.texture, (0.5, 0.5, 1.0))
        glScalef(body.radius, body.radius, body.radius)
        self.sphere.draw()
        gspyce.textures.unbind()

        glPopMatrix()

        glDepthMask(True)

    def draw(self):
        """Draw the scene"""
        # ancestors_descendants() can just be assumed to return all celestial
        # bodies, except that ancestors are in a separate list
        ancestors, descendants = ancestors_descendants(self.focus)
        bodies = ancestors + descendants

        # cache position of celestial bodies relative to the scene origin
        scene_origin = self.focus.global_position_at_time(self.time)
        for body in bodies:
            body_position = body.global_position_at_time(self.time)
            body._relative_position = body_position - scene_origin

        # draw celestial bodies
        self.sphere.bind()
        # draw system star individually (without lighting)
        self.draw_body(self.system)
        # draw planets and moons (with lighting)
        glLightfv(GL_LIGHT0, GL_POSITION, self.system._relative_position)
        self.shader_set(self.shader_lighting)
        for body in bodies:
            if body is self.system:
                continue
            self.draw_body(body)
        self.shader_reset()
        self.sphere.unbind()

        # draw circles around celestial bodies when from far away
        glPointSize(20)
        glDepthMask(False)
        self.shader_set(self.shader_position_marker)
        glBegin(GL_POINTS)
        glColor4f(1, 0, 0, 0.5)
        for body in bodies:
            self.add_pick_object(body, GL_POINTS)
            glVertex3f(*body._relative_position)
        glEnd()
        self.shader_reset()
        glDepthMask(True)

        # draw orbits
        glColor4f(1.0, 1.0, 0.0, 0.2)
        for body in descendants:  # skip ancestors (see below)
            glPushMatrix()
            glTranslatef(*body.orbit.primary._relative_position)
            self.add_pick_object(body)
            if hasattr(body.orbit, "call_list"):
                glCallList(body.orbit.call_list)
            else:
                self.draw_orbit(body.orbit)
            glPopMatrix()

        # separately draw orbits of ancestors
        # since the focused celestial body  and its ancestors are relatively
        # close to the camera, it is best to draw them with the origin the
        # orbit, rather than at the primary
        glColor4f(1.0, 1.0, 0.0, 1.0)
        for body in ancestors:
            if body.orbit is None:
                continue
            glPushMatrix()
            glTranslatef(*body._relative_position)
            self.add_pick_object(body)
            self.draw_orbit_focused(body)
            glPopMatrix()

    def set_and_draw(self):
        """Setup the camera and draw"""

        # reset everything
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.pick_reset()

        # skybox
        glLoadIdentity()
        glRotatef(self.phi,   1, 0, 0)
        glRotatef(self.theta, 0, 0, 1)
        glDisable(GL_DEPTH_TEST)
        self.skybox.draw()
        glEnable(GL_DEPTH_TEST)

        # set up camera
        glLoadIdentity()
        glTranslatef(0, 0, -1/self.zoom)
        glRotatef(self.phi,   1, 0, 0)
        glRotatef(self.theta, 0, 0, 1)

        self.draw()
        self.clear_pick_object()

    def draw_hud(self):
        """Draw the HUD"""
        self.hud_print("Focus: %s\n" % self.focus)
        super().draw_hud()

    @glut_callback
    def mouseFunc(self, button, state, x, y):
        """Handle mouse clicks (GLUT callback)"""
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            # body selection
            self.focus = self.pick(x, y, self.focus)
            self.update()
        else:
            super().mouseFunc(button, state, x, y)


def main():
    SystemGUI.from_cli_args().main()


if __name__ == '__main__':
    main()
