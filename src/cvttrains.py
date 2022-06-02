import json
import os

with open(os.path.join("trains", "trains.json"), "r") as fp:	
	trains = json.load(fp)
	
for tid in trains:
	trn = trains[tid]
	trn["origin"] = {}
	trn["origin"]["loc"] = None
	trn["origin"]["track"] = None
	trn["terminus"] = {}
	trn["terminus"]["loc"] = None
	trn["terminus"]["track"] = None
	trn["normalloco"] = None
		
with open(os.path.join("trains", "newtrains.json"), "w") as fp:
	json.dump(trains, fp, indent=4, sort_keys=True)