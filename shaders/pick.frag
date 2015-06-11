uniform int name;

void main()
{
	gl_FragColor = vec4(float(name)/255., 0., 0., 1.);
}
