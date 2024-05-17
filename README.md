# Polygraf Plagiarism Checker

This application leverages Natural Language Processing (NLP) and Google Search APIs to assess potential plagiarism in text submissions. It processes user inputs into n-grams, which are then queried against Google Search to locate similar content. The application offers two analysis modes: basic cosine similarity and an enhanced version that incorporates additional NLP features for a more nuanced comparison. Furthermore, the project includes a heatmap visualization that highlights sentences in the text that are most likely to be plagiarized, helping users quickly identify problematic areas.

## Prerequisites

Before you begin ensure you have following installed on your system:

- Node.js
- npm
- Python
- pip

## File Structe

- `Backend/`: Node.js middleware which prepares the data from the frontend.
- `Backend-FlaskServer/`: Python Flask application that runs server-side plagiarism logic
- `text-similalrity-checker/`: Frontend Application built with Node.js which the user interacts with

## Installation

On first time run it recommend to simply use
```
make
```
This will run npm-install for all needed packages and pip install for all needed dependencies

Or if you would like to install specific dependencies you can do so with
```
make install-backend
make install-frontend
make install-flask-server
```

## Running Application

You can start all components of the application with the following make command:
```bash
make run
```
This will run both the frontend and the backend sides of the application

You can also specify what parts of the app you want to run with the following commands

```
make run-backend
make run-frontend
make run-flask-server
```
