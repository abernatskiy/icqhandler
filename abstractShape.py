from abc import ABC, abstractmethod
import vapory as vpr

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

	def getScene(self, *, cameraLocation=[100,100,50], cameraTarget=[0,0,0], lightLocation=[100,100,100], lightColor=[1,1,1], backgroundColor=[0,0,0], objectColor=[0.5,0.5,0.5]):
		# POVRay uses a left-handed coordinate system, so we have to flip the Z axis on all geometric vectors
		cameraLocation[2] = -cameraLocation[2]
		cameraTarget[2] = -cameraTarget[2]
		lightLocation[2] = -lightLocation[2]

		vertices = self.getVertices()
		vertexArgs = [ len(vertices) ] + [ [x,y,-z] for x,y,z in vertices ] # Z axis must be flipped in vertex coordinates, too
		triangleIndices = self.getTriangleIndices()
		faceArgs = [ len(triangleIndices) ] + list(map(list, triangleIndices))

		return vpr.Scene( vpr.Camera('location', cameraLocation, 'look_at', cameraTarget, 'sky', [0,0,-1]),
		                  [ vpr.LightSource(lightLocation, 'color', lightColor),
		                    vpr.Background('color', backgroundColor),
		                    vpr.Mesh2(vpr.VertexVectors(*vertexArgs), vpr.FaceIndices(*faceArgs), vpr.Pigment('color', objectColor))
		                  ]
		                )
