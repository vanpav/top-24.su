# -*- coding: utf-8 -*-

import os, random, uuid, re, urlparse
from datetime import datetime, timedelta
from flask import url_for, current_app, session, request
from werkzeug.utils import cached_property
from copy import deepcopy
from mongoengine import signals
from ext import db, cache
from mixins import IntIDMixin, PathMixin, PositionMixin, BreadcrumbsMixin
from ..dispatcher.mixins import DispatcherMixin
from tasks import upload_offer_pictures
from utils.filesys import check_file_exists, delete_file_by_path
from utils.template_filters import smart_round
from utils.upload import create_offer_image


class Metas(db.EmbeddedDocument):
    title = db.StringField(max_length=500, verbose_name=u'Тайтл')
    meta_keywords = db.StringField(max_length=500, verbose_name=u'Meta: keywords')
    meta_description = db.StringField(max_length=500, verbose_name=u'Meta: description')


class CategoryStats(db.EmbeddedDocument):
    views = db.IntField(default=0)
    items = db.IntField(default=0)


class Category(DispatcherMixin, PositionMixin, IntIDMixin,
               PathMixin, BreadcrumbsMixin, db.Document):
    name = db.StringField(max_length=255, verbose_name=u'Название')
    is_active = db.BooleanField(default=True, verbose_name=u'Включена')
    parent = db.ReferenceField('Category', default=None, verbose_name=u'Родитель')

    description = db.StringField(verbose_name=u'Описание')

    stats = db.EmbeddedDocumentField('CategoryStats')
    metas = db.EmbeddedDocumentField('Metas')

    meta = {
        'ordering': ['+position'],
        'indexes': [{'fields': ['$name', "$description"],
                     'default_language': 'russian',
                     'weights': {'name': 10, 'description': 2}
                    },
                    'path',
                    'parent',
                    'position']
    }

    def __unicode__(self):
        return u'%s' % self.name

    def __repr__(self):
        return u'%s(%s)' % (self.__class__.__name__, self.id)

    def get_childrens(self):
        return self.__class__.objects(parent=self)

    def get_childs(self):
        return self.__class__.objects(__raw__={'path': {'$regex': '^{0}'
                                      .format(self.path)}}).order_by('path')

    def delete(self, *args, **kwargs):
        childrens = self.get_childrens()
        for child in childrens:
            child.delete()
        cache.delete_memoized(self.get_tree)
        super(Category, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.validate_position(kwargs.get('parent', self.parent))
        cache.delete_memoized(self.get_tree)
        super(Category, self).save(*args, **kwargs)

    @cache.memoize(3600)
    def get_tree_from(self):
        paths = self._split_path()
        root_category = self.__class__.objects.get(path=paths[0])
        tree = self.__class__.get_tree(parent=None, paths=paths)

        return tree

    def get_breadcrumbs(self):
        paths = self._split_path()
        breadcrumbs = []

        for path in paths[:-1]:
            obj = self.__class__.objects.get(path=path)
            breadcrumbs.append((obj.name, obj.path))

        return breadcrumbs

    @cache.memoize(60*60*24*7)
    def get_category_root_url(self):
        if not self.parent:
            return None

        root = self.__class__.objects(path=self.path.split('/')[0]).first()
        return urlparse.urljoin(request.url_root, url_for('site.dispatcher', path=root.path))

    @cache.memoize(60*60*24*7)
    def get_root(self):
        if not self.parent:
            return self

        paths = self._split_path()
        root = self.__class__.objects(path=paths[0]).first()
        return root

    @cached_property
    def get_title(self):
        if self.metas.title:
            return self.metas.title

        names = [self.name]
        parent = self.parent
        while parent:
            names.append(parent.name)
            parent = parent.parent

        separator = current_app.config.get('DEFAULT_TITLE_SEPARATOR', ' | ')

        return separator.join(names)

    @property
    def get_offers_count(self):
        count = self.stats.items if self.stats else 0
        return count

    @property
    def depth(self):
        return len(self.path.split('/')) - 1

    @classmethod
    @cache.memoize(3600)
    def get_tree(cls, parent=None, paths=None):
        objects = cls.objects(parent=parent)
        branch = []
        if not paths:
            for obj in objects:
                childs = obj.get_childs()
                if childs.count() > 1:
                    branch.append([obj, obj.__class__.get_tree(parent=obj)])
                else:
                    branch.append(obj)
        else:
            for obj in objects:
                if obj.path in paths:
                    childs = obj.get_childs()
                    if childs.count() > 1:
                        branch.append([obj, obj.__class__.get_tree(parent=obj, paths=paths)])
                    else:
                        branch.append(obj)
                else:
                    branch.append(obj)
        return branch

    def save(self, *args, **kwargs):
        cache.delete_memoized(self.__class__.get_tree)
        cache.delete_memoized(self.get_tree_from)
        cache.delete_memoized(self.get_category_root_url)
        cache.delete_memoized(self.get_root)
        super(Category, self).save(*args, **kwargs)

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        childs = cls.objects(__raw__={'path': {'$regex': '^{0}'
                             .format(document.old_path)}}).order_by('path')
        if len(childs) > 1 and document.old_path != document.path:
            for child in childs:
                child.save()

signals.post_save.connect(Category.post_save, sender=Category)


class Vendor(DispatcherMixin, IntIDMixin, PathMixin, db.Document):
    name = db.StringField(max_length=255, verbose_name=u'Название')

    path_prefix = 'vendor'

    @classmethod
    def get_or_create_by_name(cls, name):
        vendor = cls.objects(name=name.strip()).first()
        if not vendor:
            vendor = cls(name=name.strip())
            vendor.save()
        return vendor



class OfferPrices(db.EmbeddedDocument):
    ru = db.FloatField(default=0.0)
    by = db.FloatField(default=0.0)
    kz = db.FloatField(default=0.0)


class OfferVariant(db.EmbeddedDocument):
    store_count = db.IntField()
    aid = db.IntField()
    name = db.StringField()


class OfferPicture(db.EmbeddedDocument):
    url = db.StringField()
    original = db.StringField()
    big = db.StringField()
    medium = db.StringField()
    small = db.StringField()


class OfferStats(db.EmbeddedDocument):
    store_count = db.IntField(default=0)
    views = db.IntField(default=0)
    add_to_cart = db.IntField(default=0)
    orders = db.IntField(default=0)
    popularity = db.FloatField(default=0)


class OfferSpecial(db.Document):
    is_active = db.BooleanField(default=False)
    type = db.StringField(choices=(('real', u'Понизить цену'), ('fake', u'Повысить цену')), default='real', verbose_name=u'Тип акции')
    price_type = db.StringField(choices=(('percent', u'На проценты'), ('new', u'На сумму')), default='percent')
    price_value = db.IntField(required=True)
    timer_type = db.StringField(choices=(('date', u'До даты'), ('time', u'По времени')), default='date')
    timer_settings = db.DictField(required=True)

    created_at = db.DateTimeField()
    prices = db.EmbeddedDocumentField('OfferPrices')

    def __unicode__(self):
        return str(self.id)

    @classmethod
    def create_or_update(cls, offer, form):
        special = offer.get_special or cls()

        form.populate_obj(special)

        special.populate_price(offer)
        special.set_created_at()
        special.save()

        offer.update(set__special=special)

        return special

    def create_from_self(self):
        offer = Offer.objects(special=self).first()
        if offer:
            data = deepcopy(self._data)
            data.pop('id')
            data.pop('prices')

            new = self.__class__(**data)

            return new

    def set_created_at(self):
        self.is_active = True
        self.created_at = datetime.now()

    def populate_price(self, offer):
        if self.type == 'real':

            if not self.prices:
                self.prices = offer.price

            if self.price_type == 'percent':
                new_price = self.prices.ru * (1 - float(self.price_value) / 100)

            elif self.price_type == 'new':
                new_price = self.prices.ru - self.price_value

            offer.update(set__price__ru=new_price)
            offer.reload()

        else:

            if not self.prices:
                self.prices = offer.price

            if self.price_type == 'percent':
                new_price = self.prices.ru * (1 + float(self.price_value) / 100)

            elif self.price_type == 'new':
                new_price = self.prices.ru + self.price_value

            self.prices.ru = new_price

    def get_timer(self):

        if self.timer_type == 'date':
            date = datetime.strptime(self.timer_settings.get('timer_date'), "%d/%m/%Y").date()
            return date + timedelta(days=1)

        elif self.timer_type == 'time':
            now = datetime.now()
            delta = now - self.created_at
            days_step = int(self.timer_settings.get('timer_days', 1))

            if self.timer_settings.get('timer_repeat') == 'on' and delta.days > days_step:
                full = delta.days - (delta.days % days_step) + days_step
                new_delta = timedelta(days=full)
            else:
                new_delta = timedelta(days=days_step)

            return (self.created_at + new_delta + timedelta(days=1)).date()

    @property
    def timer(self):
        return self.get_timer().strftime('%Y/%m/%d')

    @cached_property
    def is_over(self):
        now = datetime.now()
        is_over = now.date() >= self.get_timer()
        if is_over:
            offer = Offer.objects(special=self).first()
            if offer:
                self.remove(offer)
            else:
                self.update(set__is_active=False)
        return is_over

    def remove(self, offer):
        atomic = dict(set__special=None)
        if self.type == 'real':
            atomic['set__price'] = self.prices

        offer.update(**atomic)

        self.delete()


class Offer(DispatcherMixin, IntIDMixin, PathMixin, BreadcrumbsMixin, db.Document):
    name = db.StringField(max_length=255, verbose_name=u'Название', required=True)
    model = db.StringField(max_length=255, verbose_name=u'Модель')

    aid = db.IntField(verbose_name=u'ID apishops')
    articul = db.StringField(max_length=50, verbose_name=u'Артикул')
    available = db.BooleanField()

    price = db.EmbeddedDocumentField('OfferPrices', verbose_name=u'Цены')
    commissions = db.EmbeddedDocumentField('OfferPrices', verbose_name=u'Коммиссии')

    vendor = db.ReferenceField('Vendor', verbose_name=u'Производитель')
    parent = db.ReferenceField('Category', verbose_name=u'Категория')
    metas = db.EmbeddedDocumentField('Metas')
    stats = db.EmbeddedDocumentField('OfferStats')
    variants = db.ListField(db.EmbeddedDocumentField('OfferVariant'))
    pictures = db.ListField(db.EmbeddedDocumentField('OfferPicture'))

    special = db.ReferenceField('OfferSpecial')

    short_description = db.StringField(verbose_name=u'Короткое описание')
    description = db.StringField(verbose_name=u'Описание')

    canonical = db.ReferenceField('Offer', default=None, verbose_name=u'Каноникал')

    meta = {
        'indexes': [{'fields': ['$name', "$description"],
                     'default_language': 'russian',
                     'weights': {'name': 10, 'description': 2}
                    },
                    'path', 'parent',
                    'articul', 'aid',
                    'price.ru',
                    'stats.popularity',
                    ['available', 'price.ru'],
                    ['available', 'stats.popularity']]
    }

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return u'%s(%s)' % (self.__class__.__name__, self.id)

    @cache.memoize(60*60*24*7)
    def get_canonical(self):
        if not self.canonical or self.canonical == self:
            return None
        url_root = request.url_root
        return urlparse.urljoin(url_root, url_for('site.dispatcher',
                                                  path=self.canonical.path))

    @classmethod
    def populate(cls, copied_offer, category):
        offer = cls.objects(aid=copied_offer.id, articul=copied_offer.articul).first()

        if not offer:
            offer = cls.objects(aid=copied_offer.id).first()

        offer_info = deepcopy(copied_offer.prepare_to_copy)

        if offer:
            store_count = offer_info.get('stats').get('store_count', None)
            available = offer_info.get('available', None)
            price = offer_info.get('price', None)
            commissions = offer_info.get('commissions', None)
            variants = offer_info.get('variants', None)

            updates = {}
            price_change = False

            if copied_offer.articul != offer.articul:
                updates['set__articul'] = copied_offer.articul

            if store_count != offer.stats.store_count:
                updates['set__stats__store_count'] = store_count

            if available != offer.available:
                updates['set__available'] = available

            if price:
                for key in ('ru', 'by', 'kz'):
                    if float(price.get(key)) != float(offer.get_price(key)):
                        if key == 'ru':
                            price_change = True
                        updates['set__price__{}'.format(key)] = price.get(key)

            if commissions:
                for key in ('ru', 'by', 'kz'):
                    if float(commissions.get(key)) != float(offer.get_commission(key)):
                        updates['set__commissions__{}'.format(key)] = commissions.get(key)

            if variants:
                varts = []
                for variant in variants:
                    varts.append(OfferVariant(**variant))
                updates['set__variants'] = varts


            if len(updates.keys()):
                if price_change:
                    from modules.apishop.models import ApishopPriceChange
                    if offer.special and offer.special.type == 'real':
                        old_price = float(offer.special.prices.ru)
                    else:
                        old_price = float(offer.get_price('ru'))

                    new_price = float(updates['set__price__ru'])
                    if old_price != new_price:
                        change = ApishopPriceChange(oid=offer.id,
                                                    name=offer.name,
                                                    old_price=old_price,
                                                    new_price=new_price)
                        change.save()

                updates['set__updated_at'] = datetime.now()
                offer.update(**updates)
                offer.reload()

                if price_change and offer.get_special is not None:
                    current_special = offer.get_special
                    new = current_special.create_from_self()
                    new.populate_price(offer)
                    new.save()
                    offer.update(set__special=new)
                    current_special.delete()

        else:
            vendor_name = offer_info.pop('vendor', None)
            if vendor_name:
                vendor = Vendor.get_or_create_by_name(vendor_name)
            else:
                vendor = None
            offer_info['vendor'] = vendor
            offer_info['parent'] = category
            offer = cls(**offer_info)
            offer.save()
            task = upload_offer_pictures.apply_async([offer])

    @cache.memoize(60*60)
    def get_delivery_price(self, region_id=None):
        if not region_id:
            region_id = 53

        region = Region.objects(id=region_id).first()

        if region:
            return dict(id=region.id,
                        name=region.name,
                        deliveries=[(d.method, d.price) for d in region.deliveries])
        return None

    @staticmethod
    def sub_text(match):
        id = match.group('id')
        offer = Offer.objects(id=id).only('path').first()

        if not offer:
            return ''

        return url_for('site.dispatcher', path=offer.path)

    @property
    def get_description(self):
        comp = re.compile(r'%%\s*link_to_offer\s+(?P<id>[0-9]+)\s*%%', re.IGNORECASE)
        text = comp.sub(self.sub_text, self.description)
        return u'{}'.format(text)

    @property
    def is_in_favorites(self):
        favorites = session.get('favorites', [])
        return str(str(self.id) in favorites).lower()

    @property
    def generate_picture_name(self):
        uniq = str(uuid.uuid4())[:8]
        return '_'.join([self.slug, uniq])

    def create_pictures_set(self, original):
        big = create_offer_image(original, quality=100)
        medium = create_offer_image(original, width=250, height=200, suffix='med')
        small = create_offer_image(original, width=60, height=60, suffix='sml')

        return dict(original=original,
                    big=big,
                    medium=medium,
                    small=small)

    def get_pictures(self, for_download=False, typ=None):
        if for_download:
            return self.pictures if hasattr(self, 'pictures') else []

        pictures = []
        if self.pictures:
            for picture in self.pictures:
                if typ and getattr(picture, typ, None) is not None:
                    url = url_for('media', filename=getattr(picture, typ))
                elif not typ and getattr(picture, 'big', None) is not None:
                    url = url_for('media', filename=getattr(picture, 'big'))
                else:
                    url = url_for('media', filename=picture.original) if picture.original else picture.url
                pictures.append(url)
        else:
            if not typ:
                typ = 'big'
            pictures = [url_for('static', filename='img/nophoto_{}.svg'.format(typ))]


        return pictures

    @cached_property
    @cache.memoize(3600)
    def parent_cached(self):
        return (self.parent.name,
                self.parent.path)

    def get_variant(self, aid):
        if self.variants:
            try:
                aid = int(aid)
            except (TypeError, ValueError):
                pass

            for variant in self.variants:
                if variant.aid == aid:
                    return variant
            else:
                return self.variants[0]

        return None

    def get_reviews(self):
        return Review.objects(offer=self.id, is_moderated=True)

    @cached_property
    def get_title(self):
        separator = current_app.config.get('DEFAULT_TITLE_SEPARATOR', ' | ')
        return separator.join([self.name, self.parent.get_title])

    @property
    def is_in_stock(self):
        return self.available

    @property
    def get_special(self):
        return self.special or None

    @property
    def get_oldprice(self):
        if self.special:
            return smart_round(self.special.prices.ru)
        return None

    @property
    def get_timer(self):
        if self.special:
            return self.special.timer
        return None

    @classmethod
    def get_special_offers(cls):
        import random
        special_offers = cls.objects(special__ne=None).order_by('-stats.popularity')
        special_offers = [offer for offer in special_offers if offer.special.is_active]
        random.shuffle(special_offers)
        return special_offers

    @cache.memoize(3600)
    def get_picture(self, typ=None, absolute=False):
        pictures = self.get_pictures(typ=typ)

        if len(pictures):
            url = pictures[0]
        else:
            url = url_for('static', filename='img/nophoto.svg')

        if absolute:
            url = urlparse.urljoin(request.url_root, url)

        return url

    @cached_property
    def get_absolute_picture(self):
        pic = self.get_picture()
        if not pic:
            return None
        return ''.join([request.url_root.strip('/'),
                        pic])

    @cached_property
    def get_canonical_url(self):
        return ''.join([request.url_root.strip('/'),
                        url_for('site.dispatcher', path=self.path)])

    @cache.memoize(3600)
    def get_breadcrumbs(self):
        paths = self._split_path()
        breadcrumbs = []

        objs = self.parent.__class__.objects(path__in=paths[:-1])\
                                    .only('name', 'path')\
                                    .order_by('path')
        for obj in objs:
            breadcrumbs.append((obj.name, obj.path))

        return breadcrumbs

    def set_visit(self):
        cache.delete_memoized(self.get_visited)
        visited_offers = session.get('visited_offers', [])

        if self.id not in visited_offers:
            self.update(inc__stats__views=1)
            self.reload()
            visited_offers.insert(0, self.id)

            self.calculate_popularity()
        else:
            visited_offers.remove(self.id)
            visited_offers.insert(0, self.id)

        session['visited_offers'] = visited_offers

    def set_add_to_cart(self):
        added_to_cart = session.get('added_to_cart', [])

        if self.id not in added_to_cart:
            self.update(inc__stats__add_to_cart=1)
            self.reload()
            added_to_cart.append(self.id)

            self.calculate_popularity()
            self.reload()

        session['added_to_cart'] = added_to_cart

    def calculate_popularity(self):
        popularity = (self.stats.views * 1 + self.stats.add_to_cart * 2 + self.stats.orders * 3) / 3
        self.update(set__stats__popularity=popularity)

    @classmethod
    @cache.memoize(60*5)
    def get_visited(cls):
        visited_offers = session.get('visited_offers', [])
        if len(visited_offers):
            visited = list(cls.objects(id__in=visited_offers[:15])
                           .only('id', 'name', 'price', 'pictures', 'path'))
            visited.sort(key=lambda k: visited_offers.index(k.id))
            return visited
        return None

    @classmethod
    def get_popular(cls):
        return cls.objects(available=True).order_by('-stats.popularity')

    @cache.memoize(60*60)
    def get_random_ids(self, offer_id):
        max_items = 12
        all_ids = sorted(Offer.objects(available=True,
                                       id__ne=offer_id).distinct('id'))

        length = len(all_ids)

        ids = []

        if length:
            try:
                ids = random.sample(all_ids, max_items)
            except ValueError:
                ids = random.sample(all_ids, length)

        return ids

    def get_related(self):
        return self.__class__.objects(id__in=self.get_random_ids(self.id))

    def remove_picture(self, idx):

        pictures = self.pictures

        picture = pictures.pop(idx)

        for typ in ('original', 'small', 'medium', 'big'):
            if hasattr(picture, typ):
                path = getattr(picture, typ, None)
                if path:
                    delete_file_by_path(os.path.join(current_app.config['MEDIA_DIR'],
                                                     path))

        self.update(set__pictures=pictures)
        cache.delete_memoized(self.get_picture)

    def get_price(self, key='ru'):
        return smart_round(getattr(self.price, key))

    def get_commission(self, key='ru'):
        return smart_round(getattr(self.commissions, key))
    
    def save(self, *args, **kwargs):
        cache.delete_memoized(self.get_picture)
        cache.delete_memoized(self.get_visited)
        cache.delete_memoized(self.get_canonical)
        super(Offer, self).save(*args, **kwargs)


class Review(db.Document):
    offer = db.ReferenceField('Offer')
    fullname = db.StringField(max_length=200)
    email = db.StringField(max_length=200)
    text = db.StringField()
    rating = db.IntField(default=0)
    is_moderated = db.BooleanField(default=False)
    is_viewed = db.BooleanField(default=False)
    created_at = db.DateTimeField(default=datetime.now)

    meta = {
        'ordering': ['-created_at']
    }

    def toggle_moderate(self):
        self.update(set__is_moderated=not self.is_moderated)
        self.reload()

    def set_viewed(self):
        if not self.is_viewed:
            self.update(set__is_viewed=True)
            self.reload()


class CartOffer(db.EmbeddedDocument):
    offer = db.ReferenceField('Offer')
    quantity = db.IntField(default=1)
    variant = db.StringField(default=None)


class CartTotal(db.EmbeddedDocument):
    cost = db.FloatField(default=0)
    count = db.IntField(default=0)


class Cart(db.Document):
    offers = db.ListField(db.EmbeddedDocumentField('CartOffer'), default=[])
    total = db.EmbeddedDocumentField('CartTotal')
    ordered = db.BooleanField(default=False)

    @classmethod
    def get_or_create(cls):
        cart_id = session.get('cart_id', None)

        if cart_id:
            cart = cls.objects(id=cart_id).first()
        else:
            cart = None

        if not cart:
            cart = cls()
            cart.save()
            session['cart_id'] = cart.id

        return cart

    @property
    def is_empty(self):
        return len(self.offers) == 0

    def get_offer_ids(self):
        return [offer.offer.id for offer in self.offers]

    def get_offer(self, offer_id):
        return Offer.objects(id=offer_id).first()

    def add_offer(self, offer_id, quantity=1, variant=None):
        offer = self.get_offer(offer_id)

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1

        if offer and offer.is_in_stock:
            variant = offer.get_variant(variant)
            if variant:
                variant = str(variant.aid)

            for i, cart_offer in enumerate(self.offers):
                if offer.id == cart_offer.offer.id and variant and cart_offer.variant == variant:
                    new_quantity = cart_offer.quantity + quantity
                    self.offers[i] = CartOffer(offer=offer, quantity=new_quantity, variant=variant)
                    self.save()
                    break
                elif not variant and offer.id == cart_offer.offer.id:
                    new_quantity = cart_offer.quantity + quantity
                    self.offers[i] = CartOffer(offer=offer, quantity=new_quantity)
                    self.save()
                    break
            else:
                self.update(push__offers=CartOffer(offer=offer, quantity=quantity, variant=variant))
                self.reload()

                offer.set_add_to_cart()

        self.calculate_total()


    def remove_offer(self, offer_id, variant_id=None):
        try:
            offer_id = int(offer_id)
        except (TypeError, ValueError) as e:
            return

        variant_id = str(variant_id) if variant_id != '' else None

        for idx, offer in enumerate(self.offers):
            if variant_id:
                if offer_id == offer.offer.id and variant_id == offer.variant:
                    self.offers.pop(idx)
                    break
            else:
                if offer_id == offer.offer.id:
                    self.offers.pop(idx)
                    break

        self.save()
        self.calculate_total()


    def calculate_total(self):
        total_price = []
        total_quantity = []
        for offer in self.offers:
            total_price.append(offer.offer.get_price() * offer.quantity)
            total_quantity.append(offer.quantity)

        self.update(set__total=CartTotal(cost=sum(total_price),
                    count=sum(total_quantity)))

    def prepare_offers(self):
        return [dict(articul=offer.offer.articul,
                     aid=offer.offer.aid,
                     quantity=offer.quantity,
                     variant=offer.variant,
                     price=offer.offer.get_price()) for offer in self.offers]

    def send_order(self, order_form):

        from web.site import send_order

        order_id = send_order(self.prepare_offers(), order_form)
        self.clear_cart()

        return order_id

    def clear_cart(self):
        self.update(set__offers=[])
        self.reload()
        self.calculate_total()


class OrderOffer(db.EmbeddedDocument):
    offer = db.ReferenceField('Offer')
    price = db.FloatField(default=0.0)
    oldprice = db.FloatField(default=0.0)
    quantity = db.IntField(default=1)
    variant = db.StringField(default=None)


class Order(db.Document):
    apishop_id = db.StringField(required=True)
    offers = db.ListField(db.EmbeddedDocumentField('OrderOffer'), default=[])
    ordered_at = db.DateTimeField()
    userinfo = db.DictField(default={})
    delivery_info = db.DictField(default={})
    comment = db.StringField()

    @property
    def get_delivery(self):
        return dict(price=self.delivery_info.get('delivery_price'),
                    total=self.delivery_info.get('order_sum')) \
            if self.delivery_info.get('delivery_price', None) is not None else None

    @property
    def get_total(self):
        return sum([offer.price * offer.quantity for offer in self.offers])

    def get_relevant_offers(self, max_items=4):
        offer_ids_not_to = [item.offer.id for item in self.offers]
        offer_ids = Offer.objects(available=True, id__nin=offer_ids_not_to).distinct('id')

        length = len(offer_ids)
        if length:
            try:
                ids = random.sample(offer_ids, max_items)
            except ValueError:
                ids = random.sample(offer_ids, length)

        return Offer.objects(id__in=ids)

    def get_timer(self):
        timer = self.ordered_at + timedelta(minutes=5) - timedelta(seconds=20)
        if timer < datetime.now():
            return False
        return timer.strftime('%Y/%m/%d %H:%M:%S')

    def add_offer(self, offer, quantity=1, variant=None):
        o = OrderOffer(offer=offer,
                       price=offer.get_price(),
                       oldprice=offer.get_oldprice or 0.0,
                       quantity=quantity,
                       variant=variant)
        self.update(push__offers=o)
        self.reload()

    def populate_offers(self, sended_offers):

        if not isinstance(sended_offers, (list, tuple)):
            sended_offers = [sended_offers]

        for sended_offer in sended_offers:
            offer = Offer.objects(articul=sended_offer.get('articul')).first()
            if offer:
                self.offers.append(OrderOffer(offer=offer,
                                              price=offer.get_price(),
                                              oldprice=offer.get_oldprice or 0.0,
                                              quantity=sended_offer.get('quantity', 1),
                                              variant=sended_offer.get('variant', None)))


class RegionDelivery(db.EmbeddedDocument):
    method = db.StringField(max_length=400)
    id = db.IntField()
    price = db.FloatField()


class Region(db.Document):
    id = db.IntField(primary_key=True)
    name = db.StringField(max_length=400)
    popularity = db.IntField(default=0)
    deliveries = db.ListField(db.EmbeddedDocumentField('RegionDelivery'),
                              default=[])

    updated_at = db.DateTimeField()

    meta = {
        'ordering': ['-popularity', '+id'],
        'indexes': ['name']
    }

    def __unicode__(self):
        return self.name

    def __str__(self):
        return u'%s(%s)' % (self.__class__.__name__, self.id)

    def int_popularity(self):
        popularity = (self.popularity or 0) + 1
        try:
            self.update(set__popularity=popularity)
        except db.OperationError:
            self.popularity = popularity
            self.save()

    def update_deliveries(self, methods):
        now = datetime.now()
        try:
            self.update(set__deliveries=methods, set__updated_at=now)
        except db.OperationError:
            self.deliveries = methods
            self.updated_at = now
            self.save()

    def get_delivery_prices(self, result, aid=None):
        d_methods = {str(d.id): {'id': d.id,
                                 'method': d.name} for d in DeliveryMethod.objects()}
        if not aid:
            aids = Offer.objects(available=True).distinct('aid')
            aid = random.choice(aids)

        methods = []

        if len(result):
            deliveries = result[0].deliveries
            for delivery in deliveries:
                d = d_methods.get(delivery.id, None)
                if d:
                    prices = []
                    for payment in delivery.payments:
                        price = payment.sum
                        if price is not None and price > 0 and price not in prices:
                            prices.append(price)

                    if len(prices):
                        price = min(prices)
                        d['price'] = price
                        methods.append(RegionDelivery(**d))
        return methods


class PaymentMethod(db.Document):
    id = db.IntField(primary_key=True)
    name = db.StringField(max_length=400)

    meta = {
        'ordering': ['+id'],
        'indexes': ['name']
    }

    def __unicode__(self):
        return self.name

    def __str__(self):
        return u'%s(%s)' % (self.__class__.__name__, self.id)


class DeliveryMethod(db.Document):
    id = db.IntField(primary_key=True)
    name = db.StringField(max_length=400)

    meta = {
        'ordering': ['+id'],
        'indexes': ['name']
    }

    def __unicode__(self):
        return self.name

    def __str__(self):
        return u'%s(%s)' % (self.__class__.__name__, self.id)