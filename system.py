import sys
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import vector
import textures
import skybox
import picking


class SystemGUI(picking.PickingGUI):
    """GUI for showing planetary system"""
    def __init__(self, focus, texture_directory=None):
        title = b'Spaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaace'
        title = b'Sp' + b'a'*42 + b'ce'
        picking.PickingGUI.__init__(self, title)

        self.zoom = 1e-7

        # generic sphere for drawing bodies
        sphere = gluNewQuadric()
        gluQuadricNormals(sphere, GLU_SMOOTH)
        gluQuadricTexture(sphere, GL_TRUE)
        # make it a call list for efficiency
        self.call_list_sphere = glGenLists(1)
        glNewList(self.call_list_sphere, GL_COMPILE)
        gluSphere(sphere, 1, 64, 64)
        glEndList()

        # detect current system
        self.focus = focus
        self.system = self.focus
        while self.system.orbit is not None:
            self.system = self.system.orbit.primary

        # make call lists for orbits
        def make_orbit_call_list(body):
            if body.orbit:
                body.orbit.call_list = glGenLists(1)
                glNewList(body.orbit.call_list, GL_COMPILE)
                self.draw_orbit(body.orbit)
                glEndList()
            for satellite in body.satellites:
                make_orbit_call_list(satellite)
        make_orbit_call_list(self.system)

        # textures
        def load_body(body):
            if texture_directory is not None:
                texture_file = "%s/%s.jpg" % (texture_directory, body.name)
                body.texture = textures.load(texture_file)
            else:
                body.texture = 0
            for satellite in body.satellites:
                load_body(satellite)
        glEnable(GL_TEXTURE_2D)
        load_body(self.system)

        # skybox
        self.skybox = skybox.Skybox("textures/skybox/GalaxyTex_%s.jpg")

    @classmethod
    def from_cli_args(cls):
        from load import kerbol, solar

        try:
            name = sys.argv[1]
        except IndexError:
            name = 'Kerbin'

        try:
            body = kerbol[name]
            texture_directory = 'textures/kerbol'
        except KeyError:
            try:
                body = solar[name]
                texture_directory = 'textures/solar'
            except KeyError:
                sys.stderr.write("Unknwon body '%s'\n" % name)
                sys.exit(1)

        return cls(body, texture_directory)

    def draw_orbit(self, orbit):
        # path
        glBegin(GL_LINE_STRIP)  # GL_LINE_LOOP glitches when n_points >= 139
        n_points = 512
        for i in range(n_points):
            glVertex3f(*orbit.position(2*math.pi/n_points * i))
        glVertex3f(*orbit.position(0))  # manually close the loop
        glEnd()

        # apses
        glPointSize(5)
        glBegin(GL_POINTS)
        glVertex3f(*orbit.position(0))
        glVertex3f(*orbit.position(math.pi))
        glEnd()

    def draw_orbit_focused(self, body):
        # issues when drawing the orbit a focused body:
        # 1. moving to system center and back close to camera induces
        #    loss of significance and produces jitter
        # 2. drawing the orbit as segments may put the body visibly out
        #    of the line when zooming in
        # 3. line breaks may be visible close to the camera

        # now, we fix the three issues mentioned above
        # draw the orbit from the body rather than from the orbit focus (1.)

        def corrected_orbit_position(theta):
            return body.orbit.position(theta) - focus_offset
        focus_offset = body.orbit.position_t(self.time)

        # path
        glBegin(GL_LINE_STRIP)  # GL_LINE_LOOP glitches when n_points >= 139
        n = 128
        # ensure the body will be on the line (2.)
        x = body.orbit.true_anomaly(self.time)
        for i in range(n):
            # we need more points close to the camera (3.)
            # the function i -> 2.*i/n - 1
            # has values in [-1, 1] and a lower slope around 0
            theta = x + math.pi * (2.*i/n - 1)**3
            relative_p = corrected_orbit_position(theta)
            glVertex3f(*relative_p)
        # manually close the loop
        glVertex3f(*corrected_orbit_position(x - math.pi))
        glEnd()

        # apses
        glPointSize(5)
        glBegin(GL_POINTS)
        glVertex3f(*corrected_orbit_position(0))
        glVertex3f(*corrected_orbit_position(math.pi))
        glEnd()

    def draw_sphere(self, radius):
        """Draw a sphere of given radius"""
        glPushMatrix()
        glScalef(radius, radius, radius)
        glCallList(self.call_list_sphere)
        glPopMatrix()

    def draw_body(self, body):
        """Draw a CelestialBody"""

        glPushMatrix()
        # OpenGL use single precision while Python has double precision
        # reducing modulo 2 PI in Python reduces loss of significance
        turn_fraction, _ = math.modf(self.time / body.rotational_period)
        glRotatef(360. * turn_fraction, 0, 0, 1)

        # textured quadric (representation from close by)
        # sphere with radius proportional to that of the body
        textures.bind(body.texture, (0.5, 0.5, 1.0))
        self.draw_sphere(body.radius)
        textures.unbind()

        glPopMatrix()

        # point (representation from far away)
        # draw sphere of constant visible radius at body position
        # see http://www.songho.ca/opengl/gl_transform.html
        modelview_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        distance_to_camera = vector.norm(modelview_matrix[3][:3]) / self.zoom
        glColor4f(0.5, 0.5, 1.0, 0.5)
        point_radius = distance_to_camera * .01
        self.draw_sphere(point_radius)

    def draw_satellites(self, body, skip=None, maxDepth=None):
        """Recursively draw the satellites of a body"""
        if maxDepth is not None:
            if maxDepth == 0:
                return
            maxDepth -= 1

        for satellite in body.satellites:
            if satellite != skip:
                self.add_pick_object(satellite)
                glPushMatrix()
                glColor4f(1.0, 1.0, 0.0, 1.0)
                glCallList(satellite.orbit.call_list)
                glTranslatef(*satellite.orbit.position_t(self.time))
                self.draw_body(satellite)
                self.draw_satellites(satellite, body, maxDepth)
                glPopMatrix()

    def draw_system(self, body, skip=None):
        """Draw the whole system a body belongs to"""
        self.draw_body(body)
        self.draw_satellites(body, skip, 1)

        # recursively draw primary
        if body.orbit is not None:
            self.add_pick_object(body.orbit.primary)
            glPushMatrix()
            glColor4f(1.0, 1.0, 0.0, 1.0)
            self.draw_orbit_focused(body)
            glTranslatef(*-body.orbit.position_t(self.time))
            self.draw_system(body.orbit.primary, body)
            glPopMatrix()

    def draw(self):
        """Draw the scene"""
        self.draw_system(self.focus)

    def set_and_draw(self):
        """Setup the camera and draw"""

        # reset everything
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # set up camera
        glTranslate(0, 0, -1)
        glRotate(self.phi,   1, 0, 0)
        glRotate(self.theta, 0, 0, 1)
        self.skybox.draw(1e6)  # skybox
        glScalef(self.zoom, self.zoom, self.zoom)

        self.pick_reset()
        self.draw()
        self.pick_clear()

    def mouseFunc(self, button, state, x, y):
        """Handle mouse clicks (GLUT callback)"""
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            # body selection
            self.focus = self.pick(x, y, self.focus)
            self.update()
        else:
            picking.PickingGUI.mouseFunc(self, button, state, x, y)

if __name__ == '__main__':
    SystemGUI.from_cli_args().main()
