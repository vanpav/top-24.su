# -*- coding: utf-8 -*-

import os, urllib
from werkzeug.utils import secure_filename
from filesys import create_folders
from pytils.translit import slugify

from config import Config

from flask.ext.resize import generate_image

def allowed_filename(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def upload_file_by_url(url, filename=None, collection=None):
    if not filename:
        filename = os.path.split(url)[-1]
    else:
        _url, ext = os.path.splitext(url)
        filename = ''.join([filename, ext])

    if collection:
        filepath = os.path.join(collection, filename)
    else:
        filepath = filename

    if url and allowed_filename(filename):
        file = urllib.URLopener()
        if collection:
            create_folders(os.path.join(Config.MEDIA_DIR, collection))
        file.retrieve(url, os.path.join(Config.MEDIA_DIR, filepath))

        return filepath
    else:
        raise Exception('Not allowed file extension')


def create_offer_image(image, format='jpeg', width=500, height=400, suffix='big',
                       fill=1, quality=80, bgcolor=None):
    folder, filename = os.path.split(image)
    image_path = os.path.join(Config.MEDIA_DIR, image)
    name, ext = os.path.splitext(filename)
    if suffix:
        new_filename = os.path.join(folder, '{}_{}{}'.format(name, suffix, ext))
    else:
        new_filename = os.path.join(folder, '{}{}'.format(name, ext))
    save_to_path = os.path.join(Config.MEDIA_DIR, new_filename)

    if os.path.exists(save_to_path):
        os.remove(save_to_path)

    generate_image(inpath=image_path, outpath=save_to_path,
                   format=format, width=width, height=height,
                   fill=fill, quality=quality, bgcolor=bgcolor)

    return new_filename


def upload_file(file, filename=None, collection=None):
    _filename, ext = os.path.splitext(file.filename)
    if not filename:
        filename = ''.join([slugify(_filename), ext])
    else:
        filename = ''.join([filename, ext])

    filename = secure_filename(filename)

    if collection:
        filepath = os.path.join(collection, filename)
    else:
        filepath = filename

    if file and allowed_filename(filename):
        if collection:
            create_folders(os.path.join(os.path.join(Config.MEDIA_DIR, collection)))
        file.save(os.path.join(Config.MEDIA_DIR, filepath))

        return filepath
    else:
        raise Exception('Not allowed file extension')
