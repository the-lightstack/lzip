# Implementation of Huffman Coding/Huffman Tree in python

# What's so great about it?
 - Also works on smaller files
 - compression rates up to 87%! (normally around 50%) (and even more under unrealistic circumstances :) )

# Format of lzip files
```
1 bytes - Magic Byte of lzip file \[0x23] [for checking if file is actual lzip]
1 byte - length of following bit alignments
n bits - bit alignments to fill up to full bytes
2 bytes - Length of coming huffmann tree
n bytes - The serialized huffmann tree [which holds bit - char assignment]
n bytes - The actual encoded data using the tree
```

# Installation

	git clone https://github.com/the-lightstack/lzip.git
	sudo mv ./lzip/lzip /usr/bin
	pip3 install bitstream


# Usage 

## Get Help
	lzip -h 

## Compress file
	lzip -c <file to compress> 
> Default output to **out.lzip**

## Uncompress file
	lzip -d <file to uncompress>
> Default output to **plain\_data.txt**	

## Define output file 
	lzip [-d/-c] <file> -o <filename>
> Writes output to specified file


# TODO 
[X] Add `-o` parameter to define output file
[X] Fix failure when encountering null-bytes ( which prevents from zipping most non-text files)
	>> Bytes stored as numbers, so null byte = 0; if 0 accidentally same as if None, so did direct comparision with None and fixed problem :)

