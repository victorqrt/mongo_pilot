all: env
	chmod +x run

env:
	virtualenv -p python3 env
	. env/bin/activate && pip install Flask pymongo

clean:
	chmod -x run
	rm -fr env __pycache__
