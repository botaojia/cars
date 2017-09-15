from geopy.distance import great_circle
import sys
import zipcode
import json

seedZipcodes = ["10001", "94043", "07302"]
filenames=["zipcodeNY.txt", "zipcodeCA.txt", "zipcodeNJ.txt"]
outputs=["zipcodeNY.json", "zipcodeCA.json","zipcodeNJ.json"]

for idx, val in enumerate(seedZipcodes):
	seedZipcode = seedZipcodes[idx]
	filename = filenames[idx]
	output = outputs[idx]
	
	if filename == "zipcodeNJ.txt":
		radius = 50
	elif filename == "zipcodeCA.txt":
		radius = 150
	else:
		radius = 100

	with open(filename) as f:
	     zc = f.readlines()
	 # to remove whitespace characters like `\n` at the end of each line
	zc = [x.strip() for x in zc] 

	rep_zipcode = [seedZipcode]
	cover = {}
	cover[seedZipcode] = seedZipcode
	check = set()
	check.add(seedZipcode)

	for z in zc:
		loc_z = zipcode.isequal(z)

		if loc_z is None:
			continue

		for r in rep_zipcode:
			loc_r = zipcode.isequal(r)
			away = great_circle((loc_z.lat, loc_z.lon), (loc_r.lat, loc_r.lon)).miles
			if away <= radius:
				cover[z]=r
				check.add(r)
				break

		if z not in cover:
			rep_zipcode.append(z)
			cover[z]=z
			check.add(z)

	print(rep_zipcode)
	print(len(rep_zipcode))
	print(len(check))

	with open(output, 'w') as fj:
		json.dump(cover, fj)
