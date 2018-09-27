# -*- coding: utf-8 -*-

import os
from lxml import etree

from config import Config

from adapters import CategoryAdapter, OfferAdapter

__all__ = ['parse']

def parse(yml_file):
    parser = Parser(yml_file)
    return parser()

class Parser(object):

    def __init__(self, path):
        self.file_path = path

    def _get_file(self):
        return os.path.join(Config.BASE_DIR, self.file_path)

    def _parse(self, doc, element, parent, adapter=None):
        if not adapter:
            raise Exception('No adapter for parser setted')

        objects = []
        for event, elem in doc:
            if elem.tag == element:
                obj = adapter(elem).populate()
                objects.append(obj)
                elem.clear()

            if parent and elem.tag == parent:
                elem.clear()
                break

        return objects

    def __call__(self):
        doc = etree.iterparse(self._get_file(), ('end',))
        next(doc)

        categories = self._parse(doc, 'category', 'categories', CategoryAdapter)
        OfferAdapter.model.objects.delete()
        offers = self._parse(doc, 'offer', 'offers', OfferAdapter)

        return categories, offers