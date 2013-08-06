#!/bin/bash

File="h5post.py"
host="localhost"
project="kat11_syn1"
path="/home/priya/kat11_hdf5files/anno"


for i in {4277..4280}
do
	echo python $File $host $project $path$i.h5
	
	python $File $host $project $path$i.h5
done	
