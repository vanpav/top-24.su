# -*- coding: utf-8 -*-

import os
from flask import (Blueprint, render_template, request,
                   url_for, Response, current_app)
from helpers import admin_required
from modules.apishop.models import ApishopPriceChange

admin = Blueprint('admin',
                  __name__,
                  url_prefix='/admin',
                  template_folder='templates/',
                  static_folder='static/')

@admin.route('/')
@admin_required
def index():
    page = int(request.args.get('page', 1))
    pcs = ApishopPriceChange.objects
    pcs = pcs.paginate(page=page, per_page=20)
    return render_template('admin/default.html', pcs=pcs, page=page)

@admin.route('/generate/offers-xls/')
@admin_required
def generate_offers_xls():
    import urlparse, StringIO
    from modules.catalog.models import Offer
    from xlwt import Workbook

    wb = Workbook()
    ws = wb.add_sheet('Offers')
    url_root = request.url_root

    for line, offer in enumerate(Offer.objects()):
        ws.write(line, 0, offer.name)
        ws.write(line, 1, urlparse.urljoin(url_root,
                                           url_for('site.dispatcher',
                                                   path=offer.path)))

    output = StringIO.StringIO()
    wb.save(output)

    response = Response()
    response.status_code = 200
    response.data = output.getvalue()

    response.content_type = u'application/vnd.ms-excel'
    response.headers["Content-Disposition"] = "attachment; filename=offers.xls"

    return response

from views import (ParserCategoryView, ParserView, CatalogView,
                   ReviewsView, PageEdit, PageList, BannersList,
                   BannerView)

# parser
admin.add_url_rule('/parser/', view_func=ParserView.as_view('parser'))
admin.add_url_rule('/parser/link/', view_func=ParserView.as_view('parser.category_link'))
admin.add_url_rule('/parser/<category_id>/', view_func=ParserCategoryView.as_view('parser.category'))

admin.add_url_rule('/catalog/', view_func=CatalogView.as_view('catalog'))
admin.add_url_rule('/catalog/<category_id>/', view_func=CatalogView.as_view('catalog.category'))
admin.add_url_rule('/catalog/<category_id>/edit/', view_func=CatalogView.as_view('catalog.category.edit'))
admin.add_url_rule('/catalog/offer/<offer_id>/edit/', view_func=CatalogView.as_view('catalog.offer.edit'))
admin.add_url_rule('/catalog/offer/<offer_id>/edit/special/', view_func=CatalogView.as_view('catalog.offer.edit.special'))
admin.add_url_rule('/catalog/offer/<offer_id>/upload/', view_func=CatalogView.as_view('catalog.offer.upload'))
admin.add_url_rule('/catalog/offer/<offer_id>/pic_remove/', view_func=CatalogView.as_view('catalog.offer.pic_remove'))

admin.add_url_rule('/reviews/', view_func=ReviewsView.as_view('reviews'))

admin.add_url_rule('/pages/', view_func=PageList.as_view('pages'))
admin.add_url_rule('/pages/<int:id>/', view_func=PageEdit.as_view('pages.edit'))
admin.add_url_rule('/pages/create/', view_func=PageEdit.as_view('pages.create'))
admin.add_url_rule('/pages/<int:id>/delete/', view_func=PageEdit.as_view('pages.delete'))

admin.add_url_rule('/banners/', view_func=BannersList.as_view('banners'))
admin.add_url_rule('/banners/<group>/', view_func=BannersList.as_view('banners.group'))
admin.add_url_rule('/banners/<group>/create/', view_func=BannerView.as_view('banners.group.create'))
admin.add_url_rule('/banners/<group>/<id>/', view_func=BannerView.as_view('banners.group.edit'))
admin.add_url_rule('/banners/<group>/<id>/delete/', view_func=BannerView.as_view('banners.group.delete'))