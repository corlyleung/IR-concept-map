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
	return cal_cost_helper(concepts, source, background, 0, [])

def cal_cost_helper(concepts, source,  background, depth, path):
	cur_path = []
	cur_path.append(source)
	depth += 1
	#leaf nodes
	if source not in concepts:
		return depth, path + cur_path

	cur_edge = concepts[source]

	#all the depends on path excluding background nodes
	for cur_depend in cur_edge.depend:
		if cur_depend in background:
			continue
		cur_path.append(cur_depend)

	#return value of all depends on
	if len(cur_edge.instance) == 0:
		return depth+1, path + cur_path

	#current max cost of all depends on
	max_cost = math.pow(len(cur_path), -1*depth)

	for child in cur_edge.instance:
		if child in background:
			return depth-1, path
		child_depth, temp_path = cal_cost_helper(concepts, child, background, depth, [])
		child_cost = math.pow(len(temp_path), -1*child_depth)
		if child_cost > max_cost:
			max_cost = child_cost
			cur_path = temp_path
	return depth, path + cur_path

concepts = make_graph("test_concept.csv")
to_learn = "vector_space_model"
background = set(["tf_idf_weighting"])
depth, path = cal_cost(concepts, to_learn, background)
print math.pow(len(path), -1*depth), path

