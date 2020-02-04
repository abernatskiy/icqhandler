#!/usr/bin/env python3

''' Creates a dataset of rendered synthetic asteroid shapes using Arend's
    spherical cones perturbation.

    Asteroid sampling procedure:
    1. An sculptable shape is generated as a sphere of unit radius. The
       resolution is increased baseResolution times, in Shape-class specific
       discrete steps.
    2. A spherical harmonic perturbation is sampled as follows:
       a. Degree n of the spherical harmonic perturbation is sampled from
          geometric distribution decaying at rate degreeDecay.
       b. Order m of the spherical harmonic perturbation is sampled from uniform
          distribution over {-n, -n+1, ..., n}
       c. Amplitude of the spherical harmonic perturbation is computed as
          r*baseRadius, where r is a random number from [0,1] sampled from beta
          distribution with alpha=1 and beta=1+magnitudeDecay*n*abs(m)
    3. Perturbation is applied to the shape. If the perturbation has fine
       features, resolution of the shape is increased until the feature size is
       at least resolutionMargin times larger than the largest triangle side in
       the shape's mesh.
    4. Steps 2 and 3 are repeated numPerturbationApplications times.
    5. Asteroid is assigned a unique numeric id. The shape is saved into
       asteroid<id>/icq.txt file.

    The dataset builder uses a reference frame attached to the asteroid, with
    the origin is at the center of the original sphere from which the asteroid
    was sculpted. That point plus the light source position and the camera
    position define the XY plane. X axis is the direction towards the light
    source, that is located at exactly (lightSourceDistance, 0, 0).

    Asteroid rotation axis is a uniformly sampled unit vector.
    numRotationsPerAsteroid rotation axes are sampled for each asteroid.
    Additionally, one camera approach angle is sampled uniformly from [0, 2pi)
    for each rotation axis. It is the angle between the radius-vectors of light
    source and camera.

    Rotation axes component and approach angles are saved to
    asteroid<id>/rotationAxes.txt and asteroid<id>/approachAngles.txt,
    correspondingly.

    Distance from camera to asteroid is variable and takes values from the list
    "distances". Distance to and brightness of the light source are constants
    (lightSourceDistance, lightSourceBrightness).

    Only white light and uniform grey asteroid surfaces are supported at the
    moment. Resulting images are in grayscale.

		For each asteroid, rotation axis (with corresponding approach angle) and
    distance to asteroid numPhases renders are made, corresponding to different
    phases of asteroid rotation. Asteroid is centered in all renders. Resolution
    is constant (parameters renderWidth, renderHeight). Renders are saved to
    asteroid<id>/rotation<rotAxisID>_distance<dist>_phase<phaseNum>.png.
    Rendering is multithreaded, max thread number is ruled by "cpus" variable.

'''

from pathlib import Path
import numpy as np
from multiprocessing.dummy import Pool as ThreadPool

import icq, sculptor

#####     CONFIGURATION    #####

# System
cpus = 8
randomSeed = 42

# Asteroid generator
numAsteroids = 1000
baseRadius = 15.
baseResolution = 6 # for ICQShape, Q will be 2**baseResolution unless cone
                   # with finer features is applied
#resolutionMargin = 4 # model resolution must be such that the smallest spherical
#                     # harmonic feature must be at least resolutionMargin times
#                     # larger than the smallest triangle
numCones = 200
radiusRange = [0.4, 1] # Assuming a unit sphere. WARNING: avoid zero radii
magnitudesRange = [-0.33, 0.33]
magnitudesDecay = 0 if numCones==0 else 1/numCones # leaves 1/numCones for the last cone

# Geometry generator
distances = [ 50 ]
numRotationsPerAsteroid = 1
numPhases = 8
lightSourceDistance = 1000
lightSourceBrightness = 2
approachAnglesRange = [ 0, 0 ]
#approachAnglesRange = [ np.pi/4, np.pi/4 ]
#approachAnglesRange = [ 0, 2.*np.pi ]

# Rendering
renderWidth = 600
renderHeight = 600
antialiasing = 0.01

##### END OF CONFIGURATION #####

# Useful functions

def sampleDirections(size=None):
	'''Uniformly samples directions in 3D space, as described by spherical (ISO) angles theta, phi. Courtesy of Wolfram http://mathworld.wolfram.com/SpherePointPicking.html'''
	theta = np.arccos(2.*np.random.random(size=size)-1.)
	phi = 2.*np.pi*np.random.random(size=size)
	return theta, phi

def sampleAnAsteroid():
	cubeicqpath = Path.home() / 'icqhandler' / 'shapes' / 'cube1.icq'
	ish = icq.ICQShape()
	ish.readICQ(cubeicqpath)

	scu = sculptor.Sculptor(ish)
	for _ in range(baseResolution):
		scu.upscaleShape()

	thetas, phis = sampleDirections(size=numCones)
	radii = radiusRange[0] + (radiusRange[1]-radiusRange[0])*np.random.random(size=numCones)
	magnitudes = magnitudesRange[0] + (magnitudesRange[1]-magnitudesRange[0])*np.random.random(size=numCones)
	magnitudes *= np.linspace(1., 1.-magnitudesDecay*(numCones-1), num=numCones)

	scu.shapeWithArendCones(thetas, phis, radii, magnitudes, baseRadius=baseRadius, coneType='linearWithFillet')

	return scu.getShape()

def sampleARotationAxis():
	'''Uniformly samples a rotation axis. Courtesy of Wolfram: http://mathworld.wolfram.com/SpherePointPicking.html'''
	u = -1. + 2.*np.random.rand()
	theta = 2.*np.pi*np.random.rand()
	fact = np.sqrt(1.-u*u)
	return fact*np.cos(theta), fact*np.sin(theta), u

def sampleAnApproachAngle(range=(0, 2.*np.pi)):
	minangle, maxangle = range
	return minangle + (maxangle-minangle)*np.random.rand()

def saveParams(rotations, filename):
	with open(filename, 'w') as outfile:
		try:
			for rot in rotations:
				outline = ' '.join(map(str, rot)) + '\n'
				outfile.write(outline)
		except TypeError:
			for rot in rotations:
				outline = str(rot)
				outfile.write(outline)

# The generator itself

np.random.seed(randomSeed)

workdir = Path.cwd()
phases = [ 2.*np.pi*float(i)/float(numPhases) for i in range(numPhases) ]
threadPool = ThreadPool(cpus if cpus<numPhases else numPhases)

for id in range(numAsteroids):
	astSh = sampleAnAsteroid()
	astDir = workdir / f'asteroid{id}'
	astDir.mkdir(parents=True, exist_ok=True)
	astSh.writeICQ(astDir / 'icq.txt')
	astSh.writeOBJ(astDir / 'shape.obj')

	arot = [ sampleARotationAxis() for _ in range(numRotationsPerAsteroid) ]
	saveParams(arot, workdir / f'asteroid{id}' / 'rotationAxes.txt')

	aan = [ sampleAnApproachAngle(range=approachAnglesRange) for _ in range(numRotationsPerAsteroid) ]
	saveParams(aan, workdir / f'asteroid{id}' / 'approachAngles.txt')

	for condID, astRotAxis, apprAngle in zip(range(len(arot)), arot, aan):
		for dist in distances:
			def renderPhase(phaseDesc):
				phid, ph = phaseDesc
				outfile = workdir / f'asteroid{id}' / f'condition{condID}_distance{dist}_phase{phid:04}.png'
				objColor = (0.5,0.5,0.5)
				lsColor = (lightSourceBrightness, lightSourceBrightness, lightSourceBrightness)
#				print('Calling renderer with cam at {}, light source at {}, phase {}'.format((dist,0,apprAngle), (lightSourceDistance,0,0), ph))
				astSh.renderSceneSpherical(outfile, cameraR=dist, cameraTheta=np.pi/2., cameraPhi=apprAngle,
				                                    rotationAxis=astRotAxis, rotationAngle=ph,
				                                    lightR=lightSourceDistance, lightTheta=np.pi/2, lightPhi=0,
				                                    lightColor=lsColor, backgroundColor=(0,0,0), objectColor=objColor,
				                                    width=renderWidth, height=renderHeight, antialiasing=antialiasing)
			threadPool.map(renderPhase, enumerate(phases))
