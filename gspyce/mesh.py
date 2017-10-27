import math

from spyce.vector import Vec4, Mat4
from gspyce.graphics import *


class Mesh:
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

        program = glGetIntegerv(GL_CURRENT_PROGRAM)

        # select vertex buffer object
        var = glGetAttribLocation(program, "vertex")
        glEnableVertexAttribArray(var)
        self.vertex_buffer.bind()
        glVertexAttribPointer(var, self.components, GL_FLOAT, False, 0, None)
        self.vertex_buffer.unbind()

        # select texcoord buffer object
        if hasattr(self, "texcoord_buffer"):
            var = glGetAttribLocation(program, "texcoord")
            if var != -1:  # active attribute
                glEnableVertexAttribArray(var)
                self.texcoord_buffer.bind()
                glVertexAttribPointer(var, 2, GL_FLOAT, False, 0, None)
                self.texcoord_buffer.unbind()

        # select normal buffer object
        if hasattr(self, "normal_buffer"):
            var = glGetAttribLocation(program, "normal")
            if var != -1:  # active attribute
                glEnableVertexAttribArray(var)
                self.normal_buffer.bind()
                glVertexAttribPointer(var, 3, GL_FLOAT, False, 0, None)
                self.normal_buffer.unbind()

        return False

    def unbind(self):
        """Unbind the mesh"""
        program = glGetIntegerv(GL_CURRENT_PROGRAM)
        var = glGetAttribLocation(program, "vertex")
        if var != -1:
            glDisableVertexAttribArray(var)
        var = glGetAttribLocation(program, "texcoord")
        if var != -1:
            glDisableVertexAttribArray(var)
        var = glGetAttribLocation(program, "normal")
        if var != -1:
            glDisableVertexAttribArray(var)
        Mesh.bound_mesh = None

    def draw(self):
        """Draw the mesh"""
        was_bound = self.bind()
        glDrawArrays(self.mode, 0, self.length)
        if not was_bound:
            self.unbind()


class Generic(Mesh):
    def __init__(self, mode, vertices):
        self.vertices_ = vertices
        super().__init__(mode)

    def vertices(self):
        yield from self.vertices_


class Square(Mesh):
    def __init__(self, size):
        self.size = size
        super().__init__(GL_QUADS)

    def vertices(self):
        s = self.size
        yield -s, 0, -s
        yield -s, 0, +s
        yield +s, 0, +s
        yield +s, 0, -s

    def texcoords(self):
        yield 0, 0
        yield 0, 1
        yield 1, 1
        yield 1, 0


class Sphere(Mesh):
    """Mesh: UV sphere centered on (0, 0, 0)"""
    def __init__(self, radius, slices, stacks):
        self.radius = radius
        self.slices = slices
        self.stacks = stacks
        super().__init__(GL_QUAD_STRIP)

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
        super().__init__(GL_LINE_LOOP)

    def vertices(self):
        for i in range(self.points):
            x = 2*i/self.points - 1  # from -1.0 to +1.0
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
        super().__init__(GL_LINE_LOOP)

    def vertices(self):
        for i in range(self.points):
            x = 2*i/self.points - 1  # from -1.0 to +1.0
            theta = math.pi * x**3
            yield (
                self.radius * (1 - math.cos(theta)),
                self.radius * math.sin(theta),
            )


class Parabola(Mesh):
    """Mesh: parabola"""
    def __init__(self, points):
        self.points = points
        super().__init__(GL_LINE_STRIP)

    def vertices(self):
        for i in range(self.points):
            x = 2*i/(self.points-1) - 1  # from -1.0 to +1.0
            theta = math.pi * x
            yield math.cosh(theta), math.sinh(theta)


class OrbitMesh(Mesh):
    def __init__(self, orbit):
        self.orbit = orbit
        mode = GL_LINE_LOOP if orbit.eccentricity < 1. else GL_LINE_STRIP
        super().__init__(mode)

    def vertices(self):
        orbit = self.orbit
        transform = (
            Mat4.rotate(orbit.longitude_of_ascending_node, 0, 0, 1) @
            Mat4.rotate(orbit.inclination,                 1, 0, 0) @
            Mat4.rotate(orbit.argument_of_periapsis,       0, 0, 1) @
            Mat4.translate(-orbit.focus, 0, 0) @
            Mat4.scale(orbit.semi_major_axis, orbit.semi_minor_axis, 1.0)
        )
        if orbit.eccentricity < 1.:
            base_mesh = Circle(1, 512)
        else:
            base_mesh = Parabola(256)
        for vertice in base_mesh.vertices():
            yield transform @ Vec4(*vertice)


class ApsesMesh(Mesh):
    def __init__(self, orbit):
        self.orbit = orbit
        self.transform = (
            Mat4.rotate(orbit.longitude_of_ascending_node, 0, 0, 1) @
            Mat4.rotate(orbit.inclination,                 1, 0, 0) @
            Mat4.rotate(orbit.argument_of_periapsis,       0, 0, 1) @
            Mat4.translate(-orbit.focus, 0, 0) @
            Mat4.scale(orbit.semi_major_axis, orbit.semi_minor_axis, 1.0)
        )
        super().__init__(GL_POINTS)

    def vertices(self):
        # periapsis
        yield self.transform @ Vec4(+1)
        if self.orbit.eccentricity < 1.:  # circular and elliptic orbits
            # apoapsis
            yield self.transform @ Vec4(-1)

# issues when drawing the orbit of a focused body:
# 1. moving to system center and back close to camera induces
#    loss of significance and produces jitter
# 2. drawing the orbit as segments may put the body visibly out
#    of the line when zooming in
# 3. line breaks may be visible close to the camera


class FocusedOrbitMesh(Mesh):
    def __init__(self, orbit, time):
        self.orbit = orbit
        self.time = time
        mode = GL_LINE_LOOP if orbit.eccentricity < 1. else GL_LINE_STRIP
        super().__init__(mode)

    def vertices(self):
        orbit = self.orbit

        # now, we fix the three issues mentioned above
        # draw the orbit from the body rather than from the orbit focus (1.)

        if orbit.eccentricity >= 1.:  # open orbits
            # choose interpolation points
            def _():
                true_anomaly = orbit.true_anomaly_at_time(self.time)
                # decide when to stop drawing
                max_true_anomaly = orbit.true_anomaly_at_escape()
                if max_true_anomaly is None:
                    max_true_anomaly = orbit.ejection_angle() - 1e-2
                # normal hyperbola
                n = 128
                for i in range(n+1):
                    t = 2.*i/n - 1
                    yield max_true_anomaly * t
                # ensure the body will be on the line (2.)
                # more points close to the camera (3.)
                n = 64
                for i in range(n+1):
                    t = 2.*i/n - 1
                    theta = true_anomaly + t * abs(t)
                    if abs(theta) < max_true_anomaly:
                        yield theta
            angles = sorted(_())

            focus_offset = orbit.position_at_time(self.time)
            for angle in angles:
                yield orbit.position_at_true_anomaly(angle) - focus_offset
        else:  # closed orbits
            # nice hack with circle symetry to draw the orbit from the body
            # while still using VBOs
            # unsure it can be adapted for parabolic and hyperbolic orbits

            # make tilted ellipse from a circle; and rotate at current anomaly
            anomaly = orbit.eccentric_anomaly_at_time(self.time)
            transform = (
                Mat4.rotate(orbit.longitude_of_ascending_node, 0, 0, 1) @
                Mat4.rotate(orbit.inclination,                 1, 0, 0) @
                Mat4.rotate(orbit.argument_of_periapsis,       0, 0, 1) @
                Mat4.scale(orbit.semi_major_axis, orbit.semi_minor_axis, 1.0) @
                Mat4.rotate(anomaly - math.pi, 0, 0, 1)
            )

            # the first point of circle_through_origin is (0,0) (2.)
            # more points are located near the origin (3.)
            base_mesh = CircleThroughOrigin(1, 256)
            for vertice in base_mesh.vertices():
                yield transform @ Vec4(*vertice)


class FocusedApsesMesh(Mesh):
    def __init__(self, orbit, time):
        self.orbit = orbit
        self.time = time
        super().__init__(GL_POINTS)

    def vertices(self):
        focus_offset = self.orbit.position_at_time(self.time)

        # periapsis
        yield self.orbit.position_at_true_anomaly(0) - focus_offset
        if self.orbit.eccentricity < 1.:  # circular and elliptic orbits
            # apoapsis
            yield self.orbit.position_at_true_anomaly(math.pi) - focus_offset
