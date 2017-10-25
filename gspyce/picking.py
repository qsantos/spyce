from spyce.vector import Mat4
import gspyce.hud
from gspyce.graphics import *


class PickingGUI(gspyce.hud.HUD):
    """GUI with object picking using a fragment shader"""
    def __init__(self, title=b"Click to pick!"):
        super().__init__(title)
        self.picking_enabled = False
        self.picking_name = 0

    def set_picking_name(self, name):
        r = ((name >> 16) & 0xff) / 255.
        g = ((name >> +8) & 0xff) / 255.
        b = ((name >> +0) & 0xff) / 255.
        var = glGetUniformLocation(self.current_shader, b'picking_name')
        glUniform3f(var, r, g, b)

    def add_pick_object(self, thing, mode=None):
        """Register `thing` for picking

        Anything drawn afterwards is assumed to be part of `thing`.
        Can be used within a glBegin/glEnd scope, if `mode` is given"""
        self.pick_objects.append(thing)
        self.picking_name = len(self.pick_objects)

        if self.picking_enabled:
            if mode is None:
                self.set_picking_name(self.picking_name)
            else:
                # pause the current glBegin/glEnd group
                glEnd()
                self.set_picking_name(self.picking_name)
                glBegin(mode)

    def clear_pick_object(self):
        """Clear the current pickable object"""
        self.picking_name = 0
        if self.picking_enabled:
            self.set_picking_name(self.picking_name)

    def pick_reset(self):
        """Reset the list of pickable objects"""
        self.pick_objects = []

    def set_and_draw(self):
        """Setup the camera and draw"""
        self.pick_reset()
        super().set_and_draw()
        self.clear_pick_object()

    def shader_set(self, program=None):
        super().shader_set(program)

        # update uniforms
        if program is None:
            program = self.default_shader
        var = glGetUniformLocation(program, b'picking_enabled')
        glUniform1i(var, self.picking_enabled)
        self.set_picking_name(self.picking_name)

    def pick(self, x, y, default=None):
        """Find object around given screen coordinates

        If several objects match, return the one that was provided first."""

        # draw with color picking
        self.picking_enabled = True
        glDisable(GL_MULTISAMPLE)
        self.set_and_draw()
        glEnable(GL_MULTISAMPLE)
        self.picking_enabled = False

        # invert y axis
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

        transform = self.modelview_matrix

        transform @= Mat4.translate(-4, -4, 0)
        self.set_modelview_matrix(transform)
        glColor4f(1, 0, 0, 1)
        self.add_pick_object("the cube")
        glutSolidCube(2)

        transform @= Mat4.translate(0, 8, 0)
        self.set_modelview_matrix(transform)
        glColor4f(1, 1, 0, 1)
        self.add_pick_object("the torus")
        glutSolidTorus(1, 2, 16, 16)

        transform @= Mat4.translate(8, 0, 0)
        self.set_modelview_matrix(transform)
        glColor4f(0, 0, 1, 1)
        self.add_pick_object("the cone")
        glutSolidCone(1, 2, 16, 16)

        transform @= Mat4.translate(0, -8, 0) @ Mat4.scale(.5, .5, .5)
        self.set_modelview_matrix(transform)
        glColor4f(0, 1, 1, 1)
        self.add_pick_object("the dodecahedron")
        glutSolidDodecahedron()

    @glut_callback
    def mouseFunc(self, button, state, x, y):
        """Handle mouse clicks (GLUT callback)"""
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            print("You clicked on %s!" % self.pick(x, y, "nothing!"))
        else:
            super().mouseFunc(button, state, x, y)


def main():
    PickingGUI().main()


if __name__ == '__main__':
    main()
