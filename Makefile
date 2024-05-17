.PHONY: install-backend install-frontend install-flask-server buildall run-backend run-frontend run-flask-server run-all
all: buildall run

# Install dependencies for Node.js backend
install-backend:
	cd Backend && npm install

# Install dependencies for Node.js frontend (text-similarity-checker)
install-frontend:
	cd text-similarity-checker && npm install

# Install dependencies for Flask server
install-flask-server:
	pip install -r requirements.txt

# Build command to install all dependencies
buildall: install-backend install-frontend install-flask-server

# Run commands for each part of the application
run-backend:
	cd Backend && npm start

run-frontend:
	cd text-similarity-checker && npm start

run-flask-server:
	cd Backend-Flask-Server && python app.py

# Run all components of the application
run:
	make -j run-backend run-frontend run-flask-server


