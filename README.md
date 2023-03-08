# SoftDesk

SoftDesk is an issue tracking API built with Django REST Framework.

It allows users to create and manage multiple projects
Projects contributors can create, view, update and delete issues and comment on issues.

## Features

- JWT Authentication: Users can authenticate using JSON Web Tokens (JWT).
- Create projects: Users can create new projects by providing a name and description or delete the ones they have created.
- Manage project contributors: Project owners can add or remove contributors to their projects.
- Create issues: Contributors can create new issues within a project by providing details such as title, description and priority.
- Comment on issues: Contributors can add comments to existing issues within a project.

## Requirements

1. Python 3.11

## Installation

1. Clone this repository:
```
git clone https://github.com/meldsnake/sampledeck.git
```
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Run migrations:
```
python manage.py migrate
```
4. Start the development server:
```
python manage.py runserver
```

## Usage

The server once launched is accessible at http://localhost:8000/

A documentation of the API with some usage examples is available at the following address [postman documentation](http://nowhere.com/)

In addition you can obtain a OpenAPI 3.0 schema from the server at address http://localhost:8000/openapi?format=openapi-json
