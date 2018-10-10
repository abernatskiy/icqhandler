import numpy as np

class Sculptor:
	def __init__(self, baseShape):
		self.shape = baseShape
		self.vertices = baseShape.getVertices()
		self.shapeUpToDate = True

	def updateShape(self):
		if not self.shapeUpToDate:
			self.shape.setVertices(self.vertices)
			self.shapeUpToDate = True

	def getShape(self):
		self.updateShape()
		return self.shape

	def rollIntoABall(self, radius=1.):
		newVertices = []
		for v in self.vertices:
			npv = np.array(v)
			newVertices.append(tuple(npv*radius/np.linalg.norm(npv)))
		self.vertices = newVertices
		self.shapeUpToDate = False

	def renderShape(self, outfile, **kwargs):
		shape = self.getShape()
		shape.renderSceneSpherical(outfile, **kwargs)

	def upscaleShape(self):
		self.updateShape()
		self.shape.upscale()
		self.vertices = self.shape.getVertices()
