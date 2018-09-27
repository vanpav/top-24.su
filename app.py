# -*- coding: utf-8 -*-

from factory import Factory
from config import Config
from ext import celery

app = Factory(Config)(__name__)