import sys
import time

from graphics import *


class Scene(object):
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
        glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
        glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE,
                      GLUT_ACTION_GLUTMAINLOOP_RETURNS)
        glutInitWindowSize(1024, 768)
        glutCreateWindow(title)

        # callbacks
        glutDisplayFunc(self.displayFunc)
        glutKeyboardFunc(self.keyboardFunc)
        glutReshapeFunc(self.reshapeFunc)
        glutMotionFunc(self.motionFunc)
        glutPassiveMotionFunc(self.passiveMotionFunc)
        glutMouseFunc(self.mouseFunc)
        glutCloseFunc(self.closeFunc)

        # OpenGL init
        glEnable(GL_CULL_FACE)  # one-way faces
        glEnable(GL_POINT_SMOOTH)  # may make GL_POINTS round
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.0, 0.0, 0.0, 1.0)

    def draw(self):
        """Draw the scene"""
        glRotate(90, 1, 0, 0)
        glutWireTeapot(1)

    def set_and_draw(self):
        """Setup the camera and draw"""

        # reset everything
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # set camera
        glTranslate(0, 0, -1/self.zoom)
        glRotate(self.phi,   1, 0, 0)
        glRotate(self.theta, 0, 0, 1)

        # draw!
        self.draw()

    @glut_callback
    def displayFunc(self):
        """Draw the screen (GLUT callback)"""
        self.set_and_draw()
        glutSwapBuffers()

    @glut_callback
    def keyboardFunc(self, k, x, y):
        """Handle key presses (GLUT callback)"""
        if k == b'\x1b':  # escape
            self.is_running = False
            glutLeaveMainLoop()

    def projection_matrix(self):
        """Make projection matrix"""
        x, y, width, height = glGetIntegerv(GL_VIEWPORT)
        aspect = float(height) / float(width)
        near = .1
        # see https://stackoverflow.com/a/16459424/4457767
        glFrustum(-near, near, -near*aspect, near*aspect, 2*near, 1e7)

    @glut_callback
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
            self.theta += (x - self.mouse_x) / 4.
            self.phi += (y - self.mouse_y) / 4.

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

    def update(self):
        """Force an update of the screen"""
        glutPostRedisplay()

    def main(self):
        """Main loop"""
        # use glutMainLoop() to save CPU time
        last = time.time()
        while self.is_running:
            glutMainLoopEvent()

            # passage of time
            now = time.time()
            elapsed = now - last
            last = now

            # avoid wasting cycles
            pause = 1./60 - elapsed
            if pause > 0.:
                time.sleep(pause)

            self.update()
        glutCloseFunc(None)

if __name__ == '__main__':
    Scene().main()
