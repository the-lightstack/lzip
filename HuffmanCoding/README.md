# Implementation of Huffman Coding/Huffman Tree in python

# What's so great about it?
 - Also works on smaller files
 - compression rates up to 87% ! (and even more under unrealistic circumstances :) )

# Format of lzip files
1 bytes - Magic Byte of lzip file \[0x23] [for checking if file is actual lzip]
1 byte - length of following bit alignments
n bits - bit alignments to fill up to full bytes
2 bytes - Length of coming huffmann tree
n bytes - The serialized huffmann tree [which holds bit - char assignment]
n bytes - The actual encoded data using the tree

# Usage 

## Compress file
	lzip -c <file to compress> 

## Uncompress file
	lzip -d <file to uncompress>

# TODO 
 [] Add `-o` parameter to define output file
