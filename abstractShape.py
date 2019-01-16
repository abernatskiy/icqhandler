from abc import ABC, abstractmethod
import vapory as vpr
import numpy as np
import threading

def rotation_matrix(axis, theta):
	'''Return the rotation matrix associated with counterclockwise rotation about
	   the given axis by theta radians.
	   Courtesy of unutbu (stackoverflow.com/questions/6802577/)
	'''
	axis = np.asarray(axis)
	axis = axis / np.linalg.norm(axis)
	a = np.cos(theta / 2.0)
	b, c, d = -axis * np.sin(theta / 2.0)
	aa, bb, cc, dd = a * a, b * b, c * c, d * d
	bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
	return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
	                 [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
	                 [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

class AbstractShape(ABC):
	'''Abstract base class for handling shapes'''
	@abstractmethod
	def getVertices(self):
		'''Returns vertices of the shape in form of flat (one-dimensional) iterable over coordinate triples.'''
		pass

	@abstractmethod
	def setVertices(self, newVertices):
		'''Sets the flat list of vertices to a new value. Note that the vertices will be connected to form triangles in the same way as before.'''
		pass

	@abstractmethod
	def getTriangleIndices(self):
		'''Returns triangles of the shape in form of triples of indices of vertices in the list returned by getVertices().'''
		pass

	@abstractmethod
	def getMinAngularFeatureSize(self):
		pass

	@abstractmethod
	def upscale(self):
		pass

	def getScene(self, *, cameraLocation=[100,100,50], cameraTarget=[0,0,0], lightLocation=[100,100,100],
		                    lightColor=[1,1,1], backgroundColor=[0,0,0], objectColor=[0.5,0.5,0.5],
		                    rotationAxis=None, rotationAngle=None):
		# POVRay uses a left-handed coordinate system, so we have to flip the Z axis on all geometric vectors
		cameraLocation[2] = -cameraLocation[2]
		cameraTarget[2] = -cameraTarget[2]
		lightLocation[2] = -lightLocation[2]

		vertices = self.getVertices()

		if rotationAxis and rotationAngle:
			rotationMatrix = rotation_matrix(rotationAxis, rotationAngle)
			# Z axis must be flipped in vertex coords as well, before the transform
			vertexArgs = [ len(vertices) ] + [ list(np.dot(rotationMatrix, np.array([x,y,-z]))) for x,y,z in vertices ]
		else:
			vertexArgs = [ len(vertices) ] + [ [x,y,-z] for x,y,z in vertices ] # even if there is no rotation we must flip Z axis
		triangleIndices = self.getTriangleIndices()
		faceArgs = [ len(triangleIndices) ] + list(map(list, triangleIndices))

#		print('Rendering with camera at {} and light at {}'.format(str(cameraLocation), str(lightLocation)))

		return vpr.Scene( vpr.Camera('location', cameraLocation, 'look_at', cameraTarget, 'sky', [0,0,-1]),
		                  [ vpr.LightSource(lightLocation, 'color', lightColor),
		                    vpr.Background('color', backgroundColor),
		                    vpr.Mesh2(vpr.VertexVectors(*vertexArgs), vpr.FaceIndices(*faceArgs), vpr.Pigment('color', objectColor))
		                  ]
		                )

	def getSceneSpherical(self, *, cameraR=100., cameraTheta=0., cameraPhi=0.,
	                               lightR=100., lightTheta=np.pi/4, lightPhi=np.pi/2,
	                               lightColor=(1,1,1), backgroundColor=(0,0,0), objectColor=(0.5,0.5,0.5),
	                               rotationAxis=None, rotationAngle=None):
		'''Assumptions: R\in[0,\infty), Theta\in[0,\pi), Phi\in[0,2\pi)'''
		def sphericalToCartesian(r, t, p):
			return (r*np.sin(t)*np.cos(p),
			        r*np.sin(t)*np.sin(p),
			        r*np.cos(t))
#		print('From scene generating func: got the camera coords {}'.format((cameraR, cameraTheta, cameraPhi)))
		cameraLocation = sphericalToCartesian(cameraR, cameraTheta, cameraPhi)
#		print('From scene generating func: converted to cartesian, got {}'.format(cameraLocation))
		lightLocation = sphericalToCartesian(lightR, lightTheta, lightPhi)
		return self.getScene(cameraLocation=list(cameraLocation), lightLocation=list(lightLocation),
		                      lightColor=list(lightColor), backgroundColor=list(backgroundColor), objectColor=list(objectColor),
		                      rotationAxis=rotationAxis, rotationAngle=rotationAngle)

	def renderSceneSpherical(self, outfile, width=1024, height=720, antialiasing=0.01, **kwargs):
		scene = self.getSceneSpherical(**kwargs)
		povfilename = '__temp{}__.pov'.format(threading.get_ident())
		scene.render(outfile, width=width, height=height, antialiasing=antialiasing, tempfile=povfilename, remove_temp=True)

	def writeOBJ(self, objFileName):
		'''Exports the shape in Wavefront .OBJ format'''
		with open(objFileName, 'w') as oof:
			for x,y,z in self.getVertices():
				oof.write('v {} {} {}\n'.format(x,y,z))
			for v1,v2,v3 in self.getTriangleIndices():
				oof.write('f {} {} {}\n'.format(v1+1,v2+1,v3+1))
