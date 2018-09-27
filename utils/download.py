# -*- coding: utf-8 -*-

import os
import urllib, urllib2

from filesys import create_folders
from config import Config

BASE_DIR = Config.BASE_DIR

def download_file_from_url(url, filename=None, folder='media'):

    if not filename:
        filename = os.path.split(url)[-1]

    destination = os.path.join(BASE_DIR, folder)
    create_folders(destination)
    file_path = os.path.join(destination, filename)
    file = urllib.URLopener()
    file.retrieve(url, file_path)
    file_url = os.path.join(folder, filename)

    return dict(name=filename,
                url=file_url,
                path=file_path)