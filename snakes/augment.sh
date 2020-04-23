#!/bin/bash
for f in ../books/*; do
	if [ -f "$f" ]; then
		printf "\n\t{{ BOOK $(basename $f) }}\n"

		printf "\n------------ 1 GET CHAPTER TILES ------------\n"
		./getChapters.py -f $f -o chapters_$(basename $f)
		
		printf "\n------------ 2 AUGMENT NAMES ------------\n"
		for f2 in ../bio/*; do
			./augmentify.py -f $f2 -d bibliography -c chapters_$(basename $f) -o ../menagerie/$(basename $f2)
		done

		printf "\n------------ 3 CONVERT TO JSON ------------\n"
		./jsonify.py -f $f -o ../books/JSON/$(basename $f)

		printf "\n------------ 4 AUGMENT HTML ------------\n"
		./augmentify.py -f ../books/JSON/$(basename $f) -d bibliography -c chapters_$(basename $f) -o ../books/augmented/$(basename $f)
	fi
done



