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
else:
    def load(*path):
        """Make texture from file at given path (join arguments)

        If loading the file fails, return dummy texture 0"""
        filename = os.path.join("data", "textures", *path)
        try:
            image = pkgutil.get_data("gspyce", filename)
        except FileNotFoundError:
            print("Missing %s" % filename, file=sys.stderr)
            return 0

        im = Image.open(io.BytesIO(image))
        w, h = im.size
        try:
            data = im.tobytes("raw", "RGBA", 0, -1)
        except (SystemError, ValueError):
            try:
                data = im.tobytes("raw", "RGBX", 0, -1)
            except (SystemError, ValueError):
                data = im.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

        new_tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, new_tex)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data
        )
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

        return new_tex
