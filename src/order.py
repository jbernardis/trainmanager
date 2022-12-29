import json

class Order():
	def __init__(self, fn):
		self.filename = fn
		with open(fn, "r") as fp:	
			self.json = json.load(fp)

		self.order  = [t for t in self.json["order"]]
		self.extras = [t for t in self.json["extras"]]
					
		self.ox = 0
		
	def getOrder(self):
		return self.order
	
	def getExtras(self):
		return self.extras
	
	def isExtraTrain(self, tid):
		return tid in self.extras
		
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
		self.json["order"] = [x for x in no]
		self.order  = [t for t in self.json["order"]]
	
	def setNewExtras(self, nex):
		self.json["extras"] = [x for x in nex]
		self.extras  = [t for t in self.json["extras"]]
		
	def save(self):
		with open(self.filename, "w") as fp:
			json.dump(self.json, fp, indent=4, sort_keys=True)
		
	def saveas(self, fn, schedule, extra):
		j = {"order": schedule, "extras": extra}
		with open(fn, "w") as fp:
			json.dump(j, fp, indent=4, sort_keys=True)

