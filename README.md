# Funeraria Digital Doc - Backend

REST API built with Django for managing funeral home operations: death record registration, group/company management, document generation from templates and automatic email notifications.

This repository contains the backend API, consumed by a Vue 3 frontend client.

> **Status:** personal full-stack project, built end-to-end and exercised with synthetic (Faker) data. Multi-tenancy, RBAC and the document engine are complete; subscription billing is in progress.

## Tech Stack

* Python 3.11 / Django 3.2
* Django REST Framework
* MongoDB (via djongo, an ORM adapter on top of pymongo)
* JWT (djangorestframework-simplejwt) and a custom cached token authentication
* drf-yasg for Swagger API documentation
* docxtpl and python-docx for generating Word documents from templates
* PyMuPDF for reading and extracting data from PDF files
* django-currentuser for automatic tracking of who created or updated a record
* django-cors-headers for cross origin requests from the frontend
* python-decouple for configuration through environment variables
* Faker for generating realistic fake data in development
* Gunicorn, Docker and Google App Engine for deployment

### Notes on choices

**MongoDB via djongo** — I wanted Django's ORM ergonomics (querysets, migrations, DRF integration) while targeting MongoDB, whose flexible document model suits record data that varies by funeral home and document type. djongo provides that adapter layer on top of pymongo. Trade-off: it is less battle-tested than native pymongo and some Mongo-specific operations don't map cleanly — an accepted cost for this domain.

## Features

* JWT and token based authentication, with login, logout, password change and profile editing
* Role based permissions (regular user, staff and superuser) enforced at the view level
* Multi-tenant "group" model: each funeral home's data is isolated from every other
* CRUD for death records, including bulk status updates and listing by status
* Group (funeral home/company) management, including a public lookup by slug
* Configurable document templates: upload a Word template, detect its variables and generate a filled document per record
* Template level validation rules that can be checked before generating a document
* Email sending, including a test endpoint to validate SMTP configuration
* Statistics endpoints: deaths per day/month, deaths by district, deaths by user, current month/year services and best month
* A faker service used only in development to seed the database with realistic records, groups and users

## Architecture

### Multi-tenancy

Each funeral home is a **group**; every user belongs to one group, and the business data (death records, document templates, filled documents) is scoped to that group.

* **Enforcement:** there is no dedicated tenant-scoping permission class or mixin — each view filters by `group_id`/`group_user_id` inline, where it does so. Role checks (`IsSuperUser`, `IsAdminOrUpper`, `isEqualOrUpperPermission`) gate *what* an action may do; group scoping, applied per view, gates *whose* data list/aggregate endpoints return. `records.list`, `records.listByStatus`, `groups.list` and the `stats` endpoints all filter by the requesting user's `group_user_id` unless the user is a superuser.
* **Known gap:** single-object endpoints addressed by primary key — `records.view`, `records.update`, `records.remove` — do not currently compare the record's group against the requester's group, so a non-superuser could in principle read or modify another group's record given its id. Consistent object-level group checks are on the roadmap.
* **Cross-group access:** reliably prevented on list/aggregate endpoints (a non-superuser only ever sees their own group's rows there). Object-level endpoints do not yet perform this check — see the known gap above.
* **Public tenant site:** each group has a public page addressed by **slug** (`/groups/get-group-by-slug/<group_slug>/`). Only explicitly public fields (services, locations, contacts) are exposed there; nothing PII-bearing is reachable without a valid token, and the public lookup can only return the addressed group's own public data.

### Document template engine

1. Upload a Word (`.docx`) template — its variables are **auto-detected** from the template tags (`get-variables-from-file`).
2. Validation rules defined per template are **checked before generation** (`check-validations`), so a record that fails a rule is rejected before any document is produced.
3. Generation fills the template with a single record's data and returns the document for download (`download/<record_pk>`) — one form, one complete document.

Stack: `docxtpl` + `python-docx` for generation; `PyMuPDF` for reading and extracting data from PDFs.

### Request flow

`Vue 3 SPA` → (JWT in header) → `DRF view` → role check → group scope → queryset → response. Interactive API docs served via `drf-yasg` at `/swagger/`.

## Project Structure

The project is organized into Django apps, each with a single responsibility:

| App | Responsibility |
| --- | --- |
| `accounts` | Authentication, user and profile management |
| `groups` | Group (funeral home/company) management |
| `records` | Death record registration |
| `record_templates` | Links between records and filled in templates |
| `template_logic` | Definition, validation and generation of document templates |
| `stats` | Statistics over the registered data |
| `faker_service` | Fake data generation for development environments |

## API Overview

All routes below are relative to the API base URL and require authentication unless stated otherwise.

### Accounts (/accounts/)

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `login/` | Authenticate with email and password, returns access token |
| `POST` | `logout/` | Invalidate the current session token |
| `GET` | `profile/` | Retrieve the authenticated user's profile |
| `POST` | `create-user/` | Create a new user (staff/superuser only) |
| `POST` | `profile-image/` | Upload a profile image |
| `POST` | `change-password/` | Change the authenticated user's password |
| `POST` | `edit-profile/` | Update profile information |
| `POST` | `file-upload/` | Generic file upload endpoint |
| `GET` | `list-all-users/` | List all users (staff/superuser only) |
| `DELETE` | `remove/<pk>/` | Remove a user |
| `POST` | `edit-user/<pk>/` | Edit another user's data |

### Groups (/groups/)

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `create/` | Create a new group (superuser only) |
| `POST` | `update/<pk>/` | Update a group |
| `GET` | `view/<pk>/` | Retrieve a group |
| `DELETE` | `remove/<pk>/` | Remove a group |
| `GET` | `list/` | List all groups |
| `GET` | `get-group-by-slug/<group_slug>/` | Public lookup of a group by its slug |

### Records (/records/)

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `create/` | Create a death record |
| `POST` | `update/<pk>/` | Update a record |
| `GET` | `get-record/<pk>/` | Retrieve a record |
| `DELETE` | `remove/<pk>/` | Remove a record |
| `GET` | `list/` | List all records |
| `GET` | `list-by-status/<status>/` | List records filtered by status |
| `POST` | `update-many-status/` | Bulk update the status of several records |

### Record templates (/record-templates/)

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `<pk>/list-templates/` | List the templates already generated for a record |

### Template logic (/template-logic/)

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `list/` | List all document templates |
| `GET` | `list-group-templates/` | List templates available to the requesting user's group |
| `POST` | `upload/` | Upload a new Word template |
| `POST` | `get-variables-from-file/` | Detect the variables present in an uploaded template |
| `GET` | `<template_pk>/download/` | Download the raw template |
| `GET` | `<template_pk>/download/<record_pk>/` | Generate and download the template filled in with a record's data |
| `POST` | `edit/<pk>/` | Edit a template |
| `DELETE` | `remove/<pk>/` | Remove a template |
| `GET` | `get-variables/<pk>/` | List the variables of a saved template |
| `GET` | `get-template/<pk>/` | Retrieve a template |
| `GET` | `<pk>/get-validations/` | List the validation rules of a template |
| `POST` | `<pk>/check-validations/` | Check a record's data against a template's validation rules |
| `POST` | `sendTestMail/` | Send a test email to validate SMTP configuration |

### Stats (/stats/)

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `deaths-per-day/` | Number of deaths registered per day |
| `GET` | `deaths-per-months/` | Number of deaths registered per month |
| `GET` | `deaths-by-district/` | Number of deaths grouped by district |
| `GET` | `deaths-by-user/` | Number of records created per user |
| `GET` | `current-month-services/` | Services performed in the current month |
| `GET` | `current-year-services/` | Services performed in the current year |
| `GET` | `best-month/` | Month with the highest number of services |

### Faker service (/faker/)

Development only endpoints, restricted to superusers, used to seed the database:

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `create-record/` | Generate one or more fake death records |
| `POST` | `create-group-with-users/` | Generate a fake group together with staff and regular users |
| `POST` | `create-templates/` | Inspect cached template data |

## Authentication and Permissions

Authentication is handled through a custom cached token authentication class combined with djangorestframework-simplejwt, and login is performed using the user's email address rather than a username. Authorization is based on simple role checks defined in `funeraria/permissions.py`:

* `IsSuperUser`: full access, used for sensitive operations such as creating groups or seeding fake data
* `IsAdmin` / `IsAdminOrUpper`: staff level access
* `isEqualOrUpperPermission`: allows a user to manage another user only if their role is equal to or higher than the target user's role

## Prerequisites

* Python 3.11
* An accessible MongoDB instance (local or remote)
* Docker and Docker Compose (optional, recommended)

## Getting Started

Clone the repository and enter the backend folder.

Copy the environment variables example file and fill it in with real values:

```
cp .env.example funeraria/.env
```

Install the dependencies:

```
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Apply the migrations and create the initial superuser:

```
python manage.py migrate
python manage.py initadmin
```

Run the development server:

```
python manage.py runserver
```

## Environment variables

The required variables are documented in `.env.example`, including:

* `SECRET_KEY`: Django secret key
* `DEBUG`: enables or disables debug mode
* `MONGO_HOST`: MongoDB connection string
* `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`: email sending configuration
* `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD`: credentials for the superuser created by `initadmin`

No real secrets should ever be added to the repository; the `.env` file is excluded through `.gitignore`.

## Docker

The project ships with a `Dockerfile` and two compose files: one for local development and one for deployment.

To run the project with Docker Compose:

```
docker-compose up
```

The service will be available at `http://localhost:8000`.

## Available Commands

| Command | Description |
| --- | --- |
| `python manage.py runserver` | Starts the development server |
| `python manage.py migrate` | Applies database migrations |
| `python manage.py initadmin` | Creates the initial superuser from environment variables |
| `python manage.py test` | Runs the test suite |
| `python manage.py collectstatic` | Collects static files for production |
| `make build` | Collects static files inside the Docker container |
| `make deploy` | Builds the project and deploys it to Google App Engine |

## Tests

```
python manage.py test
```

The test suite covers models, serializer validation and permissions on a few endpoints. Since the project uses MongoDB through djongo, an accessible MongoDB instance is required to run them.

Coverage is deliberately focused on the highest-risk layers (data integrity and authorization). The next steps are pytest + factory fixtures for richer scenarios, a coverage gate in CI, and API contract tests for the public slug endpoint.

## API Documentation

With the server running, the Swagger documentation is available at:

```
http://localhost:8000/swagger/
```

## Deployment

The project is set up for deployment on Google App Engine:

* `app.yaml` describes the App Engine service configuration
* `cloudbuild.yaml` defines the Cloud Build pipeline used to build and deploy the application
* `docker-compose-deploy.yml` runs the `gcloud` CLI inside a container to trigger the deployment, through the `make deploy` command
* A GitHub Actions workflow builds the project and deploys it automatically on merges to `main`
