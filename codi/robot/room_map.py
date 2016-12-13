from math import floor, pi
from PIL import Image
from copy import deepcopy
import numpy as np
import cv2
from priority_queue import priority_queue

from utils import _X, _Y, _diameter
from utils import deg2rad, smooth_path, locate_point

class room_map:
	
	# -------------------------
	# Private Static attributes
	
	_fixed_obstacle = 999999
	_max_left_angle = 30 + 1
	_max_right_angle = 330
	_max_dist_round = 700.0 # maximum distance in mm to detect an obstacle AROUND THE ROBOT
							# (i.e. an obstacle is detected iff it is within this distance from the center of the laser)
	_max_dist_front = 500.0 # maximum distance in mm to detect an obstacle IN FRONT OF THE ROBOT
							# (i.e. an obstacle is detected iff it is within this distance from the center of the laser)

	# ------------------
	# Private attributes
	
	_rows = 0
	_cols = 0
	_threshold = 0
	_map = [[]]	# matrix of size NxM (rows x columns) with numbers from 0 to +inf
				# (+inf = _fixed_obstacle)
	_obstacles = [[]]   # matrix of size NxM (rows x columns) with the obstacles detected
						# with the laser
	
	# ----------------------
	# Private Static methods
	
	@staticmethod
	def _get_enlargement_dist(diam):
		r = diam/2.0
		r = int(floor(r/10.0)) + 20
		return r
	
	# ---------------
	# Private methods
	
	# Enlarge an obstacle with center (x, y) and radius r
	def _enlarge_obstacle(self, y, x, r, val = 1):
		r2 = 1.0*r*r
		for i in xrange(y - r, y + r + 1):
			if 0 <= i and i < self._rows:
				for j in xrange(x - r, x + r + 1):
					if 0 <= j and j < self._cols:
						d = (i - y)**2.0 + (j - x)**2.0
						if d <= r2: self._mat[i][j] += val

	def _enlarge_wall(self, y, x, r):
		for i in xrange(y - r, y + r + 1):
			if 0 <= i and i < self._rows:
				for j in xrange(x - r, x + r + 1):
					if 0 <= j and j < self._cols:
						self._mat[i][j] = room_map._fixed_obstacle

	# Returns the list of valid neighbours as a list of pairs of integers
	# (row, column)
	def _get_neighbours(self, i, j):
		l = []
		if i > 0:
			if j > 0: l.append((i - 1, j - 1))
			l.append((i - 1, j))
			if j < self._cols - 1: l.append((i - 1, j + 1))
		
		if j > 0: l.append((i, j - 1))
		if j < self._cols - 1: l.append((i, j + 1))
		
		if i < self._rows - 1:
			if j > 0: l.append((i + 1, j - 1))
			l.append((i + 1, j))
			if j < self._cols - 1: l.append((i + 1, j + 1))
		return l

	# Returns whether the cell (i,j) is a wall or not.
	# pre: 0 <= i, j.  i < rows, j < cols
	def _is_wall(self, i, j): return self._mat[i][j] >= room_map._fixed_obstacle

	# laser_data: data from laser
	# l, r: angles range (l < r)
	# R_pos, theta: robot position and orientation [mm, radians]
	# R: enlargement dist [cm]
	# v: increment value in each cell
	# max_dist: maximum distance to consider obstacles
	def _set_obstacles_range(self, laser_data, l, r, R_pos, theta, R, v, max_dist):
		for i in xrange(l, r):
			d = laser_data.angles_values[i].distance
			if laser_data.angles_values[i].error_code == 0 and d < max_dist:
				Px, Py = locate_point(R_pos, d, theta, deg2rad(360.0 - 1.0*i))
				Px = int(floor(Px/10.0))
				Py = int(floor(Py/10.0))
				if Px >= 0 and Py >= 0 and Px < self._cols and Py < self._rows:
					if not self._is_wall(Py, Px):
						self._enlarge_obstacle(Py, Px, R, v)
						self._obstacles[Py][Px] = 1

	# Hill Climbing - Greedy algorithm - Fast, but sometimes can't find
	# a good path
	def _hill_climbing_search(self, R, P):
		Rx = int(R[_X]/10.0) # centimeters
		Ry = int(R[_Y]/10.0)
		Px = int(P[_X]/10.0)
		Py = int(P[_Y]/10.0)
		
		FACTOR = lambda s: 0 if s == 0 else 1.2**s
		
		visited = [[False]*self._cols for i in xrange(0, self._rows)]
		visited[Ry][Rx] = True
		
		path = [(Ry, Rx)]
		finished = False
		
		while not finished:
			current_pos = path[len(path) - 1]
			ci = current_pos[0]
			cj = current_pos[1]
			
			if ci == Py and cj == Px: finished = True
			else:
				current_dist = 999999999999999
				
				neigh = self._get_neighbours(ci, cj)
				min_neigh = None
				
				# choose closest neighbour
				for i, j in neigh:
					v = self._mat[i][j]
					if v < room_map._fixed_obstacle and not visited[i][j]:
						dist_goal = (1.0*(Py - i))**2.0 + (1.0*(Px - j))**2.0 + FACTOR(v)
						
						if dist_goal < current_dist or dist_goal == current_dist and min_neigh[0] < i:
							current_dist = dist_goal
							min_neigh = (i, j)
						
				if min_neigh == None:
					print "Error when choosing neighbour"
					return map(lambda p: (10*p[1], 10*p[0]), path)
				
				visited[min_neigh[0]][min_neigh[1]] = True
				path.append(min_neigh)
		
		path = map(lambda p: (10*p[1], 10*p[0]), path)
		return path
	
	# A* search algorithm, from: http://www.redblobgames.com/pathfinding/a-star/implementation.html
	# Good (always find a good path) but slow.
	def _a_star_search(self, R, P):
		Rx = int(R[_X]/10.0) # centimeters
		Ry = int(R[_Y]/10.0)
		Px = int(P[_X]/10.0)
		Py = int(P[_Y]/10.0)
		
		FACTOR = lambda s: 0 if s == 0 else 1.3**s
		start = (Ry, Rx)
		goal = (Py, Px)
		
		frontier = priority_queue()
		frontier.put(start, 0)
		
		came_from = {}
		length_so_far = {}
		
		came_from[start] = None
		length_so_far[start] = 0
		
		while not frontier.empty():
			current = frontier.get()
			
			if current == goal: break
			
			ci = current[0]
			cj = current[1]
			neighbours = self._get_neighbours(ci, cj)
			
			for next_neigh in neighbours:
				i = next_neigh[0]
				j = next_neigh[1]
				
				v = self._mat[i][j]
				if v < room_map._fixed_obstacle:
					new_length = length_so_far[current] + abs(i - ci) + abs(j - cj)
					priority = new_length + FACTOR(v)

					if next_neigh not in length_so_far or new_length < length_so_far[next_neigh]:
						length_so_far[next_neigh] = new_length
						frontier.put(next_neigh, priority)
						came_from[next_neigh] = current

		path = [goal]
		node = goal
		while node in came_from and came_from[node] != None:
			path.append(came_from[node])
			node = came_from[node]

		if node not in came_from:
			print "Error: no s'ha pogut desfer el cami"
			return []

		path.reverse()
		path = map(lambda p: (10*p[1], 10*p[0]), path)
		return path
	
	# --------------
	# Public methods
	
	def __init__(self, th = 0):
		self._threshold = th
	
	# Set and get the threshold used to determine whether there is, in a
	# given cell, an obstacle or not.
	def set_threshold(self, th): self._threshold = th
	def get_threshold(self): return self._threshold
	
	# Uses the matrix parameter as the map for this room
	def from_matrix(self, matrix):
		self._map = matrix
		self._rows = len(matrix)
		self._cols = len(matrix[0])
	
	# Reads an RGB image and converts it into a matrix that will be used
	# as a map.
	def from_image(self, image_name):
		im = Image.open(image_name)
		im = im.convert('RGB')
		self._cols, self._rows = im.size
		
		_mat2 = [[0]*self._cols for i in xrange(0, self._rows)]
		self._obstacles = [[0]*self._cols for i in xrange(0, self._rows)]
		
		for i in xrange(0, self._rows):
			for j in xrange(0, self._cols):
				if im.getpixel((j, i)) == (0, 0, 0) or im.getpixel((j, i)) == (0, 0, 255):
					_mat2[i][j] = room_map._fixed_obstacle
				else:
					_mat2[i][j] = 0
		
		self._mat = deepcopy(_mat2)
		r = room_map._get_enlargement_dist(_diameter)
		
		for i in xrange(0, self._rows):
			for j in xrange(0, self._cols):
				if _mat2[i][j] == room_map._fixed_obstacle:
					neighbours = filter(lambda (y, x): _mat2[y][x] == 0, self._get_neighbours(i, j))
					if len(neighbours) > 0:
						self._enlarge_wall(i, j, r)
						self._obstacles[i][j] = 1
	
	# Converts the map matrix to a grey scale image.
	def map_to_image(self):
		n_rows = self._rows
		n_cols = self._cols
		
		min_value = room_map._fixed_obstacle
		max_value = 0
		for i in xrange(0, n_rows):
			for j in xrange(0, n_cols):
				if self._mat[i][j] < room_map._fixed_obstacle:
					if self._mat[i][j] > max_value: max_value = self._mat[i][j]
					if self._mat[i][j] > 0 and self._mat[i][j] < min_value: min_value = self._mat[i][j]

		scale_pos = lambda r, l, M, m, x: ((M - m)/(r - l))*(x - l) + m # 0 -> 255
		scale_neg = lambda r, l, M, m, x: ((m - M)/(r - l))*(x - l) + M # 255 -> 0

		l = min_value
		r = max_value
		intervals = []
		interval_size = (r - l)/7.0
		for i in xrange(0, 7): intervals.append((l + i*interval_size, l + (i + 1)*interval_size))

		rgb_matrix = [[(0, 0, 0)]*n_cols for i in xrange(0, n_rows)]
		
		for i in xrange(0, n_rows):
			for j in xrange(0, n_cols):
				v = self._mat[i][j]
				if v >= room_map._fixed_obstacle: rgb_matrix[i][j] = (0, 0, 0)
				elif r > l:
					k = int(v/interval_size)
					if k == 7: k -= 1

					I_sup = intervals[k][1]
					I_inf = intervals[k][0]
					s_pos = int(scale_pos(I_sup, I_inf, 255.0, 0.0, v))
					s_neg = int(scale_neg(I_sup, I_inf, 255.0, 0.0, v))

					if k == 0: rgb_matrix[i][j] = (s_neg, 255, 255)
					elif k == 1: rgb_matrix[i][j] = (0, s_neg, 255)
					elif k == 2: rgb_matrix[i][j] = (s_pos, 0, 255)
					elif k == 3: rgb_matrix[i][j] = (255, 0, s_neg)
					elif k == 4: rgb_matrix[i][j] = (255, s_pos, 0)
					elif k == 5: rgb_matrix[i][j] = (s_neg, 255, 0)
					elif k == 6: rgb_matrix[i][j] = (0, s_neg, 0)

				else: rgb_matrix[i][j] = (255, 255, 255)

		rgb_image = Image.new('RGB', (n_cols, n_rows))
		rgb_image.putdata([p for row in rgb_matrix for p in row])
		return rgb_image

	# Converts the obstacles matrix to a black and white image.
	def obstacles_to_image(self):
		n_rows = self._rows
		n_cols = self._cols

		bw_image = Image.new('RGB', (n_cols, n_rows))
		bw_image.putdata([(255*p, 255*p, 255*p) for row in self._obstacles for p in row])
		return bw_image

	# Shows this map
	def show_map(self):
		image = self.to_image()
		image.show()
	
	# Saves this map as image in the file specified.
	def save_map_as_image(self, image_name):
		as_image = self.map_to_image()
		as_image.save(image_name)

	# Saves the obstacles as image in the file specified.
	def save_obstacles_as_image(self, image_name):
		as_image = self.obstacles_to_image()
		as_image.save(image_name)

	# Adds an obstacle at the corresponding cell of the map according to
	# what the laser detected.
	# R, theta: position in mm and orientation of the robot in radians
	# laser_data: object of class lds_data, contains what the laser detected
	def set_obstacles(self, R, theta, laser_data):
		L = locate_point(R, 95.0, theta, pi)
		r = room_map._get_enlargement_dist(_diameter) + 5
		self._set_obstacles_range(laser_data, 0, 360, L, theta, r, 1, room_map._max_dist_round)
	
	# Adds an obstacle at the corresponding cell of the map according to
	# what the laser detected in front of the robot.
	# R, theta: position in mm and orientation of the robot in radians
	# laser_data: object of class lds_data, contains what the laser detected
	def set_obstacles_front(self, R, theta, laser_data):
		L = locate_point(R, 95.0, theta, pi)
		r = room_map._get_enlargement_dist(_diameter) + 5
		self._set_obstacles_range(laser_data, 0, room_map._max_left_angle, L, theta, r, 1, room_map._max_dist_front)
		self._set_obstacles_range(laser_data, room_map._max_right_angle, 360, L, theta, r, 1, room_map._max_dist_front)

	# Returns whether there is an obstacle in front of the robot ignoring walls
	def obstacle_in_front(self, R, theta, laser_data):
		for i in xrange(0, room_map._max_left_angle):
			value = laser_data.angles_values[i]
			if value.error_code == 0:
				if value.distance < room_map._max_dist_front:
					Px, Py = locate_point(R, value.distance, theta, deg2rad(360.0 - 1.0*i))
					Px = int(floor(Px/10.0))
					Py = int(floor(Py/10.0))
					if Px >= 0 and Py >= 0 and Px < self._cols and Py < self._rows:
						if not self._is_wall(Py, Px): return True

		for i in xrange(room_map._max_right_angle, 360):
			value = laser_data.angles_values[i]
			if value.error_code == 0:
				if value.distance < room_map._max_dist_front:
					Px, Py = locate_point(R, value.distance, theta, deg2rad(360.0 - 1.0*i))
					Px = int(floor(Px/10.0))
					Py = int(floor(Py/10.0))
					if Px >= 0 and Py >= 0 and Px < self._cols and Py < self._rows:
						if not self._is_wall(Py, Px): return True

		return False

	# Find a path from R to P (x, y-coordinates in mm) using the algorithm
	# a star search algorithm.
	# Returns a list of points in mm (x, y-coordinates).
	def find_path(self, R, P):
		return self._a_star_search(R, P)
		# return self._hill_climbing_search(R, P)
	
	def find_smoothed_path(self, R, P):
		path = self.find_path(R, P)
		return smooth_path(path)

	def detect_cylindrical_objects(self):
		aux_img = self.obstacles_to_image()
		aux_img.save('obstacles.jpg')
		img = cv2.imread('obstacles.jpg', 0)
		
		circles = cv2.HoughCircles(
			img,				# image
			cv2.HOUGH_GRADIENT,	# method: Detection method
			1,					# dp: Inverse ratio of the accumulator resolution to the image resolution
								# if dp=1 , the accumulator has the same resolution as the input image
			20, 				# minDist: Minimum distance between the centers of the detected circles.
			param1=726,			# it is the higher threshold of the two passed to the Canny edge detector
			param2=25,			# it is the accumulator threshold for the circle centers at the detection stage.
								# The smaller it is, the more false circles may be detected.
			minRadius=0,
			maxRadius=500
		)

		result = None
		if circles is not None:
			img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
			result = deepcopy(circles)
			circles = np.uint16(np.around(circles))

			for i in circles[0,:]:
				cv2.circle(img,(i[0], i[1]),i[2], (0,255,0), 2)
				cv2.circle(img,(i[0], i[1]),   2, (0,0,255), 3)

			print 'Hi ha %i cercles' % len(circles[0,:])

			cv2.imshow('Cercles', img)
			cv2.imwrite('examen_exploracio/obstacles_detectats.png', img)

		return result
