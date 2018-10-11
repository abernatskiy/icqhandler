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
    the orbits (in [0, 2*pi)). Those three values are sampled uniformly and saved to asteroid{}/lightSourcePos.txt as columns. One light position is
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
degreeDecay = 0.2

# Geometry generator
# distances = [ 1000, 500, 250, 150, 100, 50 ]
distances = [ 500, 100 ]
numRotationsPerAsteroid = 1
numPhasesPerAsteroid = 4

# Rendering
renderWidth = 300
renderHeight = 300

##### END OF CONFIGURATION #####

# Useful functions

asteroidNumber = 0

def sampleAnAsteroid():
	global asteroidNumber
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
		mag = baseRadius*np.random.beta(a=1, b=1 if m==0 else n*np.abs(m))
		scu.perturbWithSphericalHarmonic(mag, m, n, upscaleMargin=resolutionMargin)

	return scu.getShape()

# The generator itself

np.random.seed(randomSeed)

workdir = getcwd()

asteroidShapes = [ sampleAnAsteroid() for _ in range(numAsteroids) ]
for id, astSh in enumerate(asteroidShapes):
	astDir = join(workdir, 'asteroid{}'.format(id))
	makedirs(astDir)
	astSh.writeICQ(join(astDir, 'icq.txt'))
