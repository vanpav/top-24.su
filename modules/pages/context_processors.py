# -*- coding: utf-8 -*-

from .models import Page

def pages():
    return dict(pages=Page.objects())