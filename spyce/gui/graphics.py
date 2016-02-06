import os
import sys
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *


def make_vbo(vertices, vbo_index=None):
    """Return a VBO of the given vertices"""
    if vbo_index is None:
        vbo_index = glGenBuffers(1)
    data_buffer = (ctypes.c_float*len(vertices))(*vertices)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_index)
    glBufferData(GL_ARRAY_BUFFER, data_buffer, GL_STATIC_DRAW)
    return vbo_index


def draw_vbo(vbo_index, n_vertices):
    glBindBuffer(GL_ARRAY_BUFFER, vbo_index)
    glVertexPointer(3, GL_FLOAT, 0, None)
    glEnableClientState(GL_VERTEX_ARRAY)
    glDrawArrays(GL_LINE_STRIP, 0, n_vertices)
    glDisableClientState(GL_VERTEX_ARRAY)
    glBindBuffer(GL_ARRAY_BUFFER, 0)


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
    glProgramUniform1i(program, variable, 0)

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
