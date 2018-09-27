# -*- coding: utf-8 -*-

from flask import Markup

def clear_tags_and_make_lines(text):
    if text is None:
        return None
    splitted = text.split('\n')
    stripped = map(lambda line: Markup(line).striptags(), splitted)
    return '<br>'.join(filter(None, stripped))