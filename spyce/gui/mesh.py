import math

from spyce.gui.graphics import *


class Mesh(object):
    """A 2D or 3D mesh"""
    bound_mesh = None

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

    def bind(self):
        """"Bind the mesh for glDrawArrays()

        Return True if the mesh was already bound"""
        if Mesh.bound_mesh is not None:
            if Mesh.bound_mesh is self:
                return True
            else:
                raise RuntimeError("Another mesh is already bound")
        Mesh.bound_mesh = self

        # select vertex buffer object
        self.vertex_buffer.bind()
        glVertexPointer(self.components, GL_FLOAT, 0, None)
        self.vertex_buffer.unbind()
        glEnableClientState(GL_VERTEX_ARRAY)

        # select texcoord buffer object
        if hasattr(self, "texcoord_buffer"):
            self.texcoord_buffer.bind()
            glTexCoordPointer(2, GL_FLOAT, 0, None)
            self.texcoord_buffer.unbind()
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        # select normal buffer object
        if hasattr(self, "normal_buffer"):
            self.normal_buffer.bind()
            glNormalPointer(GL_FLOAT, 0, None)
            self.normal_buffer.unbind()
            glEnableClientState(GL_NORMAL_ARRAY)

        return False

    def unbind(self):
        """Unbind the mesh"""
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        Mesh.bound_mesh = None

    def draw(self):
        """Draw the mesh"""
        was_bound = self.bind()
        glDrawArrays(self.mode, 0, self.length)
        if not was_bound:
            self.unbind()


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


class Circle(Mesh):
    """Mesh: circle centered on (0, 0, 0) with axis (0, 0, 1)"""
    def __init__(self, radius, points):
        self.radius = radius
        self.points = points
        super(Circle, self).__init__(GL_LINE_LOOP)

    def vertices(self):
        vertices = []
        for i in range(self.points):
            x = 2.*i/self.points - 1  # from -1.0 to +1.0
            theta = math.pi * x
            yield (
                self.radius * math.cos(theta),
                self.radius * math.sin(theta),
            )


class CircleThroughOrigin(Mesh):
    """Mesh: circle centered on (radius, 0, 0) with axis (0, 0, 1)"""
    def __init__(self, radius, points):
        self.radius = radius
        self.points = points
        super(CircleThroughOrigin, self).__init__(GL_LINE_LOOP)

    def vertices(self):
        for i in range(self.points):
            x = 2.*i/self.points - 1  # from -1.0 to +1.0
            theta = math.pi * x**3
            yield (
                self.radius * (1. - math.cos(theta)),
                self.radius * math.sin(theta),
            )


class Parabola(Mesh):
    """Mesh: parabola"""
    def __init__(self, points):
        self.points = points
        super(Parabola, self).__init__(GL_LINE_STRIP)

    def vertices(self):
        for i in range(self.points):
            x = 2.*i/(self.points-1) - 1  # from -1.0 to +1.0
            theta = math.pi * x
            yield math.cosh(theta), math.sinh(theta)
