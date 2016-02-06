import os
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
    import sys
    if sys.version_info[0] == 3:  # Python 3
        sys.stderr.write("Install python3-pil for textures\n")
    else:  # Python 2
        sys.stderr.write("Install python-pil for textures\n")

    def load(*_, **__):
        """No texture can be loaded with PIL; return dummy texture 0"""
        return 0
else:
    def load(*path):
        """Make texture from file at given path (join arguments)

        If loading the file fails, return dummy texture 0"""
        filename = os.path.join("data", "textures", *path)
        try:
            im = Image.open(filename)
        except:  # FileNotFoundError in Python 3, IOError in Python 2
            print("Missing %s" % filename)
            return 0

        w, h = im.size
        try:
            data = im.tobytes("raw", "RGBA", 0, -1)
        except SystemError:
            try:
                data = im.tobytes("raw", "RGBX", 0, -1)
            except SystemError:
                data = im.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

        new_tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, new_tex)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data
        )
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glBindTexture(GL_TEXTURE_2D, 0)

        return new_tex
