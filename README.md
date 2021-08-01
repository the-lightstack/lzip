# LZip - Just another Zip implementation

# What's so great about it?
 - Also works on smaller files
 - compression rates up to 87%! (normally around 50%) (and even more under unrealistic circumstances :) )

# Format of lzip files
```
1 bytes - Magic Byte of lzip file [0x23] [for checking if file is actual lzip]
1 byte - length of following bit alignments
n bits - bit alignments to fill up to full bytes
2 bytes - Length of coming huffmann tree
n bytes - The serialized huffmann tree [which holds bit - char assignment]
n bytes - The actual encoded data using the tree
```

# Installation
	
	git clone https://github.com/the-lightstack/lzip.git
	sudo mv ./lzip/lzip /usr/bin
	pip3 install -r requirements.txt


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

# Compression Rates
- Text files: ~ 50%
- ELF-Binaries: ~ 35%
- Images: ~ 2-5%


# TODO 

- [x] Add `-o` parameter to define output file
- [x] Fix failure when encountering null-bytes ( which prevents from zipping most non-text files)

