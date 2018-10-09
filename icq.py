import numpy as np
from abstractShape import AbstractShape

class ICQShape(AbstractShape):
	''' Class for handling 3d models in implicitly connected quadrilateral format.
  	  See https://sbib.psi.edu/spc_wiki/SHAPE.TXT for detailed format description.

	    Faces numbering:

	                                    -----------
	                                    |         |
	                                    |    0    |
	                                    |         |
	      -----------------------------------------
	      |         |         |         |         |
	      |    4    |    3    |    2    |    1    |
	      |         |         |         |         |
	      -----------------------------------------
	                                    |         |
	                                    |    5    |
	                                    |         |
	                                    -----------

	    Vertices within the face:

	         0 --------- I --------- Q
	      0  .  .  .  .  .  .  .  .  .
	      |  .  .  .  .  .  .  .  .  .
	      |  .  .  .  .  .  .  .  .  .
	      |  .  .  .  .  .  .  .  .  .
	      J  .  .  .  . F.  .  .  .  .
	      |  .  .  .  .  .  .  .  .  .
	      |  .  .  .  .  .  .  .  .  .
	      |  .  .  .  .  .  .  .  .  .
	      Q  .  .  .  .  .  .  .  .  .

	'''
	def __init__(self):
		self.q = None # Model resolution
		self.rawVertices = None # Flat list of vertices of the model
		self.vertices = None # Three-dimensional list of vertices.
		                     # Vertex at self.vertices[f][j][i] is on face f at position (i,j)
		self.rawVerticesUpToDate = False

	def readICQ(self, icqfilename):
		with open(icqfilename, 'r') as icqfile:
			self.q = int(icqfile.readline())
		self.rawVertices = list(map(tuple, np.loadtxt(icqfilename, skiprows=1).tolist()))
		self.parseRawVertices()
		self.rawVerticesUpToDate = True

	def writeICQ(self, icqfilename):
		if not self.rawVerticesUpTodate:
			if not self.vertices:
				raise ValueError('No data to write to the ICQ file!')
			else:
				self.unparseVerticesToRaw()

		# Format mirrors the output of cubeICQ.c exactly, potentially with all its errors
		with open(icqfilename, 'w') as icqfile:
			icqfile.write('\t     ' + str(self.q) + '\n')
			for vertex in self.rawVertices:
				for component in vertex:
					icqfile.write('\t{:.6f}'.format(component))
				icqfile.write('\n')

	def parseRawVertices(self):
		'''Parses the flat list of vertices self.rawVertices into the three-dimensional structure
		   self.vertices. Each element of this structure is a triple, so it's really four dimensional.
		   Additionally, a map is generated from the three indices on self.vertices to the single
		   index of self.rawVertices. The map is stored at self.indexMap3to1
		'''
		curidx = 0
		self.vertices = []
		self.indexMap3to1 = {}
		for face in range(6):
			faceMatrix = []
			for j in range(self.q+1):
				faceRow = []
				for i in range(self.q+1):
					faceRow.append(self.rawVertices[curidx])
					self.indexMap3to1[(face, j, i)] = curidx
					curidx += 1
				faceMatrix.append(faceRow)
			self.vertices.append(faceMatrix)

	def unparseVerticesToRaw(self):
		'''Updates the flat list of vertices (self.rawVertices) based on self.vertices.'''
		curIdx = 0
		self.rawVertices = []
		self.indexMap3to1 = {}
		for face in range(6):
			for j in range(self.q+1):
				for i in range(self.q+1):
					self.rawVertices.append(self.vertices[face][j][i])
					curIdx += 1
					self.indexMap3to1[(face, j, i)] = curIdx
		self.rawVerticesUpToDate = True

	def validate(self, exceptionIfInvalid=True):
		'''Checks if the coordinates of redundant vertices coincide, returns true if they do'''

		# defining a custom equality function in case we need \epsilon-equality at some point
		def eq(v1, v2):
			eqval = (v1==v2)
			if not exceptionIfInvalid:
				return eqval
			elif eqval:
				return True
			else:
				raise RuntimeError('Redundant vertex has different coordinates on different faces: {} vs {}'.format(v1, v2))

		# comparing edge vertices in a pairwise manner
		edges = [ [ eq(self.vertices[5][self.q][i], self.vertices[3][self.q][self.q-i]) for i in range(self.q+1) ], # v(I,Q,5)=v(Q-I,Q,3)
		          [ eq(self.vertices[5][0][i], self.vertices[1][self.q][i]) for i in range(self.q+1) ],             # v(I,0,5)=v(I,Q,1)
		          [ eq(self.vertices[4][0][i], self.vertices[0][self.q-i][self.q]) for i in range(self.q+1) ],      # v(I,0,4)=v(Q,Q-I,0)
		          [ eq(self.vertices[3][0][i], self.vertices[0][0][self.q-i]) for i in range(self.q+1) ],           # v(I,0,3)=v(Q-i,0,0)
		          [ eq(self.vertices[2][0][i], self.vertices[0][i][0]) for i in range(self.q+1) ],                  # v(I,0,2)=v(0,I,0)
		          [ eq(self.vertices[1][0][i], self.vertices[0][self.q][i]) for i in range(self.q+1) ],             # v(I,0,1)=v(I,Q,0)
		          [ eq(self.vertices[5][i][self.q], self.vertices[4][self.q][i]) for i in range(self.q+1) ],        # v(q,I,5)=v(I,Q,4)
		          [ eq(self.vertices[4][i][self.q], self.vertices[3][i][0]) for i in range(self.q+1) ],             # v(q,I,4)=v(0,I,3)
		          [ eq(self.vertices[3][i][self.q], self.vertices[2][i][0]) for i in range(self.q+1) ],             # v(q,I,3)=v(0,I,2)
		          [ eq(self.vertices[2][i][self.q], self.vertices[1][i][0]) for i in range(self.q+1) ],             # v(q,I,2)=v(0,I,1)
		          [ eq(self.vertices[5][i][0], self.vertices[2][self.q][self.q-i]) for i in range(self.q+1) ],      # v(0,I,5)=v(Q-I,Q,2)
		          [ eq(self.vertices[4][i][0], self.vertices[1][i][self.q]) for i in range(self.q+1) ]              # v(0,I,4)=v(Q,I,1)
		]

		# comparing each pair within the three corner vertices
		# three comparisons are necessary because at some point we might be interested in \epsilon-equality that is not transitive
		# note: corner checking is redundant - same comparisons are while comparing edge vertices
		corners = [ [ eq(self.vertices[0][0][0], self.vertices[2][0][0]),
		              eq(self.vertices[2][0][0], self.vertices[3][0][self.q]),
		              eq(self.vertices[0][0][0], self.vertices[3][0][self.q]) ],               # v(0,0,0) = v(0,0,2) = v(Q,0,3)
                [ eq(self.vertices[0][self.q][0], self.vertices[1][0][0]),
                  eq(self.vertices[1][0][0], self.vertices[2][0][self.q]),
                  eq(self.vertices[0][self.q][0], self.vertices[2][0][self.q]) ],          # v(0,Q,0) = v(0,0,1) = v(Q,0,2)
                [ eq(self.vertices[0][0][self.q], self.vertices[3][0][0]),
                  eq(self.vertices[3][0][0], self.vertices[4][0][self.q]),
                  eq(self.vertices[0][0][self.q], self.vertices[4][0][self.q]) ],          # v(Q,0,0) = v(0,0,3) = v(Q,0,4)
                [ eq(self.vertices[0][self.q][self.q], self.vertices[4][0][0]),
                  eq(self.vertices[4][0][0], self.vertices[1][0][self.q]),
                  eq(self.vertices[0][self.q][self.q], self.vertices[1][0][self.q]) ],     # v(Q,Q,0) = v(0,0,4) = v(Q,0,1)
                [ eq(self.vertices[5][0][0], self.vertices[1][self.q][0]),
                  eq(self.vertices[1][self.q][0], self.vertices[2][self.q][self.q]),
                  eq(self.vertices[5][0][0], self.vertices[2][self.q][self.q]) ],          # v(0,0,5) = v(0,Q,1) = v(Q,Q,2)
                [ eq(self.vertices[5][self.q][0], self.vertices[2][self.q][0]),
                  eq(self.vertices[2][self.q][0], self.vertices[3][self.q][self.q]),
                  eq(self.vertices[5][self.q][0], self.vertices[3][self.q][self.q]) ],     # v(0,Q,5) = v(0,Q,2) = v(Q,Q,3)
                [ eq(self.vertices[5][0][self.q], self.vertices[4][self.q][0]),
                  eq(self.vertices[4][self.q][0], self.vertices[1][self.q][self.q]),
                  eq(self.vertices[5][0][self.q], self.vertices[1][self.q][self.q]) ],     # v(Q,0,5) = v(0,Q,4) = v(Q,Q,1)
                [ eq(self.vertices[5][self.q][self.q], self.vertices[3][self.q][0]),
                  eq(self.vertices[3][self.q][0], self.vertices[4][self.q][self.q]),
                  eq(self.vertices[5][self.q][self.q], self.vertices[4][self.q][self.q]) ] # v(Q,Q,5) = v(0,Q,3) = v(Q,Q,4)
		]

		return all(map(all, edges)) and all(map(all, corners))

	def getTrianglesOn3DIndices(self):
		'''Returns the list of six lists of triangles constituting the model.
		   Each sublist contains all trianges of the corresponding face.
		   Each triangle is represented as a triple of triples of indices in self.vertices.
		'''
		faceLists = []
		for face in range(6):
			faceTriangles = []
			for i in range(self.q):
				for j in range(self.q):
					faceTriangles.append( ( (face,j,i), (face,j,i+1), (face,j+1,i+1) ) )
					faceTriangles.append( ( (face,j,i), (face,j+1,i), (face,j+1,i+1) ) )
			faceLists.append(faceTriangles)
		return faceLists

	def getTrianglesOnFlatIndices(self):
		'''Returns the list of triangles constituting the model.
		   Each triangle is represented as a triple of indices in self.rawVertices.
		'''
		if not self.rawVerticesUpToDate:
			self.unparseVerticesToRaw()
		triangles3di = sum(self.getTrianglesOn3DIndices(), [])
		return [ (self.indexMap3to1[i], self.indexMap3to1[j], self.indexMap3to1[k]) for i,j,k in triangles3di ]

	def densifyTwofold(self, passes=1):
		def interpolate(face, j1, i1, j2, i2):
			vec1 = self.vertices[face][j1][i1]
			vec2 = self.vertices[face][j2][i2]
			return tuple( (c1+c2)/2. for c1,c2 in zip(vec1, vec2) )
		newVertices = []
		for face in range(6):
			faceMatrix = []
			lastRow = []
			for j in range(self.q):
				upperRow = []
				lowerRow = []
				for i in range(self.q):
					# i,j     X      i+1,j   <--- upper row
					#  X      X        X     <--- lower row
					# i,j+1   X      i+1,j+1 <--- last row (only processed on the lower boundary)
					# last column elements are only added on the right boundary

					upperRow.append(self.vertices[face][j][i])
					upperRow.append(interpolate(face, j, i, j, i+1))
					if i==self.q-1:
						upperRow.append(self.vertices[face][j][i+1])

					lowerRow.append(interpolate(face, j, i, j+1, i))
					lowerRow.append(interpolate(face, j, i, j+1, i+1))
					if i==self.q-1:
						lowerRow.append(interpolate(face, j, i+1, j+1, i+1))

					if j==self.q-1:
						lastRow.append(self.vertices[face][j+1][i])
						lastRow.append(interpolate(face, j+1, i, j+1, i+1))
						if i==self.q-1:
							lastRow.append(self.vertices[face][j+1][i+1])

				faceMatrix.append(upperRow)
				faceMatrix.append(lowerRow)

			faceMatrix.append(lastRow)

			newVertices.append(faceMatrix)

		self.vertices = newVertices
		self.q *= 2

		if passes>1:
			self.densifyTwofold(passes=passes-1)

		self.rawVerticesUpToDate = False

	def dumberTwofold(self, passes=1):
		if self.q//(2**passes) < 1:
			raise ValueError('Model resolution cannot be lowered (q={}, {} passes of twofold coarse graining requested)'.format(self.q, passes))
		newVertices = []
		for face in range(6):
			faceMatrix = []
			for j in range(self.q//2+1):
				row = []
				for i in range(self.q//2+1):
					row.append(self.vertices[face][2*j][2*i])
				faceMatrix.append(row)
			newVertices.append(faceMatrix)

		self.vertices = newVertices
		self.q //= 2

		if passes>1:
			self.dumberTwofold(passes=passes-1)

		self.rawVerticesUpToDate = False

	###### Overloading abstract methods of AbstractShape #####

	def getTriangleIndices(self):
		return self.getTrianglesOnFlatIndices()

	def getVertices(self):
		if not self.rawVerticesUpToDate:
			self.unparseVerticesToRaw()
		return self.rawVertices

	def setVertices(self, newVertices, newq=None): # TODO: make sure that the new verices are adequate for the q
		if newq:
			self.q = newq
		self.rawVertices = newVertices
		self.parseRawVertices()

	def getMinAngularFeatureSize(self):
		'''Returns the minimum side length of any triangle in the mesh representation of the model'''
		def angleBetween(face, j1, i1, j2, i2):
			vec1 = self.vertices[face][j1][i1]
			vec2 = self.vertices[face][j2][i2]
			result = np.arccos( np.dot(vec1, vec2) / (np.linalg.norm(vec1)*np.linalg.norm(vec2)) )
			if face == 0:
				print('At face {} angle between vectors {} and {} fas found to be {} pi radians'.format(face, (j1,i1), (j2,i2), result/np.pi))
			return np.arccos( np.dot(vec1, vec2) / (np.linalg.norm(vec1)*np.linalg.norm(vec2)) )
		facemaxs = []
		for face in range(6):
			rowmaxs = []
			for j in range(self.q):
				rowdists = []
				for i in range(self.q):
					rowdists.append(angleBetween(face, j, i, j, i+1))
					rowdists.append(angleBetween(face, j, i, j+1, i))
					rowdists.append(angleBetween(face, j, i, j+1, i+1))
				rowdists.append(angleBetween(face, j, self.q, j+1, self.q))
				rowmaxs.append(max(rowdists))
			rowdists = []
			for i in range(self.q):
				rowdists.append(angleBetween(face, self.q, i, self.q, i+1))
			rowmaxs.append(max(rowdists))

			facemaxs.append(max(rowmaxs))
		return max(facemaxs)

	def upscale(self):
		self.densifyTwofold()
