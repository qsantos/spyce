#version 110

uniform sampler2D Texture0;

varying float flogz; // fixed depth

uniform bool pick_enabled;
uniform int pick_name;

void shader();

void main()
{
	// default color
	vec4 texColor = texture2D(Texture0, gl_TexCoord[0].xy);
	gl_FragColor = gl_Color * texColor;

	// fixed depth
	// http://outerra.blogspot.com/2013/07/logarithmic-depth-buffer-optimizations.html
	float farplane = 1e20;
	float Fcoef = 2.0 / log2(farplane + 1.0);
	float Fcoef_half = 0.5 * Fcoef;
	gl_FragDepth = log2(flogz) * Fcoef_half;

	shader();

	// picking
	if (pick_enabled)
	{
		// picking is rare enough that we can just branch
		if (gl_FragColor.a != 0.)
			gl_FragColor = vec4(float(pick_name)/255., 0., 0., 1.);
	}
}
