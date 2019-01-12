all: env
	chmod +x run

env:
	virtualenv -p python3 env
	. env/bin/activate && pip install Flask pymongo

wsgi: all
	. env/bin/activate && pip install uwsgi

clean:
	chmod -x run
	rm -fr mongo_pilot.sock env __pycache__
