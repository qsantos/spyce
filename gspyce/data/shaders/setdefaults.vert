#version 110

attribute vec4 vertex;
attribute vec3 normal;
attribute vec2 texcoord;

varying vec2 TexCoord;

uniform mat4 model_view_projection_matrix;
uniform mat4 model_view_matrix;
uniform vec4 color;

void setdefaults() {
    TexCoord = texcoord;
    gl_Position = model_view_projection_matrix * vertex;
    gl_FrontColor = color;
}
