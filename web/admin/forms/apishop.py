# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, HiddenField, validators
from flask.ext.mongoengine.wtf.fields import ModelSelectField

from web.admin.fields import ButtonField
from modules.catalog.models import Category as RealCategory

class ApishopConfigLoginForm(Form):
    login = StringField(u'Логин', validators=[validators.DataRequired()])
    password = PasswordField(u'Пароль', validators=[validators.DataRequired()])
    shop_id = StringField(u'ID магазина', validators=[validators.DataRequired()])
    submit = ButtonField(u'Сохранить')


class ApishopConfigSettingsForm(Form):
    update = ButtonField(u'Обновить каталог')
    parse = ButtonField(u'Парсить каталог')
    delete = ButtonField(u'Удалить')


class ApishopCategoryLinkForm(Form):
    id = HiddenField(u'Категория')
    category = ModelSelectField(u'Связь', model=RealCategory,
                                allow_blank=True, blank_text=u'Нет связи')