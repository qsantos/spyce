import math

import gui
from graphics import *


class PickingGUI(gui.GUI):
    """GUI with object picking using a fragment shader"""
    def __init__(self, title=b"Click to pick!"):
        gui.GUI.__init__(self, title)
        self.pick_shader = make_program(None, "shaders/pick.frag")
        self.pick_enabled = False
        self.pick_current_name = 0

    def add_pick_object(self, thing):
        """Add thing to pick list and setup shader"""
        self.pick_objects.append(thing)
        name = len(self.pick_objects)
        self.pick_current_name = name
        if self.pick_enabled:
            glUniform1i(self.pick_name, name)

    def pick_clear(self):
        """Clear the current pickable object"""
        self.pick_current_name = 0
        if self.pick_enabled:
            glUniform1i(self.pick_name, 0)

    def pick_reset(self):
        """Reset the list of pickable objects"""
        self.pick_objects = []

    def set_and_draw(self):
        """Setup the camera and draw"""
        self.pick_reset()
        gui.GUI.set_and_draw(self)
        self.pick_clear()

    def shader_set(self, program):
        """Switch the current shader, set pick uniforms to correct values"""
        glUseProgram(program)
        var_flag = glGetUniformLocation(program, b"pick_enabled")
        glUniform1i(var_flag, int(self.pick_enabled))
        self.pick_name = glGetUniformLocation(program, b"pick_name")
        glUniform1i(self.pick_name, self.pick_current_name)

    def shader_reset(self):
        """Restore the default shader"""
        if self.pick_enabled:
            self.shader_set(self.pick_shader)
        else:
            glUseProgram(0)

    def pick(self, x, y, default=None):
        """Find object at given screen coordinates"""

        # draw with color picking
        self.pick_enabled = True
        self.shader_reset()
        self.set_and_draw()
        self.pick_enabled = False
        self.shader_reset()

        # inverse y axis
        viewport = glGetIntegerv(GL_VIEWPORT)
        y = viewport[3] - y

        # retrieve names
        search_radius = 10
        r = search_radius
        size = 2*r + 1
        red = glReadPixels(x-r, y-r, size, size, GL_RED, GL_UNSIGNED_BYTE)

        if len(red[0]) == 1:  # Python 2
            red = [ord(pixel) for pixel in red]
            red = [red[i:i+size] for i in range(0, len(red), size)]

        # find best match
        best = float("inf")
        closest = 0
        for i, row in enumerate(red):
            for j, pixel in enumerate(row):
                try:  # Python 2
                    pixel = ord(pixel)
                except TypeError:  # Python 3
                    pass

                # no match
                if pixel == 0:
                    continue

                # compute distance to mouse pointer
                distance = math.hypot(i - search_radius, j - search_radius)
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

    @glut_callback
    def mouseFunc(self, button, state, x, y):
        """Handle mouse clicks (GLUT callback)"""
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            print("You clicked on %s!" % self.pick(x, y, "nothing!"))
        else:
            gui.GUI.mouseFunc(self, button, state, x, y)

if __name__ == '__main__':
    PickingGUI().main()
