# -*- coding: utf-8 -*-

import os
import json

def create_textfiles(in_fname='dataset', out_dname='texts'):
	# create output directory
	if not os.path.isdir(out_dname):
		os.mkdir(out_dname)

	# parse the dataset
	with open(in_fname, 'r') as f:
		dataset = f.read()
		dataset = dataset.split(',\n')
		dataset = [ data.split(',',3) for data in dataset ]

	# create textfiles extracted name and text
	for data in dataset:
		with open(os.path.join(out_dname,data[0]), 'w') as f:
			f.write(data[3])


def create_jsonfile(in_fname='dataset', out_fname='jsonfile.json', out_dname='json'):
	# create output directory
	if not os.path.isdir(out_dname):
		os.mkdir(out_dname)

	# parse the dataset
	with open(in_fname, 'r') as f:
		dataset = f.read()
		dataset = dataset.split(',\n')
		dataset = [ data.split(',',3) for data in dataset ]

	# create jsonfile extracted name and text
	dictdata = {}
	for data in dataset:
		dictdata[data[0]] = data[3]

	jsondata = json.dumps(dictdata, sort_keys=True, ensure_ascii=False, indent=2)
	with open(os.path.join(out_dname,out_fname), 'w') as f:
		f.write(jsondata)

