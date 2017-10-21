#version 110

varying vec3 cubemap_dir;

void cubemap() {
    cubemap_dir = normalize(gl_Vertex.xyz);
}
