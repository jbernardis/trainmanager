

class Order():
	def __init__(self, fn):
		with open(fn, "r") as x:
			self.order = [e.strip() for e in x.readlines()]
					
		self.ox = 0
		
	def getTid(self, tx):
		if tx < 0 or tx >= len(self.order):
			return None
		
		return self.order[tx]
		
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
	
	def setNewOrder(self, no):
		self.order = [x for x in no]