# -*- coding: utf-8 -*-

from flask import session

from flask.ext.wtf import Form
from wtforms import StringField, SelectField, validators
from wtforms.fields.html5 import TelField


class OrderForm(Form):
    fullname = StringField(u'ФИО', validators=[validators.DataRequired(message=u'Укажите ваше имя'),
                                               validators.Length(min=3, max=200, message=u'Минимальная длина 3 символа')])
    phone = TelField(u'Телефон', validators=[validators.DataRequired(message=u'Укажите телефон для связи')])
    email = StringField(u'Электронная почта', validators=[validators.Optional(),
                                                          validators.Email(message=u'Неправильный адрес электронной почты')])

    # town = SelectField(u'Регион или город', validators=[validators.Optional()], choices=[])


class SubscribeForm(Form):
    name = StringField(u'Имя',
                       validators=[validators.DataRequired(message=u'Укажите имя'),
                                   validators.Length(min=3, max=200, message=u'Минимальная длина имени 3 символа')])
    email = StringField(u'Электронная почта',
                        validators=[validators.DataRequired(message=u'Укажите электронную почту'),
                                    validators.Email(message=u'Неправильный адрес электронной почты')])
        
    def __init__(self, *args, **kwargs):
        if 'userinfo' in session:
            userinfo = session.get('userinfo')
            kwargs['name'] = userinfo.get('fullname', '')
            kwargs['email'] = userinfo.get('email', '')
        super(SubscribeForm, self).__init__(*args, **kwargs)