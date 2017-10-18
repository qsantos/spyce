#include <Python.h>

#include "orbit.c"

static PyObject* wrapper_elements_from_state(PyObject* self, PyObject* args)
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

static PyObject* wrapper_eccentric_anomaly_at_mean_anomaly(PyObject* self, PyObject* args)
{
	(void) self;

	double eccentricity;
	double mean_anomaly;

	if (!PyArg_ParseTuple(args, "dd", &eccentricity, &mean_anomaly))
		return NULL;

	double ret = eccentric_anomaly_at_mean_anomaly(eccentricity, mean_anomaly);
	return Py_BuildValue("d", ret);
}

static PyObject* wrapper_eccentric_anomaly_at_true_anomaly(PyObject* self, PyObject* args)
{
	(void) self;

	double eccentricity;
	double true_anomaly;

	if (!PyArg_ParseTuple(args, "dd", &eccentricity, &true_anomaly))
		return NULL;

	double ret = eccentric_anomaly_at_true_anomaly(eccentricity, true_anomaly);
	return Py_BuildValue("d", ret);
}

static PyObject* wrapper_true_anomaly_at_mean_anomaly(PyObject* self, PyObject* args)
{
	(void) self;

	double eccentricity;
	double mean_anomaly;

	if (!PyArg_ParseTuple(args, "dd", &eccentricity, &mean_anomaly))
		return NULL;

	double ret = true_anomaly_at_mean_anomaly(eccentricity, mean_anomaly);
	return Py_BuildValue("d", ret);
}

static PyObject* wrapper_true_anomaly_at_eccentric_anomaly(PyObject* self, PyObject* args)
{
	(void) self;

	double eccentricity;
	double eccentric_anomaly;

	if (!PyArg_ParseTuple(args, "dd", &eccentricity, &eccentric_anomaly))
		return NULL;

	double ret = true_anomaly_at_eccentric_anomaly(eccentricity, eccentric_anomaly);
	return Py_BuildValue("d", ret);
}



static PyMethodDef methods[] =
{
	{
        "elements_from_state", wrapper_elements_from_state, METH_VARARGS,
        "Compute orbital elements from given state vectors",
    },
	{
        "eccentric_anomaly_at_mean_anomaly",
        wrapper_eccentric_anomaly_at_mean_anomaly, METH_VARARGS,
        "Computes the eccentric anomaly at a given mean anomaly",
    },
	{
        "eccentric_anomaly_at_true_anomaly",
        wrapper_eccentric_anomaly_at_true_anomaly, METH_VARARGS,
        "Computes the eccentric anomaly at a given true anomaly",
    },
	{
        "true_anomaly_at_mean_anomaly",
        wrapper_true_anomaly_at_mean_anomaly, METH_VARARGS,
        "Computes the true anomaly at a given mean anomaly",
    },
	{
        "true_anomaly_at_eccentric_anomaly",
        wrapper_true_anomaly_at_eccentric_anomaly, METH_VARARGS,
        "Computes the true anomaly at a given eccentric anomaly",
    },
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
	PyModuleDef_HEAD_INIT, "Common functions for orbits",
	NULL, 0, methods,
	NULL, NULL, NULL, NULL,
};

PyMODINIT_FUNC PyInit_orbit()
{
	return PyModule_Create(&moduledef);
}
