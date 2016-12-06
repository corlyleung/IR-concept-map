import csv
import math
import sys

class Edge: 
	def __init__(self, name):
		self.name = name
		self.depend = []
		self.instance = []

	def show (self):
		print self.name, self.depend, self.instance

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
		print 'score: ' + str(self.score)
		print 'path: ' + str(self.path)
		print 'depth: ' + str(self.depth)

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

	def add_source(self, source):
		if self.nb_sol != None:
			self.nb_sol.update(self.nb_sol.depth + 1, self.nb_sol.path + [source])
		if self.b_sol != None:
			self.b_sol.update(self.b_sol.depth + 1, self.b_sol.path + [source])
  
	def print_(self):
		print '-------------background---------'
		if self.b_sol != None:
			self.b_sol.print_()

		print '-------------normal---------'
		if self.nb_sol != None:
			self.nb_sol.print_()

def get_score(depth, path):
	return math.pow(len(path), -1.00 * depth)

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

def path_to_graph(concepts, source, background, path, result_map):
	if source not in path:
		print 'error'
		return
	result = Edge(source)
	path.remove(source)
	if source in background or source not in concepts:
		result_map[source] = result
		return
	for child in concepts[source].depend:
		path_to_graph(concepts, child, background, path, result_map)
		result.depend.append(child)
	if len(concepts[source].instance) == 0:
		result_map[source] = result
		return
	intersection = set(concepts[source].instance).intersection(path)
	if len(intersection) != 1:
		print 'error converting'
		print intersection
		result_map[source] = result
		return
	iter0 = iter(intersection)
	child_inst = next(iter0)
	result.instance.append(child_inst)
	path_to_graph(concepts, child_inst, background, path, result_map)
	result_map[source] = result

def write_to_csv(file_name, path_map):
	print 'saving to ' + file_name
	with open(file_name, "wb") as file:
		writer = csv.writer(file, delimiter=',')
		for cur in path_map.keys():
			for child in path_map[cur].depend:
				writer.writerow([cur, child, "depends_on"])
			if len(path_map[cur].instance) != 0:
				writer.writerow([cur, path_map[cur].instance[0], "has_instance"])


def cal_cost (concepts, source, background):
	result = cal_cost_helper(concepts, source, background)
	normal = {}
	back = {}
	if result.nb_sol != None:
		path_set = set(result.nb_sol.path)
		path_set.remove("base")
		path_to_graph(concepts, source, background, path_set, normal)
		write_to_csv("normal.csv", normal)
	if result.b_sol != None:
		path_set = set(result.b_sol.path)
		path_set.remove("base")
		path_to_graph(concepts, source, background, set(result.b_sol.path), back)
		write_to_csv("background.csv", back)
	return normal, back


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
		result.nb_sol.update(1,[source, "base"])
		return result

	depends = concepts[source].depend

	depends_nb_depth = 0
	depends_nb_path = []
	depends_b_depth = 0
	depends_b_path = []
	all_nb = True
	at_least_one_b = False

	for child_dep in depends:
		child_result = cal_cost_helper(concepts, child_dep, background)
		if child_result.nb_sol == None:
				all_nb = False
		if child_result.b_sol != None:
				at_least_one_b = True
		if all_nb == True:
			depends_nb_path = depends_nb_path + child_result.nb_sol.path
			depends_nb_depth = max(depends_nb_depth, child_result.nb_sol.depth)
			if child_result.b_sol != None and child_result.b_sol.score > child_result.nb_sol.score:
				depends_b_path = depends_b_path + child_result.b_sol.path
				depends_b_depth = max(depends_b_depth, child_result.b_sol.depth)
			else:
				depends_b_path = depends_b_path + child_result.nb_sol.path
				depends_b_depth = max(depends_b_depth, child_result.nb_sol.depth)
		elif child_result.b_sol == None:
			depends_b_path = depends_b_path + child_result.nb_sol.path
			depends_b_depth = max(depends_b_depth, child_result.nb_sol.depth)
		elif child_result.nb_sol == None:
			depends_b_path = depends_b_path + child_result.b_sol.path
			depends_b_depth = max(depends_b_depth, child_result.b_sol.depth)
		elif child_result.b_sol.score > child_result.nb_sol.score:
			depends_b_path = depends_b_path + child_result.b_sol.path
			depends_b_depth = max(depends_b_depth, child_result.b_sol.depth)
		else:
			depends_b_path = depends_b_path + child_result.nb_sol.path
			depends_b_depth = max(depends_b_depth, child_result.nb_sol.depth)

	if all_nb == True:
		result.nb_sol = Graph()
		result.nb_sol.update(depends_nb_depth, depends_nb_path)
	if at_least_one_b == True:
		result.b_sol = Graph()
		result.b_sol.update(depends_b_depth, depends_b_path)

	instances = concepts[source].instance
	if len(instances) == 0:
		result.add_source(source)
		return result
	temp_sol = Result()
	for child_inst in instances:
		child_result = cal_cost_helper(concepts, child_inst, background)
		if temp_sol == None:
			temp_sol = child_result
			continue
		if temp_sol.nb_sol == None:
			temp_sol.nb_sol = child_result.nb_sol
		elif child_result.nb_sol != None and temp_sol.nb_sol.score < child_result.nb_sol.score:
			temp_sol.nb_sol = child_result.nb_sol
			temp_sol.nb_sol.update(temp_sol.nb_sol.depth + 1, temp_sol.nb_sol.path.append(cur_inst))

		if temp_sol.b_sol == None:
			temp_sol.b_sol = child_result.b_sol
		elif child_result.b_sol != None and temp_sol.b_sol.score < child_result.b_sol.score:
			temp_sol.b_sol = child_result.b_sol
			temp_sol.b_sol.update(temp_sol.b_sol.depth + 1, temp_sol.b_sol.path.append(cur_inst))

	if len(depends) != 0:
		if result.nb_sol == None:
			temp_sol.nb_sol = None
		if result.b_sol == None:
			temp_sol.b_sol = None
	result.update(temp_sol)
	result.add_source(source)
	return result

if (len(sys.argv) <= 2):
	print 'not enough argument'

concepts = make_graph("test_concept.csv")
to_learn = sys.argv[1]
background = set([])
for idx in range(2, len(sys.argv)):
	background.add(sys.argv[idx])
normal_sol, back_sol = cal_cost(concepts, to_learn, background)
