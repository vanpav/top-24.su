# -*- coding: utf-8 -*-

from flask import render_template as r_t

def render_template(template, **context):
    return r_t(template, **context)