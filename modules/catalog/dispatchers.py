# -*- coding: utf-8 -*-

from flask import request, session
from modules.catalog.models import Category, Offer, Vendor
from modules.banners.models import Banner
from forms import ProductsOrderForm, get_ordering

class BaseDispatcher(object):

    def __init__(self, path):
        self.path = path


class CategoryDispatcher(BaseDispatcher):

    def dispatch(self):
        c = Category.objects.get_or_404(path=self.path)
        tree = c.get_tree_from()

        page = request.args.get('page', 1)

        typ = request.args.get('sort', None)
        if not typ:
            typ = session.get('category_sort', None)
        else:
            session['category_sort'] = typ

        sort = get_ordering(typ)

        ordering_form = ProductsOrderForm(data={'sort': sort[0]})

        try:
            page = int(page)
        except ValueError:
            return 'redirect', {'location': request.path,
                                'code': 301}

        per_page = 18
        if not c.parent:
            per_page = 1000

        category_root_url = c.get_category_root_url()

        os = Offer.objects(parent__in=c.get_childs())\
                  .order_by('-available', sort[2])\
                  .paginate(per_page=per_page, page=page)

        return 'category.html', {'category': c,
                                 'category_root_url': category_root_url,
                                 'offers': os,
                                 'tree': tree,
                                 'has_active': True,
                                 'breadcrumbs': c.get_breadcrumbs(),
                                 'ordering_form': ordering_form}

class OfferDispatcher(BaseDispatcher):

    def dispatch(self):
        o = Offer.objects.get_or_404(path=self.path)
        o.set_visit()
        if session.get('userinfo', None):
            region_id = session['userinfo']['region'].get('id', None) \
                if session['userinfo'].get('region', None) else None
        else:
            region_id = None
        return 'offer.html', {'region_id': region_id,
                              'offer': o,
                              'category': o.parent,
                              'has_active': True,
                              'breadcrumbs': o.get_breadcrumbs(),
                              'reviews': o.get_reviews(),
                              'related_offers': o.get_related(),
                              'popular_offers': Offer.get_popular().filter(id__ne=o.id)[:12],
                              'banners': Banner.get_banners('wide')}


class VendorDispatcher(BaseDispatcher):

    def dispatch(self):
        vendor = Vendor.objects.get_or_404(path=self.path)
        os = Offer.objects(vendor=vendor)
        return 'base.html', {'vendor': vendor, 'offers': os}