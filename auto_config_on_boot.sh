sudo service redis-server start
source  drone/flaskProject/venv/bin/activate
celery -A  udpflaskapp.celery     worker
