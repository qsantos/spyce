import sys
import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import vector
import textures
import skybox


def make_shader(program, type_, filename):
        """Compile and attach a shader of given type"""
        if filename is None:
            return

        shader = glCreateShader(type_)
        glShaderSource(shader, open(filename).read())
        glCompileShader(shader)
        error = glGetShaderInfoLog(shader)
        if error:
            raise SyntaxError(error)
        glAttachShader(program, shader)


def make_program(vertex_file=None, fragment_file=None):
        """Make a program from shader files"""
        program = glCreateProgram()
        make_shader(program, GL_VERTEX_SHADER, vertex_file)
        make_shader(program, GL_FRAGMENT_SHADER, fragment_file)
        glLinkProgram(program)
        return program


class GUI:
    def __init__(self, focus, texture_directory=None):
        # set to False for soft exit
        self.is_running = True

        # default settings
        self.zoom = 1e-7
        self.drag_active = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.theta = 0
        self.phi = -90
        self.time = 0

        # detect current system from focus
        self.focus = focus
        self.system = self.focus
        while self.system.orbit is not None:
            self.system = self.system.orbit.primary

        # GLUT init
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
        glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE,
                      GLUT_ACTION_GLUTMAINLOOP_RETURNS)
        glutInitWindowSize(1024, 768)
        glutCreateWindow(b'Spaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaace')

        self.pick_shader = make_program(None, "shaders/pick.frag")
        self.pick_name = glGetUniformLocation(self.pick_shader, b"name")

        # OpenGL init
        glEnable(GL_POINT_SMOOTH)  # may make GL_POINTS round
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.0, 0.0, 0.0, 1.0)

        # generic sphere for drawing bodies
        sphere = gluNewQuadric()
        gluQuadricNormals(sphere, GLU_SMOOTH)
        gluQuadricTexture(sphere, GL_TRUE)
        # make it a call list for efficiency
        self.call_list_sphere = glGenLists(1)
        glNewList(self.call_list_sphere, GL_COMPILE)
        gluSphere(sphere, 1, 64, 64)
        glEndList()

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

        # callbacks
        glutCloseFunc(self.closeFunc)
        glutDisplayFunc(self.displayFunc)
        glutKeyboardFunc(self.keyboardFunc)
        glutReshapeFunc(self.reshapeFunc)
        glutMotionFunc(self.motionFunc)
        glutPassiveMotionFunc(self.passiveMotionFunc)
        glutMouseFunc(self.mouseFunc)

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

    def draw_satellites(self, body, skip=None):
        """Recursively draw the satellites of a body"""
        for satellite in body.satellites:
            if satellite != skip:
                self.add_pick_object(satellite)
                glPushMatrix()
                glColor4f(1.0, 1.0, 0.0, 1.0)
                glCallList(satellite.orbit.call_list)
                glTranslatef(*satellite.orbit.position_t(self.time))
                self.draw_body(satellite)
                self.draw_satellites(satellite, body)
                glPopMatrix()

    def draw_system(self, body, skip=None):
        """Draw the whole system a body belongs to"""
        self.draw_body(body)
        self.draw_satellites(body, skip)

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
        """Draw the screen"""

        # reset everything
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.pick_objects = []

        # move camera out of focus
        glTranslate(0, 0, -1)

        # orientation
        glRotate(self.phi,   1, 0, 0)
        glRotate(self.theta, 0, 0, 1)

        # skybox
        self.skybox.draw(1e6)

        # using glScalef() rather than glTranslate() avoid
        # abusing the depth buffer (see glFrustum())
        glScalef(self.zoom, self.zoom, self.zoom)

        # system
        self.draw_system(self.focus)

        # disable the color picking shader
        glProgramUniform1i(self.pick_shader, self.pick_name, 0)

    def hud_print(self, string):
        glutBitmapString(GLUT_BITMAP_HELVETICA_18, string.encode())

    def draw_hud(self):
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glRasterPos2i(10, 20)
        self.hud_print("Zoom x%g\n" % self.zoom)

    def displayFunc(self):
        """Draw the screen (GLUT callback)"""
        self.draw()

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0.0, self.width, self.height, 0.0, -1.0, 10.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_CULL_FACE)
        glClear(GL_DEPTH_BUFFER_BIT)

        self.draw_hud()

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glutSwapBuffers()

    def add_pick_object(self, thing):
        """Add thing to pick list and setup shader"""
        self.pick_objects.append(thing)
        name = len(self.pick_objects)
        glProgramUniform1i(self.pick_shader, self.pick_name, name)

    def pick(self, x, y):
        """Find object at given screen coordinates"""

        # draw with color picking
        glUseProgram(self.pick_shader)
        self.draw()
        glUseProgram(0)

        # inverse y axis
        viewport = glGetIntegerv(GL_VIEWPORT)
        y = viewport[3] - y

        # retrieve names
        search_radius = 10
        r = search_radius
        red = glReadPixels(x-r, y-r, 1+2*r, 1+2*r, GL_RED, GL_UNSIGNED_BYTE)

        # find best match
        best = float("inf")
        closest = 0
        for index, pixel in enumerate(red):
            # get integer value
            pixel = pixel[0]
            try:  # Python 2
                pixel = ord(pixel)
            except TypeError:  # Python 3
                pass

            # no match
            if pixel == 0:
                continue

            # compute distance to mouse pointer
            x, y = index // search_radius, index % search_radius,
            distance = math.hypot(x - search_radius, y - search_radius)
            if distance < best and distance <= search_radius:
                best = distance
                closest = pixel

        return closest

    def closeFunc(self):
        """Handle window closing (GLUT callback)"""
        self.is_running = False

    def keyboardFunc(self, k, x, y):
        """Handle key presses (GLUT callback)"""
        if k == b'\x1b':  # escape
            self.is_running = False

    def projection_matrix(self):
        """Make projection matrix"""
        x, y, width, height = glGetIntegerv(GL_VIEWPORT)
        aspect = float(height) / float(width)
        near = .1
        # see https://stackoverflow.com/a/16459424/4457767
        glFrustum(-near, near, -near*aspect, near*aspect, 2*near, 1e7)

    def reshapeFunc(self, width, height):
        """Handle window reshapings (GLUT callback)"""
        glViewport(0, 0, width, height)
        self.width = width
        self.height = height

        # reset projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.projection_matrix()
        glMatrixMode(GL_MODELVIEW)

    def passiveMotionFunc(self, x, y):
        """Handle (passive) mouse motions (GLUT callback)"""
        # have to check which button is pressed anyway
        self.motionFunc(x, y)

    def motionFunc(self, x, y):
        """Handle (active) mouse motions (GLUT callback)"""
        if self.drag_active:
            # update orientation
            self.theta += (x - self.mouse_x) / 4.
            self.phi += (y - self.mouse_y) / 4.

            # clamp phi to [-180, 0]
            self.phi = max(-180, min(self.phi, 0))

            self.update()

        # save mouse coordinates
        self.mouse_x = x
        self.mouse_y = y

    def mouseFunc(self, button, state, x, y):
        """Handle mouse clicks (GLUT callback)"""
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            # body selection
            name = self.pick(x, y)
            if name > 0:
                self.focus = self.pick_objects[name-1]
                self.update()
        if button == GLUT_RIGHT_BUTTON:
            # drag'n drop for camera orientation
            if state == GLUT_DOWN:
                self.drag_active = True
                self.mouse_x = x
                self.mouse_y = y
            else:
                self.drag_active = False
        if button == 3 and state == GLUT_DOWN:  # wheel up
            self.zoom *= 1.2
            self.update()
        if button == 4 and state == GLUT_DOWN:  # wheel down
            self.zoom /= 1.2
            self.update()

    def update(self):
        """Force an update of the screen"""
        glutPostRedisplay()

    def main(self):
        while self.is_running:
            glutMainLoopEvent()
        glutCloseFunc(None)

if __name__ == '__main__':
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

    GUI(body, texture_directory).main()
