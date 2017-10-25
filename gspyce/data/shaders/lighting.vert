#version 120

varying vec3 lighting_vertex;
varying vec3 lighting_normal;
uniform mat4 model_view_matrix;

void lighting() {
    lighting_vertex = vec3(model_view_matrix * gl_Vertex);
    lighting_normal = normalize(mat3(model_view_matrix) * gl_Normal);
}
