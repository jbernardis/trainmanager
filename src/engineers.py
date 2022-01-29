

class Engineers():
	def __init__(self):
		fn = "engineers.txt"
		try:
			with open(fn, "r") as x:
				self.engineers = [e.strip() for e in x.readlines()]
					
		except FileNotFoundError:
			print("File not found: %s" % fn)
			exit(1)
			
		self.ex = 0
		
	def __len__(self):
		return len(self.engineers)

	def __iter__(self):
		self.ex = 0
		return self
	
	def __next__(self):
		if self.ex >= len(self.engineers):
			raise StopIteration
		
		rv = self.engineers[self.ex]
		self.ex += 1
		return rv