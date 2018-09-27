# -*- coding: utf-8 -*-

from models import Category, Cart, Offer

def categories():
    return dict(categories=Category.objects(parent=None))

def cart():
    return dict(cart=Cart.get_or_create())

def visited_offers():
    return dict(visited_offers=Offer.get_visited())
