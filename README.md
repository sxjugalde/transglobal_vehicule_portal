# Vehicle Service Portal

Django based vehicle service system, with customer and administrative portals.

## Installation & Usage

### Requirements

- Python 3.8
- Pipenv (used for package and virtualenv management). More info at: https://pypi.org/project/pipenv/.
- PostgreSQL (preferred DBMS).
- Visual Studio Code (preferred IDE).

### Clone & install dependencies

- Clone repository to your local machine
- Install dependencies through pipenv:

> install pipenv using pip if required (must have Python installed)

```shell
$ pip install pipenv
```

> now move to the repository folder, initialize pipenv shell and install development dependencies

```shell
$ cd path_to_repository
$ pipenv shell
$ pipenv install --dev
```

**Note:** In order to run the project, install new dependencies (for any environment) and uninstall dependencies, you must be inside the pipenv shell. When the pipenv shell is active, you should see the clarification to the left, like (2020-vehicle-portal-XXXXXXXX). This clarification will not show up in PowerShell.

### Create development DB in PostgreSQL through psql

- Install PostgreSQL v12.3, include psql.
- Open cmd, start psql and authenticate user, then create development db:

> -p is used for port, default is 5432. -u is used for user, default is current user.

```shell
$ psql -p 5432 -U postgres
$ create database vehicle_service_portal_dev;
```

### Create & configure .env file

Before migrating the DB and running the project, please ensure you have setup the .env file the system uses to store environment variables. To do this, copy the existing `.env.example` file into a new `.env` file, and replace the variables inside accordingly.

### Start project

- Run migrations (creates the database tables):

```shell
$ py manage.py migrate
```

- Create superuser:

```shell
$ py manage.py createsuperuser
```

- Run project:

```shell
$ py manage.py runserver
```

After these steps, you should be able to navigate to http://localhost:8000/admin and log in with your superuser account.

#### Other commands

- Make migration files when a model is changed:

```shell
$ py manage.py makemigrations
```

- Run tests:

```shell
$ py manage.py test
```

- Create coverage report:

```shell
$ coverage run --source='.' manage.py test
$ coverage html
```

## Environment variable glossary

### Deployment and GCP

- `DEPLOYMENT_ENV`: Used to determine the deployment environment for subsequent configuration. Options are `development`, `qa` and `production`.
- `GCP_PROJECT_ID`: ID of the GCP project to deploy on App Engine.
- `GCP_STORAGE_BUCKET`: Name of the GCP Cloud Storage bucket to use for storage of static assets and media.
- `GCP_CREDENTIALS_PATH`: Path for JSON file with service account credentials to use the GCP Storage bucket.
- `GCP_CONNECTION_NAME`: The connection name for the GCP Cloud SQL instance to use as database.
- `GCP_STORAGE_STATIC`: A boolean flag. Whether to use Google Cloud Storage bucket to serve static assets (otherwise, serve directly from App Engine filesystem).

### Django

- `DEBUG`: Whether to set debug mode on django server.
- `SECRET_KEY`: Secret key for django server.
- `DJANGO_ADMINS`: System administrators as a django-environ compatible list.
- `DJANGO_MANAGERS`: System managers as a django-environ compatible list. Will receive quote request emails.

### Email

- `EMAIL_BACKEND`: Django email backend to use. Defaults to django.core.mail.backends.smtp.EmailBackend.
- `EMAIL_HOST`: Email host to use. Defaults to gmail (smtp.gmail.com).
- `EMAIL_USE_TLS`: Defines whether to use TLS or not when sending email. Defaults to True.
- `EMAIL_PORT`: Email port to use. Defaults to gmail's port (587).
- `EMAIL_HOST_USER`: Email to use when delivering messages. Defaults to empty.
- `EMAIL_HOST_PASSWORD`: Password for the email to use. Defaults to empty.
- `DEFAULT_FROM_EMAIL`: Default email that appears in "From". Defaults to EMAIL_HOST_USER.
- `EMAIL_SUBJECT_PREFIX`: Subject-line prefix for email messages sent with mail_admins or mail_managers. Used on quote request emails. Defaults to "[TG]".

### PostgreSQL

- `DATABASE_HOST`: Hostname for the database. It is ignored if GCP is used as deployment platform.
- `DATABASE_USER`: Username for database access.
- `DATABASE_PASSWORD`: Password for the provided database user.
- `DATABASE_PORT`: Port of database service on host. It is ignored if GCP is used as deployment platform.
- `DATABASE_NAME`: Name of app database on database server.

## Deploy to Google Cloud Platform

You will need to set the following environment variables: `DEPLOYMENT_ENV`, `GCP_PROJECT_ID`,`GCP_STORAGE_BUCKET`, `GCP_CREDENTIALS_PATH`, `GCP_CONNECTION_NAME` (you may use the `.env` file for this purpose). You will also need to install the Google Cloud SDK (with beta components enabled) or use the Google Cloud Shell on GCP. Additionally, you will have to choose your App Engine environment. Copy or rename the `app.standard.yaml` file to `app.yaml` to use the App Engine Standard environment. Currently only the Standard environment is supported. You will also need to collect the static assets to your desired storage.
Once your environment is configured, you may deploy your app to GCP by executing one of the deployment scripts (remember to have your pipenv environment activated):

```shell
$ pipenv shell
$ python manage.py collectstatic
```

```shell
$ # Powershell script (Windows)
$ .\gcp_deploy.ps1
```

```shell
$ pipenv shell
$ # Bourne shell script (Unix - Linux/BSD/OSX)
$ .\gcp_deploy.sh
```

If you are on a Windows system, execution of scripts may be disabled. In that case, issue the following command to change the policy:

```shell
$ Set-ExecutionPolicy -ExecutionPolicy Unrestricted
```

## Configure VS Code

This project uses Black as an automatic python code formatter, and flake8 as a linter. To configure VS Code to format on save automatically, please make the changes below:

- Go to settings in your VS-Code typing “Ctrl + ,” or clicking at the gear on the bottom left and selecting “Settings [Ctrl+,]” option.
- Type “format on save” at the search bar on top of the Settings tab and check the box.
- Search for “python formatting provider” and select “black”.

On the other hand, for JavaScript, eslint is the preferred linter. Prettier is used by any language that's not python as a code formatter (including HTML, CSS and Markdown). To enable automatic format on save, please install the required extensions and add the required changes to your settings.json in VSCode, for each language mentioned. For example:

```
"[javascript]": {
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode"
},
"[html]": {
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode"
},
```

Required extensions:

- Python
- EditorConfig for VS Code
- Debugger for Firefox/Chrome
- Eslint
- Prettier
