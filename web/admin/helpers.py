# -*- coding: utf-8 -*-

from functools import wraps
from flask import render_template as r_t
from flask.views import MethodView
from flask.ext.security import login_required, roles_required

# Декоратор для запроса прав админа
def admin_required(fn, ):
    @wraps(fn)
    @login_required
    @roles_required('admin')
    def wrapped(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapped

# Перезапись функции рендеринга шаблонов
def render_template(template_name, **context):
    return r_t(template_name, **context)

# Класс с запросом прав админа
class AdminMethodView(MethodView):
    decorators = [admin_required]