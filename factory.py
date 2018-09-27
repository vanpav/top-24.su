# -*- coding: utf-8 -*-
import os.path as op

from datetime import timedelta
from flask import Flask, redirect, flash, request
from mongoengine import register_connection
from flask.ext.mongoengine import MongoEngineSessionInterface
from flask.ext.security import Security, MongoEngineUserDatastore
from modules.accounts.models import User, Role
from werkzeug import SharedDataMiddleware

from config import DB_TEMP_NAME
from ext import db, mail, celery, csrf, cache, htmlmin, toolbar
from web import BLUEPRINTS
from web.admin.forms import ExtLoginForm, ExtRegisterForm
from modules.accounts.tasks import send_security_mail

from utils.template_filters import time_distance, is_list, smart_round, \
    get_plural, pretty_date, phonofize

from modules.catalog.context_processors import categories, cart, visited_offers
from modules.pages.context_processors import pages

class Factory(object):

    def __init__(self, config):
        self.config = config

    def __call__(self, name, **kwargs):
        self.app = Flask(name, **kwargs)
        self.app.config.from_object(self.config)

        self.bind_extensions(db,
                             mail,
                             celery,
                             csrf,
                             cache,
                             htmlmin,
                             toolbar)

        register_connection(DB_TEMP_NAME, DB_TEMP_NAME)

        self.app.session_interface = MongoEngineSessionInterface(db)
        self.app.permanent_session_lifetime = timedelta(weeks=1)

        self.app.user_datastore = MongoEngineUserDatastore(db, User, Role)
        self.app.security = Security(self.app,
                                     self.app.user_datastore,
                                     login_form=ExtLoginForm)

        @self.app.security.send_mail_task
        def delay_security_email(msg):
            send_security_mail.delay(msg)

        # @self.app.errorhandler(Exception)
        # def validation_error(err):
        #     flash(err.message, 'error')
        #     return redirect(request.path)

        self.register_blueprints(BLUEPRINTS)
        self.register_template_filters(time_distance, is_list, smart_round,
                                       pretty_date, phonofize)
        self.register_context_processors(categories, cart, visited_offers, pages)

        self.app.jinja_env.globals['get_plural'] = get_plural

        self.app.add_url_rule('/media/<filename>', 'media',
                         build_only=True)
        self.app.wsgi_app = SharedDataMiddleware(self.app.wsgi_app, {
            '/media':  self.app.config['MEDIA_DIR']
        })

        return self.app

    def register_template_filters(self, *filters):
        for filter in filters:
            self.app.jinja_env.filters[filter.__name__] = filter

    def register_blueprints(self, blueprints):
        for bp in blueprints:
            self.app.register_blueprint(bp)

    def register_context_processors(self, *processors):
        for processor in processors:
            self.app.context_processor(processor)

    def bind_extensions(self, *extensions):
        for ext in extensions:
            if hasattr(ext, 'init_app'):
                ext.init_app(self.app)
            elif callable(ext):
                ext(self.app)

