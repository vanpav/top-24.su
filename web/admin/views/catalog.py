# -*- coding: utf-8 -*-

from flask import request, redirect, url_for, jsonify, session
from flask.ext.mongoengine.wtf import model_form
from modules.catalog.models import Category, Offer, OfferPicture, OfferSpecial
from ..helpers import AdminMethodView, render_template
from ..forms import CategoryForm, OfferForm, SpecialForm

__all__ = ('CatalogView',)

class CatalogView(AdminMethodView):

    offer_form = model_form(Offer, OfferForm, exclude=('id', 'path', 'stats',
                                                       'available', 'price', 'articul',
                                                       'aid', 'commissions', 'special'),
                            field_args={'parent': dict(allow_blank=True,
                                                       blank_text=u'Нет родителя'),
                                        'canonical': dict(allow_blank=True,
                                                          blank_text=u'Нет родителя')})
    category_form = model_form(Category, CategoryForm,
                               exclude=('id', 'path', 'position', 'stats'),
                               field_args={'parent': dict(allow_blank=True,
                                                          blank_text=u'Нет родителя')})

    add_category_form = model_form(Category, CategoryForm, exclude=('id', 'path', 'position', 'stats'),
                                   field_args={'parent': dict(allow_blank=True,
                                                              blank_text=u'Нет родителя')})

    special_form = model_form(OfferSpecial, SpecialForm, exclude=('created_at', 'prices', 'is_active'))


    template = 'admin/catalog.html'

    def get_context(self, category_id, offer_id):
        context = {}
        categories = Category.get_tree()

        page = int(request.args.get('page', 1))

        if not offer_id:
            if not category_id:
                category = Category()
                offers = Offer.objects()
            else:
                category = Category.objects.get_or_404(id=category_id)
                offers = Offer.objects(parent__in=category.get_childs())

            if request.method == 'POST':
                form = self.category_form(request.form, initial=category._data)
            else:
                form = self.category_form(request.form, obj=category)

            if category.id and request.path == url_for('admin.catalog.category.edit', category_id=category.id):
                context['edit'] = True
                self.template = 'admin/catalog_category_edit.html'

            context['category'] = category
            context['category_form'] = form
            context['add_category_form'] = self.add_category_form(request.form, initial=category._data)
            context['categories'] = categories
            context['offers'] = offers.paginate(page=page, per_page=18)
        else:
            offer = Offer.objects.get(id=offer_id)
            context['offer'] = offer

            if request.path == url_for('admin.catalog.offer.upload', offer_id=offer.id):
                context['upload'] = True

            if request.path == url_for('admin.catalog.offer.pic_remove', offer_id=offer.id):
                context['pic_remove'] = True

            if request.path == url_for('admin.catalog.offer.edit', offer_id=offer.id):
                context['edit'] = True
                self.template = 'admin/catalog_offer_edit.html'

                if request.method == 'POST':
                    form = self.offer_form(request.form, initial=offer._data)
                else:
                    form = self.offer_form(request.form, obj=offer)

                context['offer_form'] = form

            if request.path == url_for('admin.catalog.offer.edit.special', offer_id=offer.id):
                context['edit_special'] = True
                special = offer.get_special
                self.template = 'admin/catalog_offer_edit_special.html'

                if request.method == 'POST':
                    if special:
                        form = self.special_form(request.form, initial=special._data)
                    else:
                        form = self.special_form(request.form)
                else:
                    if special:
                        form = self.special_form(request.form, obj=special)
                    else:
                        form = self.special_form(request.form)

                context['special'] = special
                context['special_form'] = form

        return context

    def get(self, category_id=None, offer_id=None):

        context = self.get_context(category_id, offer_id)
        return render_template(self.template, **context)

    def post(self, category_id=None, offer_id=None):
        context = self.get_context(category_id, offer_id)
        if not offer_id:
            category_form = context.get('category_form')
            if category_form.validate():
                category = context.get('category')
                if 'delete' in request.form:
                    category.delete()
                    return redirect(url_for('admin.catalog'))
                category_form.populate_obj(category)
                category.save()
                if 'submit_and_stay' in request.form:
                    return redirect(url_for('admin.catalog.category.edit', category_id=category.id))
                return redirect(url_for('admin.catalog'))

        elif offer_id:
            offer_form = context.get('offer_form')
            upload = context.get('upload', False)
            pic_remove = context.get('pic_remove', False)
            offer = context.get('offer')
            if offer_form and offer_form.validate():
                # pictures = [OfferPicture(url=p.url,
                #                          original=p.original,
                #                          big=p.big,
                #                          medium=p.medium,
                #                          small=p.small) for p in offer.pictures]
                offer_form.populate_obj(offer)
                offer.save()
                # offer.update(set__pictures=pictures)
                cp = request.args.get('cp', None)
                if 'submit_and_stay' in request.form:
                    return redirect(url_for('admin.catalog.offer.edit', offer_id=offer.id, cp=cp))
                return redirect(url_for('admin.catalog', page=cp))

            if context.get('edit_special', None):
                special_form = context.get('special_form')
                if 'remove_special' in request.form:

                    special = context.get('special')
                    special.remove(offer)
                    return redirect(url_for('admin.catalog.offer.edit.special', offer_id=offer.id))

                if special_form.validate():
                    special = OfferSpecial.create_or_update(offer, special_form)

                    return redirect(url_for('admin.catalog.offer.edit.special', offer_id=offer.id))

                return redirect(url_for('admin.catalog.offer.edit.special', offer_id=offer.id))

            if upload:
                from utils.upload import upload_file
                file = request.files['file']
                original = upload_file(file, offer.generate_picture_name, str(offer.id))
                maked = offer.create_pictures_set(original)
                offer.update(push__pictures=OfferPicture(**maked))
                return jsonify(filepath=url_for('media', filename=original))

            if pic_remove:
                idx = request.form.get('idx', False)
                if idx:
                    idx = int(idx)
                    offer.remove_picture(idx)

        return render_template(self.template, **context)