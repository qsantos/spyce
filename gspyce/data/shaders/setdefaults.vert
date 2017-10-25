#version 110

uniform mat4 model_view_projection_matrix;
uniform mat4 model_view_matrix;

void setdefaults() {
    gl_TexCoord[0] = gl_MultiTexCoord0;
    gl_Position = model_view_projection_matrix * gl_Vertex;
    gl_FrontColor = gl_Color;
}
