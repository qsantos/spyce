#version 120  // mat3

attribute vec4 vertex;
attribute vec3 normal;
attribute vec2 texcoord;

varying vec3 lighting_vertex;
varying vec3 lighting_normal;
uniform mat4 model_view_matrix;

void lighting() {
    lighting_vertex = vec3(model_view_matrix * vertex);
    lighting_normal = normalize(mat3(model_view_matrix) * normal);
}
