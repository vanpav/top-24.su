# -*- coding: utf-8 -*-

import json, random, urlparse
from datetime import datetime, timedelta
from flask import (Blueprint, abort, redirect, request,
                   url_for, session, Markup, jsonify, current_app,
                   make_response)
from flask.ext.login import current_user

from ext import csrf, cache
from modules.apishop import ApishopConfig, api_connect
from modules.catalog.models import (Category, Offer, Cart, Order, Review,
                                    Region, DeliveryMethod, PaymentMethod, RegionDelivery)
from modules.pages.models import Page
from modules.dispatcher.models import Dispatcher
from modules.catalog.dispatchers import CategoryDispatcher, OfferDispatcher, VendorDispatcher
from modules.pages.dispatchers import PageDispatcher
from modules.subscribe.models import Subscriber
from modules.banners.models import Banner

from forms import OrderForm, SubscribeForm
from helpers import render_template
from utils.text import clear_tags_and_make_lines
from utils.json import request_wants_json


site = Blueprint('site', __name__)

d_map = {
    'category': CategoryDispatcher,
    'offer': OfferDispatcher,
    'vendor': VendorDispatcher,
    'page': PageDispatcher
}


@site.context_processor
def site_context():
    return dict(current_year=datetime.now().year,
                default_title=current_app.config.get('DEFAULT_TITLE'),
                default_title_separator=current_app.config.get('DEFAULT_TITLE_SEPARATOR', ' | '),
                subscribe_form=SubscribeForm(),
                is_subscribed=session.get('is_subscribed', False))


@site.before_request
def set_permanent_session():
    session.permanent = True


# Should be commented or deleted
#
# @site.route('/email/<typ>/')
# def email(typ):
#     return render_template('email/{}.html'.format(typ))


@site.route('/')
def index():
    return render_template('index.html',
                           popular_offers=Offer.get_popular()[:8],
                           special_offers=Offer.get_special_offers()[:12],
                           banners=Banner.get_banners())


@site.route('/sitemap.xml')
def sitemap():
    url_root = request.url_root

    categories = [[urlparse.urljoin(url_root, url_for('site.dispatcher', path=cat.path)),
                   cat.updated_at.strftime('%Y-%m-%d') if cat.updated_at is not None else None]
                  for cat in Category.objects.only('path', 'updated_at').order_by('+position')]

    offers = [[urlparse.urljoin(url_root, url_for('site.dispatcher', path=o.path)),
               o.updated_at.strftime('%Y-%m-%d') if o.updated_at is not None else None]
             for o in Offer.objects.only('path', 'updated_at').order_by('+path')]

    pages = [[urlparse.urljoin(url_root, url_for('site.dispatcher', path=page.path)),
              page.updated_at.strftime('%Y-%m-%d') if page.updated_at is not None else None]
             for page in Page.objects.only('path', 'updated_at').order_by('+position')]

    now = datetime.now().strftime('%Y-%m-%d')
    temp_pages = [[urlparse.urljoin(url_root, url_for('site.{}'.format(rule))), now]
                  for rule in ('upto1000', 'specials')]

    context = {'root': [url_root, datetime.now().strftime('%Y-%m-%d')],
               'categories': categories,
               'offers': offers,
               'pages': pages,
               'temp_pages': temp_pages}

    sitemap = render_template('misc/sitemap.xml', **context)
    response = make_response(sitemap)
    response.headers['Content-Type'] = 'application/xml'

    return response


@site.route('/specials/')
def specials():
    offers = Offer.objects(special__ne=None).order_by('price.ru')
    return render_template('specials.html', offers=offers)


@site.route('/up-to-1000/')
def upto1000():
    offers = Offer.objects(price__ru__lt=1000.00,
                           available=True).order_by('-stats.populatiry')
    return render_template('upto1000.html', offers=offers)


@site.route('/search/')
def search():
    s = request.args.get('s', '')

    if s:
        offers = Offer.objects.search_text(s).order_by('$text_score')
    else:
        offers = []

    return render_template('search.html',
                           offers=offers,
                           s=s)

@site.route('/profile/')
def profile():

    return render_template('profile.html')


@site.errorhandler(404)
def page_not_found(e):
    context = {'error': e}
    context['title'] = u'Страница не найдена'
    context['error_name'] = u'Ошибка 404'
    context['error_text'] = u'Вы перешли по неправильной ссылке<br />или страница была удалена'
    return render_template('errors.html', **context), e.code


@site.errorhandler(403)
def page_not_found(e):
    context = {'error': e}
    context['title'] = u'Страница не доступна'
    context['error_name'] = u'Ошибка 403'
    context['error_text'] = u'У вас нет прав для<br />доступа к этой странице'
    return render_template('errors.html', **context), e.code


@site.route('/cart/', methods=['GET', 'POST'])
def cart():
    cart = Cart.get_or_create()

    if request.method == 'POST':
        offer_id = request.form.get('offer_id', None)

        if offer_id:
            quantity = request.form.get('quantity', 1)
            variant = request.form.get('variant', None)
            cart.add_offer(offer_id, quantity, variant)

            return redirect(url_for('site.cart'))

    return render_template('cart.html')


@site.route('/order/', defaults={'order_id': None}, methods=['POST'])
@site.route('/order/<order_id>/')
def order(order_id=None):
    if not order_id and request.method == 'POST':
        cart = Cart.get_or_create()
        order_id = cart.send_order(request.form)
        if order_id:
            return json.dumps(dict(order_id=order_id, backurl=url_for('site.order', order_id=order_id)))
        else:
            error = u'Что-то пошло не так и заказ не отправился'
            return json.dumps(dict(error=error))

    order = Order.objects.get_or_404(id=order_id)

    region_id = order.userinfo.get('region_id', None)
    payment_id = order.userinfo.get('payment_method', None)
    delivery_id = order.userinfo.get('delivery_method', None)

    region = Region.objects(id=region_id).first() if region_id else None
    payment = PaymentMethod.objects(id=payment_id).first() if payment_id else None
    delivery = DeliveryMethod.objects(id=delivery_id).first() if delivery_id else None

    # conf = ApishopConfig.get_config()
    # conn = api_connect(conf)
    #
    # from pprint import pprint
    # for key, item in conn.get_order_states().items():
    #     print key, item
    #
    # info = conn.get_orders_info(str(order.apishop_id))[0]
    #
    # for attr in vars(info):
    #     print u'{}\t\t\t: {}'.format(attr, getattr(info, attr, None))

    return render_template('order.html',
                           order=order,
                           region=region,
                           payment=payment,
                           delivery=delivery)


@site.route('/order/<order_id>/api/upsale/', methods=['GET', 'POST'])
def order_upsale(order_id):
    if request_wants_json():
        order = Order.objects(id=order_id).first()

        if order and request.method == 'GET':
            offers = order.get_relevant_offers(3)

            if not offers.count():
                return None

            favorites = session.get('favorites', [])
            offers = [dict(id=str(offer.id),
                           name=offer.name,
                           url=url_for('site.dispatcher', path=offer.path),
                           favorited=str(offer.id) in favorites,
                           category=dict(name=offer.parent.name,
                                         url=url_for('site.dispatcher',
                                                     path=offer.parent.path)),
                           price=offer.get_price(),
                           oldprice=offer.get_oldprice,
                           timer=offer.get_timer,
                           picture=offer.get_picture()) for offer in offers]

            return jsonify(offers=offers)

        if order and request.method == 'POST':
            offer_id = request.form.get('offer_id', None)
            if not offer_id:
                return jsonify(error=True)

            offer = Offer.objects(id=offer_id).first()
            if not offer:
                return jsonify(error=True)

            quantity = request.form.get('quantity', 1)
            variant_id = request.form.get('variant_id', None)
            variant = offer.get_variant(variant_id)

            sale = send_upsale(order, offer, quantity, variant)

            order.add_offer(offer, quantity, variant)

            # item = {
            #     'picture': offer.get_picture(),
            #     'name': offer.name,
            #     'price': offer.get_price(),
            #     'quantity': quantity,
            #     'total': offer.get_price() * quantity,
            #     'url': url_for('site.dispatcher', path=offer.path),
            # }

            return jsonify(error=False)

    return abort(404)


@site.route('/cart/api/', defaults={'offer_id': None}, methods=['POST'])
@site.route('/cart/api/<offer_id>/', methods=['POST'])
@csrf.exempt
def cart_api(offer_id=None):

    if offer_id:
        variants = []
        offer = Offer.objects(id=offer_id).first()
        if offer:
            variants = [dict(name=variant.name,
                             count=variant.store_count,
                             id=variant.aid) for variant in offer.variants]

        return json.dumps(dict(variants=variants))
    else:
        cart = Cart.get_or_create()
        form = request.form

        offer_id = form.get('offer_id', None)
        if offer_id:
            remove = True if form.get('remove') == 'true' else False
            variant_id = form.get('variant_id')
            if remove:
                cart.remove_offer(offer_id, variant_id)
            else:
                cart.add_offer(offer_id, form.get('quantity', 1), variant_id)

            cart.reload()


        offers = []
        for offer in cart.offers:
            cart_offer = dict(id=offer.offer.id,
                              quantity=offer.quantity,
                              name=offer.offer.name,
                              url=url_for('site.dispatcher', path=offer.offer.path),
                              image=offer.offer.get_picture('small'),
                              price=offer.offer.get_price(),
                              oldprice=offer.offer.get_oldprice)
            if offer.variant:
                cart_offer['variant'] = dict(id=offer.variant,
                                             name=offer.offer.get_variant(offer.variant).name)
            offers.append(cart_offer)

        data = dict(offers=offers,
                    userinfo=session.get('userinfo', None))

        return json.dumps(data)


@site.route('/cart/api/aul/', methods=['POST'])
@csrf.exempt
def get_offer_articul():
    if request_wants_json():
        oid = request.form.get('offer_id', None)
        if not oid:
            return jsonify(error=True)

        offer = Offer.objects(id=oid).only('articul').first()
        if not offer:
            return jsonify(error=True)

        return jsonify(articul=offer.articul)

    return abort(404)


@site.route('/cart/api/d/regions/', methods=['POST'])
@csrf.exempt
def cart_delivery():
    if request_wants_json():
        q = request.form.get('q', '')
        if len(q) >= 2:
            regions = [{'id': str(region.id), 'text': region.name}
                       for region
                       in Region.objects(name__istartswith=q)[:10]]
        else:
            regions = [{'id': str(region.id), 'text': region.name}
                       for region
                       in Region.objects[:10]]
        return jsonify(regions=regions)

    return abort(404)


@site.route('/cart/api/d/paydel/', methods=['POST'])
@csrf.exempt
def cart_payment_delivery():

    def get_delivery_payment_ids(cart_delivery):
        delivery_ids = []
        payment_ids = []
        for delivery in cart_delivery:
            delivery, payment = delivery.get_deliveries_ids()
            delivery_ids = delivery_ids + delivery
            payment_ids = payment_ids + payment

        return list(set(delivery_ids)), list(set(payment_ids))


    def get_delivery_payment(delivery_ids=[], payment_ids=[]):
        deliveries = DeliveryMethod.objects()
        payments = PaymentMethod.objects()

        r_deliveries = [{'id': d.id, 'name': d.name} for d in deliveries if str(d.id) in delivery_ids]
        r_payments = [{'id': p.id, 'name': p.name} for p in payments if str(p.id) in payment_ids]

        return {'deliveries': r_deliveries,
                'payments': r_payments}

    if request_wants_json():
        region_id = request.form.get('region_id', None)
        if region_id is None:
            return jsonify(data=get_delivery_payment())

        region = Region.objects(id=region_id).first()
        if not region:
            return jsonify(data=get_delivery_payment())

        userinfo = session.get('userinfo', None)
        if userinfo:
            session_region = userinfo.get('region', None)
            if not session_region or not isinstance(session_region, dict) or session_region['id'] != region_id:
                session['userinfo']['region'] = {'name': region.name, 'id': region_id}
                region.int_popularity()
        else:
            session['userinfo'] = {'region': {'name': region.name, 'id': region_id}}
            region.int_popularity()

        conf = ApishopConfig.get_config()
        conn = api_connect(conf)

        aid = request.form.get('aid', None)
        curr_id = 0
        if not aid:
            cart = Cart.get_or_create()
            cart_string = ','.join(['-'.join([str(o.offer.aid), str(o.quantity)]) for o in cart.offers])
        else:
            cart = None
            cart_string = '-'.join([str(aid), str(1)])

        result = None
        if not region.updated_at or datetime.now() - region.updated_at > timedelta(days=5):
            result = conn.get_cart_delivery(cart_string, curr_id, int(region_id))

            if not aid and len(cart.offers):
                aid = cart.offers[0].offer.aid

            methods = region.get_delivery_prices(result, aid)
            region.update_deliveries(methods)
        else:
            methods = region.deliveries

        if cart and len(cart.offers):
            if not result:
                result = conn.get_cart_delivery(cart_string, curr_id, int(region_id))
            delivery_ids, payment_ids = get_delivery_payment_ids(result)
            return jsonify(data=get_delivery_payment(delivery_ids, payment_ids))
        else:
            return jsonify(data=methods)

    return abort(404)


@site.route('/cart/api/d/check/', methods=['POST'])
@csrf.exempt
def cart_check():

    if request_wants_json():
        region_id = request.form.get('region_id', None)
        payment_method = request.form.get('payment_method', None)
        delivery_method = request.form.get('delivery_method', None)

        if any([region_id, payment_method, delivery_method]) is None:
            return jsonify(data={})

        conf = ApishopConfig.get_config()
        conn = api_connect(conf)
        cart = Cart.get_or_create()

        cart_string = ','.join(['-'.join([str(o.offer.aid),
                                          str(o.quantity),
                                          str(delivery_method),
                                          str(payment_method)]) for o in cart.offers])


        result = conn.check_order(cart_string, 0, int(region_id))

        from utils.template_filters import smart_round

        if result:
            return jsonify(data=dict(price=smart_round(result.price),
                                     delivery_price=smart_round(result.delivery),
                                     order_sum=smart_round(result.sum),
                                     days=result.days))

        return jsonify(data=dict(error=True))

    return abort(404)


@site.route('/cart/api/q/', methods=['POST'])
@site.route('/cart/api/q/<offer_id>/')
@csrf.exempt
def quick_cart(offer_id=None):

    if request.method == 'POST' and request_wants_json():
        offer_id = request.form.get('offer_id', None)
        offer = Offer.objects(id=offer_id).first()

        if offer:
            quantity = request.form.get('count', 1)
            variant_id = request.form.get('variant', None)

            if variant_id:
                variant = offer.get_variant(variant_id)
                variant = str(variant.aid)
            else:
                variant = None

            cart_offer = dict(articul=offer.articul,
                              aid=offer.aid,
                              quantity=quantity,
                              variant=variant,
                              price=offer.get_price())

            form = dict(phone=request.form.get('phone'))


            order_id = send_order([cart_offer], form)

            return jsonify(order=dict(order_id=order_id,
                                      url=url_for('site.order', order_id=order_id)))

        return jsonify(errors=True)

    if offer_id and request_wants_json():
        offer = Offer.objects(id=offer_id).first()
        if offer:
            offer = dict(name=offer.name,
                         url=url_for('site.dispatcher', path=offer.path),
                         category=dict(
                             name=offer.parent.name,
                             url=url_for('site.dispatcher', path=offer.parent.path),
                         ),
                         price=offer.get_price(),
                         oldprice=offer.get_oldprice,
                         timer=offer.get_timer,
                         variants=[dict(name=variant.name,
                                        count=variant.store_count,
                                        id=variant.aid) for variant in offer.variants],
                         picture=offer.get_picture('medium'))



            user = session.get('userinfo', None)
            if user:
                name = user.get('fullname', '')
                phone = user.get('phone', '')

                offer['user'] = dict(name=name,
                                     phone=phone)

            return jsonify(offer=offer)

        return jsonify(offer={})

    return abort(404)

@site.route('/cart/api/r/')
@csrf.exempt
def related_cart():
    if request_wants_json():
        cart = Cart.get_or_create()
        ids_in_cart = cart.get_offer_ids()

        filters = {
            'available': True,
            'id__nin': ids_in_cart,
        }

        founded_ids = Offer.objects(**filters).distinct('id')

        try:
            max_items = 4
            random_ids = random.sample(founded_ids, max_items)
        except ValueError:
            random_ids = random.sample(founded_ids, len(founded_ids))

        offers = Offer.objects(id__in=random_ids)
        favorites = session.get('favorites', [])
        if offers.count():
            offers = [dict(id=str(offer.id),
                           name=offer.name,
                           url=url_for('site.dispatcher', path=offer.path),
                           favorited=str(offer.id) in favorites,
                           category=dict(name=offer.parent.name,
                                         url=url_for('site.dispatcher',
                                                     path=offer.parent.path)),
                           price=offer.get_price(),
                           oldprice=offer.get_oldprice,
                           timer=offer.get_timer,
                           picture=offer.get_picture()) for offer in offers]

        return jsonify(offers=offers)

    return abort(404)


@csrf.exempt
@site.route('/reviews/', methods=['POST'])
def reviews():
    form = request.form
    offer_id = form.get('offer_id', None)
    offer = Offer.objects(id=offer_id).first()

    if offer:
        fullname = Markup(form.get('fullname')).striptags()
        email = Markup(form.get('email')).striptags()
        text = clear_tags_and_make_lines(form.get('review'))
        rating = Markup(form.get('rating')).striptags()

        try:
            rating = int(rating)
        except (TypeError, ValueError):
            rating = 0

        review = Review(offer=offer,
                        fullname=fullname,
                        email=email,
                        text=text,
                        rating=rating)

        if current_user.is_authenticated and current_user.has_role('admin'):
            review.is_moderated = True

        review.save()

        userinfo = session.get('userinfo', None)
        if userinfo:
            if not userinfo.get('fullname', None):
                userinfo['fullname'] = fullname
            if not userinfo.get('email', None):
                userinfo['email'] = email
        else:
            userinfo = dict(fullname=fullname,
                            email=email)

        session['userinfo'] = userinfo

    return json.dumps(dict(hello='world'))


@site.route('/subscribe/', methods=['POST'])
@csrf.exempt
def subscribe():
    form = SubscribeForm(request.form, csrf_enabled=False)

    if form.validate_on_submit():
        subscriber = Subscriber.objects(email=form.email.data).first()

        if not subscriber:
            subscriber = Subscriber(email=form.email.data,
                                    name=form.name.data)
            subscriber.save()

        else:
            if subscriber.name != form.name.data:
                subscriber.update(set__name=form.name.data)

        subscriber.mark_subscribed()

        if request_wants_json():
            return jsonify(errors=False)
    else:
        if request_wants_json():
            errors = {n: v[0] for n, v in form.errors.items()}
            return jsonify(errors=errors)

    return redirect(request.args.get('next') or url_for('site.index'))


@site.route('/favorites/', methods=['GET', 'POST'])
@csrf.exempt
def favorites():
    favorites = session.get('favorites', [])

    for fav in favorites:
        try:
            int(fav)
        except ValueError:
            favorites.remove(fav)
            session['favorites'] = favorites

    if request.method == 'POST':
        offer_id = request.form.get('offer_id', None)

        if request_wants_json():
            if offer_id and offer_id in favorites:
                favorites.remove(offer_id)

            elif offer_id and offer_id not in favorites:
                favorites.append(offer_id)

            session['favorites'] = favorites

            return jsonify(favorites=favorites)

        return

    offers = Offer.objects(id__in=favorites)
    ids = offers.distinct('id')

    # Проверяем, совпадает ли количество найденых товаров
    # Если нет, то популяризируем favorites
    if len(ids) != len(favorites):
        favorites = [str(id) for id in ids]
        session['favorites'] = favorites

    return render_template('favorites.html', offers=offers)




@site.route('/<path:path>/')
def dispatcher(path):
    d_key = Dispatcher.get_by_path(path)
    d = d_map.get(d_key, None)

    if not d:
        return abort(404)

    template, context = d(path).dispatch()

    if template == 'redirect':
        return redirect(**context)
    elif template == 'abort':
        return abort(404)

    return render_template(template, **context)


def send_order(offers, form):

    full_name = Markup(form.get('fullname', u'Имя не указано')).striptags()
    phone = Markup(form.get('phone', None)).striptags()
    address = Markup(form.get('address', u'')).striptags()
    email = Markup(form.get('email', u'')).striptags()
    comment = clear_tags_and_make_lines(form.get('comment', None))

    region_id = form.get('region[id]', None)
    delivery_method = form.get('delivery', None)
    payment_method = form.get('payment', None)

    delivery_info = {}

    for item in ('days', 'price', 'order_sum', 'delivery_price'):
        getted = form.get('delivery_info[{}]'.format(item), None)
        if getted:
            delivery_info[item] = getted

    if not len(offers) or not phone:
        # Если нет товаров или имени и телефона возвращаем ошибку
        return None

    conf = ApishopConfig.get_config()
    apishop = api_connect(conf)

    order_id = None
    sended_offers = []
    for idx, offer in enumerate(offers):
        articul = offer.get('articul')
        product_id = offer.get('aid')
        quantity = offer.get('quantity', 1)
        variant = offer.get('variant', None)
        price = offer.get('price')

        if not order_id:
            _address = address if address != u'' else u'Уточнить при звонке'
            order_id = apishop.submit_fast_order(articul, quantity, full_name, phone, _address,
                                                 None, None, None, None, None, None,
                                                 None, None, comment, None, variant, price)
            if order_id:
                sended_offers.append(offer)
        else:
            error = apishop.add_product_to_order(order_id, articul, product_id, quantity,
                                                variant, price, True)
            if not error:
                sended_offers.append(offer)


    # Сохраняем данные пользователя в сессии
    userinfo = dict(phone=phone,
                    address=address,
                    email=email,
                    region_id=region_id,
                    payment_method=payment_method,
                    delivery_method=delivery_method,
                    comment=comment)

    if full_name != u'Имя не указано':
        userinfo['fullname'] = full_name

    if not session.get('userinfo', None):
        session['userinfo'] = userinfo
    else:
        for key, value in userinfo.items():
            session['userinfo'][key] = value

    if not order_id:
        return None

    order = Order(apishop_id=order_id,
                  ordered_at=datetime.now(),
                  userinfo=userinfo,
                  comment=comment)
    order.delivery_info = delivery_info
    order.populate_offers(sended_offers)
    order.save()

    our_order_id = str(order.id)

    if session.get('orders', None) and isinstance(session['orders'], list):
        session['orders'].append(our_order_id)
    else:
        session['orders'] = [our_order_id]

    # В итоге возвращаем order.id в нашей системе
    return our_order_id


def send_upsale(order, offer, quantity, variant=None):
    if not order.get_timer or not offer.available:
        return

    conf = ApishopConfig.get_config()
    apishop = api_connect(conf)

    result = apishop.add_product_to_order(order.apishop_id, offer.articul, offer.aid,
                                          quantity, variant, offer.get_price(), True)

    return result