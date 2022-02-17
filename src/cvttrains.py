import json
import os

with open(os.path.join("trains", "trains.json"), "r") as fp:	
	trains = json.load(fp)
	
for tid in trains:
	trn = trains[tid]
	if 'extra' not in trn:
		trn['extra'] = False
		
	for step in trn["steps"]:
		step.append(0)
		
with open(os.path.join("trains", "newtrains.json"), "w") as fp:
	json.dump(trains, fp, indent=4, sort_keys=True)