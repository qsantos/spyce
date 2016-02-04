#version 120 // needed for gl_PointCoord

void shader()
{
	// clip to circle
	vec2 pos = gl_PointCoord * gl_FragCoord.z;
	vec2 center = vec2(.25, .25);
	float d = distance(pos, center);
	if (d > .25 || d < .2)
		gl_FragColor = vec4(0, 0, 0, 0);
}
