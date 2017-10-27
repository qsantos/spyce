from gspyce.graphics import *
import gspyce.textures


class Skybox:
    """Simulate the sky with a textured box"""

    def __init__(self, *path):
        """Create a skybox

        Arguments are joined together to make the paths to the textures. Last
        argument should be a pattern with a "%s", which will be completed as
        "PositiveX", "NegativeY" and so on."""

        self.texture = gspyce.textures.load_cubemap(*path)
        s = 10
        vertices = [
            # +X
            (+s, +s, +s), (+s, +s, -s), (+s, -s, +s),
            (+s, -s, +s), (+s, +s, -s), (+s, -s, -s),
            # -X
            (-s, -s, +s), (-s, -s, -s), (-s, +s, +s),
            (-s, +s, +s), (-s, -s, -s), (-s, +s, -s),
            # +Y
            (-s, +s, +s), (-s, +s, -s), (+s, +s, +s),
            (+s, +s, +s), (-s, +s, -s), (+s, +s, -s),
            # -Y
            (+s, -s, +s), (+s, -s, -s), (-s, -s, +s),
            (-s, -s, +s), (+s, -s, -s), (-s, -s, -s),
            # +Z
            (+s, +s, +s), (+s, -s, +s), (-s, +s, +s),
            (-s, +s, +s), (+s, -s, +s), (-s, -s, +s),
            # -Z
            (+s, +s, -s), (-s, +s, -s), (+s, -s, -s),
            (+s, -s, -s), (-s, +s, -s), (-s, -s, -s),
        ]
        self.vertex_buffer = BufferObject(vertices, flatten=True)

    def draw(self):
        """Draw a skybox of given size"""
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)

        self.vertex_buffer.bind()

        program = glGetIntegerv(GL_CURRENT_PROGRAM)
        var = glGetAttribLocation(program, "vertex")
        glEnableVertexAttribArray(var)
        glVertexAttribPointer(var, 3, GL_FLOAT, False, 0, None)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glDisableVertexAttribArray(var)
        self.vertex_buffer.unbind()
        glBindTexture(GL_TEXTURE_CUBE_MAP, 0)
