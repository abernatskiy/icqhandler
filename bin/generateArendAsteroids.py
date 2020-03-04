#!/usr/bin/env python3

''' Creates a dataset of rendered synthetic asteroid shapes using Arend's
    spherical cones perturbation.

    Script generate numAsteroids asteroid shapes.
    Shape sampling procedure is described in arendConesAsteroidGenerator.py.
    For each shape, a folder asteroid<id> is made in the current directory.
    The directory is then populated with the following files:

      shape.icq - asteroid shape in ICQ format
      conditions.ssv - asteroid rotation axis + spacecraft approach angle
        combinations, with this version one per asteroid
      condition<cid>_distance<dist>_phase<phid>.png - asteroid renders,
        one for each combination of conditions, distance and phase

    Conditions generation and iteration over combinations are described in
    spatialState.py.

    Distance from camera to asteroid is variable and takes values from the list
    "distances". Distance to and brightness of the light source are constants
    (lightSourceDistance, lightSourceBrightness). Only white light and uniform
    grey asteroid surfaces are supported at the moment. Resulting images are in
    grayscale. Rendering is multithreaded, with number of threads governed by
    the cpus variable.
'''

from pathlib import Path
import numpy as np
from multiprocessing.dummy import Pool as ThreadPool

from arendConesAsteroidGenerator import ArendConesAsteroidGenerator
import spatialState

#####     CONFIGURATION    #####

# System
cpus = 1
randomSeed = 42

# Asteroid generator
numAsteroids = 1000

# Geometry generator
distances = [50]
numPhases = 8
approachAnglesRange = [0, 0]
#approachAnglesRange = [np.pi/4, np.pi/4]
#approachAnglesRange = [0, 2.*np.pi]

# Rendering
lightSourceDistance = 1000
lightSourceBrightness = 2
renderWidth = 600
renderHeight = 600
antialiasing = 0.01

##### END OF CONFIGURATION #####

if __name__=='__main__':
	np.random.seed(randomSeed)

	workdir = Path.cwd()
	astGen = ArendConesAsteroidGenerator(baseResolution=6)

	threadPool = ThreadPool(cpus)

	for id in range(numAsteroids):
		print(f'ast id {id}')

		astSh, shDesc = astGen.sampleAnAsteroid()
		astDir = workdir / f'asteroid{id:05}'
		astDir.mkdir(parents=True, exist_ok=True)
		astSh.writeICQ(astDir / 'shape.icq')
#		astSh.writeOBJ(astDir / 'shape.obj')
		astGen.saveShapeDescription(shDesc, astDir / 'shape_description.ssv')

		conditions = spatialState.sampleConditions(1, approachAngleRange=approachAnglesRange)
		spatialState.saveConditions(conditions, astDir / 'conditions.ssv')

		spatialStates = spatialState.SpatialStatesIterator(conditions, distances=distances, numPhases=numPhases)

		def renderPhase(ssDesc):
			condID, astRotAxis, apprAngle, dist, phid, ph = ssDesc
			outfile = astDir / f'condition{condID}_distance{dist}_phase{phid:04}.png'
			objColor = (0.5,0.5,0.5)
			lsColor = (lightSourceBrightness, lightSourceBrightness, lightSourceBrightness)
#			print(f'Calling renderer with cam at {(dist,0,apprAngle)}, light source at {(lightSourceDistance,0,0)}, phase {ph}')
			astSh.renderSceneSpherical(outfile, cameraR=dist, cameraTheta=np.pi/2., cameraPhi=apprAngle,
			                                    rotationAxis=astRotAxis, rotationAngle=ph,
			                                    lightR=lightSourceDistance, lightTheta=np.pi/2, lightPhi=0,
			                                    lightColor=lsColor, backgroundColor=(0,0,0), objectColor=objColor,
			                                    width=renderWidth, height=renderHeight, antialiasing=antialiasing)
		threadPool.map(renderPhase, spatialStates)
