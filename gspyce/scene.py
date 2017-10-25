import sys
from math import radians

from spyce.vector import Mat4
from gspyce.graphics import *
import gspyce.textures


class Scene:
    """A simple Scene handling zooming and camera orientation"""
    def __init__(self, title=b'Scene'):
        # default settings
        self.zoom = .25
        self.drag_active = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.theta = 0
        self.phi = -90
        self.is_running = True  # set to False for soft exit

        # GLUT init
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH |
                            GLUT_MULTISAMPLE)
        glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE,
                      GLUT_ACTION_GLUTMAINLOOP_RETURNS)
        glutInitWindowSize(1024, 768)
        glutCreateWindow(title)
        self.fullscreen = False

        # callbacks
        glutDisplayFunc(self.displayFunc)
        glutKeyboardFunc(self.keyboardFunc)
        glutSpecialFunc(self.specialFunc)
        glutReshapeFunc(self.reshapeFunc)
        glutMotionFunc(self.motionFunc)
        glutPassiveMotionFunc(self.passiveMotionFunc)
        glutMouseFunc(self.mouseFunc)
        glutCloseFunc(self.closeFunc)

        # OpenGL init
        glEnable(GL_CULL_FACE)  # one-way faces
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glEnable(GL_MULTISAMPLE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        self.modelview_matrix = Mat4()
        self.projection_matrix = Mat4()

        # initialize textures
        gspyce.textures.init()

        # shader management
        program = main_program()
        self.default_shader = program
        self.current_shader = program
        glUseProgram(program)

    def draw(self):
        """Draw the scene"""
        transform = self.modelview_matrix @ \
            Mat4.rotate(radians(90), 1, 0, 0)

        # fixed-pipeline transforms in glutWireTeapot() from freeglut_teapot.c
        transform @= Mat4.rotate(radians(270.0), 1, 0, 0)
        transform @= Mat4.scale(.5, .5, .5)
        transform @= Mat4.translate(0, 0, -1.5);

        self.set_modelview_matrix(transform)
        glutWireTeapot(1)

    def set_and_draw(self):
        """Setup the camera and draw"""

        # reset everything
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.shader_set()

        # set camera
        transform = \
            Mat4.translate(0, 0, -1/self.zoom) @ \
            Mat4.rotate(radians(self.phi),   1, 0, 0) @ \
            Mat4.rotate(radians(self.theta), 0, 0, 1)
        self.set_modelview_matrix(transform)

        # draw!
        self.draw()

    def shader_set(self, program=None):
        """Change the current shader

        If program is None, use the default shader."""
        if program is None:
            program = self.default_shader
        self.current_shader = program
        glUseProgram(self.current_shader)

    def toggle_fullscreen(self, enable=None):
        """Toggle fullscreen mode

        If argument is given, enable or disable fullscreen instead.
        """
        if enable is None:
            enable = not self.fullscreen
        if enable:
            self.window_width, self.window_height = self.width, self.height
            glutFullScreen()
            self.fullscreen = True
        else:
            glutReshapeWindow(self.window_width, self.window_height)
            self.fullscreen = False

    @glut_callback
    def displayFunc(self):
        """Draw the screen (GLUT callback)"""
        self.set_and_draw()
        glutSwapBuffers()

    @glut_callback
    def keyboardFunc(self, k, x, y):
        """Handle key presses (GLUT callback)"""
        if k == b'\x1b':  # escape
            self.quit()

    @glut_callback
    def specialFunc(self, k, x, y):
        """Handle special key presses (GLUT callback)"""
        if k == GLUT_KEY_F11:
            self.toggle_fullscreen()

    def set_shader_matrices(self):
        var = glGetUniformLocation(self.current_shader, b'model_view_matrix')
        glUniformMatrix4fv(var, 1, False, self.modelview_matrix.column_major())

        var = glGetUniformLocation(self.current_shader,
                                   b'model_view_projection_matrix')
        m = self.projection_matrix @ self.modelview_matrix
        glUniformMatrix4fv(var, 1, False, m.column_major())

    def set_modelview_matrix(self, m):
        self.modelview_matrix = m
        self.set_shader_matrices()

    def set_projection_matrix(self, m):
        self.projection_matrix = m
        self.set_shader_matrices()

    @glut_callback
    def reshapeFunc(self, width, height):
        """Handle window reshapings (GLUT callback)"""
        glViewport(0, 0, width, height)
        self.width = width
        self.height = height

        aspect = height / width
        near = .1
        # see https://stackoverflow.com/a/16459424/4457767
        self.set_projection_matrix(
            Mat4.frustrum(-near, near, -near*aspect, near*aspect, 2*near, 1e7)
        )

    @glut_callback
    def passiveMotionFunc(self, x, y):
        """Handle (passive) mouse motions (GLUT callback)"""
        # have to check which button is pressed anyway
        self.motionFunc(x, y)

    @glut_callback
    def motionFunc(self, x, y):
        """Handle (active) mouse motions (GLUT callback)"""
        if self.drag_active:
            # update orientation
            self.theta += (x - self.mouse_x) / 4
            self.phi += (y - self.mouse_y) / 4

            # clamp phi to [-180, 0]
            self.phi = max(-180, min(self.phi, 0))

            self.update()

        # save mouse coordinates
        self.mouse_x = x
        self.mouse_y = y

    @glut_callback
    def mouseFunc(self, button, state, x, y):
        """Handle mouse clicks (GLUT callback)"""
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

    @glut_callback
    def closeFunc(self):
        """Handle window closing (GLUT callback)"""
        self.is_running = False

    def quit(self):
        self.is_running = False
        glutLeaveMainLoop()

    def update(self):
        """Force an update of the screen"""
        glutPostRedisplay()

    def main(self):
        """Main loop"""
        glutMainLoop()


def main():
    Scene().main()


if __name__ == '__main__':
    main()
