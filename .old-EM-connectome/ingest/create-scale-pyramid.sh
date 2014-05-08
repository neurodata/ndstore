#!/bin/bash

#
# Script to generate the complete scale hierarchy and small image
# for each slice.
#
# The full-resolution tiles (scale=0) need to exist.
#

START=2917
END=4150

COUNTER=$START

while [ $COUNTER -le $END ]; do
	python /home/eric/brain/python/create-scale-pyramid.py /data/brain $COUNTER
	python /home/eric/brain/python/create-small.py /data/brain $COUNTER

	let COUNTER=COUNTER+1
done




#
