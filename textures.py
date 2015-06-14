from OpenGL.GL import *

try:
    from PIL import Image
except ImportError:
    import sys
    if sys.version_info[0] == 3:  # Python 3
        sys.stderr.write("Install python3-pil for textures\n")
    else:  # Python 2
        sys.stderr.write("Install python-pil for textures\n")

    def load(*_, **__):
        return 0

    def bind(*_, **__):
        pass

    def unbind(*_, **__):
        pass
else:
    def load(filename):
        try:
            im = Image.open(filename)
        except:  # FileNotFoundError in Python 3, IOError in Python 2
            print("Missing %s" % filename)
            return 0

        w, h = im.size
        try:
            data = im.tostring("raw", "RGBA", 0, -1)
        except SystemError:
            try:
                data = im.tostring("raw", "RGBX", 0, -1)
            except SystemError:
                data = im.convert("RGBA").tostring("raw", "RGBA", 0, -1)

        new_tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, new_tex)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data
        )
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glBindTexture(GL_TEXTURE_2D, 0)

        return new_tex

    def bind(tex_id, default_color=(1.0, 1.0, 1.0)):
        if tex_id == 0:
            r, g, b = default_color
            glColor4f(r, g, b, 1.0)
        else:
            glColor4f(1.0, 1.0, 1.0, 1.0)
            glBindTexture(GL_TEXTURE_2D, tex_id)

    def unbind():
        glBindTexture(GL_TEXTURE_2D, 0)
