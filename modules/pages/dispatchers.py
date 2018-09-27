# -*- coding: utf-8 -*-

from modules.catalog.dispatchers import BaseDispatcher

from .models import Page

class PageDispatcher(BaseDispatcher):

    def dispatch(self):
        page = Page.objects.get_or_404(path=self.path)

        return 'page.html', {'page': page}