uniform sampler2D Texture0;

uniform bool pick_enabled;
uniform int pick_name;

void shader();

void main()
{
	// default color
	vec4 texColor = texture2D(Texture0, gl_TexCoord[0].xy);
	gl_FragColor = gl_Color * texColor;

	shader();

	// picking
	if (pick_enabled)
	{
		// picking is rare enough that we can just branch
		if (gl_FragColor.a != 0.)
			gl_FragColor = vec4(float(pick_name)/255., 0., 0., 1.);
	}
}
