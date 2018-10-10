import numpy as np
from scipy.special import sph_harm

class Sculptor:
	def __init__(self, baseShape):
		self.shape = baseShape

	def getShape(self):
		return self.shape

	def renderShape(self, outfile, **kwargs):
		self.shape.renderSceneSpherical(outfile, **kwargs)

	def upscaleShape(self):
		self.shape.upscale()

	def applyShaperFunction(self, shaperFunc):
		newVertices = []
		for v in self.shape.getVertices():
			newVertices.append(shaperFunc(v))
		self.shape.setVertices(newVertices)

	def rollIntoABall(self, radius=1.):
		def normalize(v):
			npv = np.array(v)
			return tuple(npv*radius/np.linalg.norm(npv))
		self.applyShaperFunction(normalize)

	def perturbWithSphericalHarmonic(self, magnitude, m, n):
		'''Magnitude is absolute, not relative'''
		def scaleVertexAppropriately(vertex):
			vmag = np.linalg.norm(vertex)
			vtheta = np.arccos(vertex[2]/vmag)
			vphi = np.arctan(vertex[1]/vmag)
			newmag = 1. + magnitude*np.real(sph_harm(m, n, vphi, vtheta))/vmag # the coordinates are swapped because code follows physical (ISO) convention while scikit follows mathematical convention
			return ( v*newmag for v in vertex )
		self.applyShaperFunction(scaleVertexAppropriately)
