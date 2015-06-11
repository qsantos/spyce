#include <Python.h>

#include "elements.c"

static PyObject* wrapper(PyObject* self, PyObject* args)
{
	(void) self;

	double mu;
	double position[3];
	double velocity[3];
	double epoch;

	if (!PyArg_ParseTuple(args, "d(ddd)(ddd)d", &mu,
		&position[0], &position[1], &position[2],
		&velocity[0], &velocity[1], &velocity[2],
		&epoch
	))
		return NULL;

	struct elements ret;
	elements_from_state(mu, position, velocity, epoch, &ret);

	return Py_BuildValue("ddddddd",
		ret.periapsis,
		ret.eccentricity,
		ret.inclination,
		ret.longitude_of_ascending_node,
		ret.argument_of_periapsis,
		ret.epoch,
		ret.mean_anomaly_at_epoch
	);
}

static PyMethodDef methods[] =
{
	{"elements_from_state", wrapper, METH_VARARGS, "Find orbital elements from position and velocity"},
	{NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef moduledef = {
	PyModuleDef_HEAD_INIT, "hello",
	NULL, 0, methods,
	NULL, NULL, NULL, NULL,
};

PyMODINIT_FUNC PyInit_elements_py3()
{
	return PyModule_Create(&moduledef);
}
#else
PyMODINIT_FUNC initelements_py2()
{
	Py_InitModule("elements_py2", methods);
}
#endif
