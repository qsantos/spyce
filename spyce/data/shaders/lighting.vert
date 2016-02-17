#version 110

varying vec3 lighting_vertex;
varying vec3 lighting_normal;

void lighting() {
    lighting_vertex = vec3(gl_ModelViewMatrix * gl_Vertex);
    lighting_normal = normalize(gl_NormalMatrix * gl_Normal);
}
