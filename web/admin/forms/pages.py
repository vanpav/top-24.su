# -*- coding: utf-8 -*-

from flask.ext.mongoengine.wtf.models import ModelForm
from web.admin.fields import ButtonField


class PageForm(ModelForm):
    submit = ButtonField(u'Сохранить')
    submit_and_stay = ButtonField(u'Сохранить и продолжить')
    delete = ButtonField(u'Удалить')