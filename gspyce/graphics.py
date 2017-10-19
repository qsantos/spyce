import os
import pkgutil
import itertools
import functools
from OpenGL.GLUT import *
from OpenGL.GL import *


def read_pixels(x, y, w, h):
    """Wrapper function to fix inconsistencies PyOpenGL's glReadPixels()"""
    # `outputType` forces output to be a grid (avoids Linux vs Windows issues)
    data = glReadPixels(x, y, w, h, GL_RGB, GL_UNSIGNED_BYTE, outputType=0)

    # fix for inversion of dimensions when Numpy is not installed
    if isinstance(data, ctypes.Array):
        # flatten grid (names show how PyOpenGL interprets the data)
        data = [pixel for color in data for row in color for pixel in row]
        # group colors into pixels
        data = [data[i:i+3] for i in range(0, len(data), 3)]
        # group pixels into rows
        data = [data[i:i+w] for i in range(0, len(data), w)]
    return data


class BufferObject(object):
    """OpenGL Buffer Object helper"""
    def __init__(self, data=None, flatten=False):
        """Create a new Buffer Object, optionally fill it (see `fill()`)"""
        self.index = glGenBuffers(1)
        self.size = 0
        if data is not None:
            self.fill(data, flatten)

    def bind(self):
        """Bind the Buffer Object to GL_ARRAY_BUFFER"""
        glBindBuffer(GL_ARRAY_BUFFER, self.index)

    def unbind(self):
        """Unbind the Buffer Object off GL_ARRAY_BUFFER"""
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def fill(self, data, flatten=False):
        """Fill the Buffer Object with data (assume list of floats)

        If `flatten`, assume data is an iterable of iterables and flatten it"""
        if flatten:
            data = itertools.chain(*data)
        # pack as float[]
        data = list(data)  # need length for ctypes array
        self.size = len(data)
        data_buffer = (ctypes.c_float*self.size)(*data)
        # send to GPU
        self.bind()
        glBufferData(GL_ARRAY_BUFFER, data_buffer, GL_STATIC_DRAW)
        self.unbind()


def make_shader_source(program, source, type_, filename="-"):
    """Compile and attach shader of given type from source"""
    shader = glCreateShader(type_)
    glShaderSource(shader, source)
    glCompileShader(shader)
    error = glGetShaderInfoLog(shader)
    if error:
        # filename in messages for locating error
        error = error.decode().replace('0:', filename+':')
        raise SyntaxError('while compiling shaders\n' + error)
    glAttachShader(program, shader)


def make_shader_filename(program, filename, type_):
    """Compile and attach shader of given type from file"""
    path = os.path.join("data", "shaders", filename)
    source = pkgutil.get_data('gspyce', path)
    return make_shader_source(program, source, type_)


def make_program(*features):
    """Create a program with only given features"""
    # compile features
    program = glCreateProgram()
    for feature in features:
        make_shader_filename(program, feature + '.vert', GL_VERTEX_SHADER)
        make_shader_filename(program, feature + '.frag', GL_FRAGMENT_SHADER)

    # main() functions just call each feature in given order
    main = (
        "#version 110\n" +
        # declarations
        "\n".join("void %s();" % feature for feature in features) +
        "void main(){\n" +
        "\n".join("%s();" % feature for feature in features) +  # calls
        "}"
    )
    make_shader_source(program, main, GL_VERTEX_SHADER, "<main>")
    make_shader_source(program, main, GL_FRAGMENT_SHADER, "<main>")

    # link program
    glLinkProgram(program)
    error = glGetProgramInfoLog(program)
    if error:
        raise SyntaxError('while linking shaders\n' + error.decode())

    # make `Texture0` refer to the first texture
    variable = glGetUniformLocation(program, b"Texture0")
    current_program = glGetIntegerv(GL_CURRENT_PROGRAM)
    glUseProgram(program)
    glUniform1i(variable, 0)
    glUseProgram(current_program)

    return program


def main_program(*features):
    """Create a program with some preset features"""
    features = ("setdefaults", "logdepth") + features + ("picking",)
    return make_program(*features)


def glut_callback(f):
    """Wrap a GLUT callback method so that exceptions are not ignored"""
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except:
            self.is_running = False
            glutLeaveMainLoop()
            raise
    return wrapper
