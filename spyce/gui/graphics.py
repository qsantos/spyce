import os
import sys
import itertools
import functools
from OpenGL.GLUT import *
from OpenGL.GL import *


class BufferObject(object):
    """OpenGL Buffer Object helper"""
    def __init__(self, data=None, flatten=False):
        """Create a new Buffer Object, optionally fill it (see `load()`)"""
        self.index = glGenBuffers(1)
        self.size = 0
        if data is not None:
            self.load(data, flatten)

    def bind(self):
        """Bind the Buffer Object to GL_ARRAY_BUFFER"""
        glBindBuffer(GL_ARRAY_BUFFER, self.index)

    def load(self, data, flatten=False):
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

    def draw(vertices, mode, texcoords=None, size=3):
        """Draw the Buffer Object (assumed to contain vertices)

        mode       passed to glDrawArrays() (GL_POINTS, GL_LINES, ...)
        texcoords  Buffer Object to use as texture coordinates
        size       passed to glVertexPointer (number of values per vertex)
        """
        # select vertex buffer object
        vertices.bind()
        glVertexPointer(size, GL_FLOAT, 0, None)
        glEnableClientState(GL_VERTEX_ARRAY)

        if texcoords is not None:
            # select texture coordinatess buffer object
            texcoords.bind()
            glTexCoordPointer(2, GL_FLOAT, 0, None)
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        # actually draw
        glDrawArrays(mode, 0, vertices.size // size)

        # disable buffer objects
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)


def make_shader(program, filename):
    """Compile and attach a shader of given type"""

    if filename.endswith(".vert"):
        type_ = GL_VERTEX_SHADER
    elif filename.endswith(".frag"):
        type_ = GL_FRAGMENT_SHADER
    else:
        raise Exception("Unable to determine type of shader '%s'" % filename)
    path = os.path.join("data", "shaders", filename)
    source = open(path).read()

    shader = glCreateShader(type_)
    glShaderSource(shader, source)
    glCompileShader(shader)
    error = glGetShaderInfoLog(shader)
    if error:
        # filename in messages for locating error
        error = error.decode().replace('0:', filename+':')
        raise SyntaxError('while compiling shaders\n' + error)
    glAttachShader(program, shader)


def make_program(*files):
    """Make a program from shader files"""
    program = glCreateProgram()
    for filename in files:
        make_shader(program, filename)
    glLinkProgram(program)

    # make `Texture0` refer to the first texture
    variable = glGetUniformLocation(program, b"Texture0")
    current_program = glGetIntegerv(GL_CURRENT_PROGRAM)
    glUseProgram(program)
    glUniform1i(variable, 0)
    glUseProgram(current_program)

    return program


def main_program(vertex_shader=None, fragment_shader=None):
    """Make a program from local shaders and fixed global shaders"""
    return make_program(
        "main.vert", "main.frag",  # global shader
        vertex_shader or "default.vert",  # local vertex shader
        fragment_shader or "default.frag",  # local fragment shader
    )


def glut_callback(f):
    """Wrap a GLUT callback method so that exceptions are not ignored"""
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except Exception as e:
            self.is_running = False
            glutLeaveMainLoop()

            # propagate exception with complete traceback
            if hasattr(e, "with_traceback"):  # Python 3
                raise e.with_traceback(sys.exc_info()[2])
            else:  # Python 2
                cmd = "raise type(e), e.args, sys.exc_info()[2]"
                exec(cmd, globals(), locals())
    return wrapper
