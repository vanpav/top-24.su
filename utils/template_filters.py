# -*- coding: utf-8 -*-

import re
from pytils.numeral import get_plural
from pytils.dt import distance_of_time_in_words, ru_strftime
from datetime import datetime

__all__ = ('time_distance', 'is_list', 'smart_round')

def time_distance(value):
    return distance_of_time_in_words(value)

def is_list(value):
    return isinstance(value, list)

def smart_round(value):
    value = str(float(value))
    val, flt = value.split('.')
    if int(flt) > 0:
        return float('{0:.2f}'.format(float(value)))
    else:
        return int(val)

def pretty_date(date):
    now_year = datetime.now().year
    year = date.year

    if now_year == year:
        format = '%d %B'
    else:
        format = '%d %B %Y'



    return ru_strftime(format=format, date=date, inflected=True)


def phonofize(phone):

    phone = re.sub(r'[\(\)\s\-]+', u'', phone)

    return phone