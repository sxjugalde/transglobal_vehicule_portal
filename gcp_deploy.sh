pip freeze > requirements.txt && echo "gunicorn" >> requirements.txt && gcloud beta app deploy && rm requirements.txt;
