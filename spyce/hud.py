import time
import collections

import textures
import scene
from graphics import *


class HUD(scene.Scene):
    """Scene with an HUD"""
    def __init__(self, title=b'HUD'):
        super(HUD, self).__init__(title)

        # initialize textures
        textures.init()

        # font bitmap information
        self.character_width = 10
        self.character_height = 19
        self.font = textures.load("font.png")

        # set up buffer objects
        self.text_vbo = glGenBuffers(1)
        self.text_tbo = glGenBuffers(1)

        # sliding window of frame timings
        self.frame_timings = collections.deque([time.time()], 60)

    def hud_move(self, x, y):
        """Move the cursor to float coordinates (x, y)"""
        self.hud_x = x
        self.hud_y = y

    def hud_grid(self, row, col):
        """Move the cursor on a virtual grid at (row, col)

        Negative values are supported.
        """

        # handle negative values
        if col < 0:
            col += (self.width / self.character_width)
        if row < 0:
            row += (self.height / self.character_height)

        x = col * self.character_width
        y = row * self.character_height
        self.hud_move(x, y)

    def hud_print(self, string):
        """Print a string to HUD after draw_hud() has been called"""

        def append_vertex(row, col, delta_x, delta_y):
            """Add quad vertex for a character at (row, col)"""
            self.vertcoords += [
                self.hud_x + self.character_width * delta_x,
                self.hud_y + self.character_height * delta_y,
            ]
            self.texcoords += [
                (col + delta_x) / 16.,
                (6 - (row + delta_y)) / 6.,
            ]

        initial_x = self.hud_x  # save column for carriage returns
        for c in string:
            if c == "\n":
                # go down and back for next line
                self.hud_x = initial_x
                self.hud_y += self.character_height
                continue

            # locate the character in the font bitmap
            c = ord(c)
            if not (32 <= c < 127):
                c = 63  # '?'
            c -= 32  # skip non-printable characters
            row, col = c // 16, c % 16

            # append vertices
            append_vertex(row, col, 0, 0)
            append_vertex(row, col, 0, 1)
            append_vertex(row, col, 1, 1)
            append_vertex(row, col, 1, 0)

            # skip forward to next character
            self.hud_x += self.character_width

    def draw_hud(self):
        """Draw the HUD"""
        # reset HUD
        self.texcoords = []
        self.vertcoords = []
        self.hud_grid(0, 1)

        # compute fps
        self.frame_timings.append(time.time())
        elapsed = self.frame_timings[-1] - self.frame_timings[0]
        fps = len(self.frame_timings) / elapsed

        self.hud_print("%i FPS\n" % fps)
        self.hud_print("Zoom x%g\n" % self.zoom)

    def set_and_draw_hud(self):
        """Set up the camera and draw the HUD"""

        # set up OpenGL context for HUD
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0.0, self.width, self.height, 0.0, -1.0, 10.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # fill vertex lists
        self.draw_hud()

        # fill buffer objects
        make_vbo(self.vertcoords, self.text_vbo)
        glVertexPointer(2, GL_FLOAT, 0, None)
        make_vbo(self.texcoords, self.text_tbo)
        glTexCoordPointer(2, GL_FLOAT, 0, None)

        # actually draw the HUD
        textures.bind(self.font)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glDrawArrays(GL_QUADS, 0, len(self.vertcoords)//2)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        textures.unbind()

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
