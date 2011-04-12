#!/bin/bash

#
# Small script to call create-tiles.sh over a range of slices.
#

START=2917
END=4150

COUNTER=$START

while [ $COUNTER -le $END ]; do
	python /home/eric/brain/python/create-tiles.py /mnt/data/combined/z$COUNTER /data/brain

	let COUNTER=COUNTER+1
done




#
