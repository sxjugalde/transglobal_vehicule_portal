import os
from google.oauth2 import service_account

from .base import *

# Setup DB connection
if os.getenv("GAE_APPLICATION", None) and (connection_name := env.str("GCP_CONNECTION_NAME", None)):
    # Running on production App Engine, so connect to Google Cloud SQL using
    # the unix socket at /cloudsql/<your-cloudsql-connection string>
    DATABASES["default"]["HOST"] = f"/cloudsql/{connection_name}"


ALLOWED_HOSTS += ["transglobal-live.ue.r.appspot.com","www.vikingmviws.com","vikingmviws.com"]  # noqa F405

# GCP Storage
if bucket_name := env.str("GCP_STORAGE_BUCKET", None):
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    GS_FILE_OVERWRITE = False
    GS_BUCKET_NAME = bucket_name
    MEDIA_URL = f"https://storage.googleapis.com/{bucket_name}/"
    MEDIA_ROOT = "media"
    if env.bool("GCP_STORAGE_STATIC", False):
        STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
        STATIC_URL = f"https://storage.googleapis.com/{bucket_name}/"
        STATIC_ROOT = "static"

if project_id := env.str("GCP_PROJECT_ID", None):
    GS_PROJECT_ID = project_id

if credentials_path := env.str("GCP_CREDENTIALS_PATH", None):
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        credentials_path
    )
