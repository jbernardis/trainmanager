class CompletedTrains:
	def __init__(self):
		self.completedTrains = {}
		
	def clear(self):
		self.completedTrains = {}
		
	def append(self, tid, engineer, loco):
		self.completedTrains[tid] = [engineer, loco]
		
	def __contains__(self, tid):
		return tid in self.completedTrains.keys()

	def __iter__(self):
		self.order = sorted(self.completedTrains.keys())
		self._tx = 0
		return self
		
	def __next__(self):
		if self._tx >= len(self.order):
			raise StopIteration
		
		tr = self.order[self._tx]
		self._tx += 1
		return tr, self.completedTrains[tr]
