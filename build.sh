#!/bin/bash
export NO_PROXY="/var/run/docker.sock"
#docker-machine create -d virtualbox dev;
#eval "$(docker-machine env dev)"
#docker-machine ls
docker-compose build
docker-compose up -d
docker-compose run dojo /usr/src/rapidflask/rAPPenv/bin/python manage.py db init
docker-compose run dojo /usr/src/rapidflask/rAPPenv/bin/python manage.py db migrate -m "init docker" 
docker-compose run dojo /usr/src/rapidflask/rAPPenv/bin/python manage.py db upgrade
#echo "navigate your browser to `docker-machine ip dev`"

