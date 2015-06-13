uniform int pick_name;
uniform bool pick_enabled;

void main()
{
	if (pick_enabled)
	{
		gl_FragColor = vec4(float(pick_name)/255., 0., 0., 1.);
		return;
	}

	gl_FragColor = gl_Color;
}
