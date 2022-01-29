import json

class TrainRoster:
	def __init__(self, fn):
		self.filename = fn
		try:
			with open(fn, "r") as fp:	
				tr = json.load(fp)
		except FileNotFoundError:
			print("File not found: %s" % fn)
			exit(1)
			
		self.order = tr["order"]
		self.trains = tr["trains"]

		err = 0		
		for tid in self.order:
			if tid not in self.trains:
				print("Train %s from order list is not in roster" % tid)
				err += 1
		if err != 0:
			exit(1)
			
		for tid in self.order:
			trn = self.trains[tid]
			if trn["steps"][0][0] == "":
				trn["origin"] = trn["steps"][0][1]
			else:
				trn["origin"] = trn["steps"][0][0]
				
			if trn["steps"][-1][0] == "":
				trn["terminus"] = trn["steps"][-1][1]
			else:
				trn["terminus"] = trn["steps"][-1][0]
		
	def getTrainOrder(self):
		return self.order
	
	def getTrain(self, tid):
		if not tid in self.trains:
			return None
		
		return self.trains[tid]
