pip freeze > requirements.txt;
if ($?) {
    echo "gunicorn" >> requirements.txt;
}
if ($?) {
    gcloud beta app deploy;
}
Remove-Item requirements.txt;
