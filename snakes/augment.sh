#!/bin/bash
./getChapters.py -f ../all.txt -o chapters
./jsonify.py -f ../all.txt -o allJSON
for f in ../bio/*; do
	./augmentify.py -f $f -d bibliography -c chapters -o ../menagerie/$(basename $f)
done
./augmentify.py -f allJSON -d bibliography -c chapters -o ../chapters/AllPages
