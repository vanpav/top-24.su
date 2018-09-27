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

    # def social_connections(self):
    #     return Connection.objects(user=self)


# class Connection(db.Document):
#     user = db.ReferenceField(User)
#     provider = db.StringField(max_length=255)
#     profile_id = db.StringField(max_length=255)
#     username = db.StringField(max_length=255)
#     email = db.StringField(max_length=255)
#     access_token = db.StringField(max_length=255)
#     secret = db.StringField(max_length=255)
#     first_name = db.StringField(max_length=255, help_text=u"First Name")
#     last_name = db.StringField(max_length=255, help_text=u"Last Name")
#     cn = db.StringField(max_length=255, help_text=u"Common Name")
#     profile_url = db.StringField(max_length=512)
#     image_url = db.StringField(max_length=512)
#
#     @property
#     def user(self):
#         return self.user
#
#     @classmethod
#     def by_profile(cls, profile):
#         provider = profile.data["provider"]
#         return cls.objects(provider=provider, profile_id=profile.id).first()
#
#     @classmethod
#     def from_profile(cls, user, profile):
#         if not user or user.is_anonymous():
#             print profile.data
#             email = profile.data.get("email")
#             if not email:
#                 msg = "Cannot create new user, authentication provider did not not provide email"
#                 # logging.warning(msg)
#                 raise Exception(msg)
#
#             conflict = User.objects(email=email).first()
#             if conflict:
#                 msg = "Cannot create new user, email {} is already used. Login and then connect external profile."
#                 msg = msg.format(email)
#                 # logging.warning(msg)
#                 raise Exception(msg)
#
#             user = User(email=email, active=True)
#             user.save()
#
#         connection = cls(user=user, **profile.data)
#         connection.save()
#         return connection