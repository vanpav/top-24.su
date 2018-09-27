# -*- coding: utf-8 -*-

from wtforms import BooleanField
from widgets import ButtonInput

class ButtonField(BooleanField):
    widget = ButtonInput()