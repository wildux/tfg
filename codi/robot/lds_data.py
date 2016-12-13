
class lds_data:
	
	# -----------------
	# Public attributes
	
	class angle_data:
		angle = 0 	# degrees
		dist = 0 	# mm
		intensity = 0
		error_code = 0 # hexadecimal
		
		def __init__(self, a, d, i, ec):
			self.angle = a
			self.distance = d
			self.intensity = i
			self.error_code = ec
	
	angles_values = []
	rotation_speed = 0
	
	# --------------
	# Public methods
	
	# Initializes this class.
	# a_values: list of 360 4-tuples: [(0, 0, 0, 0)*360]
	# rot_speed: scalar
	def __init__(self, a_values, rot_speed):
		self.angles_values = map(lambda (a, d, i, ec): lds_data.angle_data(a, d, i, ec), a_values)
		self.rotation_speed = rot_speed
	
	# ---------------------
	# Public Static methods
	
	# Parses a string and returns a motors_data object with the information
	# extracted from that string.
	# string format:
	# 0 0 0 0 1 0 0 0 2 0 0 0 ... 359 0 0 0 0
	# angle_0 value_1 value_2 value_3
	# angle_1 value_1 value_2 value_3
	# ...
	# angle_359 value_1 value_2 value_3
	# rotation_speed
	@staticmethod
	def from_simple_string(string):
		values = map(int, string.split(' '))
		angles = [[0]*4 for i in xrange(0, 360)]
		i = 0
		while i < 360: # 1440 = 4*360
			angles[i] = float(values[i])
			angles[i + 1] = float(values[i + 1])
			angles[i + 2] = float(values[i + 2])
			angles[i + 3] = float(values[i + 3])
			i += 4
		
		rot_speed = values[360*4]
		return lds_data(angles, rot_speed)
	
	# Parses a string and returns a motors_data object with the information
	# extracted from that string.
	# string format:
	# 0.523147106171 | GetLDSScan;AngleInDegrees,DistInMM,Intensity,ErrorCodeHEX;
	# 0,0,4,8050;
	# 1,0,4,8050;
	# 2,0,4,8050;
	# ...
	# 358,583,452,0;
	# 359,576,544,0;
	# ROTATION_SPEED,4.97
	@staticmethod
	def parse_from_string(string):
		values = string.split(';')
		angles = [[0]*4 for i in xrange(0, 360)]
		
		for i in range (0,360):
			angles[i][0] = float(values[i + 2].split(',')[0])
			angles[i][1] = float(values[i + 2].split(',')[1])
			angles[i][2] = float(values[i + 2].split(',')[2])
			angles[i][3] = float(values[i + 2].split(',')[3])
		
		rot_speed = float(values[362].split(',')[1])
		return lds_data(angles, rot_speed)


