import io
import os
import sys
import pkgutil
from OpenGL.GLU import *
from OpenGL.GL import *


def init():
    """Set relevant OpenGL options"""
    glEnable(GL_TEXTURE_2D)

    # fill default texture with white
    # (for some reasons, this is not the default behavior)
    glBindTexture(GL_TEXTURE_2D, 0)
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA, 1, 1, 0, GL_RGBA, GL_FLOAT,
        [1., 1., 1., 1.]  # opaque white pixel
    )


def bind(tex_id, default_color=(1.0, 1.0, 1.0)):
    """Bind texture if non-null; otherwise fill with default color"""
    if tex_id == 0:
        r, g, b = default_color
        glColor4f(r, g, b, 1.0)
    else:
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBindTexture(GL_TEXTURE_2D, tex_id)


def unbind():
    """Unbind texture"""
    glBindTexture(GL_TEXTURE_2D, 0)


try:
    from PIL import Image
except ImportError:
    print("Install python3-pil for textures", file=sys.stderr)

    def load(*_, **__):
        """No texture can be loaded with PIL; return dummy texture 0"""
        return 0

    def load_cubemap(*path):
        return 0
else:
    def load_image(*path):
        """Return raw picels from file at given path (join arguments)"""
        filename = os.path.join("data", "textures", *path)
        try:
            image = pkgutil.get_data("gspyce", filename)
        except FileNotFoundError:
            print("Missing %s" % filename, file=sys.stderr)
            return None, None, None

        im = Image.open(io.BytesIO(image))
        w, h = im.size
        # <https://pillow.readthedocs.io/en/4.3.x/handbook/writing-your-own-file-decoder.html#the-raw-decoder>
        # orientation=-1 ⇒ first row at bottom (as OpenGL expects)
        data = im.convert("RGBA").tobytes("raw", "RGBA", 0, -1)
        return w, h, data

    def load(*path):
        """Make texture from file at given path (join arguments)

        If loading the file fails, return dummy texture 0"""
        w, h, data = load_image(*path)
        if data is None:
            return 0

        new_tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, new_tex)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data
        )
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

        return new_tex

    def load_cubemap(*path):
        """Create a cubemap

        Arguments are joined together to make the paths to the textures. Last
        argument should be a pattern with a "%s", which will be completed as
        "PositiveX", "NegativeY" and so on."""

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, texture)
        path, file_pattern = list(path[:-1]), path[-1]
        faces = ["PositiveX", "NegativeX", "PositiveY", "NegativeY", "PositiveZ", "NegativeZ"]
        for i, face in enumerate(faces):
            full_path = path + [file_pattern % face]
            w, h, data = load_image(*full_path)
            if data is None:
                continue
            glTexImage2D(
                GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data
            )
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_CUBE_MAP, 0)

        return texture
