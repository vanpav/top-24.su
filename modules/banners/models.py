# -*- coding: utf-8 -*-

import random, os
from pytils.translit import slugify
from flask import url_for, current_app, request
from ext import db, cache
from utils.upload import upload_file, create_offer_image
from flask.ext.resize import generate_image

type_choices = (('main', u'На главной'),
                ('wide', u'Растяжка'),
                ('small', u'Маленький'))

max_banners_items = {'MAX_MAIN_BANNERS': 5,
                     'MAX_SMALL_BANNERS': 2,
                     'MAX_WIDE_BANNERS': 1}

class Banner(db.Document):
    banner_type = db.StringField(choices=type_choices, default=u'small',
                                 max_length=100, verbose_name=u'Тип баннера')
    bg_color = db.StringField(default='#333333', max_length=7, verbose_name=u'Цвет фона')

    is_enabled = db.BooleanField(default=True)

    meta = {
        'allow_inheritance': True
    }

    @classmethod
    def get_class_by_group(cls, group):
        return eval('{}Banner'.format(group.capitalize()))

    @classmethod
    @cache.memoize(60)
    def get_banners_grouped(cls, only_enabled=True):
        filters = {}
        if only_enabled:
            filters['is_enabled'] = True

        banners = cls.objects(**filters)

        grouped_banners = {}
        for banner in banners:
            if banner.banner_type in grouped_banners:
                grouped_banners[banner.banner_type].append(banner)
            else:
                grouped_banners[banner.banner_type] = [banner]
        return grouped_banners

    @classmethod
    def get_banners(cls, group=None, only_enabled=True):
        banners = cls.get_banners_grouped(only_enabled)

        grouped_banners = {}
        for g, bs in banners.items():
            path = request.path
            new_bs = []
            for b in bs:
                if path != b.link_to:
                    new_bs.append(b)
            max = max_banners_items.get('MAX_{}_BANNERS'.format(g.upper()))
            random.shuffle(new_bs)
            if len(new_bs) > max:
                new_bs = new_bs[:max]
            grouped_banners[g] = new_bs

        if group:
            return grouped_banners.get(group, [])

        return grouped_banners

    @property
    def get_link_to(self):
        if not self.link_to:
            return url_for('site.index')
        return '/{}/'.format(self.link_to.strip('/'))

    def generate_image_name(self):
        return str(self.id)

    def upload_image(self, file):
        size = self.image_size or (300, 300)
        original = upload_file(file, self.generate_image_name(), 'banners')
        image = create_offer_image(original, format='png', width=size[0], height=size[1], suffix='b',
                                   fill=0, quality=100)

        if os.path.exists(os.path.join(current_app.config.get('MEDIA_DIR'), original)):
            os.remove(os.path.join(current_app.config.get('MEDIA_DIR'), original))

        return image


    def save(self, *args, **kwargs):
        cache.delete_memoized(Banner.get_banners_grouped)
        super(Banner, self).save(*args, **kwargs)


class MainBanner(Banner):
    pass


class WideBanner(Banner):
    bg_image = db.StringField(verbose_name=u'Фоновое изображение')
    link_to = db.StringField(verbose_name=u'Ссылка')
    left_top = db.StringField(max_length=100, verbose_name=u'Слева сверху')
    left_bot = db.StringField(max_length=100, verbose_name=u'Слева снизу')
    right_top = db.StringField(max_length=100, verbose_name=u'Справа сверху')
    right_bot = db.StringField(max_length=100, verbose_name=u'Справа снизу')

    image_size = (320, 320)

    def generate_image_name(self):
        return slugify('-'.join([self.left_bot, self.right_bot]))


class SmallBanner(Banner):
    bg_image = db.StringField(verbose_name=u'Фоновое изображение')
    link_to = db.StringField(verbose_name=u'Ссылка')
    header = db.StringField(max_length=100, verbose_name=u'Заголовок')
    bottom = db.StringField(max_length=200, verbose_name=u'Нижний текст')
    bottom_size = db.StringField(choices=(('sm', u'Маленький'), ('bg', u'Большой')),
                                 verbose_name=u'Размер нижнего текста')

    image_size = (400, 320)

    def generate_image_name(self):
        name = slugify(self.header)
        if self.bottom:
            name = slugify('-'.join([name, slugify(self.bottom)]))
        return name