#version 110

uniform vec3 lighting_source;
varying vec3 lighting_vertex;
varying vec3 lighting_normal;

// lighting
const vec4 light_ambient = vec4(1., 1., 1., 1.);
const vec4 light_diffuse = vec4(3., 3., 3., 1.);
const vec4 light_specular = vec4(1., 1., 1., 1.);
// materials
const vec4 material_ambient = vec4(.2, .2, .2, 1.);  // fixed pipeline default
const vec4 material_diffuse = vec4(.8, .8, .8, 1.);  // fixed pipeline default
const vec4 material_specular = vec4(.3, .3, .3, 1.);
const float shininess = 16.;

const vec4 product_ambient = light_ambient * material_ambient;
const vec4 product_diffuse = light_diffuse * material_diffuse;
const vec4 product_specular = light_specular * material_specular;

void lighting() {
    vec3 perceived_light = normalize(-lighting_vertex); // vector to eye position (0, 0, 0)
    vec3 incident_light = normalize(lighting_source - lighting_vertex);
    vec3 reflected_light = normalize(-reflect(incident_light, lighting_normal));

    // geometry-dependent values
    float component_ambient = 1.0;
    float component_diffuse = max(dot(lighting_normal, incident_light), 0.0);
    float component_specular = pow(max(dot(reflected_light, perceived_light), 0.0), 0.3 * shininess);

    // light-dependent values
    vec4 light_ambient = product_ambient * component_ambient;
    vec4 light_diffuse = product_diffuse * component_diffuse;
    vec4 light_specular = product_specular * component_specular;

    // clamp values
    //light_ambient = clamp(light_ambient, 0.0, 1.0);  // already clamped
    light_diffuse = clamp(light_diffuse, 0.0, 1.0);
    light_specular = clamp(light_specular, 0.0, 1.0);

    gl_FragColor *= light_ambient + light_diffuse;
    gl_FragColor += light_specular;
}
