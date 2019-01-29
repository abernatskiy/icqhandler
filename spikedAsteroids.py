#!/usr/bin/env python3

#####     CONFIGURATION    #####

# System
cpus = 8
randomSeed = 42

# Asteroid generator
numAsteroids = 10
resolutionPower = 2
resolutionQ = int(2**resolutionPower)
numSpikes = 1
spikableFaces = [1, 4, 5] # render from [-R, R, -R]
spikeSize = 0.1

## Rendering
# distance = 4
# cameraX = ...
# cameraY = ...
# cameraZ = ...
# renderWidth = 300
# renderHeight = 300
# antialiasing = 0.01
# NOTE: no rendering here for now

##### END OF CONFIGURATION #####

import numpy as np
from os.path import expanduser, join
from os import getcwd, makedirs
from multiprocessing.dummy import Pool as ThreadPool

import icq

# Useful functions

def getFaceNormals(icqshape):
	'''Returns coordinates of middle vertices of each of the six ICQ faces'''
	normals = []
	for f in range(6):
		normals.append(icqshape.getVertex(f, resolutionQ//2, resolutionQ//2))
	return normals

def sampleAnAsteroid():
	global spikableFaces
	cubeicq = join(expanduser('~'), 'icqhandler', 'shapes', 'cube2.icq')
	ish = icq.ICQShape()
	ish.readICQ(cubeicq)
	ish.densifyTwofold(passes=resolutionPower)

	if spikableFaces is None:
		spikableFaces = [0, 1, 2, 3, 4, 5]
	faceNormals = getFaceNormals(ish)

	spikes = set()
	while True:
		f = np.random.choice(spikableFaces)
		i = np.random.randint(1, resolutionQ)
		j = np.random.randint(1, resolutionQ)
		spikes.add((f, i, j))
		if len(spikes)>=numSpikes:
			break

	for f, i, j in spikes:
		oldVertex = ish.getVertex(f, i, j)
		updatedVertex = tuple( x+spikeSize*y for x, y in zip(oldVertex, faceNormals[f]) )
		ish.setVertex(f, i, j, updatedVertex)

	return ish, spikes

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
workdir = getcwd()

asteroidParams = [ sampleAnAsteroid() for _ in range(numAsteroids) ]
for id, (astSh, sp) in enumerate(asteroidParams):
	astDir = join(workdir, 'shape_{}'.format(id))
	makedirs(astDir)
	saveParams(sp, join(astDir, 'logfile.txt'))
	astSh.writeICQ(join(astDir, 'SHAPE.txt'))
	astSh.writeOBJ(join(astDir, 'SHAPE.obj'))

#phases = [ 2.*np.pi*float(i)/float(numPhases) for i in range(numPhases) ]
#threadPool = ThreadPool(cpus if cpus<numPhases else numPhases)
#for astID, astSh, astRotAxes, apprAngles in zip(range(len(asteroidShapes)), asteroidShapes, asteroidRotationAxes, approachAngles):
#	for condID, astRotAxis, apprAngle in zip(range(len(astRotAxes)), astRotAxes, apprAngles):
#		for dist in distances:
#			def renderPhase(phaseDesc):
#				phid, ph = phaseDesc
#				outfile = join(workdir, 'asteroid{}'.format(astID), 'condition{}_distance{}_phase{}.png'.format(condID, dist, '%04d' % phid))
#				objColor = (0.5,0.5,0.5)
#				lsColor = (lightSourceBrightness, lightSourceBrightness, lightSourceBrightness)
##				print('Calling renderer with cam at {}, light source at {}, phase {}'.format((dist,0,apprAngle), (lightSourceDistance,0,0), ph))
#				astSh.renderSceneSpherical(outfile, cameraR=dist, cameraTheta=np.pi/2., cameraPhi=apprAngle,
#				                                    rotationAxis=astRotAxis, rotationAngle=ph,
#				                                    lightR=lightSourceDistance, lightTheta=np.pi/2, lightPhi=0,
#				                                    lightColor=lsColor, backgroundColor=(0,0,0), objectColor=objColor,
#				                                    width=renderWidth, height=renderHeight, antialiasing=antialiasing)
#			threadPool.map(renderPhase, enumerate(phases))
