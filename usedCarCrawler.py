import json
from crawling import crawling

with open("json/brandModel.json") as data_file:
	bm_data = json.load(data_file)
with open("json/zipcodeNY.json") as data_file:
	zipNY = json.load(data_file)
with open("json/zipcodeNJ.json") as data_file:
	zipNJ = json.load(data_file)
with open("json/zipcodeCA.json") as data_file:
	zipCA = json.load(data_file)

bm_dict = {}
for d in bm_data:
        bm_dict[d["brand"]] = d["model"]

rep_zipNY = set()
rep_zipNJ = set()
rep_zipCA = set()

for key, val in zipNY.items():
	rep_zipNY.add(val)

for key, val in zipNJ.items():
	rep_zipNJ.add(val)

for key, val in zipCA.items():
	rep_zipCA.add(val)

#total 711 models
#one state at a time
#in the order of NJ, NY, CA
for zipcode in rep_zipNJ:
	for brand, model in bm_dict.items():
		for m in model:
			crawling(brand.lower(), m.lower(), zipcode)