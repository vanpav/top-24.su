Created at year 2015.

Live: [www.top-24.su](http://www.top-24.su)

### Stack:

* Python 2.7
* Flask
* Mongo
* Celery
* Gulp
* RiotJS

### Start development:
```
pip install -r reqs.txt
```

#### Start Website dev-server:
```
python manage.py server
```

#### Celery server:
```
celery worker -A app.celery -B -l=INFO
```

#### JS Assets:
```
gulp watch
```


### Production:
```
pip install -r reqs.txt
gulp build
gunicorn app:app // + workers and socket/IP
celery worker -A app.celery -B -l=INFO
```
