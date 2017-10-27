#version 110

attribute vec4 vertex;
attribute vec3 normal;
attribute vec2 texcoord;

varying vec3 cubemap_dir;

void cubemap() {
    cubemap_dir = normalize(vertex.xyz);
}
