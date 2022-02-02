import json

class Locomotives:
	def __init__(self, fn):
		self.filename = fn
		with open(fn, "r") as fp:	
			self.locos = json.load(fp)
		
	def getLocoList(self):
		return list(self.locos.keys())
		
	def getLoco(self, lId):
		if lId not in self.locos:
			return None
		
		return self.locos[lId]
			
