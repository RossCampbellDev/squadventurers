#!/bin/bash
echo "------------ GET CHAPTER TILES ------------"
for f in ../books/*; do
	./getChapters.py -f $f -o chapters_$(basename $f)
done

echo "------------ CONVERT TO JSON ------------"
for f in ../books/*; do
	./jsonify.py -f $f -o ../books/$(basename $f)
done

echo "------------ AUGMENT NAMES ------------"
for f in ../bio/*; do
	./augmentify.py -f $f -d bibliography -c chapters_$(basename $f) -o ../menagerie/$(basename $f)
done

echo "------------ AUGMENT HTML ------------"
for f in ../books/*; do
	./augmentify.py -f $f -d bibliography -c chapters_$(basename $f) -o ../books/augmented/$(basename $f)
done
