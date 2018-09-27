# -*- coding: utf-8 -*-

from ext import celery
from utils.upload import upload_file_by_url, create_offer_image

@celery.task(name='catalog.upload_pictures')
def upload_offer_pictures(offer):
    pictures = offer.get_pictures(for_download=True)
    if len(pictures):
        for idx, picture in enumerate(pictures):
            if picture.url and not picture.original:
                p = upload_file_by_url(picture.url,
                                       offer.generate_picture_name,
                                       str(offer.id))

                maked = offer.create_pictures_set(p)
                maked['url'] = picture.url
                pictures[idx] = maked

        offer.update(set__pictures=pictures)


@celery.task(name='catalog.get_delivery_payment')
def get_delivery_payment():
    pass
