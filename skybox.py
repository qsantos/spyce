from OpenGL.GL import *

import textures


class Skybox:
    def __init__(self, *path):
        self.faces = []
        path, file_pattern = list(path[:-1]), path[-1]
        for coordinate in "XYZ":
            for direction in "Positive", "Negative":
                full_path = path + [file_pattern % (direction + coordinate)]
                texture = textures.load(*full_path)
                self.faces.append(texture)

    def draw(self, size):
        glPushMatrix()
        glScale(size, size, size)

        textures.bind(self.faces[0], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord(0.0, 0.0) or glVertex3f(+1.0, +1.0, +1.0)
        glTexCoord(0.0, 1.0) or glVertex3f(+1.0, -1.0, +1.0)
        glTexCoord(1.0, 1.0) or glVertex3f(+1.0, -1.0, -1.0)
        glTexCoord(1.0, 0.0) or glVertex3f(+1.0, +1.0, -1.0)
        glEnd()

        textures.bind(self.faces[1], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord(0.0, 0.0) or glVertex3f(-1.0, +1.0, -1.0)
        glTexCoord(0.0, 1.0) or glVertex3f(-1.0, -1.0, -1.0)
        glTexCoord(1.0, 1.0) or glVertex3f(-1.0, -1.0, +1.0)
        glTexCoord(1.0, 0.0) or glVertex3f(-1.0, +1.0, +1.0)
        glEnd()

        textures.bind(self.faces[2], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord(0.0, 0.0) or glVertex3f(+1.0, +1.0, +1.0)
        glTexCoord(0.0, 1.0) or glVertex3f(+1.0, +1.0, -1.0)
        glTexCoord(1.0, 1.0) or glVertex3f(-1.0, +1.0, -1.0)
        glTexCoord(1.0, 0.0) or glVertex3f(-1.0, +1.0, +1.0)
        glEnd()

        textures.bind(self.faces[3], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord(0.0, 0.0) or glVertex3f(-1.0, -1.0, +1.0)
        glTexCoord(0.0, 1.0) or glVertex3f(-1.0, -1.0, -1.0)
        glTexCoord(1.0, 1.0) or glVertex3f(+1.0, -1.0, -1.0)
        glTexCoord(1.0, 0.0) or glVertex3f(+1.0, -1.0, +1.0)
        glEnd()

        textures.bind(self.faces[4], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord(0.0, 0.0) or glVertex3f(-1.0, +1.0, +1.0)
        glTexCoord(0.0, 1.0) or glVertex3f(-1.0, -1.0, +1.0)
        glTexCoord(1.0, 1.0) or glVertex3f(+1.0, -1.0, +1.0)
        glTexCoord(1.0, 0.0) or glVertex3f(+1.0, +1.0, +1.0)
        glEnd()

        textures.bind(self.faces[5], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord(0.0, 0.0) or glVertex3f(+1.0, +1.0, -1.0)
        glTexCoord(0.0, 1.0) or glVertex3f(+1.0, -1.0, -1.0)
        glTexCoord(1.0, 1.0) or glVertex3f(-1.0, -1.0, -1.0)
        glTexCoord(1.0, 0.0) or glVertex3f(-1.0, +1.0, -1.0)
        glEnd()

        textures.unbind()
        glPopMatrix()
