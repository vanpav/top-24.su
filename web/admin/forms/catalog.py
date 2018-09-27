# -*- coding: utf-8 -*-

from datetime import datetime
from flask import request
from flask.ext.mongoengine.wtf.models import ModelForm
from flask.ext.wtf import Form
from web.admin.fields import ButtonField


class CategoryForm(ModelForm):
    submit = ButtonField(u'Сохранить')
    submit_and_stay = ButtonField(u'Сохранить и продолжить')
    delete = ButtonField(u'Удалить')


class OfferForm(ModelForm):
    submit = ButtonField(u'Сохранить')
    submit_and_stay = ButtonField(u'Сохранить и продолжить')
    disable = ButtonField(u'Отключить')


class SpecialForm(ModelForm):
    submit = ButtonField(u'Сохранить')
    disable = ButtonField(u'Отключить')

    # Попробовать вписать ошибки к полю, чтобы их выводить
    # Писать в БД
    def validate(form):
        timer_type = form.timer_type.data
        timer_settings = {}
        if timer_type == 'date':
            timer_date = request.form.get('timer_date', None)
            if timer_date:
                # date = datetime.strptime(timer_date, "%d/%m/%Y").date()
                timer_settings['timer_date'] = timer_date
        elif timer_type == 'time':
            timer_days = request.form.get('timer_days', None)
            timer_repeat = request.form.get('timer_repeat', False)
            if timer_days:
                timer_settings['timer_days'] = timer_days
                timer_settings['timer_repeat'] = timer_repeat

        form.timer_settings.data = timer_settings


        return super(SpecialForm, form).validate()
