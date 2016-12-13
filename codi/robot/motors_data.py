
class motors_data:
	
	# -----------------
	# Public attributes
	
	left_rpm = 0
	left_load = 0
	left_position = 0	# mm
	left_speed = 0		# mm/s
	
	right_rpm = 0
	right_load = 0
	right_position = 0	# mm
	right_speed = 0		# mm/s
	
	# --------------
	# Public methods
	
	# Initializes this class.
	# l_rpm: rpm of the left wheel
	# l_load: load of the left wheel
	# l_pos: position in mm of the left wheel
	# l_speed: speed in mm/s of the left wheel
	# r_rpm: rpm of the right wheel
	# r_load: load of the right wheel 
	# r_pos: position in mm of the right wheel
	# r_speed: speed in mm/s of the right wheel
	def __init__(self, l_rpm, l_load, l_pos, l_speed, r_rpm, r_load, r_pos, r_speed):
		self.left_rpm = l_rpm
		self.left_load = l_load
		self.left_position = l_pos
		self.left_speed = l_speed
		self.right_rpm = r_rpm
		self.right_load = r_load
		self.right_position = r_pos
		self.right_speed = r_speed
	
	# ---------------------
	# Public Static methods
	
	# Parses a string and returns a motors_data object with the information
	# extracted from that string.
	# string format:
	# left_rpm left_load left_pos left_speed right_rpm right_load right_pos right_speed
	# example: 0 0 0 0 0 0 0 0
	
	@staticmethod
	def from_simple_string(string):
		values = map(int, string.split(' '))
		l_r = float(values[0])
		l_l = float(values[1])
		l_p = float(values[2])
		l_s = float(values[3])
		r_r = float(values[4])
		r_l = float(values[5])
		r_p = float(values[6])
		r_s = float(values[7])
		return motors_data(l_r, l_l, l_p, l_s, r_r, r_l, r_p, r_s)
	
	# Parses a string and returns a motors_data object with the information
	# extracted from that string.
	# string format:
	# 0.265249013901 | GetMotors LeftWheel RightWheel;Parameter,Value;
	# LeftWheel_RPM,0;LeftWheel_Load%,19;LeftWheel_PositionInMM,-1;
	# LeftWheel_Speed,0;RightWheel_RPM,0;RightWheel_Load%,18;
	# RightWheel_PositionInMM,0;RightWheel_Speed,0
	
	@staticmethod
	def parse_from_string(string):
		motors = string.split(';')
		l_r = float(motors[2].split(',')[1])
		l_l = float(motors[3].split(',')[1])
		l_p = float(motors[4].split(',')[1])
		l_s = float(motors[5].split(',')[1])
		r_r = float(motors[6].split(',')[1])
		r_l = float(motors[7].split(',')[1])
		r_p = float(motors[8].split(',')[1])
		r_s = float(motors[9].split(',')[1])
		return motors_data(l_r, l_l, l_p, l_s, r_r, r_l, r_p, r_s)


