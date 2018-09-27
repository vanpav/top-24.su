# -*- coding: utf-8 -*-

from flask import render_template, request, url_for, redirect, flash
from flask.ext.mongoengine.wtf import model_form

from modules.pages.models import Page
from ..helpers import AdminMethodView
from ..forms.pages import PageForm


class PageList(AdminMethodView):

    template = 'admin/page_list.html'

    def get(self):
        return render_template(self.template)


class PageEdit(AdminMethodView):

    template = 'admin/page_edit.html'
    form = model_form(Page, PageForm, exclude=('id', 'path', 'position', 'stats'),
                      field_args={'parent': dict(allow_blank=True,
                                                 blank_text=u'Нет родителя'),
                                  'name': dict()})

    def get_extra(self, form):
        ef = {}
        for name, value in form.items():
            if name.startswith('extra'):
                name = name.split('_')[-1]
                ef[name] = value
                if name == 'type' and value == 'None':
                    break
        return ef

    def get(self, id=None):
        if id:
            page = Page.objects.get_or_404(id=id)

            if request.path == url_for('admin.pages.delete', id=page.id):
                flash(u'Страница "{}" удалена'.format(page.name))
                page.delete()
                return redirect(url_for('admin.pages'))

        if request.path == url_for('admin.pages.create'):
            page = Page()

        form = self.form(request.form, obj=page)
        extra = page.get_extra()

        return render_template(self.template, form=form, page=page, extra=extra)


    def post(self, id=None):

        if id:
            page = Page.objects.get_or_404(id=id)
        else:
            page = Page()

        form = self.form(request.form, initial=page._data)
        extra = self.get_extra(request.form)

        print request.form.items()

        if form.validate():
            form.populate_obj(page)

            page.extra = extra
            page.save()

            flash(u'Страница {} сохранена'.format(page.name))

            if 'submit_and_stay' in request.form:
                return redirect(url_for('admin.pages.edit', id=page.id))

            return redirect(url_for('admin.pages'))

        return render_template(self.template, form=form, page=page, extra=extra)
