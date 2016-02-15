#version 110

uniform bool picking_enabled;
uniform int picking_name;

void picking() {
    // branching on a uniform should be okay for now
    if (picking_enabled) {
        // picking is rare enough that we can just branch
        if (gl_FragColor.a != 0.) {
            gl_FragColor = vec4(float(picking_name)/255., 0., 0., 1.);
        }
    }
}
