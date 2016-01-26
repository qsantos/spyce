varying float flogz;

void shader();

void main()
{
	// default settings
	gl_TexCoord[0] = gl_MultiTexCoord0;
	gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
	gl_FrontColor = gl_Color;

	shader();

	// fixed depth
	// http://outerra.blogspot.com/2013/07/logarithmic-depth-buffer-optimizations.html
	float farplane = 1e20;
	float Fcoef = 2.0 / log2(farplane + 1.0);
	gl_Position.z = log2(max(1e-6, 1.0 + gl_Position.w)) * Fcoef - 1.0;
	flogz = 1.0 + gl_Position.w;
}
