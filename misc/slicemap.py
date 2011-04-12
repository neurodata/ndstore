#!/usr/bin/python

print("#")
print("# Tile map for mod_rewrite in Apache")
print("# This is to make CATMAID happy.")
print("#")

for x in xrange(0,1250):
	print("{0}\t{1}".format(x,x+2917))
