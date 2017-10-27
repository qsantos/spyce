#version 110

uniform vec4 color;
uniform samplerCube cubemap_texture;
varying vec3 cubemap_dir;

void cubemap() {
    gl_FragColor = color * textureCube(cubemap_texture, cubemap_dir);
}
