# -*- coding: utf-8 -*-

from models import Dispatcher

class DispatcherMixin(object):

    def save(self, *args, **kwargs):
        super(DispatcherMixin, self).save(*args, **kwargs)
        Dispatcher.create_or_change(self)

    def delete(self, *args, **kwargs):
        d = Dispatcher.objects.get(path=self.path)
        d.delete()
        super(DispatcherMixin, self).delete(*args, **kwargs)

    @property
    def dispatcher_key(self):
        return self.__class__.__name__.lower()