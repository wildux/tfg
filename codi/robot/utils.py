from math import pi, floor, sin, cos, atan, sqrt

# useful values

_r_90 = pi/2.0
_r_180 = pi
_r_270 = 3.0*pi/2.0
_r_360 = 2.0*pi
_X = 0 # access the x-coordinate of a point
_Y = 1 # access the y-coordinate of a point

#_diameter = 243.0 # diameter in mm - distance between WHEELS
_diameter = 760.0/pi # diameter in mm - distance between WHEELS
#_diameter = 241.5 # diameter in mm - distance between WHEELS

# Converts the angle rad (in radians) into degrees
def rad2deg(rad): return rad*180.0/pi

# Converts the angle deg (in degrees) into radians
def deg2rad(deg): return deg*pi/180.0

# Returns the normalization of alpha. Returns 0 <= angle < 2*pi
# alpha: angle in radians.
def normalize_angle(alpha):
	angle = alpha
	k = floor(abs(angle)/_r_360)
	if angle > 0: angle = angle - k*_r_360
	else: angle = angle + k*_r_360
	
	if angle < 0: angle = _r_360 + angle
	return angle

# Locates a point at a distance d from Rx, Ry and at an angle of theta + beta.
# Returns the (x, y)-coordinates of the point P at distance d and angle
# between this point and the robot of theta + beta
# R: 2-tuple (x, y)
# d: distace from R to the point returned
# theta: orientation of the robot
# beta: angle between the front part of the robot and the point returned
def locate_point(R, d, theta, beta):
	phi = normalize_angle(theta + beta)
	alpha = 0
	
	if 0 <= phi and phi < _r_90: alpha = phi
	elif _r_90 <= phi and phi < _r_180: alpha = _r_180 - phi
	elif _r_180 <= phi and phi < _r_270: alpha = phi - _r_180
	else: alpha = _r_360 - phi
	
	dx = d*cos(alpha)
	dy = d*sin(alpha)
	
	if 0 <= phi and phi < _r_90: return R[_X] + dx, R[_Y] + dy
	if _r_90 <= phi and phi < _r_180: return R[_X] - dx, R[_Y] + dy
	if _r_180 <= phi and phi < _r_270: return R[_X] - dx, R[_Y] - dy
	return R[_X] + dx, R[_Y] - dy

# Returns how many degrees the robot has to turn to face the point P.
# Returns a value: -180 <= angle <= 180 (degrees)
# R, theta: position in mm and orientation in radiants of the robot
# 0 <= theta < 2*pi
# P: the point we want the robot to point to
def turning_angle(R, theta, P):
	P = map(lambda x: 1.0*x, P)
	R = map(lambda x: 1.0*x, R)
	theta = 1.0*theta
	
	incrx = P[_X] - R[_X]
	incry = P[_Y] - R[_Y]
	
	alpha = 0
	if P[_Y] == R[_Y]:
		if P[_X] > R[_X]: alpha = 0
		else: alpha = pi
	elif P[_X] == R[_X]:
		if P[_Y] > R[_Y]: alpha = pi/2
		else: alpha = 3*pi/2
	else:
		if P[_X] > R[_X]:
			if P[_Y] > R[_Y]: alpha = atan(incry/incrx)
			else: alpha = -atan(incrx/incry) + 3.0*pi/2.0
		else:
			if P[_Y] > R[_Y]: alpha = -atan(incrx/incry) + pi/2.0
			else: alpha = atan(incry/incrx) + pi
	
	if alpha > theta:
		if alpha - theta < pi: phi = alpha - theta
		else: phi = -(theta + 2.0*pi - alpha)
	else:
		if theta - alpha < pi: phi = -(theta - alpha)
		else: phi = alpha + 2.0*pi - theta
	
	return phi

# Returns the smallest angle phi between alpha and beta (from alpha to beta)
# alpha and beta must be normalized
# post -180 <= phi <= 180
def smallest_angle(alpha, beta):
	phi = 0

	if beta > alpha:
		if beta - alpha < pi: phi = beta - alpha
		else: phi = -(alpha + 2.0*pi - beta)
	else:
		if alpha - beta < pi: phi = -(alpha - beta)
		else: phi = beta + 2.0*pi - alpha

	return phi

# Calculates the new position and orientation of the robot at a previous
# position R (in mm) and orientation theta (in radians) after the wheels
# have moved an increment of dl and dr mm respectively. If norm is True
# the orientation returned is normalized.
# D: distance between the two wheels
def odometry(R, theta, D, dl, dr, norm = True):
	ds = (dr + dl)/2.0
	dtheta = (dl - dr)/D
	
	next_theta = normalize_angle(theta + dtheta)

	if norm: phi = normalize_angle(theta + dtheta/2.0)
	else: phi = theta + dtheta/2.0
	
	dx = ds*cos(phi)
	dy = ds*sin(phi)
	
	next_R = [R[_X] + dx, R[_Y] + dy]
	return next_R, next_theta

# Returns the distance from the point pm to the rect through p1 and p2.
def distance_point_to_rect(p1, p2, pm):
	x1 = 1.0*p1[_X]
	y1 = 1.0*p1[_Y]
	x2 = 1.0*p2[_X]
	y2 = 1.0*p2[_Y]
	xm = 1.0*pm[_X]
	ym = 1.0*pm[_Y]
	
	num = abs( (y2 - y1)*xm - (x2 - x1)*ym + x2*y1 - y2*x1 )
	den = sqrt( (y2 - y1)**2.0 + (x2 - x1)**2.0 )
	return num/den

#
# POLYLINE ALGORITHMS
# http://www.codeproject.com/Articles/114797/Polyline-Simplification
#

# Smoothes a given list of points (x, y-coordinates) approximated with a
# polyline.
def smooth_path(path, tol = 5.0):
	n = len(path)
	if n == 0: return []
	
	smoothed_path = [path[0]]
	i0 = 0
	i1 = 1
	while i1 + 1 < n:
		d = distance_point_to_rect(smoothed_path[i0], path[i1 + 1], path[i1])
		if d > tol:
			smoothed_path.append(path[i1])
			i0 += 1
		
		i1 += 1
	
	if i1 + 1 == n: smoothed_path.append(path[i1])
	
	return smoothed_path

