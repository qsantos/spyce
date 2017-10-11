#version 110

varying float flogz; // fixed depth

void logdepth() {
    // fixed depth
    // http://outerra.blogspot.com/2013/07/logarithmic-depth-buffer-optimizations.html
    float farplane = 1e20;
    float Fcoef = 2.0 / log2(farplane + 1.0);
    gl_Position.z = log2(max(1e-6, 1.0 + gl_Position.w)) * Fcoef - 1.0;
    flogz = 1.0 + gl_Position.w;
}
