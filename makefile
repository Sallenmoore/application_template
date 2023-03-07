
.PHONY: all build run clean deepclean test

all: test clean run start

APP_NAME?=auto
CONTAINERS=$(sudo docker ps -a -q)

build:
	docker-compose build --no-cache

run: 
	docker-compose up --build -d
	docker logs -f --since=5m -t $(APP_NAME)

###### CLEANING #######

clean:
	sudo docker ps -a
	-docker-compose down --remove-orphans
	-sudo docker kill $(CONTAINERS)

deepclean: clean
	-sudo docker container prune -f
	-sudo docker image prune -f
	-sudo docker system prune -a -f --volumes

###### TESTING #######

debug: 
	docker-compose up --build -d
	docker logs -f --since=5m -t $(APP_NAME)

tests: clean
	echo "Running tests"
	docker-compose up --build -d
	docker exec -it $(APP_NAME) python -m pytest -v --log-level=INFO -rx -l -x 

RUNTEST?="test_"

test:
	echo "Running tests"
	docker-compose up --build -d
	docker exec -it $(APP_NAME) python -m pytest -v --log-level=INFO -rx -l -x -k $(RUNTEST)