import time

class Log:
	def __init__(self):
		self.log = []
		
	def append(self, msg):
		ts = time.strftime('%y/%m/%d-%H:%M:%S', time.localtime())
		self.log.append("%s: %s" % (ts, msg))
		
	def clear(self):
		self.log = []
		
	def __len__(self):
		return len(self.log)

	def __iter__(self):
		self.lx = 0
		return self
	
	def __next__(self):
		if self.lx >= len(self.log):
			raise StopIteration
		
		rv = self.log[self.lx]
		self.lx += 1
		return rv
	
	def saveAs(self, path):
		with open(path, "w") as ofp:
			for ln in self.log:
				ofp.write("%s\n" % ln)
