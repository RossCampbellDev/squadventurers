#!/bin/bash
./getChapters.py -f ../all.txt -o chapters
./jsonify.py -f ../all.txt -o allJSON
./augmentify.py -f allJSON -d bibliography -c chapters -o ../chapters/AllPages
