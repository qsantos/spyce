from OpenGL.GL import *

import gspyce.textures


class Skybox:
    """Simulate the sky with a textured box"""

    def __init__(self, *path):
        """Create a skybox

        Arguments are joined together to make the paths to the textures. Last
        argument should be a pattern with a "%s", which will be completed as
        "PositiveX", "NegativeY" and so on."""
        self.faces = []
        path, file_pattern = list(path[:-1]), path[-1]
        for coordinate in "XYZ":
            for direction in "Positive", "Negative":
                full_path = path + [file_pattern % (direction + coordinate)]
                texture = gspyce.textures.load(*full_path)
                self.faces.append(texture)

    def draw(self):
        """Draw a skybox of given size"""
        gspyce.textures.bind(self.faces[0], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0) or glVertex3f(+10, +10, +10)
        glTexCoord2f(1.0, 0.0) or glVertex3f(+10, +10, -10)
        glTexCoord2f(1.0, 1.0) or glVertex3f(+10, -10, -10)
        glTexCoord2f(0.0, 1.0) or glVertex3f(+10, -10, +10)
        glEnd()

        gspyce.textures.bind(self.faces[1], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0) or glVertex3f(-10, +10, -10)
        glTexCoord2f(1.0, 0.0) or glVertex3f(-10, +10, +10)
        glTexCoord2f(1.0, 1.0) or glVertex3f(-10, -10, +10)
        glTexCoord2f(0.0, 1.0) or glVertex3f(-10, -10, -10)
        glEnd()

        gspyce.textures.bind(self.faces[2], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0) or glVertex3f(+10, +10, +10)
        glTexCoord2f(1.0, 0.0) or glVertex3f(-10, +10, +10)
        glTexCoord2f(1.0, 1.0) or glVertex3f(-10, +10, -10)
        glTexCoord2f(0.0, 1.0) or glVertex3f(+10, +10, -10)
        glEnd()

        gspyce.textures.bind(self.faces[3], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0) or glVertex3f(+10, -10, +10)
        glTexCoord2f(1.0, 0.0) or glVertex3f(+10, -10, -10)
        glTexCoord2f(1.0, 1.0) or glVertex3f(-10, -10, -10)
        glTexCoord2f(0.0, 1.0) or glVertex3f(-10, -10, +10)
        glEnd()

        gspyce.textures.bind(self.faces[4], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0) or glVertex3f(-10, +10, +10)
        glTexCoord2f(1.0, 0.0) or glVertex3f(+10, +10, +10)
        glTexCoord2f(1.0, 1.0) or glVertex3f(+10, -10, +10)
        glTexCoord2f(0.0, 1.0) or glVertex3f(-10, -10, +10)
        glEnd()

        gspyce.textures.bind(self.faces[5], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0) or glVertex3f(+10, +10, -10)
        glTexCoord2f(1.0, 0.0) or glVertex3f(-10, +10, -10)
        glTexCoord2f(1.0, 1.0) or glVertex3f(-10, -10, -10)
        glTexCoord2f(0.0, 1.0) or glVertex3f(+10, -10, -10)
        glEnd()

        gspyce.textures.unbind()
