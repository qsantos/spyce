#version 110

varying vec3 lighting_vertex;
varying vec3 lighting_normal;

void lighting() {
    vec3 perceived_light = normalize(-lighting_vertex); // vector to eye position (0, 0, 0)
    vec3 incident_light = normalize(gl_LightSource[0].position.xyz - lighting_vertex);
    vec3 reflected_light = normalize(-reflect(incident_light, lighting_normal));

    // geometry-dependent values
    float component_ambient = 1.0;
    float component_diffuse = max(dot(lighting_normal, incident_light), 0.0);
    float component_specular = pow(max(dot(reflected_light, perceived_light), 0.0), 0.3 * gl_FrontMaterial.shininess);

    // light-dependent values
    vec4 light_ambient = gl_FrontLightProduct[0].ambient * component_ambient;
    vec4 light_diffuse = gl_FrontLightProduct[0].diffuse * component_diffuse;
    vec4 light_specular = gl_FrontLightProduct[0].specular * component_specular;

    // clamp values
    //light_ambient = clamp(light_ambient, 0.0, 1.0);  // already clamped
    light_diffuse = clamp(light_diffuse, 0.0, 1.0);
    light_specular = clamp(light_specular, 0.0, 1.0);

    gl_FragColor *= light_ambient + light_diffuse;
    gl_FragColor += light_specular;
}
