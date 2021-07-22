#!/usr/bin/env python3
import sys
import bitstream
from bitstream import BitStream
import json


class Node:
	current_traversal = ""
	recursion_done = False
	def __init__(self,val,child1,child2,letter=None):
		# The combined frequency of all the child nodes
		#self.value = val.to_bytes(1,"big")
		self.value = val

		# Both child nodes
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

def cleanIntWrite(stream,inter):
	s = str(bin(inter))[2:]
	cleanWrite(stream,s)

def zipContent(tree,data):
	#print(tree.find(sys.argv[2]))
	zipped = BitStream()
	for i in data:
		cleanWrite(zipped,tree.find(i))		

	print(zipped)
	return zipped

def dindDeepness(tree):
	global deepest
	deepest = 0

	def recFindDeep(node,score):
		global deepest
		own_score = score + 1
		if own_score > deepest:
			deepest = own_score
		if node.child1:
			recFindDeep(node.child1,own_score)
		if node.child2:
			recFindDeep(node.child2,own_score)

	recFindDeep(tree,0)
	print("Deepness of tree:",deepest)
	return deepest
	

def binTreeToBinary(tree):
	# If not working, maybe one includes the root/tree node, other (deserialize) doesn't => confusion + errors
	# Tree will ALWAYS start with a 1 bit, else it is broken 
	# ( first node cannot be leaf, unless file only has one letter which is stupid :))

	global serializedTree	
	serializedTree = BitStream()	
	node = tree # This is the root node
	def recGenBinary(node):
		# It is a leaf node
		if node.letter:
			serializedTree.write(True)	
			cleanIntWrite(serializedTree,node.letter)
		else:
			serializedTree.write(False)
			recGenBinary(node.child1)
			recGenBinary(node.child2)
	recGenBinary(node)
	print(serializedTree)


	# Filling up bits before 1 until it is divisible by 8
	a = len(serializedTree)
	fillersLeft = a-((a//8+1)*8) # Will yield negative number
	filler = BitStream()	
	for i in range(-fillersLeft):
		filler.write(False)
	print("filler:",filler)
	print("Length of tree:",len(serializedTree))	
	filler.write(serializedTree)

	return filler


def treeFromSerialized(stream):
	# All nodes will have a value of -1

	def decodeChild(stream):
		identifier = bool(stream.read(1))	
		if identifier:
			node = Node(-1,None,None,stream.read(bytes,1))	
			return node
		elif not identifier:
			node = Node(-1,decodeChild(stream),decodeChild(stream),None)
			return node
	# Doing this since we don't have to manually create root node 
	while True:
		if bool(stream.read(1)) == True:
			break
	tree = Node(-1,decodeChild(stream),decodeChild(stream),None)
	return tree
		

def main():
	try:
		sample_file = sys.argv[1]
	except:
		exit("You have to supply file to be compressed.")
	with open(sample_file,"rb") as f:
		sample_file_contents = f.read()
	
	tree = createTree(sample_file_contents)
	tree.display()
	zipped = zipContent(tree,sample_file_contents)	
	
	print("Type of shit:",type(tree.child1.child1.letter))

	binTree = binTreeToBinary(tree)
	with open("binary_tree_serialzed.bt","wb") as f:
		a = binTree.read(bytes)
		print(a)
		f.write(a)
	
	with open("binary_tree_serialzed.bt","rb") as f:
		data = f.read() 
		treeModel = BitStream(data)
	
	desTree = treeFromSerialized(treeModel)
	desTree.display()
	print("Both streams are equal:",a == data)
	print("Both trees equal:",desTree == tree)

	
	
if __name__ == "__main__":
	main()
