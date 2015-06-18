import time
import collections

import textures
import gui
from graphics import *


class HUD(gui.GUI):
    """GUI with an HUD"""
    def __init__(self, title=b'HUD'):
        gui.GUI.__init__(self, title)

        # sliding window of frame timings
        self.frame_timings = collections.deque([time.time()], 60)

    def hud_print(self, string):
        """Print a string to HUD after draw_hud() has been called"""
        glutBitmapString(GLUT_BITMAP_HELVETICA_18, string.encode())

    def draw_hud(self):
        """Draw an HUD"""
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glRasterPos2i(10, 20)

        # compute fps
        self.frame_timings.append(time.time())
        elapsed = self.frame_timings[-1] - self.frame_timings[0]
        fps = len(self.frame_timings) / elapsed

        self.hud_print("%i FPS\n" % fps)
        self.hud_print("Zoom x%g\n" % self.zoom)

    def set_and_draw_hud(self):
        # set up OpenGL context for HUD
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0.0, self.width, self.height, 0.0, -1.0, 10.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_CULL_FACE)
        glClear(GL_DEPTH_BUFFER_BIT)

        # fill vertex lists
        self.draw_hud()

        # restore OpenGL context
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    @glut_callback
    def displayFunc(self):
        """Draw the screen (GLUT callback)"""
        self.set_and_draw()
        self.set_and_draw_hud()
        glutSwapBuffers()

if __name__ == '__main__':
    HUD().main()
