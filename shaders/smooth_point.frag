#version 120 // needed for gl_PointCoord

void shader()
{
	// clip to circle
	vec2 pos = gl_PointCoord * gl_FragCoord.w;
	vec2 center = vec2(.5, .5);
	if (distance(pos, center) > .5)
		gl_FragColor = vec4(0, 0, 0, 0);
}
