import heapq

class priority_queue:
	
	# ------------------
	# Private attributes
	
	_elements = []
	
	# --------------
	# Public methods
	
	def __init__(self):
		self._elements = []
	
	def empty(self):
		return len(self._elements ) == 0
	
	def put(self, item, priority):
		heapq.heappush(self._elements , (priority, item))
	
	def get(self):
		return heapq.heappop(self._elements)[1]
