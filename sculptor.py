import numpy as np
from scipy.special import sph_harm

_sqrt2 = np.sqrt(2.)

def real_sph_harm(m, n, theta, phi):
	'''Real spherical harmonics based on complex ones from scipy.See
	   https://en.wikipedia.org/wiki/Spherical_harmonics#Real_form
	'''
	if m==0:
		return np.real(sph_harm(0, n, theta, phi))
	else:
		sign = 1. if m%2==0 else -1.
		if m<0:
			return sign*_sqrt2*np.imag(sph_harm(-m, n, theta, phi))
		elif m>0:
			return sign*_sqrt2*np.real(sph_harm(m, n, theta, phi))
	raise ValueError('Unacceptable value of m: {}'.format(m))

class Sculptor:
	def __init__(self, baseShape):
		self.shape = baseShape

	def getShape(self):
		return self.shape

	def renderShape(self, outfile, **kwargs):
		self.shape.renderSceneSpherical(outfile, **kwargs)

	def upscaleShape(self):
		self.shape.upscale()

	def adaptiveUpscale(self, angularFeatureSize, margin=2.):
		while margin*self.shape.getMinAngularFeatureSize() > angularFeatureSize:
			self.upscaleShape()

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

	def perturbWithSphericalHarmonic(self, magnitude, m, n, adaptiveUpscale=True, upscaleMargin=2.):
		'''Magnitude is absolute, not relative'''
		if adaptiveUpscale:
			shAngularFeatureSize = min(np.pi/(n-np.abs(m)+1), 2*np.pi if m==0 else np.pi/np.abs(m)) # ...they vanish are l-m parallels of latitude and 2m meridians...
			                                                                   # http://mathworld.wolfram.com/TesseralHarmonic.html
			self.adaptiveUpscale(shAngularFeatureSize, margin=upscaleMargin)
		def scaleVertexAppropriately(vertex):
			vmag = np.linalg.norm(vertex)
			vtheta = np.arccos(vertex[2]/vmag)
			vphi = np.arctan(vertex[1]/vmag)
			newmag = 1. + magnitude*real_sph_harm(m, n, vphi, vtheta)/vmag # the coordinates are swapped because code follows physical (ISO) convention while scikit follows mathematical convention
#			print('old mag = {}, new mag = {}'.format(vmag, vmag*newmag))
			return tuple( v*newmag for v in vertex )
		self.applyShaperFunction(scaleVertexAppropriately)
