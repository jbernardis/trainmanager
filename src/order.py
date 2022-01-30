

class Order():
	def __init__(self, fn):
		with open(fn, "r") as x:
			self.order = [e.strip() for e in x.readlines()]
					
		self.ox = 0
		
	def __len__(self):
		return len(self.order)

	def __iter__(self):
		self.ox = 0
		return self
	
	def __next__(self):
		if self.ox >= len(self.order):
			raise StopIteration
		
		rv = self.order[self.ox]
		self.ox += 1
		return rv