from OpenGL.GL import *

import gui.textures


class Skybox(object):
    def __init__(self, *path):
        self.faces = []
        path, file_pattern = list(path[:-1]), path[-1]
        for coordinate in "XYZ":
            for direction in "Positive", "Negative":
                full_path = path + [file_pattern % (direction + coordinate)]
                texture = gui.textures.load(*full_path)
                self.faces.append(texture)

    def draw(self, size):
        glCullFace(GL_FRONT)
        glPushMatrix()
        glScale(size, size, size)

        gui.textures.bind(self.faces[0], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord(0.0, 0.0) or glVertex3f(+1.0, +1.0, +1.0)
        glTexCoord(0.0, 1.0) or glVertex3f(+1.0, -1.0, +1.0)
        glTexCoord(1.0, 1.0) or glVertex3f(+1.0, -1.0, -1.0)
        glTexCoord(1.0, 0.0) or glVertex3f(+1.0, +1.0, -1.0)
        glEnd()

        gui.textures.bind(self.faces[1], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord(0.0, 0.0) or glVertex3f(-1.0, +1.0, -1.0)
        glTexCoord(0.0, 1.0) or glVertex3f(-1.0, -1.0, -1.0)
        glTexCoord(1.0, 1.0) or glVertex3f(-1.0, -1.0, +1.0)
        glTexCoord(1.0, 0.0) or glVertex3f(-1.0, +1.0, +1.0)
        glEnd()

        gui.textures.bind(self.faces[2], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord(0.0, 0.0) or glVertex3f(+1.0, +1.0, +1.0)
        glTexCoord(0.0, 1.0) or glVertex3f(+1.0, +1.0, -1.0)
        glTexCoord(1.0, 1.0) or glVertex3f(-1.0, +1.0, -1.0)
        glTexCoord(1.0, 0.0) or glVertex3f(-1.0, +1.0, +1.0)
        glEnd()

        gui.textures.bind(self.faces[3], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord(0.0, 0.0) or glVertex3f(-1.0, -1.0, +1.0)
        glTexCoord(0.0, 1.0) or glVertex3f(-1.0, -1.0, -1.0)
        glTexCoord(1.0, 1.0) or glVertex3f(+1.0, -1.0, -1.0)
        glTexCoord(1.0, 0.0) or glVertex3f(+1.0, -1.0, +1.0)
        glEnd()

        gui.textures.bind(self.faces[4], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord(0.0, 0.0) or glVertex3f(-1.0, +1.0, +1.0)
        glTexCoord(0.0, 1.0) or glVertex3f(-1.0, -1.0, +1.0)
        glTexCoord(1.0, 1.0) or glVertex3f(+1.0, -1.0, +1.0)
        glTexCoord(1.0, 0.0) or glVertex3f(+1.0, +1.0, +1.0)
        glEnd()

        gui.textures.bind(self.faces[5], (0, 0, 0))
        glBegin(GL_QUADS)
        glTexCoord(0.0, 0.0) or glVertex3f(+1.0, +1.0, -1.0)
        glTexCoord(0.0, 1.0) or glVertex3f(+1.0, -1.0, -1.0)
        glTexCoord(1.0, 1.0) or glVertex3f(-1.0, -1.0, -1.0)
        glTexCoord(1.0, 0.0) or glVertex3f(-1.0, +1.0, -1.0)
        glEnd()

        gui.textures.unbind()
        glPopMatrix()
        glCullFace(GL_BACK)
