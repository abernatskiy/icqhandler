import numpy as np
from scipy.special import sph_harm

_sqrt2 = np.sqrt(2.)

def filletCone(rs, magnitude, mainRadius, sideFilletRadius, topFilletRadius=0.):
	rho = sideFilletRadius
	R = mainRadius
	m = magnitude
	d1 = rho*m*R / (R**2 + m**2 + R*np.sqrt(R**2+m**2))
	d2 = rho*m / (R + np.sqrt(R**2+m**2))
	if topFilletRadius == 0.:
		return np.piecewise(rs, [rs<R-d1, rs>R+d2, np.logical_and(rs>=R-d1, rs<=R+d2)],
		                    [lambda r : m*(1-r/R),
		                     lambda r : 0,
		                     lambda r : rho - np.sqrt(rho**2 - (r-R-d2)**2)])
	else:
		rhop = topFilletRadius
		d3 = m*rhop/np.sqrt(R**2 + m**2)
		fd = rhop*np.sqrt(1 + (m/R)**2)
		return np.piecewise(rs, [rs<d3, np.logical_and(rs>=d3, rs<R-d1), rs>R+d2, np.logical_and(rs>=R-d1, rs<=R+d2)],
		                    [lambda r : m - fd + np.sqrt(rhop**2 - r**2),
		                     lambda r : m*(1-r/R),
		                     lambda r : 0,
		                     lambda r : rho - np.sqrt(rho**2 - (r-R-d2)**2)])

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

	def shapeWithArendCones(self, thetas, phis, radii, magnitudes, baseRadius=1., coneType='linear'):
		self.rollIntoABall(radius=1.)
		verts = self.shape.getVertices()
		numVerts = len(verts)
		numCones = len(thetas)

		npverts = np.array(verts, dtype=np.float)
		weights = np.ones(numVerts)
		for nc in range(numCones):
			dirvec = np.array([np.sin(thetas[nc])*np.cos(phis[nc]), np.sin(thetas[nc])*np.sin(phis[nc]), np.cos(thetas[nc])], dtype=np.float)

			if coneType == 'gaussian':
				pows = (npverts.dot(dirvec)-1.) / radii[nc]**2
				weights += magnitudes[nc]*np.exp(pows)
			elif coneType == 'linear' or coneType == 'quadratic' or coneType == 'linearWithFillet':
				distances = np.sqrt(2.*(1.-npverts.dot(dirvec)))
				wholeSphereCone = radii[nc]-distances
				wholeSphereCone = wholeSphereCone.clip(min=0.)
				if coneType == 'linear':
					weights += magnitudes[nc]*wholeSphereCone # the original Arend cones
				elif coneType == 'linearWithFillet':
					if magnitudes[nc]>0:
						weights += filletCone(distances, magnitudes[nc]*radii[nc], radii[nc], 1.*radii[nc], topFilletRadius=0.5*radii[nc])
					else:
						weights += -1.*filletCone(distances, -1.*magnitudes[nc]*radii[nc], radii[nc], 1.*radii[nc], topFilletRadius=radii[nc])
				else:
					weights += magnitudes[nc]*wholeSphereCone**2/radii[nc]**2
			else:
				raise ValueError(f'sculptor.shapeWithArendCones: unknown cone type {coneType}')

		newVertices = []
		for i in range(numVerts):
			newVertices.append([ baseRadius*weights[i]*x for x in verts[i] ])
		self.shape.setVertices(newVertices)
