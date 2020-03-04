#!/bin/bash

DISTANCE=35

for dir in shape_*; do
	cd $dir
	${HOME}/icqhandler/bin/renderICQCartesian.py SHAPE.txt -$DISTANCE $DISTANCE -$DISTANCE condition0_distance${DISTANCE}_phase0000.png > /dev/null
	cd ..
done
