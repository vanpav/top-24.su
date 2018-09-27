# -*- coding: utf-8 -*-

from models import ApishopCategory, ApishopOffer

class BaseAdapter(object):
    model = None

    def __init__(self, element):
        if not self.model:
            raise Exception('Model is required to set to adapter class')
        self.element = element

    def _get_tag_text(self, tag, default='', element=None):
        element = element if element is not None else self.element
        tag = element.find(tag)
        # Почему-то у некоторых товаров не читаются таги name и т.п.
        # if element.get('id') in ('616109', '619024'):
        #     print tag, tag is None
        text = default

        if tag is not None:
            if tag.text is not None:
                text = tag.text

        if not isinstance(text, (int, float)):
            text = text.encode('utf-8')

        return str(text).strip()


class CategoryAdapter(BaseAdapter):
    model = ApishopCategory

    def populate(self):

        attribs = dict(self.element.attrib)
        parent_id = int(attribs.get('parentId')) if attribs.get('parentId') \
                                                    is not None else 0

        return self.model.get_or_create(
            id = int(attribs.get('id')),
            parent_id = parent_id,
            name = self.element.text.encode('utf-8')
        )


class OfferAdapter(BaseAdapter):
    model = ApishopOffer

    def _parse_pictures(self):
        images = []
        for elem in self.element.findall('pictures/picture'):
            image_url = elem.text.encode('utf-8') if elem is not None else None
            images.append(image_url)
        return images

    def _parse_commissions(self):
        return dict(ru=self._get_tag_text('commission', default=float(0)),
                    by=self._get_tag_text('commissionBy', default=float(0)),
                    kz=self._get_tag_text('commissionKz', default=float(0)))

    def _parse_prices(self):
        return dict(ru=self._get_tag_text('price'),
                    by=self._get_tag_text('priceBy'),
                    kz=self._get_tag_text('priceKz'))

    def _parse_variants(self):
        variants = []
        for elem in self.element.findall('productVariants/productVariant'):
            variant = dict(name=elem.text.encode('utf-8') if elem is not None else '',
                           id=elem.get('id'),
                           store_count=elem.get('storeCount', 0))
            variants.append(variant)
        return variants

    def populate(self):
        attribs = dict(self.element.attrib)
        id = attribs.get('id')
        available = True if attribs.get('available') == 'true' else False

        return self.model.get_or_create(
            id = id,
            available = available,
            articul = self._get_tag_text('articul'),
            price = self._parse_prices(),
            category_id = self._get_tag_text('categoryId', 0),
            name = self._get_tag_text('name'),
            vendor = self._get_tag_text('vendor'),
            model = self._get_tag_text('model'),
            description = self._get_tag_text('description'),
            pictures = self._parse_pictures(),
            variants = self._parse_variants(),
            store_count = self._get_tag_text('storeCount', 0),
            commissions = self._parse_commissions()
        )


