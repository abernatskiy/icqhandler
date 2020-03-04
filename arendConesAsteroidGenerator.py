from pathlib import Path
import numpy as np

import icq, sculptor

class ArendConesAsteroidGenerator:
	''' A class for sampling synthetic asteroid shapes using Arend's
	    spherical cones perturbation.

	    Asteroid sampling procedure:
	    1. An sculptable shape (ICQ) is generated as a sphere of unit radius. The
	       resolution is increased baseResolution times. In ICQs that bring Q to
	       2**baseResolution.
	    2. numCones Arend cones with fillets are sampled according to the
	       parameters of the constructor. Magnitudes decay according to the
	       magnitudeDecay parameter; the rest of the parameters are sampled
	       uniformly.
	    3. Perturbations are applied to the shape.

	    The function that performs the sampling
	    (ArendConesAsteroidGenerator.sampleAnAsteroid()) returns the shape and
	    the description of the cones used as perturbations. A method for saving
	    the said description is provided.

	    The class relies on the default NumPy RNG for random numbers.
	'''
	def __init__(self,
	             baseRadius = 15.,
	             baseResolution = 6, # for ICQShape, Q will be 2**baseResolution
	             numCones = 200,
	             radiusRange = [0.4, 1], # assuming a unit sphere. WARNING: avoid zero radii
	             magnitudesRange = [-0.33, 0.33],
	             magnitudesDecay = None): # the default is linear decay to 1/numCones if numCones>0 else 0
		self.baseRadius = baseRadius
		self.baseResolution = baseResolution
		self.numCones = numCones
		self.radiusRange = radiusRange
		self.magnitudesRange = magnitudesRange
		self.magnitudesDecay = magnitudesDecay if magnitudesDecay else (0 if numCones==0 else 1/numCones) # leaves 1/numCones for the last cone
		self.shapeDescriptionTitle = 'Overall asteroid shape produced by sequentially applying Arend cones with fillets'

	def sampleAnAsteroid(self):
		cubeicqpath = Path.home() / 'icqhandler' / 'shapes' / 'cube1.icq'
		ish = icq.ICQShape()
		ish.readICQ(cubeicqpath)

		scu = sculptor.Sculptor(ish)
		for _ in range(self.baseResolution):
			scu.upscaleShape()

		thetas, phis = self.sampleDirections(size=self.numCones)
		radii = self.radiusRange[0] + (self.radiusRange[1]-self.radiusRange[0])*np.random.random(size=self.numCones)
		magnitudes = self.magnitudesRange[0] + (self.magnitudesRange[1]-self.magnitudesRange[0])*np.random.random(size=self.numCones)
		magnitudes *= np.linspace(1., 1.-self.magnitudesDecay*(self.numCones-1), num=self.numCones)

		scu.shapeWithArendCones(thetas, phis, radii, magnitudes, baseRadius=self.baseRadius, coneType='linearWithFillet')

		shapeDescription = { 'thetas': thetas, 'phis': phis, 'radii': radii, 'magnitudes': magnitudes }

		return scu.getShape(), shapeDescription

	def sampleDirections(self, size=None):
		'''Uniformly samples directions in 3D space, as described by
		   spherical (ISO) angles theta, phi. Courtesy of Wolfram
		   http://mathworld.wolfram.com/SpherePointPicking.html
		'''
		theta = np.arccos(2.*np.random.random(size=size)-1.)
		phi = 2.*np.pi*np.random.random(size=size)
		return theta, phi

	def saveShapeDescription(self, shapeDescription, filePath):
		with open(filePath, 'w') as outFile:
			outFile.write('# ' + self.shapeDescriptionTitle + '\n')
			vars = list(shapeDescription.keys())
			numVars = len(shapeDescription[vars[0]])
			outFile.write('# ' + ' '.join(vars) + '\n')
			for i in range(numVars):
				outFile.write(' '.join([ str(shapeDescription[var][i]) for var in vars ]) + '\n')
