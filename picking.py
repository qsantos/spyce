import math
from OpenGL.GL import *
from OpenGL.GLUT import *

import gui


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


class PickingGUI(gui.GUI):
    """GUI with object picking using a fragment shader"""
    def __init__(self, title=b"Click to pick!"):
        gui.GUI.__init__(self, title)
        self.pick_shader = make_program(None, "shaders/pick.frag")
        self.pick_name = glGetUniformLocation(self.pick_shader, b"name")

    def add_pick_object(self, thing):
        """Add thing to pick list and setup shader"""
        self.pick_objects.append(thing)
        name = len(self.pick_objects)
        glProgramUniform1i(self.pick_shader, self.pick_name, name)

    def pick_clear(self):
        """Clear the current pickable object"""
        glProgramUniform1i(self.pick_shader, self.pick_name, 0)

    def pick_reset(self):
        """Reset the list of pickable objects"""
        self.pick_objects = []

    def set_and_draw(self):
        """Setup the camera and draw"""
        self.pick_reset()
        gui.GUI.set_and_draw(self)
        self.pick_clear()

    def pick(self, x, y, default=None):
        """Find object at given screen coordinates"""

        # draw with color picking
        glUseProgram(self.pick_shader)
        self.set_and_draw()
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

        return self.pick_objects[closest-1] if closest > 0 else default

    # demo code

    def draw(self):
        """Draw the scene"""
        glColor4f(1, 1, 1, 1)
        self.add_pick_object("the sphere")
        glutSolidSphere(1, 16, 16)

        glColor4f(1, 0, 0, 1)
        glTranslate(-4, -4, 0)
        self.add_pick_object("the cube")
        glutSolidCube(2)

        glColor4f(1, 1, 0, 1)
        glTranslate(0, 8, 0)
        self.add_pick_object("the torus")
        glutSolidTorus(1, 2, 16, 16)

        glColor4f(0, 0, 1, 1)
        glTranslate(8, 0, -1)
        self.add_pick_object("the cone")
        glutSolidCone(1, 2, 16, 16)

        glColor4f(0, 1, 1, 1)
        glTranslate(0, -8, 1)
        glScale(.5, .5, .5)
        self.add_pick_object("the dodecahedron")
        glutSolidDodecahedron(1, 2, 16, 16)

    def mouseFunc(self, button, state, x, y):
        """Handle mouse clicks (GLUT callback)"""
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            print("You clicked on %s!" % self.pick(x, y, "nothing!"))
        else:
            gui.GUI.mouseFunc(self, button, state, x, y)

if __name__ == '__main__':
    PickingGUI().main()
