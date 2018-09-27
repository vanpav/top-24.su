# -*- coding: utf-8 -*-

import datetime
from flask import request
from wtforms import HiddenField
from flask.ext.wtf import Form
from flask.ext.mongoengine.wtf.fields import ModelSelectField
from ext import db, celery, cache
from config import DB_TEMP_NAME
from ..catalog.models import Category as RealCategory, Offer as RealOffer
from utils.filesys import delete_file_by_path, check_file_exists
from utils.crypto import encode_string, decode_string

class ApishopCategoryLinkForm(Form):
    id = HiddenField(u'Категория')
    category = ModelSelectField(u'Связь', model=RealCategory,
                                allow_blank=True, blank_text=u'Нет связи')


class TempDBMixin(object):
    meta = {
        'db_alias': DB_TEMP_NAME
    }


class GetOrCreateMixin(object):

    @classmethod
    def get_or_create(cls, **kwargs):
        obj = cls.objects(id=kwargs.get('id')).first()
        if not obj:
            obj = cls(**kwargs)
            obj.save()
        return obj


class ApishopConfig(TempDBMixin, db.Document):
    login = db.StringField(max_length=50, required=True)
    shop_id = db.IntField(required=True)
    yml_file = db.StringField(max_length=255)
    task = db.DictField(default={'id': None, 'name': None})
    updated_at = db.DateTimeField()

    _password = db.StringField(required=True)

    def __unicode__(self):
        return self.login

    @classmethod
    def get_config(cls):
        return cls.objects.first()

    @property
    def password(self):
        return decode_string(self._password)

    @password.setter
    def password(self, value):
        self._password = encode_string(value)

    def set_task(self, task):
        self.update(set__task=dict(id=task.task_id,
                                   name=task.task_name))

    def set_updated_at(self):
        self.update(set__updated_at=datetime.datetime.now())

    @property
    def is_yml_exists(self):
        if self.yml_file:
            return check_file_exists(self.yml_file, relative=True)
        return False

    @property
    def task_is_ready(self):
        if self.task.get('id'):
            return celery.AsyncResult(self.task.get('id')).ready()
        return True

    def delete(self, *args, **kwargs):
        delete_file_by_path(self.yml_file, relative=True)
        ApishopCategory.objects.delete()
        ApishopOffer.objects.delete()
        super(ApishopConfig, self).delete(*args, **kwargs)


class ApishopCategory(TempDBMixin, GetOrCreateMixin, db.Document):
    id = db.IntField(primary_key=True, unique=True)
    parent_id = db.IntField()
    name = db.StringField(max_length=255)
    category = db.ReferenceField(RealCategory, default=None)

    meta = {
        'indexes': ['parent_id', 'category']
    }

    def __unicode__(self):
        return self.name

    @classmethod
    def get_full_tree(cls):

        def build_tree(categories, parent_id=0):
            branch = []
            for index, category in enumerate(categories):
                if category.parent_id == parent_id:
                    form = ApishopCategoryLinkForm(request.form, obj=category)
                    branch.append(dict(id=category.id,
                                       name=category.name,
                                       offers=category.get_offers_count,
                                       form=form,
                                       childs=build_tree(categories, category.id)))
            return branch

        categories = cls.objects.order_by('+parent_id')

        return build_tree(categories)

    @property
    def get_offers_count(self):
        return ApishopOffer.objects(category_id=self.id).count()

    @classmethod
    def copy_offers(cls):
        # Для каждой категории со связью отправить товар в RealOffer
        # для дальнейшей обработки и сохранения. После копирования очистить
        # базу временных товаров.
        categories_with_link = cls.objects(category__ne=None)
        for category in categories_with_link:
            for offer in ApishopOffer.objects(category_id=category.id):
                RealOffer.populate(offer, category.category)


class ApishopOffer(TempDBMixin, GetOrCreateMixin, db.Document):
    id = db.IntField(primary_key=True)
    available = db.BooleanField()
    articul = db.StringField()
    price = db.DictField(default=dict(ru=None,
                                      by=None,
                                      kz=None))
    commissions = db.DictField(default=dict(ru=None,
                                            by=None,
                                            kz=None))
    category_id = db.IntField()
    name = db.StringField(max_length=255)
    model = db.StringField(max_length=255)
    vendor = db.StringField(max_length=100)
    pictures = db.ListField(db.StringField(max_length=255), default=[])
    description = db.StringField()
    variants = db.ListField(db.DictField())
    store_count = db.IntField()

    enabled_to_copy = db.BooleanField(default=True)

    meta = {
        'indexes': ['category_id']
    }

    def __unicode__(self):
        return '%s: %s' % (self.id, self.name)

    def get_picture(self):
        if len(self.pictures):
            return self.pictures[0]

    @property
    def prepare_to_copy(self):
        return dict(aid=self.id,
                    articul=self.articul,
                    available=self.available,
                    price=self.price,
                    commissions=self.commissions,
                    name=self.name,
                    model=self.model,
                    vendor=self.vendor,
                    pictures=[{'url': picture} for picture in self.pictures],
                    description=self.description,
                    stats=dict(store_count=self.store_count),
                    variants=[{'store_count': variant.get('store_count'),
                               'aid': variant.get('id'),
                               'name': variant.get('name')} for variant in self.variants]
                )


class ApishopPriceChange(TempDBMixin, db.Document):
    oid = db.IntField()
    name = db.StringField()
    old_price = db.FloatField()
    new_price = db.FloatField()
    date = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'ordering': ['-date']
    }

    @classmethod
    def create_or_update(cls, **kwargs):
        oid = kwargs.pop('oid')

        obj = cls.objects(oid=oid)
        if len(obj) >= 1:
            for o in obj:
                o.delete()

        obj = cls(**kwargs)
        obj.save()
        return obj
