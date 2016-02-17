import math

import gui.hud
from gui.graphics import *


class PickingGUI(gui.hud.HUD):
    """GUI with object picking using a fragment shader"""
    def __init__(self, title=b"Click to pick!"):
        super(PickingGUI, self).__init__(title)
        self.pick_shader = main_program()
        self.pick_enabled = False
        self.pick_current_name = 0
        self.shader_reset()

    def set_pick_name(self, name):
        r = ((name >> 16) & 0xff) / 255.
        g = ((name >> +8) & 0xff) / 255.
        b = ((name >> +0) & 0xff) / 255.
        glUniform3f(self.pick_name, r, g, b)

    def add_pick_object(self, thing, mode=None):
        """Register `thing` for picking

        Anything drawn afterwards is assumed to be part of `thing`.
        Can be used within a glBegin/glEnd scope, if `mode` is given"""
        self.pick_objects.append(thing)
        name = len(self.pick_objects)
        self.pick_current_name = name

        if self.pick_enabled:
            if mode is None:
                self.set_pick_name(name)
            else:
                # pause the current glBegin/glEnd group
                glEnd()
                self.set_pick_name(name)
                glBegin(mode)

    def clear_pick_object(self):
        """Clear the current pickable object"""
        self.pick_current_name = 0
        if self.pick_enabled:
            self.set_pick_name(0)

    def pick_reset(self):
        """Reset the list of pickable objects"""
        self.pick_objects = []

    def set_and_draw(self):
        """Setup the camera and draw"""
        self.pick_reset()
        super(PickingGUI, self).set_and_draw()
        self.clear_pick_object()

    def shader_set(self, program):
        """Switch the current shader, set pick uniforms to correct values"""
        glUseProgram(program)
        var_flag = glGetUniformLocation(program, b"picking_enabled")
        glUniform1i(var_flag, int(self.pick_enabled))
        self.pick_name = glGetUniformLocation(program, b"picking_name")
        self.set_pick_name(self.pick_current_name)

    def shader_reset(self):
        """Restore the default shader"""
        self.shader_set(self.pick_shader)

    def pick(self, x, y, default=None):
        """Find object around given screen coordinates

        If several objects match, return the one that was provided first."""

        # draw with color picking
        self.pick_enabled = True
        self.shader_reset()
        glDisable(GL_MULTISAMPLE)
        self.set_and_draw()
        glEnable(GL_MULTISAMPLE)
        self.pick_enabled = False
        self.shader_reset()

        # inverse y axis
        viewport = glGetIntegerv(GL_VIEWPORT)
        y = viewport[3] - y

        # retrieve names
        search_radius = 30
        size = 2*search_radius + 1
        pixels = read_pixels(x-search_radius, y-search_radius, size, size)

        # interpret each pixel as a name
        names = ((r << 16) | (g << 8) | b for row in pixels for r, g, b in row)
        # find best match
        try:
            best_match = min(name for name in names if name)
        except ValueError:  # no match
            return default
        else:
            return self.pick_objects[best_match-1]

    # demo code

    def draw(self):
        """Draw the scene"""
        glColor4f(1, 1, 1, 1)
        self.add_pick_object("the sphere")
        glutSolidSphere(1, 16, 16)

        glColor4f(1, 0, 0, 1)
        glTranslatef(-4, -4, 0)
        self.add_pick_object("the cube")
        glutSolidCube(2)

        glColor4f(1, 1, 0, 1)
        glTranslatef(0, 8, 0)
        self.add_pick_object("the torus")
        glutSolidTorus(1, 2, 16, 16)

        glColor4f(0, 0, 1, 1)
        glTranslatef(8, 0, -1)
        self.add_pick_object("the cone")
        glutSolidCone(1, 2, 16, 16)

        glColor4f(0, 1, 1, 1)
        glTranslatef(0, -8, 1)
        glScalef(.5, .5, .5)
        self.add_pick_object("the dodecahedron")
        glutSolidDodecahedron()

    @glut_callback
    def mouseFunc(self, button, state, x, y):
        """Handle mouse clicks (GLUT callback)"""
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            print("You clicked on %s!" % self.pick(x, y, "nothing!"))
        else:
            super(PickingGUI, self).mouseFunc(button, state, x, y)

if __name__ == '__main__':
    PickingGUI().main()
