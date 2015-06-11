/* To use this in a Pytohn script, run:
$ gcc std=c99 -shared -fPIC elements.c -o elements.so

Then, use:

import ctypes
lib = ctypes.CDLL("./elements.so")
def elements_from_state(mu, position, velocity):
	mu = ctypes.c_double(mu)
	position = (ctypes.c_double*3)(*position)
	velocity = (ctypes.c_double*3)(*velocity)
	elements = (ctypes.c_double*6)()
	lib.elements_from_state(mu, position, velocity, elements)
	return elements
*/

#include <math.h>

#define M_PI 3.14159265358979323846

static inline double min(double a, double b)
{
	return a < b ? a : b;
}

static inline double max(double a, double b)
{
	return a > b ? a : b;
}

static inline double dot(const double* u, const double* v)
{
	/* Dot product of vectors */
	return u[0]*v[0] + u[1]*v[1] + u[2]*v[2];
}

static inline double norm(const double* v)
{
	/* Norm of a vector */
	return sqrt(dot(v, v));
}

static inline void cross(double* r, const double* u, const double* v)
{
	/* Cross product of vectors */
	r[0] = u[1]*v[2] - u[2]*v[1];
	r[1] = u[2]*v[0] - u[0]*v[2];
	r[2] = u[0]*v[1] - u[1]*v[0];
}

static inline double angle(const double* u, const double* v)
{
	/* Angle formed by two vectors */
	double r = dot(u, v) / norm(u) / norm(v);
	r = max(-1., min(r, 1.));
	return acos(r);
}

static inline double oriented_angle(const double* u, const double* v, const double* n)
{
	/* Angle formed by two vectors */
	double geometric_angle = angle(u, v);
	double c[3];
	cross(c, u, v);
	return dot(n, c) < 0. ? -geometric_angle : geometric_angle;
}

struct elements
{
	double periapsis;
	double eccentricity;
	double inclination;
	double longitude_of_ascending_node;
	double argument_of_periapsis;
	double epoch;
	double mean_anomaly_at_epoch;
};

void elements_from_state(double mu, double* position, double* velocity, double epoch, struct elements* ret)
{
	double distance = norm(position);
	double speed = norm(velocity);

	const double x_axis[3] = {1., 0., 0.};
	const double z_axis[3] = {0., 0., 1.};

	double orbital_plane_normal_vector[3];
	cross(orbital_plane_normal_vector, position, velocity);

	// eccentricity
	double rv = dot(position, velocity);
	double speed2 = speed*speed;
	double eccentricity_vector[3];
	for (int i = 0; i < 3; i++)
	{
		eccentricity_vector[i] = (speed2 * position[i] - rv*velocity[i]) / mu - position[i] / distance;
	}
	double eccentricity = norm(eccentricity_vector);

	// periapsis
	// from r(t) = 1 / mu * h / (1 + e cos t)
	double specific_angular_momentum = norm(orbital_plane_normal_vector);
	double periapsis = specific_angular_momentum*specific_angular_momentum / mu / (1 + eccentricity);
	const double* periapsis_dir = eccentricity != 0. ? eccentricity_vector : x_axis;

	// inclination
	double inclination = angle(orbital_plane_normal_vector, z_axis);

	// direction of the ascending node
	double ascend_node_dir[3] = {1., 0., 0.};
	if (inclination != 0. && inclination != M_PI)
		cross(ascend_node_dir, z_axis, orbital_plane_normal_vector);

	// longitude of ascending node
	double longitude_of_ascending_node = angle(x_axis, ascend_node_dir);
	if (orbital_plane_normal_vector[0] < 0.)
		longitude_of_ascending_node = - longitude_of_ascending_node;

	double argument_of_periapsis = oriented_angle(ascend_node_dir, periapsis_dir, orbital_plane_normal_vector);
	double true_anomaly_at_epoch = oriented_angle(periapsis_dir, position, orbital_plane_normal_vector);

	// mean anomaly from true anomaly
	double v = true_anomaly_at_epoch;
	double M;
	if (eccentricity < 1.)  // circular or elliptic orbit
	{
		double x = sqrt(1.+eccentricity)*cos(v/2.);
		double y = sqrt(1.-eccentricity)*sin(v/2.);
		double E = 2. * atan2(y, x);
		M = E - eccentricity * sin(E);
	}
	else if (eccentricity == 1.)  // parabolic trajectory
	{
		M = 0.;
	}
	else  // hyperbolic trajectory
	{
		double x = sqrt(eccentricity+1.)*cos(v/2.);
		double y = sqrt(eccentricity-1.)*sin(v/2.);
		double ratio = y / x;
		double E;
		if (fabs(ratio) <= 1.)
			E = 2. * atanh(ratio);
		else
			E = copysign(INFINITY, ratio);
		M = eccentricity * sinh(E) - E;
	}
	double mean_anomaly_at_epoch = M;

	*ret = (struct elements)
	{
		periapsis,
		eccentricity,
		inclination,
		longitude_of_ascending_node,
		argument_of_periapsis,
		epoch,
		mean_anomaly_at_epoch,
	};
}
