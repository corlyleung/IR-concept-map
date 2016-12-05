import csv
import math
import sys

class Edge: 
	def __init__(self, name):
		self.name = name
		self.depend = []
		self.instance = []

	def show (self):
		print self.name, len(self.depend), len(self.instance)

class Graph:
	def __init__(self):
		self.score = 0
		self.path = []
		self.depth = sys.maxint

	def update(self,depth, path):
		self.score = get_score(depth, path)
		self.path = path
		self.depth = depth

	def print_(self):
		print 'score:' + str(self.score)
		print 'path' + str(self.path)
		print 'depth' + str(self.depth)

	def replace(self, other):
		self.score = other.score
		self.path = other.path
		self.depth = other.depth

class Result:
	def __init__(self):
		self.b_sol = None
		self.nb_sol = None

	def update(self, other):
		if other == None:
			return
		if self.nb_sol == None:
			self.nb_sol = other.nb_sol
		elif other.nb_sol != None:
			depth = self.nb_sol.depth
			if depth < other.nb_sol.depth:
				depth = other.nb_sol.depth
			self.nb_sol.update(depth, self.nb_sol.path + other.nb_sol.path)

		if self.b_sol == None:
			self.b_sol = other.b_sol
		elif other.b_sol != None:
			depth = self.b_sol.depth
			if depth < other.b_sol.depth:
				depth = other.b_sol.depth
			self.b_sol.update(depth, self.b_sol.path + other.b_sol.path)
  
	def print_(self):
		print '-------------background---------'
		if self.b_sol != None:
			self.b_sol.print_()

		print '-------------normal---------'
		if self.nb_sol != None:
			self.nb_sol.print_()

def get_score(depth, path):
	return math.pow(len(path), -1 * depth)

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
	return cal_cost_helper(concepts, source, background)

def cal_cost_helper (concepts, source, background):
	result = Result()

	#stop parsing because background
	if source in background:
		result.b_sol = Graph()
		result.b_sol.update(1,[source])
		return result

	# source
	if source not in concepts:
		result.nb_sol = Graph ()
		result.nb_sol.update(1,[source])
		return result

	depends = concepts[source].depend
	depends_depth = 0
	depends_path = []
	for child_dep in depends:
		child_result = cal_cost_helper(concepts, child_dep, background)
		result.update(child_result)

	instances = concepts[source].instance
	if len(instances) == None:
		return result

	temp_sol = None
	for child_inst in instances:
		child_result = cal_cost_helper(concepts, child_inst, background)
		if temp_sol == None:
			temp_sol = child_result
			continue
		if child_result.nb_sol == None:
			child_result.nb_sol == temp_sol.nb_sol
		elif temp_sol.nb_sol != None and temp_sol.nb_sol.score < child_result.nb_sol.score:
			temp_sol.nb_sol = child_result.nb_sol
			temp_sol.nb_sol.update(temp_sol.nb_sol.depth + 1, temp_sol.nb_sol.path.append(cur_inst))

		if child_result.b_sol == None:
			child_result.b_sol == temp_sol.b_sol
		elif temp_sol.b_sol != None and temp_sol.b_sol.score < child_result.b_sol.score:
			temp_sol.b_sol = child_result.b_sol
			temp_sol.b_sol.update(temp_sol.b_sol.depth + 1, temp_sol.b_sol.path.append(cur_inst))

	result.update(temp_sol)
	return result

concepts = make_graph("test_concept.csv")
to_learn = "vector_space_model"
background = set(["tf_idf_weighting"])
result = cal_cost(concepts, to_learn, background)
result.print_()


