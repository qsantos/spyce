#version 110

varying vec2 TexCoord;
uniform sampler2D Texture0;

void setdefaults() {
    vec4 texColor = texture2D(Texture0, TexCoord);
    gl_FragColor = gl_Color * texColor;
}
