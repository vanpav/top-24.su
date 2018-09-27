# -*- coding: utf-8 -*-

from datetime import datetime
from ext import db
from pytils.translit import slugify

class IntIDMixin(object):
    id = db.IntField(primary_key=True)
    created_at = db.DateTimeField(default=datetime.now)
    updated_at = db.DateTimeField()

    def _generate_id(self):
        last_obj = self.__class__.objects.only('id').order_by('-id').first()
        self.id = last_obj.id + 1 if last_obj else 1

    def save(self, *args, **kwargs):
        if not self.id:
            self._generate_id()
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        super(IntIDMixin, self).save(*args, **kwargs)

class SlugMixin(object):
    slug = db.StringField(max_length=255, verbose_name=u'Ссылка')

    def validate_slug(self, name=None):
        if self.slug:
            self.slug = slugify(self.slug)
        else:
            self.slug = slugify(name if name else self.name)
        self.slug = slugify(self.slug)


class PathMixin(SlugMixin):
    path = db.StringField(unique=True)

    def _check_path_exists(self):
        filters = dict(path=self.path)
        if self.id:
            filters['id__ne'] = self.id

        exist = self.__class__.objects(**filters).count()
        return exist

    def validate_path(self):
        self.old_path = self.path or None

        self.validate_slug()

        suffix = 1

        if hasattr(self, 'parent') and self.parent and self.parent != self:
            self.path = '/'.join([self.parent.path, self.slug])
        else:
            if hasattr(self, 'path_prefix'):
                self.path = '/'.join([getattr(self, 'path_prefix'), self.slug])
            else:
                self.path = self.slug

        while self._check_path_exists():
            self.path = '-'.join([self.path, str(suffix)])
            suffix += 1

    def save(self, *args, **kwargs):
        self.validate_path()
        super(PathMixin, self).save(*args, **kwargs)


class PositionMixin(object):
    position = db.IntField()

    def validate_position(self, parent=None):
        if self.position is None:
            parent = getattr(self, 'parent', parent)
            filters = dict(parent=parent)
            if self.id:
                filters['id__ne'] = self.id
            last = self.__class__.objects(**filters).order_by('-position').first()

            if last:
                self.position = last.position + 1
            else:
                self.position = 0


class BreadcrumbsMixin(object):

    def _split_path(self):
        splt = self.path.split('/')
        paths = []
        tmp = ''

        for path in splt:
            tmp = '/'.join([tmp, path])
            paths.append(tmp.strip('/'))

        return paths

    def get_breadcrumbs(self):
        pass


class GetTitleMixin(object):

    @property
    def get_title(self):
        return self.name