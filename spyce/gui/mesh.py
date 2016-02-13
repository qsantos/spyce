import math

from gui.graphics import *


class Mesh(object):
    """A 2D or 3D mesh"""
    def __init__(self, mode):
        """Create a new mesh

        A Vertex Buffer Object is filled with data from self.vertices()
        A Texcoord Buffer Object is filled with data from self.texcoords()
        A Normal Buffer Object is filled with data from self.normals()
        Mesh will be drawn using given OpenGL mode (GL_TRIANGLES, etc.)
        """
        # save meta-data
        self.mode = mode
        vertices = list(self.vertices())
        self.length = len(vertices)
        self.components = len(vertices[0])

        # fill vertex buffer object
        self.vertex_buffer = BufferObject(vertices, flatten=True)

        # fill texcoord buffer object
        if hasattr(self, "texcoords"):
            self.texcoord_buffer = BufferObject(self.texcoords(), flatten=True)

        # fill normal buffer boject
        if hasattr(self, "normals"):
            self.normal_buffer = BufferObject(self.normals(), flatten=True)

    def draw(self):
        """Draw the mesh"""
        # select vertex buffer object
        self.vertex_buffer.bind()
        glVertexPointer(self.components, GL_FLOAT, 0, None)
        glEnableClientState(GL_VERTEX_ARRAY)

        # select texcoord buffer object
        if hasattr(self, "texcoord_buffer"):
            self.texcoord_buffer.bind()
            glTexCoordPointer(2, GL_FLOAT, 0, None)
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        # select normal buffer object
        if hasattr(self, "normal_buffer"):
            self.normal_buffer.bind()
            glNormalPointer(GL_FLOAT, 0, None)
            glEnableClientState(GL_NORMAL_ARRAY)

        # actually draw
        glDrawArrays(self.mode, 0, self.length)

        # disable buffer objects
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)


class Sphere(Mesh):
    """Mesh: UV sphere centered on (0, 0, 0)"""
    def __init__(self, radius, slices, stacks):
        self.radius = radius
        self.slices = slices
        self.stacks = stacks
        super(Sphere, self).__init__(GL_QUAD_STRIP)

    def vertices(self):
        for j in range(self.stacks):
            for i in range(self.slices+1):
                angle_i = (2*math.pi * i) / self.slices
                angle_j = (math.pi * (j+1)) / self.stacks
                yield (
                    self.radius * math.sin(angle_j) * math.sin(angle_i),
                    self.radius * math.sin(angle_j) * math.cos(angle_i),
                    self.radius * math.cos(angle_j),
                )
                angle_j = (math.pi * j) / self.stacks
                yield (
                    self.radius * math.sin(angle_j) * math.sin(angle_i),
                    self.radius * math.sin(angle_j) * math.cos(angle_i),
                    self.radius * math.cos(angle_j),
                )

    def texcoords(self):
        for j in range(self.stacks):
            for i in range(self.slices+1):
                yield 1 - float(i) / self.slices, 1 - float(j+1) / self.stacks
                yield 1 - float(i) / self.slices, 1 - float(j) / self.stacks

    def normals(self):
        """Generate normals for sphere mesh"""
        for j in range(self.stacks):
            for i in range(self.slices+1):
                angle_i = (2*math.pi * i) / self.slices
                angle_j = (math.pi * (j+1)) / self.stacks
                yield (
                    math.sin(angle_i) * math.sin(angle_j),
                    math.cos(angle_i) * math.sin(angle_j),
                    math.cos(angle_j),
                )
                angle_j = (math.pi * j) / self.stacks
                yield (
                    math.sin(angle_i) * math.sin(angle_j),
                    math.cos(angle_i) * math.sin(angle_j),
                    math.cos(angle_j),
                )
