''' A module for sampling spatial states of a system consisting of the Sun,
    a rotating asteroid and a small spacecraft approaching it.

    The frame of reference is attached to the asteroid, with
    the origin at the center of the original sphere from which the asteroid
    was sculpted. That point plus Sun position and spacecraft position
    position define the XY plane. X axis is the direction towards the Sun.

    Asteroid rotation axis is a uniformly sampled 3D unit vector.
    numConditions rotation axes ("conditions") are sampled for
    each asteroid. This models the situations when an asteroid is approached
    several times during its orbital period. However, perhaps more importantly,
    it enable producing several different percepts from a single shape,
    allowing to produce larger datasets when shape generation is a bottleneck.

    One camera approach angle is sampled uniformly from its range for each
    condition. It is the angle between the radius-vectors of light
    source and camera.

    These four number completely describe a condition. A function is provided
    to conveniently save lists of these.

    Modules relies on the default NumPy RNG for random numbers.
'''

import numpy as np

def _sampleARotationAxis():
	'''Uniformly samples an asteroid rotation axis. Courtesy of Wolfram:
	   http://mathworld.wolfram.com/SpherePointPicking.html
	'''
	u = -1. + 2.*np.random.rand()
	theta = 2.*np.pi*np.random.rand()
	fact = np.sqrt(1.-u*u)
	return fact*np.cos(theta), fact*np.sin(theta), u

def _sampleAnApproachAngle(approachAngleRange=[0, 2.*np.pi]):
	'''Uniformly samples the approach angle of the spacecraft from specified range'''
	minangle, maxangle = approachAngleRange
	return minangle + (maxangle-minangle)*np.random.rand()

def sampleConditions(numConditions, approachAngleRange=[0, 2.*np.pi]):
	'''Useful range values:
	     [0, 2.*np.pi] - all approach angles
	     [0, 0] - Sun deterministically behind the spacecraft
	     [np.pi/4, np.pi/4] - deterministically crescent asteroid
	'''
	return [ (_sampleARotationAxis(), _sampleAnApproachAngle(approachAngleRange=approachAngleRange)) for _ in range(numConditions) ]

def saveConditions(conditions, filename):
	with open(filename, 'w') as outfile:
		outfile.write('# RotAxis_x RotAxis_y RotAxis_z ApproachAngle\n')
		for axis, angle in conditions:
			x, y, z = axis
			vars = [x, y, z, angle]
			outfile.write(' '.join(map(str, vars)) + '\n')

class SpatialStatesIterator:
	'''An iterator over values of spatial parameters of the asteroid'''
	def __init__(self,
	             conditions, # a list of tuples (rotationAxis, approachAngle)
	             distances = [ 50 ],
	             numPhases = 8):
		self.conditions = conditions
		self.distances = distances
		self.phases = [ 2.*np.pi*float(i)/float(numPhases) for i in range(numPhases) ]

	def __iter__(self):
		for condID, condition in enumerate(self.conditions):
			axis, aangle = condition
			for dist in self.distances:
				for phid, phase in enumerate(self.phases):
					yield condID, axis, aangle, dist, phid, phase
