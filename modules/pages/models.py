# -*- coding: utf-8 -*-

from werkzeug.utils import cached_property

from ext import db, cache
from modules.dispatcher.mixins import DispatcherMixin
from modules.catalog.mixins import (PathMixin, IntIDMixin,
                                    BreadcrumbsMixin, PositionMixin)
from modules.catalog.models import Metas


class Page(DispatcherMixin, PositionMixin, IntIDMixin,
           PathMixin, BreadcrumbsMixin, db.Document):

    name = db.StringField(max_length=255, verbose_name=u'Название', required=True)

    parent = db.ReferenceField('Page', default=None, verbose_name=u'Родитель')
    metas = db.EmbeddedDocumentField(Metas)

    content = db.StringField(verbose_name=u'Описание')

    extra = db.DictField(default={'type': 'None'})

    meta = {
        'ordering': ['+position'],
        'indexes': ['path',
                    'parent',
                    'position']
    }

    def __unicode__(self):
        return u'%s' % self.name

    def __repr__(self):
        return u'%s(%s)' % (self.__class__.__name__, self.id)

    @cached_property
    def get_title(self):
        if self.metas and self.metas.title:
            return self.metas.title

        return self.name

    def get_extra(self):
        return self.extra

    def save(self, *args, **kwargs):
        self.validate_position(kwargs.get('parent', self.parent))
        super(Page, self).save(*args, **kwargs)