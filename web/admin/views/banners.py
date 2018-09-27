# -*- coding: utf-8 -*-

import os
from flask import request, redirect, url_for
from modules.banners.models import type_choices, Banner
from ..helpers import AdminMethodView, render_template
from ..forms import MainBannerForm, SmallBannerForm, WideBannerForm
from werkzeug.utils import import_string
from utils.filesys import delete_file_by_path

def get_name_by_group(group):
    for g, name in type_choices:
        if g== group:
            return name.lower()
    return ''

class BannersList(AdminMethodView):
    template = 'admin/banners_list.html'

    def get(self, group=None):
        filters = {}
        if group:
            filters['banner_type'] = group
        banners = Banner.objects(**filters)
        return render_template(self.template,
                               type_choices=type_choices,
                               banners=banners)


class BannerView(AdminMethodView):
    template = 'admin/banners_edit.html'

    def get_context(self, group, id):
        form_class = eval('{}BannerForm'.format(group.capitalize()))

        if id:
            banner = Banner.objects.get_or_404(banner_type=group, id=id)
        else:
            banner = Banner.get_class_by_group(group)()

        if request.method == 'POST':
            form = form_class(request.form, initial=banner._data)
        else:
            form = form_class(request.form, obj=banner)

        form.banner_type.data = group

        return {'form': form, 'banner': banner}

    def post(self, group, id=None):
        context = self.get_context(group, id)
        form = context.get('form')
        banner = context.get('banner')

        if form and form.validate():
            image = None
            if banner.id and banner.bg_image:
                image = banner.bg_image

            form.populate_obj(banner)
            banner.save()

            if request.files['bg_image']:
                image = banner.upload_image(request.files['bg_image'])

            if image:
                banner.bg_image = image
                banner.save()

            if 'submit_and_stay' in request.form:
                return redirect(url_for('admin.banners.group.edit', group=group, id=banner.id))

            return redirect(url_for('admin.banners'))

        return render_template(self.template, group=group, group_name=get_name_by_group(group), **context)


    def get(self, group, id=None):
        context = self.get_context(group, id)

        if id and url_for('admin.banners.group.delete', id=id, group=group) == request.path:
            banner = context.get('banner')
            if banner.bg_image:
                delete_file_by_path(os.path.join('media/', banner.bg_image), True)
            banner.delete()
            return redirect(url_for('admin.banners.group', group=group))

        return render_template(self.template, group=group, group_name=get_name_by_group(group), **context)