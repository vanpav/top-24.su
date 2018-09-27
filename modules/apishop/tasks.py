# -*- coding: utf-8 -*-

import random, time
from datetime import datetime, timedelta
from ext import celery
from utils.download import download_file_from_url
from utils.filesys import delete_file_by_path
from modules.apishop import parse
from modules.apishop.models import ApishopConfig, ApishopCategory
from modules.catalog.models import (Region, Offer, RegionDelivery,
                                    DeliveryMethod,
                                    PaymentMethod)

@celery.task(name='apishop.download_yml', bind=True)
def download_yml_task(self, config):

    if config.yml_file:
        delete_file_by_path(config.yml_file, relative=True)
        config.update(set__yml_file=None)

    url = '%s%s' % (self.app.conf.get('APISHOPS_YML_URL'), config.shop_id)

    yml_file = download_file_from_url(url,
                                      'shop{}.yml'.format(config.shop_id),
                                      folder='data')

    config.update(set__yml_file=yml_file.get('url'))
    if not config.updated_at:
        update_regions_delivery(config)
    config.set_updated_at()
    config.reload()

    parse(config.yml_file)


@celery.task(name='apishop.parse_yml')
def parse_yml_task(config):
    if not config.is_yml_exists:
        raise Exception('YML file is not provided or broken')

    parse(config.yml_file)
    print 'Yml parsed'


@celery.task(name='apishop.autoupdate')
def autoupdate():
    config = ApishopConfig.get_config()
    status = 'Autoupdate skipped'
    if config:
        now = datetime.now()
        if not config.updated_at or (config.updated_at is not None and
                     (now - config.updated_at) > timedelta(hours=1)):
            download_yml_task(config)
            ApishopCategory.copy_offers()
            config.set_updated_at()
            config.reload()
            status = 'Catalog updated.'

        if not config.updated_at \
                or Region.objects.count() == 0 \
                or DeliveryMethod.objects.count() == 0 \
                or PaymentMethod.objects.count() == 0:
            update_regions_delivery(config)
            status = status + '. Regions updated'

        moscow = Region.objects(name=u'Москва').first()
        if not config.updated_at and moscow or \
                        moscow.deliveries == None or moscow.deliveries == []:
            get_delivery_for_each_region(config, moscow)
            status = status + '. Moscow region delievry getted'

        config.update(set__task={'id':None, 'name': None})

    print status


@celery.task(name='apishop.update_delivery')
def get_delivery_for_each_region(config, regions=None):
    from modules.apishop import api_connect
    aids = Offer.objects(available=True).distinct('aid')

    if not len(aids):
        return

    d_methods = {str(d.id): {'id': d.id,
                             'method': d.name} for d in DeliveryMethod.objects()}
    conn = api_connect(config)

    def request(region):
        aid = random.choice(aids)
        methods = []
        cart_string = '-'.join([str(aid),
                                str(1)])
        result = conn.get_cart_delivery(cart_string, 0, region.id)
        methods = region.get_delivery_prices(result, aid)

        return methods

    if regions:
        regions = [regions]
    else:
        regions = Region.objects

    for region in regions:
        result = request(region)

        if len(result):
            region.update(set__deliveries=result)
    return


@celery.task(name='apishop.regions_delivery')
def update_regions_delivery(config):
    from modules.apishop import api_connect
    conn = api_connect(config)

    regions = conn.get_regions()
    payment_types = conn.get_payment_types()
    delivery_types = conn.get_delivery_types()

    for data, model in ((regions, Region),
                        (payment_types, PaymentMethod),
                        (delivery_types, DeliveryMethod)):
        for id, name in data.items():
            instance = model.objects(id=int(id)).first()

            if not instance:
                instance = model(id=int(id), name=name)
                instance.save()
            else:
                if instance.name != name:
                    instance.name = name
                    instance.save()


