#!/usr/bin/env python3

''' Creates a dataset of rendered asteroid shapes using the spherical harmonics approximation

    Asteroid sampling procedure:
    1. An sculptable shape is generated as a sphere of radius baseRadius. The resolution is increased baseResolution times.
    2. A spherical harmonic perturbation is sampled as follows:
       a. Degree n of the spherical harmonic perturbation is sampled from geometric distribution decaying at rate degreeDecay.
       b. Order m of the spherical harmonic perturbation is sampled from uniform distribution over [-n, -n+1, ..., n]
       c. Amplitude of the spherical harmonic perturbation is computed as r*baseRadius, where r is a random number from [0,1] sampled from beta distribution with a=1 and b=1+n*abs(m)
    3. Perturbation is applied to the shape. If the perturbation has fine features, resolution of the shape is increased accordingly.
    4. Steps 2 and 3 are repeated numPerturbationApplications times.
    5. Asteroid is assigned a unique numeric id. The shape is saved into asteroid{}/icq.txt file.

    Asteroid rotation direction is expressed as inclination and longitude of ascending node of the spacecraft's orbit in asteroid's reference frame.
    Those parameters are uniformly sampled from [0, pi/2) and [0, 2*pi), correspondingly. More than one rotation per asteroid can be sampled (variable numRotationsPerAsteroid).
		Rotation parameters are saved into asteroid{}/rotations.txt, in which each line is inclination, then space, then longitude of ascending node.

    Light source is assumed to be at rest in spacecraft's reference frame. Hence, in the asteroid reference frame it follows a circular orbit with the
    same period as the spacecraft. Light position is therefore described by the same two parameters as the asteroid rotation, plus phase offset between
    the orbits (in [0, 2*pi)). Those three values are sampled uniformly and saved to asteroid{}/lightSourcePositions.txt as columns. One light position is
    sampled for every rotation.

    Distance from spacecraft to asteroid is variable and takes values from the list "distances". Distance to and brightness of the light source are
    constants (lightSourceDistance, lightSourceBrightness).

    Only white light and white asteroid surfaces are supported at the moment. Resulting asteroids are in grayscale.

		For each asteroid, rotation (with corresponding light source position) and distance to asteroid numPhases renders are made, corresponding to different
    phases of asteroid rotation. Asteroid is centered in all renders. Resolution is constant (parameters renderWidth, renderHeight). Renders are saved to
    asteroid{}/rotation{}_distance{}_phase{}.png (format asteroid id, rotation id, distance, phase in radians). Rendering is multithreaded.

'''

import numpy as np
from os.path import expanduser, join
from os import getcwd, makedirs
from multiprocessing.dummy import Pool as ThreadPool

import icq, sculptor

#####     CONFIGURATION    #####

# System
cpus = 8
randomSeed = 42

# Asteroid generator
#asteroids = 10
numAsteroids = 2
baseRadius = 15.
baseResolution = 4 # Q will be 2**4 unless a spherical harmonic with finer features is applied
resolutionMargin = 4 # model resolution must be such that the smallest spherical harmonic feature must be at least resolutionMargin times larger than the smallest triangle
numPerturbationApplications = 10
degreeDecay = 0.15
magnitudeDecay = 0.5

# Geometry generator
# distances = [ 1000, 500, 250, 150, 100, 50 ]
distances = [ 100 ]
numRotationsPerAsteroid = 1
numPhases = 15
lightSourceDistance = 1000
lightSourceBrightness = 3

# Rendering
renderWidth = 300
renderHeight = 300
antialiasing = 0.01

##### END OF CONFIGURATION #####

# Useful functions

def sampleAnAsteroid():
	cubeicq = join(expanduser('~'), 'icqhandler', 'shapes', 'cube2.icq')
	ish = icq.ICQShape()
	ish.readICQ(cubeicq)

	scu = sculptor.Sculptor(ish)
	for _ in range(baseResolution):
		scu.upscaleShape()
	scu.rollIntoABall(radius=baseRadius)

	for _ in range(numPerturbationApplications):
		n = np.random.geometric(degreeDecay)
		m = np.random.randint(-n, n+1)
		beta = 1. + magnitudeDecay*n*np.abs(m)
		mag = baseRadius*np.random.beta(a=1, b=beta)
		scu.perturbWithSphericalHarmonic(mag, m, n, upscaleMargin=resolutionMargin)

	return scu.getShape()

def sampleARotation():
	return 0.5*np.pi*np.random.rand(), 2.*np.pi*np.random.rand()

def sampleARotationWithPhaseOffset():
	return 0.5*np.pi*np.random.rand(), 2.*np.pi*np.random.rand(), 2.*np.pi*np.random.rand()

def saveRotations(rotations, filename):
	with open(filename, 'w') as outfile:
		for rot in rotations:
			outfile.write(' '.join(map(str, rot)) + '\n')

class CircularOrbit:
	'''Computes spherical coordinates theta and phi based on orbital phase,
     inclination i, longitude of ascending node omega and phaseOffset.
  '''
	def __init__(self, i, omega, phaseOffset=0.):
		'''i stands for inclination, omega for longitude of ascending node'''
		self.i = i
		self.omega = omega
		self.phaseOffset = phaseOffset
	def getSphericalCoordinates(self, phase):
		return self.i*np.cos(phase+self.phaseOffset), (self.omega+phase+self.phaseOffset+np.pi/2) % (2.*np.pi)

# The generator itself

np.random.seed(randomSeed)

workdir = getcwd()

asteroidShapes = [ sampleAnAsteroid() for _ in range(numAsteroids) ]
for id, astSh in enumerate(asteroidShapes):
	astDir = join(workdir, 'asteroid{}'.format(id))
	makedirs(astDir)
	astSh.writeICQ(join(astDir, 'icq.txt'))

asteroidRotations = [ [ sampleARotation() for _ in range(numRotationsPerAsteroid) ] for _ in range(numAsteroids) ]
for id, arot in enumerate(asteroidRotations):
	saveRotations(arot, join(workdir, 'asteroid{}/rotations.txt'.format(id)))

lightSourcePositions = [ [ sampleARotationWithPhaseOffset() for _ in range(numRotationsPerAsteroid) ] for _ in range(numAsteroids) ]
for id, lpos in enumerate(lightSourcePositions):
	saveRotations(lpos, join(workdir, 'asteroid{}/lightSourcePositions.txt'.format(id)))

phases = [ 2.*np.pi*float(i)/float(numPhases) for i in range(numPhases) ]
for astID, astSh, astRots, lsPoss in zip(range(len(asteroidShapes)), asteroidShapes, asteroidRotations, lightSourcePositions):
	for rotID, astRot, lsPos in zip(range(len(astRots)), astRots, lsPoss):
		camOrbit = CircularOrbit(*astRot)
		lsOrbit = CircularOrbit(lsPos[0], lsPos[1], phaseOffset=lsPos[2])
		for dist in distances:
			for phid, ph in enumerate(phases):
				outfile = join(workdir, 'asteroid{}'.format(astID), 'rotation{}_distance{}_phase{}.png'.format(rotID, dist, phid))
				camr = dist
				camth, camph = camOrbit.getSphericalCoordinates(ph)
				lsr = lightSourceDistance
				lsth, lsph = lsOrbit.getSphericalCoordinates(ph)
				lsColor = (lightSourceBrightness, lightSourceBrightness, lightSourceBrightness)
				astSh.renderSceneSpherical(outfile, cameraR=camr, cameraTheta=camth, cameraPhi=camph,
				                                    lightR=lsr, lightTheta=lsth, lightPhi=lsph,
				                                    lightColor=lsColor, backgroundColor=(0,0,0), objectColor=(0.5,0.5,0.5),
				                                    width=renderWidth, height=renderHeight, antialiasing=antialiasing)
