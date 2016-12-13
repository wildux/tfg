from utils import odometry, deg2rad, rad2deg, normalize_angle, smallest_angle, turning_angle
from utils import _X, _Y, _diameter
from motors_data import motors_data
import socket, time
from copy import deepcopy
from math import sqrt

class neato:

	# ------------------
	# Private attributes
	
	# Parameters used for the connection with the robot.
	_socket = None
	_rbuffer = None
	_ip = ""
	_port = 0
	
	# Position of the robot.
	_pos = [0, 0] # x, y. In mm!
	_theta = 0
	
	# --------------
	# Public methods
	
	# Initializes this class with the ip and port needed to communicate
	# with the robot.
	def __init__(self, ip, port):
		self._ip = ip
		self._port = port
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	# Get ip and port of the robot.
	def get_ip(self): return self._ip
	def get_port(self): return self._port
	
	# Send a message to the robot.
	def send_msg(self, msg):
		self._socket.sendall(msg + chr(10))
		return self.get_msg()
	
	# Recive a message from the robot.
	def get_msg(self):
		resp = ""
		self._rbuffer = ""

		while not resp:
			try:
				self._rbuffer += self._socket.recv(8192)
				if chr(10) in self._rbuffer:
					resp, empty_string = self._rbuffer.split(chr(10),1)

			except Exception as e:
				print e
		
		return resp
	
	# Connect with the robot. Open a socket between the computer and the
	# robot using the ip and port passed as parameters in the constructor.
	# data_mode:
	#     default: listener
	#     other values: constant, moody
	def connect(self, data_mode = "listener"):
		# Connect the socket to the port where the server is listening
		server_address = (self._ip, self._port)
		print "connecting to %s port %s" % server_address
		self._socket.connect(server_address)
		
		# Handshaking - Get Serial OK
		data = self.get_msg()
		if "OK" in data:
			print "Serial port (Raspberry-Neato) OK"
			print "    Sending DataMode", data_mode
			datamode = self.send_msg("DataMode " + data_mode)
			
			print "    Sending JoystickMode Off"
			joystickmode = self.send_msg('JoystickMode Off')
			
			return True, datamode, joystickmode
		
		# connection failed
		self._socket.close()
		print "Serial port (Raspberry-Neato) not found, please check",
		print "cable connection and Neato power on, and restart Raspberry"
		return False, "", ""
	
	# Closes the connection with the robot.
	def close(self):
		self._socket.sendall("Close" + chr(10))
		self._socket.close()
	
	# Move the robot telling what distance (mm) the motors have to travel
	# and at what speed (mm/s).
	# left: left wheel distance (mm)
	# right: right wheel distance (mm)
	# s: speed (mm/s)
	def advance(self, left, right, s, wait = False, wait_offset = 0):
		m = self.send_msg("SetMotor LWheelDist " + str(left) + " RWheelDist " + str(right) + " Speed " + str(s))
		
		wait_time = 0
		if wait: time.sleep(1.0*left/s + wait_offset)
		elif s != 0: wait_time = 1.0*left/s
		
		return m, wait_time

	# Precisely moves the robot telling what distance (mm) the motors have to travel
	# and at what speed (mm/s).
	# P: position the robot has to reach (in mm)
	# s: speed (mm/s)
	# wait_offset: extra time to wait after each turn and advance
	# max_error: maximum distance from P
	def advance_precise(self, P, s, wait_offset = 0, max_error = 30.0):
		[cx, cy], theta = self._pos, self._theta
		nx, ny = P[_X], P[_Y]

		distance = sqrt((nx - cx)**2.0 + (ny - cy)**2.0)
		motors_cur = motors_data.parse_from_string(self.get_motors())

		while distance > max_error:
			motors_pre = motors_cur

			angle_gir = turning_angle([cx, cy], theta, [nx, ny])
			self.turn_precise(rad2deg(angle_gir), 50, wait_offset)

			motors_cur = motors_data.parse_from_string(self.get_motors())
			dl = motors_cur.left_position - motors_pre.left_position
			dr = motors_cur.right_position - motors_pre.right_position
			self.set_next_position(dl, dr)
			[cx, cy], theta = self._pos, self._theta

			self.advance(distance, distance, s, True, wait_offset)

			motors_pre = deepcopy(motors_cur)
			motors_cur = motors_data.parse_from_string(self.get_motors())
			dl = motors_cur.left_position - motors_pre.left_position
			dr = motors_cur.right_position - motors_pre.right_position
			self.set_next_position(dl, dr)
			[cx, cy], theta = self._pos, self._theta
			distance = sqrt((nx - cx)**2 + (ny - cy)**2)

	# Turns the robot a certain amount of degrees around its center.
	# phi: angle in degrees that the robot will turn on itself
	#      phi > 0 -> clockwise turn
	#      phi < 0 -> counter-clockwise turn
	# s: speed (mm/s)
	# wait: wait until the movement is completed
	# wait_offset: extra time to wait after the movement is completed
	def turn(self, phi, s, wait = False, wait_offset = 0):
		if phi == 0: return "", 0.0

		l = abs(deg2rad(phi))*_diameter/2.0
		msg = ""

		if phi > 0: msg = self.advance(l, -l, s)
		elif phi < 0: msg = self.advance(-l, l, s)

		wait_time = 0
		if wait: time.sleep(1.0*l/s + wait_offset)
		elif s != 0: wait_time = 1.0*l/s

		return msg, wait_time

	# Precisely turns the robot a certain amount of degrees around its center.
	# phi: angle in degrees that the robot will turn on itself
	#      phi > 0 -> clockwise turn
	#      phi < 0 -> counter-clockwise turn
	# s: speed (mm/s)
	# wait_offset: extra time to wait after the movement is completed
	# max_error: maximum radians from the current orientation plus phi
	# max_it: maximum number of iterations (5 is optimal)
	def turn_precise(self, phi, s, wait_offset = 0, max_error = 0.0085, max_it = 5):
		if abs(phi) <= 0.487: return "", 0.0

		phi = deg2rad(phi)
		last_orientation_norm = normalize_angle(phi)

		current_orientation = 0
		div = 1
		it = 0
		motors_end = motors_data.parse_from_string(self.get_motors())

		while abs(phi) >= max_error and it <= max_it:

			motors_begin = motors_end
			self.turn(rad2deg(phi), s/div, True, wait_offset)
			motors_end = motors_data.parse_from_string(self.get_motors())

			dl = motors_end.left_position - motors_begin.left_position
			dr = motors_end.right_position - motors_begin.right_position

			_, degrees_of_turn = odometry(self._pos, 0.0, _diameter, dl, dr, False)
			current_orientation += degrees_of_turn
			current_orientation_norm = normalize_angle(current_orientation)

			phi = smallest_angle(current_orientation_norm, last_orientation_norm)
			div += 0.5
			it += 1

	# Reads the state of the motors of the robot.
	def get_motors(self): return self.send_msg('GetMotors LeftWheel RightWheel')

	# Stops the robot wherever it is
	def stop(self): return self.advance(1, 1, 1)
	
	# Performs an LDS scan.
	def get_lds(self): return self.send_msg('GetLDSScan')

	# Sets the initial position (in mm) and the orientation (in radians)
	# of the robot.
	# initial_position: a list with two values: the initial x and y coordinates in mm
	# initial_orientation: the initial orientation of the robot in radians
	def set_initial_position(self, initial_position, initial_orientation):
		self._pos = initial_position
		self._theta = initial_orientation
	
	# Use odometry (the increments of the positions of the wheels) to
	# determine the new position and the orientation of the robot.
	# dl: increment of the position of the left wheel
	# dr: increment of the position of the right wheel
	def set_next_position(self, dl, dr):
		self._pos, self._theta = odometry(self._pos, self._theta, _diameter, dl, dr)
	
	def get_position(self): return self._pos
	def get_orientation(self): return self._theta

neatoA = neato("172.16.10.5", 20000)
neatoB = neato("172.16.10.5", 20001)
neatoC = neato("172.16.10.5", 20002)
neatoD = neato("172.16.10.5", 20003)
neatoE = neato("172.16.10.5", 20004)
neatoF = neato("172.16.10.5", 20005)

