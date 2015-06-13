#version 120 // needed for glPointCoord

uniform int pick_name;
uniform bool pick_enabled;

void main()
{
	// clip to circle
	vec2 pos = gl_PointCoord * gl_FragCoord.w;
	vec2 center = vec2(.5, .5);
	if (distance(pos, center) > .5)
	{
		gl_FragColor = vec4(0, 0, 0, 0);
		return;
	}

	// picking
	if (pick_enabled)
	{
		gl_FragColor = vec4(float(pick_name)/255., float(pick_name)/10., float(pick_name)/10., 1.);
		return;
	}

	gl_FragColor = gl_Color;
}
