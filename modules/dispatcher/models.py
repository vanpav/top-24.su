# -*- coding: utf-8 -*-

from ext import db


class Dispatcher(db.Document):
    path = db.StringField(primary_key=True)
    key = db.StringField(max_length=255)
    args = db.DictField()

    # dispatcher_map = DISPATCHER_KEYS

    meta = {
        'indexes': ['path']
    }


    @classmethod
    def create_or_change(cls, obj):
        # print getattr(obj, 'old_path'), getattr(obj, 'path')
        if hasattr(obj, 'path'):
            old_path = getattr(obj, 'old_path', None)
            dispatcher_key = obj.dispatcher_key
            path = obj.path

            if old_path and old_path != path:
                # Если пути не совпадают, взять объект по старому пути,
                # обновить путь. Старый путь сохранить в новый объект
                # для редиректа
                dispatcher = cls.objects(path=old_path).first()
                if dispatcher:
                    dispatcher.delete()

            dispatcher = cls(path=path, key=dispatcher_key)
            dispatcher.save()

    @classmethod
    def get_by_path(cls, path):
        dispatcher = cls.objects.get_or_404(path=path)
        return dispatcher.key
