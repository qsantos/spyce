from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


def make_vbo(vertices):
    """Return a VBO of the given vertices"""
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


def make_shader(program, type_, filename):
    """Compile and attach a shader of given type"""
    if filename is None:
        return

    shader = glCreateShader(type_)
    glShaderSource(shader, open(filename).read())
    glCompileShader(shader)
    error = glGetShaderInfoLog(shader)
    if error:
        raise SyntaxError(error)
    glAttachShader(program, shader)


def make_program(vertex_file=None, fragment_file=None):
    """Make a program from shader files"""
    program = glCreateProgram()
    make_shader(program, GL_VERTEX_SHADER, vertex_file)
    make_shader(program, GL_FRAGMENT_SHADER, fragment_file)
    glLinkProgram(program)
    return program
