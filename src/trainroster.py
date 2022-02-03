import json
import copy

import pprint

class TrainRoster:
	def __init__(self, fn):
		self.filename = fn
		with open(fn, "r") as fp:	
			self.trains = json.load(fp)
			
		for tid in self.trains:
			trn = self.trains[tid]
			if trn["steps"][0][0] == "":
				trn["origin"] = trn["steps"][0][1]
			else:
				trn["origin"] = trn["steps"][0][0]
				
			if trn["steps"][-1][0] == "":
				trn["terminus"] = trn["steps"][-1][1]
			else:
				trn["terminus"] = trn["steps"][-1][0]
				
	def getTrainList(self):
		return list(self.trains.keys())
	
	def getTrain(self, tid):
		if not tid in self.trains:
			return None
		
		return self.trains[tid]
	
	def save(self):
		newJson = copy.deepcopy(self.trains)
		for tid in newJson:
			trn = newJson[tid]
			del(trn["origin"])
			del(trn["terminus"])

		with open(self.filename, "w") as fp:
			json.dump(newJson, fp, indent=4, sort_keys=True)
