#version 110

uniform samplerCube cubemap_texture;
varying vec3 cubemap_dir;

void cubemap() {
    gl_FragColor = gl_Color * textureCube(cubemap_texture, cubemap_dir);
}
