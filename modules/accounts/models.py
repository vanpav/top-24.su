# -*- coding: utf-8 -*-

from datetime import datetime
from ext import db
from flask.ext.security import UserMixin, RoleMixin


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=255, unique=True)
    description = db.StringField(max_length=255)

    def __unicode__(self):
        return self.name


class User(db.Document, UserMixin):
    email = db.StringField(max_length=255, unique=True)
    password = db.StringField(max_length=255, required=True)
    name = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    roles = db.ListField(db.ReferenceField(Role), default=[])
    registered_at = db.DateTimeField()

    def __unicode__(self):
        return 'User %s' % self.email

    @property
    def is_admin(self):
        return self.has_role('admin')

    def save(self, *args, **kwargs):
        self.registered_at = datetime.now()
        super(User, self).save(*args, **kwargs)
