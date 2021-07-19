#!/usr/bin/env python3
import sys
#from collections import OrderedDict
from bitstream import BitStream

class Node:
	current_traversal = ""
	recursion_done = False
	def __init__(self,val,child1,child2,letter=None):
		# The combined frequency of all the child nodes
		self.value = val

		# Both child nodes
		if child1 and child2:
			self.child1 = child1	
			self.child2 = child2

		# If it has no child nodes it is a bottom node ->
		# it has to have a letter associated with it
		self.letter = letter
	
	def display(self):
		if not self.letter:
			self.child1.display()
			self.child2.display()
	
			print(self.value)
		else:
			print(self.letter)


	def recFind(self,target):
		if not Node.recursion_done:
			if self.letter == target:
				Node.recursion_done = True
				return 
			if not self.letter:			
				# Recursive Find, doesn't do setup
				if not Node.recursion_done:
					Node.current_traversal += "0"
					self.child1.recFind(target)	
					if not Node.recursion_done:
						Node.current_traversal = Node.current_traversal[:-1]

				if not Node.recursion_done:
					Node.current_traversal += "1"
					self.child2.recFind(target)
					if not Node.recursion_done:
						Node.current_traversal = Node.current_traversal[:-1]
			
	
	def find(self,target):
		Node.current_traversal = ""
		Node.recursion_done = False
		self.recFind(target)
		return Node.current_traversal
	

	
	def __str__(self):
		return "{} - {}\n".format(self.letter,self.value)
	def __repr__(self):
		return "{} - {}\n".format(self.letter,self.value)
		


def count_chars(text):
	pairs = {}
	for i in text:
		if pairs.get(i):
			pairs[i] += 1
		else:
			pairs[i] = 1
	# Sorting it
	#pairs = OrderedDict(sorted(pairs.items(),key=lambda x:x[1],reverse=True))
	return pairs


def _transformToNodes(pairs):
	nodes = []
	while pairs.items():
		i = pairs.popitem()
		nodes.append(Node(i[1],None,None,letter=i[0]))
	return nodes
	
	
def createTree(file_contents):
	pairs_d = count_chars(file_contents)	
	# Convert it to list of single nodes	
	nodes_list = _transformToNodes(pairs_d)
	# Sort the nodes
	nodes_list = sorted(nodes_list,key=lambda x:x.value,reverse=True)
	
	while len(nodes_list) > 1:
		n1 = nodes_list.pop()
		n2 = nodes_list.pop()

		n_node = Node(n1.value+n2.value,n1,n2)	
		nodes_list.append(n_node)
		# Resorting it 
		nodes_list = sorted(nodes_list,key=lambda x:x.value,reverse=True)
	
	return nodes_list[0]

def cleanWrite(stream,string):
	for i in string:
		stream.write(bool(int(i)),bool)
	

def zipContent(tree,data):
	#print(tree.find(sys.argv[2]))
	zipped = BitStream()
	for i in data:
		cleanWrite(zipped,tree.find(i))		

	print(zipped)
	return zipped

def binTreeToNums(tree):
	"""
	The binary tree will be transformed into a list of
	values and data in the format '<exists><data>'
	so two consecutive bytes for each element in the tree,
	branches with only one child will have the other one be filled
	with doesn't exist + null byte (so '\x00\x00)
	If data exists, we will have \x01<data>
	"""
	data = []




def main():
	try:
		sample_file = sys.argv[1]
	except:
		exit("You have to supply file to be compressed.")
	with open(sample_file,"r") as f:
		sample_file_contents = f.read()
	
	tree = createTree(sample_file_contents)
	#tree.display()
	zipped = zipContent(tree,sample_file_contents)	

if __name__ == "__main__":
	main()
