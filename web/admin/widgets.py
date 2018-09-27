# -*- coding: utf-8 -*-

from wtforms.widgets.core import Input, HTMLString

class ButtonInput(Input):

    input_type = 'submit'

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        icon_class = kwargs.pop('icon_class', None)
        icon_string = '<i class="fa %s"></i> ' % icon_class if icon_class else ''
        return HTMLString('<button %s>%s%s</button>' % (self.html_params(name=field.name, **kwargs),
                                                        icon_string,
                                                        field.label.text))