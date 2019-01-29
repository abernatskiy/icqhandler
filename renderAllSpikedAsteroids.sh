#!/bin/bash

DISTANCE=35

for dir in shape_*; do
	cd $dir
	${HOME}/icqhandler/renderICQCartesian.py SHAPE.txt -$DISTANCE $DISTANCE -$DISTANCE SHAPE.png > /dev/null
	cd ..
done
