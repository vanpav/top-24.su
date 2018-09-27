# -*- coding: utf-8 -*-

from flask import request, redirect, url_for, jsonify

from modules.apishop import ApishopConfig, ApishopCategory, ApishopOffer, download_yml_task
from modules.catalog.models import Category as RealCategory
from ..forms import ApishopConfigLoginForm, ApishopConfigSettingsForm, ApishopCategoryLinkForm
from ..helpers import AdminMethodView, render_template

__all__ = ('ParserView', 'ParserCategoryView',)

class ParserView(AdminMethodView):

    def get_context(self):
        config = ApishopConfig.get_config()
        if not config:
            config = ApishopConfig()
            form = ApishopConfigLoginForm(request.form)
            link_form = None
        else:
            link_form = ApishopCategoryLinkForm(request.form)
            form = ApishopConfigSettingsForm(request.form)

        return dict(config=config,
                    form=form,
                    categories=ApishopCategory.get_full_tree())

    def get(self):
        context = self.get_context()
        if request.args.get('download-task', None):
            config = context.get('config', None)
            return jsonify(complete=config.task_is_ready)
        return render_template('admin/parser.html', **context)

    def post(self):
        context = self.get_context()
        config = context.get('config')
        form = context.get('form')
        if not config.id and form.validate_on_submit():
            config.login = form.login.data
            config.password = form.password.data
            config.shop_id = form.shop_id.data
            config.save()
            # Таск на загрузку yml-файла из партнерки,
            # парсинга категорий партнерки и обновления данных конфига
            task = download_yml_task.apply_async([config])
            config.set_task(task)
            return redirect(url_for('admin.parser'))
        elif form.validate_on_submit():
            if 'delete' in request.form:
                config.delete()
            elif 'copy' in request.form:
                ApishopCategory.copy_offers()
            elif 'update' in request.form:
                # Таск на загрузку yml-файла из партнерки,
                # парсинга категорий партнерки и обновления данных конфига
                task = download_yml_task.apply_async([config])
                config.set_task(task)
            return redirect(url_for('admin.parser'))

        return render_template('admin/parser.html', **context)


class ParserCategoryView(AdminMethodView):

    def get_context(self, category_id):
        category = ApishopCategory.objects.get_or_404(id=category_id)
        offers = ApishopOffer.objects(category_id=category_id)
        return dict(category=category, offers=offers)

    def get(self, category_id):
        context = self.get_context(category_id)
        return render_template('admin/parser_category.html', **context)

    def post(self, category_id):
        context = self.get_context(category_id)
        category = context.get('category')
        if 'realcategory' in request.form:
            id = request.form.get('realcategory')
            if id != '__None':
                real_category = RealCategory.objects.get(id=id)
                category.update(set__category=real_category)
            else:
                category.update(set__category=None)
        return render_template('admin/parser_category.html', **context)