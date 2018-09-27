# -*- coding: utf-8 -*-

from flask.ext.wtf.csrf import CsrfProtect
from flask.ext.mongoengine import MongoEngine
from flask.ext.mail import Mail
from flask.ext.celery import Celery
from flask.ext.cache import Cache
from flask.ext.htmlmin import HTMLMIN
# from flask.ext.resize import Resize

db = MongoEngine()
mail = Mail()
celery = Celery()
csrf = CsrfProtect()
cache = Cache()
htmlmin = HTMLMIN()
# resize = Resize()

from flask.ext.debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension()