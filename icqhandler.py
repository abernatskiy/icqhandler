''' Library for handling 3d models in implicitly connected quadrilateral format.
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

'''

import numpy as np

class ICQShape(object):
	def __init__(self):
		self.q = None # Model resolution
		self.rawVertices = None # Flat list of vertices of the model
		self.vertices = None # Three-dimensional list of vertices.
		                     # Vertex at self.vertices[f][j][i] is on face f at position (i,j)

	def readICQ(self, icqfilename):
		with open(icqfilename, 'r') as icqfile:
			self.q = int(icqfile.readline())
		self.rawVertices = list(map(tuple, np.loadtxt(icqfilename, skiprows=1).tolist()))
		self.parseRawVertices()
		# self.validate()

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

	def generateTrianglesOn3DIndices(self):
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

	def generateTrianglesOnFlatIndices(self):
		'''Returns the list of triangles constituting the model.
		   Each triangle is represented as a triple of indices in self.rawVertices.
		'''
		triangles3di = sum(self.generateTrianglesOn3DIndices(), [])
		return [ (self.indexMap3to1[i], self.indexMap3to1[j], self.indexMap3to1[k]) for i,j,k in triangles3di ]
