import time
import collections

from spyce.vector import Mat4
import gspyce.scene
from gspyce.graphics import *


class HUD(gspyce.scene.Scene):
    """Scene with an HUD"""
    def __init__(self, title=b'HUD'):
        super().__init__(title)

        # font bitmap information
        self.character_width = 10
        self.character_height = 19
        self.font = gspyce.textures.load("font.png")

        # set up buffer objects
        self.text_vbo = BufferObject()
        self.text_tbo = BufferObject()

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
            elif c == "\t":
                self.hud_x += self.character_width*4
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
            append_vertex(row, col, 1, 1)
            append_vertex(row, col, 1, 0)
            append_vertex(row, col, 0, 0)

            # skip forward to next character
            self.hud_x += self.character_width

    def draw_hud(self):
        """Draw the HUD"""

        # this is a fixed-length queue (automatically drops oldest timing)
        self.frame_timings.append(time.time())
        # compute fps as the inverse of a moving average
        elapsed = self.frame_timings[-1] - self.frame_timings[0]
        # with n timings, we measure n-1 consecutives frames
        fps = (len(self.frame_timings) - 1.) / elapsed

        if fps < 9.5:  # 10 is even so 9.5 is rounded up
            self.hud_print("%.1f FPS\n" % fps)
        else:
            self.hud_print("%i FPS\n" % round(fps))
        self.hud_print("Zoom x%g\n" % self.zoom)

    def set_and_draw_hud(self):
        """Set up the camera and draw the HUD"""

        # save matrix state
        original_projection_matrix = self.projection_matrix
        original_modelview_matrix = self.modelview_matrix

        # set up matrices for HUD
        transform = Mat4.ortho(0.0, self.width, self.height, 0.0, -1.0, 10.0)
        self.set_projection_matrix(transform)
        self.set_modelview_matrix(Mat4())

        # reset HUD
        self.texcoords = []
        self.vertcoords = []
        self.hud_grid(0, 1)

        # fill vertex lists
        self.draw_hud()

        program = self.current_shader

        # vertices
        var = glGetAttribLocation(program, "vertex")
        glEnableVertexAttribArray(var)
        self.text_vbo.fill(self.vertcoords)
        self.text_vbo.bind()
        glVertexAttribPointer(var, 2, GL_FLOAT, False, 0, None)
        self.text_vbo.unbind()

        # textures coordinates
        var = glGetAttribLocation(program, "texcoord")
        glEnableVertexAttribArray(var)
        self.text_tbo.fill(self.texcoords)
        self.text_tbo.bind()
        glVertexAttribPointer(var, 2, GL_FLOAT, False, 0, None)
        self.text_tbo.unbind()

        # actually draw
        self.set_color(1, 1, 1, 1)
        glBindTexture(GL_TEXTURE_2D, self.font)
        glDrawArrays(GL_TRIANGLES, 0, self.text_vbo.size // 2)
        glBindTexture(GL_TEXTURE_2D, 0)

        # restore state
        var = glGetAttribLocation(program, "texcoord")
        glDisableVertexAttribArray(var)
        var = glGetAttribLocation(program, "vertex")
        glDisableVertexAttribArray(var)
        self.set_modelview_matrix(original_modelview_matrix)
        self.set_projection_matrix(original_projection_matrix)

    @glut_callback
    def displayFunc(self):
        """Draw the screen (GLUT callback)"""
        self.set_and_draw()
        self.set_and_draw_hud()
        glutSwapBuffers()


def main():
    HUD().main()


if __name__ == '__main__':
    main()
