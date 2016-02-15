#version 110

uniform sampler2D Texture0;

void setdefaults() {
    vec4 texColor = texture2D(Texture0, gl_TexCoord[0].xy);
    gl_FragColor = gl_Color * texColor;
}
