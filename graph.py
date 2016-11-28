import csv
import math

class Edge: 
	def __init__(self, name):
		self.name = name
		self.depend = []
		self.instance = []

	def show (self):
		print self.name, len(self.depend), len(self.instance)

def make_graph(file_name):
	concepts = {}
	with open(file_name, 'rU') as file:
		data = csv.DictReader(file, delimiter = ',')
		for row in data:
			source = row["Source"]
			target = row["Target"]
			edge = row["Edge Type"]
			if source not in concepts:
				concepts[source] = Edge(source)
			if edge == "depend_on":
				concepts[source].depend.append(target)
			else:
				concepts[source].instance.append(target)
	return concepts

def cal_cost (concepts, source, background):
	path = []
	return cal_cost_helper(concepts, source, background, 1, path), path

def cal_cost_helper(concepts, source,  background, curWeigh, path):
	path.append(source)
	if source not in concepts:
		return curWeigh, path
	curEdge = concepts[source]
	min_cost = len(curEdge.depend)
	if len(curEdge.instance) == 0:
		for cur_depend in curEdge.depend:
			if cur_depend in background:
				min_cost -= 1
				continue
			path.append(cur_depend)
		return curWeigh * min_cost, path
	for child in curEdge.instance:
		if child in background:
			return 0
		child, temp_path = cal_cost_helper(concepts, child, background, curWeigh + 1, [])
		print child, temp_path
		if child < min_cost:
			min_cost = child
			path[len(path)-1] = temp_path
			print min_cost, temp_path
	return curWeigh * min_cost, path

concepts = make_graph("test_concept.csv")
to_learn = "vector_space_model"
background = set(["tf_idf_weighting"])
cost, path = cal_cost(concepts, to_learn, background)
print cost, path

