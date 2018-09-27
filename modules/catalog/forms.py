# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import SelectField

PRODUCTS_ORDER = (
    ('cheap', u'Сначала дешевые', '+price.ru'),
    ('expensive', u'Сначала дорогие', '-price.ru'),
    ('popular', u'Популярные', '-stats.popularity'),
    ('special', u'Акционные', ''),
)

def get_ordering(name):
    for typ in PRODUCTS_ORDER:
        if typ[0] == name:
            return typ
    else:
        return PRODUCTS_ORDER[0]

class ProductsOrderForm(Form):
    sort = SelectField(u'Сортировка', choices=[(typ[0], typ[1]) for typ in PRODUCTS_ORDER], default='cheap')