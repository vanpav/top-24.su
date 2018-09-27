# -*- coding: utf-8 -*-

from datetime import datetime

from flask import session

from ext import db
from modules.catalog.mixins import IntIDMixin


class Subscriber(IntIDMixin, db.Document):
    name = db.StringField(max_length=200, required=True)
    email = db.StringField(max_length=200, required=True)

    subscribed_at = db.DateTimeField(default=datetime.now())
    is_active = db.BooleanField(default=True)

    def __unicode__(self):
        return '<Subscriber {}: {}>'.format(self.id, self.email)

    def mark_subscribed(self):
        userinfo = session.get('userinfo', None)
        if not userinfo:
            session['userinfo'] = dict(fullname=self.name,
                                       email=self.email)
        else:
            if 'fullname' not in userinfo:
                userinfo['fullname'] = self.name
            if 'email' not in userinfo:
                userinfo['email'] = self.email

        session['is_subscribed'] = True


