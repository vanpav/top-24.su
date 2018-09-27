# -*- coding: utf-8 -*-

from wtforms import StringField, TextAreaField

class ContentFormMixin(object):
    description = TextAreaField(u'Описание')

class MetasFormMixin(object):
    title = StringField(u'Тайтл')
    meta_description = StringField(u'Meta: description')
    meta_keywords = StringField(u'Meta: keywords')