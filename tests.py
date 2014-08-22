import math


import vector

# easily verified
assert vector.dot  ([1,0,0], [0,1,1]) == 0
assert vector.norm ([8,9,12])         == 17
assert vector.cross([0,1,0], [1,0,0]) == [0,0,-1]
assert vector.angle([0,1,0], [1,0,0]) == -math.pi/2

# initial results
assert vector.dot  ([1,4,7], [2,5,8]) == 78
assert vector.norm ([4,5,6])          == 8.774964387392123
assert vector.cross([9,8,7], [2,3,1]) == [-13, 5, 11]
assert vector.angle([4,7,5], [3,5,8]) == -0.3861364787976416
assert vector.angle([4,5,7], [3,8,5]) ==  0.3861364787976416


import matrix

def checkdiff(A,B):
	for i in range(3):
		for j in range(3):
			a = A[i][j]
			b = B[i][j]
			if abs(a - b) > 1e-10:
				return False
	return True

# easily verified
i = matrix.identity()
m = [[2,0,0],[0,2,0],[0,0,2]]
r = matrix.rotation(90, 1, 0, 0)
assert i == [[1,0,0],[0,1,0],[0,0,1]]
assert matrix.dot_v(i, [1,2,3]) == [1,2,3]
assert matrix.dot_v(m, [1,2,3]) == [2,4,6]
assert matrix.dot_m(i, i) == i
assert matrix.dot_m(m, m) == [[4,0,0],[0,4,0],[0,0,4]]
assert r == matrix.rotation_rad(math.pi/2, 1, 0, 0)
assert checkdiff(r, [[1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]])

# initial results
A = [[1,2,3],[4,5,6],[7,8,9]]
B = [[3,2,1],[6,5,4],[9,8,7]]
m = [[0.33482917221585295, 0.8711838511445769, -0.3590656248350022], [-0.66651590413407, 0.4883301324737331, 0.5632852130622015], [0.6660675453507625, 0.050718627969319086, 0.7441650662368666]]
assert matrix.dot_m(A,B) == [[42, 36, 30], [96, 81, 66], [150, 126, 102]]
assert matrix.dot_m(B,A) == [[18, 24, 30], [54, 69, 84], [ 90, 114, 138]]
assert checkdiff(matrix.rotation_rad(5, 1, 2, 3), m)
