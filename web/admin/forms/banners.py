# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import (StringField, BooleanField, HiddenField,
                     SelectField, FileField, SubmitField, validators)


class BaseBannerForm(Form):
    banner_type = HiddenField(u'Тип баннера')
    bg_color = StringField(u'Цвет фона')
    bg_image = FileField(u'Картинка фона')
    link_to = StringField(u'Ссылка', validators=[validators.DataRequired()])
    is_enabled = BooleanField(u'Включен')

    submit = SubmitField(u'Сохранить')
    submit_and_stay = SubmitField(u'Сохранить и продолжить')


class MainBannerForm(BaseBannerForm):
    pass


class WideBannerForm(BaseBannerForm):
    left_top = StringField(u'Текст слева сверху')
    left_bot = StringField(u'Текст слева снизу', validators=[validators.DataRequired(),
                                                             validators.Length(min=5)])
    right_top = StringField(u'Текст справа сверху')
    right_bot = StringField(u'Текст справа снизу', validators=[validators.DataRequired(),
                                                              validators.Length(min=5)])


class SmallBannerForm(BaseBannerForm):
    header = StringField(u'Заголовок', validators=[validators.DataRequired(),
                                                   validators.Length(min=5)])
    bottom = StringField(u'Текст снизу')
    bottom_size = SelectField(u'Размер текста снизу',
                              choices=(('sm', u'Маленький'), ('bg', u'Большой')))