#!/usr/bin/env python3
import sys
import bitstream
from bitstream import BitStream
import json
import struct

MAGIC_BYTE = b"\x23"

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

def zipContent(tree,data):
	zipped = BitStream()
	for i in data:
		cleanWrite(zipped,tree.find(i))		

	print("zipContent ",zipped)
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
			serializedTree.write(node.letter.to_bytes(1,"big"))
		else:
			serializedTree.write(False)
			recGenBinary(node.child1)
			recGenBinary(node.child2)
	recGenBinary(node)
	#print(serializedTree)


	# Filling up bits before 1 until it is divisible by 8
	a = len(serializedTree)
	fillersLeft = a-((a//8+1)*8) # Will yield negative number
	filler = BitStream()	
	for i in range(-fillersLeft):
		filler.write(True)
	#print("filler:",filler)
	print("Length of tree:",len(serializedTree))	
	filler.write(serializedTree)

	return filler


def treeFromSerialized(stream):
	# All nodes will have a value of -1

	def decodeChild(stream):
		identifier = stream.read(bool,1)[0]
		if identifier:
			node = Node(-1,None,None,stream.read(bytes,1))	
			return node
		elif not identifier:
			node = Node(-1,decodeChild(stream),decodeChild(stream),None)
			return node
	# Doing this since we don't have to manually create root node 
	while True:
		if stream.read(bool,1)[0] == False:
			break
	tree = Node(-1,decodeChild(stream),decodeChild(stream),None)
	return tree


def compressData(data):
	# Create Tree with data
	tree = createTree(data)
	# Serialize Tree
	serialized_tree = binTreeToBinary(tree)
	length_of_tree = len(serialized_tree)//8	
	print("Length of serialized Tree:",length_of_tree)

	# Get zipped data
	zipped = zipContent(tree,data)	
	print("compressing length of zipped data:",len(zipped))

	# Data alignment bits	
	a = len(zipped)
	data_align_bits = -(a-((a//8+1)*8))
	print("Data alignment bits:",data_align_bits)
	
		
	# Creating Output stream
	zip_file = BitStream()
	zip_file.write(MAGIC_BYTE)
	# Writing bits for alignment to be read
	zip_file.write(data_align_bits.to_bytes(1,"big"))
	# Putting actual alignment bits in stream
	for i in range(data_align_bits):
		zip_file.write(False) 

	# Writing length of tree (2 bytes) ( len in bytes)
	# Reverse is struct.unpack(">H",<2_bytes>)[0]
	zip_file.write(length_of_tree.to_bytes(2,"big"))
	# Planting acutal tree :)
	zip_file.write(serialized_tree)

	# And now the zipped data
	zip_file.write(zipped)
	
	return zip_file.read(bytes)


def decompressDataTree(tree,stream):
	data = b""
	cur_node = tree
	while len(stream)>0:	
		way_stone = stream.read(bool,1)[0]
		if not way_stone: # Go left
			cur_node = cur_node.child1
			if cur_node.letter:
				data += cur_node.letter	
				cur_node = tree
		else:
			cur_node = cur_node.child2
			if cur_node.letter:
				data += cur_node.letter
				cur_node = tree
	
	return data
	

def uncompressData(data):
	stream = BitStream(data)

	magic_byte = stream.read(bytes,1)
	if magic_byte != MAGIC_BYTE:
		exit("Not a lzip file!")

	_r_data = stream.read(bytes,1)
	print("Reading one byte (align length)")
	alignment_bits_len = int.from_bytes(_r_data,"big")

	print("Reading ",alignment_bits_len,"bits (byte alignment)")
	for i in range(alignment_bits_len):
		# Means alignment bit is wrong
		if stream.read(bool,1)[0] == True: 
			print("ERROR OCCURED, Alignment bit was 1")
	print("Reading two bytes (length of bin tree)")
	bin_tree_length = struct.unpack(">H",stream.read(bytes,2))[0]
	print("Length of binary tree")

	tree_stream = stream.read(bin_tree_length*8)
	tree = treeFromSerialized(tree_stream)
	print("t.c1.c1.l",tree.child1.child1.letter)
	
	# Reading rest of data	
	print("Reading rest of data")
	zipped_data = stream.read()
	print("Length of zpped data:",len(zipped_data))

	plain_data = decompressDataTree(tree,zipped_data)
	
	return plain_data		
	
	
	

def main():
	try:
		sample_file = sys.argv[2]
	except:
		exit("You have to supply file to be compressed.")
	with open(sample_file,"rb") as f:
		sample_file_contents = f.read()
	'''	
	tree = createTree(sample_file_contents)
	tree.display()
	zipped = zipContent(tree,sample_file_contents)	
	
	print("Type of shit:",type(tree.child1.child1.letter))

	binTree = binTreeToBinary(tree)
	with open("binary_tree_serialzed.bt","wb") as f:
		a = binTree.read(bytes)
		f.write(a)
	
	with open("binary_tree_serialzed.bt","rb") as f:
		data = f.read() 
		treeModel = BitStream(data)
	
	desTree = treeFromSerialized(treeModel)
	print(desTree.child1.child2.child1.letter)
	'''

	
	if sys.argv[1] == "-c":
		comp_data = compressData(sample_file_contents)
		with open("out.lzip","wb") as f:
			f.write(comp_data)

	elif sys.argv[1] == "-d":
		with open(sample_file,"rb") as f:
			decomp_data = f.read()
		plain_data = uncompressData(decomp_data)	
		with open("plain_data.bin","wb") as f:
			f.write(plain_data)
		
	
if __name__ == "__main__":
	main()
