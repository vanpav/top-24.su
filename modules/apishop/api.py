# -*- coding: utf-8 -*- #

from hashlib import md5
import xml.etree.cElementTree as ET
from suds.client import Client

class AsApi(object):

    def __init__(self, login, password, url, site):
        self.login = login
        self.password = md5(password).hexdigest()
        self.site = site
        self.client = Client(url)

    def get_regions(self):
        params = dict(login = self.login,
                      password = self.password)
        answer = self.client.service.getRegions(**params).resultXml        
        tree = ET.fromstring(answer.encode('utf-8'))

        return dict(
                    (region.attrib.get('id'), region.find('name').text) \
                    for region in tree.find('regions').findall('region')
                  )

    def get_addr_regions(self):
        params = dict(login = self.login,
                      password = self.password)
        answer = self.client.service.getAddrRegions(**params).resultXml
        tree = ET.fromstring(answer.encode('utf-8'))

        return dict((region.attrib.get('id'), region.find('name').text) \
                    for region in tree.find('regions').findall('region'))

    # DEPRECATED    
    def get_regions_for_products(self, ids):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        ids = ids
                     )        
        answer = self.client.service.getRegionsForProducts(**params).resultXml
        tree = ET.fromstring(answer.encode('utf-8'))

        return dict(
                    (region.attrib.get('id'), region.find('name').text) \
                    for region in tree.find('regions').findall('region'))

    def get_currencies(self):
        params = dict(
                        login = self.login,
                        password = self.password
                     )
        answer = self.client.service.getCurrencies(**params).resultXml
        tree = ET.fromstring(answer.encode('utf-8'))

        return dict(
                        (currency.attrib.get('id'), currency.find('name').text) \
                        for currency in tree.find('currencies').findall('currency')
                     )


    def get_payment_types(self):
        params = dict(
                        login = self.login,
                        password = self.password
                     )
        answer = self.client.service.getPaymentTypes(**params).resultXml
        tree = ET.fromstring(answer.encode('utf-8'))

        return dict(
                        (payment.attrib.get('id'), payment.find('name').text) \
                        for payment in tree.find('payments').findall('payment')
                   )


    def get_delivery_types(self):
        params = dict(
                        login = self.login,
                        password = self.password
                     )
        answer = self.client.service.getDeliveryTypes(**params).resultXml
        tree = ET.fromstring(answer.encode('utf-8'))

        return dict(
                        (delivery.attrib.get('id'), delivery.find('name').text) \
                        for delivery in tree.find('deliveries').findall('delivery')
                     )


    def get_order_states(self):
        params = dict(
                        login = self.login,
                        password = self.password
                     )
        answer = self.client.service.getOrderStates(**params).resultXml        
        tree = ET.fromstring(answer.encode('utf-8'))  

        return dict(
                    (state.attrib.get('id'), state.find('name').text) \
                    for state in tree.find('states').findall('state')
                 )      


    def get_sites(self):
        params = dict(
                        login = self.login,
                        password = self.password
                     )
        answer = self.client.service.getSites(**params).resultXml
        tree = ET.fromstring(answer.encode('utf-8'))

        return dict(
                    (site.attrib.get('id'), site.find('url').text) \
                    for site in tree.find('sites').findall('site')
                 )  


    # # DEPRECATED
    def get_product_categories(self, parent):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        parent = parent
                     )
        answer = self.client.service.getProductCategories(**params).resultXml        
        tree = ET.fromstring(answer.encode('utf-8'))        

        return dict(
                    (category.attrib.get('id'), category.find('name').text) \
                    for category in tree.find('categories').findall('category')
                ) 
            

    def get_products(self, category, currency = 0):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        category = category,
                        currency = currency
                     )
        answer = self.client.service.getProducts(**params).resultXml        
        tree = ET.fromstring(answer.encode('utf-8'))        

        return list(
                    AsProductBean(
                        product.attrib.get('wpid'),
                        product.attrib.get('id'),
                        product.find('name').text if product.find('name') is not None else None,
                        product.find('price').text if product.find('price') is not None else None,
                        product.find('url').text if product.find('url') is not None else None                        
                    ) for product in tree.find('products').findall('product')
               )


    def get_products_by_ids(self, currency, ids):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        currency = currency,
                        ids = ids
                    )        
        answer = self.client.service.getProductsForIds(**params).resultXml        
        tree = ET.fromstring(answer.encode('utf-8'))        

        return list(
                    AsProductBean(
                        id = product.attrib.get('id'),
                        pid = product.attrib.get('wpid'),
                        name = product.find('name').text if product.find('name') is not None else None,
                        price = product.find('price').text if product.find('price') is not None else None,
                        url = product.find('url').text if product.find('url') is not None else None
                    ) for product in tree.find('products').findall('product')
                   )
    
    def get_self_deliveries_for_region(self, region_id):
        params = dict(
                        login = self.login,
                        password = self.password,
                        regionId = region_id
                    )
        answer = self.client.service.getSelfDeliveriesForRegion(**params).resultXml        
        tree = ET.fromstring(answer.encode('utf-8')) 

        return list(
                    AsSelfDelivery(
                        sd.attrib.get('id'),
                        sd.find('regionId').text if sd.find('regionId') is not None else None,
                        sd.find('name').text if sd.find('name') is not None else None,
                        sd.find('address').text if sd.find('address') is not None else None,
                        sd.find('phone').text if sd.find('phone') is not None else None,
                        sd.find('workTime').text if sd.find('workTime') is not None else None,
                        sd.find('deliveryTime').text if sd.find('deliveryTime') is not None else None
                    ) for sd in tree.find('sdlist').findall('sd')
               )


    def get_cart_items(self, cart, currency):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        currency = currency,
                        cart = cart
                    )
        answer = self.client.service.getCartItems(**params).resultXml        
        tree = ET.fromstring(answer.encode('utf-8'))  

        return list(
                    AsCartItem(
                        item.attrib.get('id'),
                        item.find('name').text if item.find('name') is not None else None,
                        item.find('price').text if item.find('price') is not None else None,
                        item.find('count').text if item.find('count') is not None else None
                    ) for item in tree.find('items').findall('item')
               )              


    def get_product_id_by_articul(self, articul):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        articul = articul
                    )
        answer = self.client.service.getProductIdForArticul(**params).resultXml        
        tree = ET.fromstring(answer.encode('utf-8'))        

        return tree.find('id').attrib.get('id', None)

    
    def get_cart_delivery(self, cart, currency, region):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        currency = currency,
                        cart = cart,
                        region = region
                    )
        answer = self.client.service.getCartDelivery(**params).resultXml
        tree = ET.fromstring(answer.encode('utf-8'))

        return list(
                    AsCartDelivery(
                        item.attrib.get('id'),
                        item.find('count').text,
                        list(
                            AsDelivery(
                                delivery.attrib.get('id'),
                                list(
                                    AsDeliveryPayment(
                                        payment.attrib.get('id'),
                                        payment.find('sum').text
                                    ) for payment in delivery.findall('payment')
                                )
                            ) for delivery in item.findall('delivery')
                        )
                    ) for item in tree.find('items').findall('item')
                )


    def check_order(self, cart, currency, region, zip=''):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,                        
                        cart = cart,
                        currency = currency,
                        region = region,
                        zip = zip
                    )

        answer = self.client.service.checkOrder(**params).resultXml
        tree = ET.fromstring(answer.encode('utf-8'))

        error = tree.find('order').text == '0' if tree.find('order') is not None else False
        if error:
            return None

        return AsCheckOrder(
                    tree.find('order').text,
                    tree.find('cart').text if tree.find('cart') is not None else None,
                    tree.find('price').text if tree.find('price') is not None else None,
                    tree.find('delivery').text if tree.find('delivery') is not None else None,
                    tree.find('sum').text if tree.find('sum') is not None else None,
                    tree.find('days').text if tree.find('days') is not None else None,
                    tree.find('date').text if tree.find('date') is not None else None,
                    list(
                        AsCheckOrderItem(
                            item.attrib.get('id'),
                            item.find('count').text if item.find('count') is not None else None,
                            item.find('price').text if item.find('price') is not None else None,
                            item.find('delivery').text if item.find('delivery') is not None else None,
                            item.find('sum').text if item.find('sum') is not None else None,
                            item.find('days').text if item.find('days') is not None else None,
                            item.find('date').text if item.find('date') is not None else None
                        ) for item in tree.find('items').findall('item')
                    )
               )


    def submit_fast_order(self, articul, count, fio, phone,
                          address, source_param, source_ref,
                          client_timezone, sub_account, sub_wmid,
                          sub_account_website, client_ip,
                          promocode=None, address_comment=None,
                          lang_id=None, product_variant_id=None,
                          new_price=None):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,                        
                        articul = articul,
                        count = count,
                        fio = fio,
                        phone = phone,
                        address = address,
                        sourceParam = source_param,
                        sourceRef = source_ref,
                        clientTimeZone = client_timezone,
                        ip = client_ip,
                        subAccount = sub_account,
                        subWmid = sub_wmid,
                        subAccountWebsite = sub_account_website,
                        promocode = promocode,
                        addressComment = address_comment,
                        langId = lang_id,
                        productVariantId = product_variant_id,
                        newPrice = new_price
                    )
        answer = self.client.service.submitFastOrder(**params).resultXml

        if not answer:
            return False

        tree = ET.fromstring(answer.encode('utf-8'))

        return tree.find('id').text if tree.find('id') is not None else False


    ###### Метод не проверен ######
    def submit_order(self, cart, currency, region, zip, 
                     user_sum, user_date, skip_errors, 
                     recipient, source_param, source_ref, 
                     client_timezone = None, promocode = None):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,                        
                        currency = currency,
                        cart = cart,
                        region = region,
                        zip = zip,
                        userSum = user_sum,
                        userDate = user_date,
                        skip_errors = skip_errors,
                        userInfo = dict(
                                        name = recipient.name,
                                        address = recipient.address,
                                        phone1 = recipient.phone1,
                                        phoneTime1 = recipient.phone_time1,
                                        phone2 = recipient.phone2,
                                        phoneTime2 = recipient.phone_time2,
                                        email = recipient.email,
                                        addressComment = recipient.address_comment,
                                        orgAddress = recipient.org_address,
                                        orgBank = recipient.org_bank,
                                        orgBankcity = recipient.org_bankcity,
                                        orgBik = recipient.org_bik,
                                        orgInn = recipient.org_inn,
                                        orgKpp = recipient.org_kpp,
                                        orgKs = recipient.org_ks,
                                        orgName = recipient.org_name,
                                        orgOkpo = recipient.org_okpo,
                                        orgOkved = recipient.org_okved,
                                        orgRs = recipient.org_rs,
                                        orgType = recipient.org_type
                                   ),                            
                        sourceParam = source_param,
                        sourceRef = source_ref,
                        clientTimeZone = client_timezone,
                        promocode = promocode
                    )

        answer = self.client.service.submitOrder(**params).resultXml
        tree = ET.fromstring(answer.encode('utf-8'))

        return AsSubmitOrder(
                    tree.find('id').text,                    
                    tree.find('cart').text if tree.find('cart') is not None else None,
                    tree.find('price').text if tree.find('price') is not None else None,
                    tree.find('delivery').text if tree.find('delivery') is not None else None,
                    tree.find('sum').text if tree.find('sum') is not None else None,
                    tree.find('days').text if tree.find('days') is not None else None,
                    tree.find('date').text if tree.find('date') is not None else None,
                    tree.find('url').text if tree.find('url') is not None else None,
                    tree.find('info1').text if tree.find('info1') is not None else None,
                    tree.find('info2').text if tree.find('info2') is not None else None,
                    list(
                        AsCheckOrderItem(
                            item.attrib.get('id'),
                            item.find('count').text if item.find('count') is not None else None,
                            item.find('price').text if item.find('price') is not None else None,
                            item.find('delivery').text if item.find('delivery') is not None else None,
                            item.find('sum').text if item.find('sum') is not None else None,
                            item.find('days').text if item.find('days') is not None else None,
                            item.find('date').text if item.find('date') is not None else None
                        ) for item in tree.find('items').findall('item')
                    )
               )


    def add_product_to_order(self, order_id, articul, product_id, count,
                             product_variant_id=None, new_price=None, error=False):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        orderId = order_id,
                        articul = articul,
                        productId = str(product_id),
                        count = count,
                        productVariantId = product_variant_id,
                        newPrice = new_price,
                        error = error

                     )
        answer = self.client.service.addProductToOrder(**params)
        
        return answer.errorId is 0


    def create_order_ticket(self, name, email, text):
        params = dict(
                        name = name,
                        email = email,
                        siteId = self.site,
                        text = text
                     )
        answer = self.client.service.createOrderTicket(**params)

        return answer if answer else None


    def get_orders(self, offset = None, limit = None):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        offset = offset,
                        limit = limit
                     )
        answer = self.client.service.getOrders(**params).resultXml
        tree = ET.fromstring(answer.encode('utf-8'))

        return list(
                    AsOrder(
                        order.attrib.get('id'),
                        order.attrib.get('confirmed'),
                        order.attrib.get('refuseReason'),
                        order.attrib.get('postId'),
                        order.attrib.get('address'),
                        '',
                        order.attrib.get('phone1'),
                        order.attrib.get('email'),
                        order.attrib.get('sourceRef'),
                        order.attrib.get('sourceParam'),
                        list(
                                AsOrderItem(
                                    item.attrib.get('id'),
                                    item.attrib.get('statusId'),
                                    '',
                                    '',
                                    item.attrib.get('count'),
                                    item.attrib.get('commission')
                                ) for item in order.findall('items')
                            ) 
                    ) for order in tree.find('orders').findall('order')
                )
        

    def get_orders_info(self, ids):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        ids = ids
                     )
        answer = self.client.service.getOrdersInfo(**params).resultXml
        tree = ET.fromstring(answer.encode('utf-8'))

        return list(
                    AsOrder(
                        order.attrib.get('id'),
                        order.attrib.get('confirmed'),
                        order.attrib.get('refuseReason'),
                        order.attrib.get('postId'),
                        order.attrib.get('address'),
                        '',
                        order.attrib.get('phone1'),
                        order.attrib.get('email'),
                        order.attrib.get('sourceRef'),
                        order.attrib.get('sourceParam'),
                        list(
                                AsOrderItem(
                                    item.attrib.get('id'),
                                    item.attrib.get('statusId'),
                                    '',
                                    '',
                                    item.attrib.get('count'),
                                    item.attrib.get('commission')
                                ) for item in order.findall('items')
                            ) 
                    ) for order in tree.find('orders').findall('order')
                )

    
    def get_financial_info(self):
        params = dict(
                        login = self.login,
                        password = self.password                      
                     )
        answer = self.client.service.getFinancialInfo(**params)
        tree = ET.fromstring(answer.encode('utf-8'))

        return AsUserFinanceInfo(
                    tree.find('balance').text if tree.find('balance') is not None else None,
                    tree.find('available').text if tree.find('available') is not None else None,
                    tree.find('blocked').text if tree.find('blocked') is not None else None,
                    tree.find('campaignexpense24h').text if tree.find('campaignexpense24h') is not None else None,
                    tree.find('websiteprofit24h').text if tree.find('websiteprofit24h') is not None else None,
                    tree.find('referralprofit24h').text if tree.find('referralprofit24h') is not None else None,
                    tree.find('profit24h').text if tree.find('profit24h') is not None else None
               )


    def search_webmaster_product_producer(self, key):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        key = key
                     )
        answer = self.client.service \
                     .seachWebmasterProductProducer(**params).resultXml
        tree = ET.fromstring(answer.encode('utf-8'))

        return list(
                    AsProductProducer(
                        wpp.attrib.get('id'),
                        wpp.find('productProducerId').text \
                            if wpp.find('productProducerId') is not None else None,
                        wpp.find('name').text if wpp.find('name') is not None else None,
                        wpp.find('latName').text if wpp.find('latName') is not None else None,
                        wpp.find('desc').text if wpp.find('desc') is not None else None,
                        wpp.find('metakeywords').text \
                            if wpp.find('metakeywords') is not None else None,
                        wpp.find('metadescription').text \
                            if wpp.find('metadescription') is not None else None,
                    ) for wpp in tree.find('webmasterProductProducers') \
                                     .findall('webmasterProductProducer')
               )

    ##### Метод не проверен
    def  parse_webmaster_product_xml(self, xml):                
        return list(
                    AsWebmasterProduct(
                        wp.attrib.get('id'),
                        wp.find('wp_name').text if wp.find('wp_name') is not None else None,
                        wp.find('wp_lat_name').text if wp.find('wp_lat_name') is not None else None,
                        wp.find('wp_articul').text if wp.find('wp_articul') is not None else None,
                        wp.find('wp_model').text if wp.find('wp_model') is not None else None,
                        wp.find('wp_text').text if wp.find('wp_text') is not None else None,
                        wp.find('wp_short_name').text if wp.find('wp_short_name') is not None else None,
                        wp.find('wp_price').text if wp.find('wp_price') is not None else None,
                        wp.find('wp_webmaster_cat_id').text \
                            if wp.find('wp_webmaster_cat_id') is not None else None,
                        wp.find('wp_category_id').text if wp.find('wp_category_id') is not None else None,
                        wp.find('wp_website_id').text if wp.find('wp_website_id') is not None else None,
                        wp.find('wp_product_id').text if wp.find('wp_product_id') is not None else None,
                        wp.find('wp_producer_id').text if wp.find('wp_producer_id') is not None else None,
                        wp.find('wp_not_for_sale').text \
                            if wp.find('wp_not_for_sale') is not None else None,
                        wp.find('wp_desc').text if wp.find('wp_desc') is not None else None,
                        wp.find('wp_key').text if wp.find('wp_key') is not None else None,
                        wp.find('wp_sort_val').text if wp.find('wp_sort_val') is not None else None,
                        wp.find('wp_create_date').text if wp.find('wp_create_date') is not None else None,
                        wp.find('wp_need_to_upload').text \
                            if wp.find('wp_need_to_upload') is not None else None,
                        wp.find('imgUrl').text if wp.find('imgUrl') is not None else None,
                        wp.find('defaultImg').text if wp.find('defaultImg') is not None else None,
                        wp.find('webmasterProductPictureUrl').text \
                            if wp.find('webmasterProductPictureUrl') is not None else None,
                        wp.find('webmasterCategoryUrl').text \
                            if wp.find('webmasterCategoryUrl') is not None else None,
                        wp.find('webmasterCategoryName').text \
                            if wp.find('webmasterCategoryName') is not None else None,
                        wp.find('webmasterCategoryLatName').text \
                            if wp.find('webmasterCategoryLatName') is not None else None,
                    ) for wp in xml.find('webmasterproducts') \
                                   .findall('webmasterproduct')
               )

    ##### Ошибка при генерации, т.к. возвращает xml с webmasterProducts
    def search_webmaster_product_by_web_category_id(self, web_category_id):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        webCategoryId = web_category_id
                     ) 
        answer = self.client.service \
                     .seachWebmasterProductByWebCategoryId(**params).resultXml        
        tree = ET.fromstring(answer.encode('utf-8'))
        
        return  self.parse_webmaster_product_xml(tree)

    
    def search_webmaster_product(self, key):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        key = key
                     )
        answer = self.client.service \
                     .seachWebmasterProduct(**params).resultXml
        tree = ET.fromstring(answer.encode('utf-8'))
        
        return  self.parse_webmaster_product_xml(tree)

    ##### Метод не проверен, не возвращает ответ, не понятно что такое data
    def product_search(self, cat_id, data):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        catId = cat_id,
                        data = data
                     )
        answer = self.client.service.productSearch(**params).resultXml         
        if answer:            
            tree = ET.fromstring(answer.encode('utf-8'))
            return  self.parse_webmaster_product_xml(tree)
        return list()


    def compare_webmaster_product(self, keys, show_all = False):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        keys = keys
                     )
        answer = self.client.service.compareWebmasterProduct(**params).resultXml        
        tree = ET.fromstring(answer.encode('utf-8'))

        products = list( 
                        AsCompareWebmasterProduct(
                            wp.find('id').text if wp.find('id') is not None else None,
                            wp.find('name').text if wp.find('name') is not None else None,
                            wp.find('imageUrl').text if wp.find('imageUrl') is not None else None
                        ) for wp in tree.find('table').find('header') \
                                        .findall('webmasterproduct')
                   )

        rows = list()

        for row in tree.find('table').findall('row'):
            values = list()
            c = 0
            for row_value in row.find('webmasterproductvalue'):
                values.append(row_value.find('value').text \
                                    if row_value.find('value') is not None else None)
                if row_value.find('value') is not None and \
                            row_value.find('value').text.strip() != '-':
                    c += 1

            if c or show_all:
                rows.append(
                        AsCompareProperty(
                            row.find('property').find('name').text \
                                if row.find('property').find('name') is not None else None,
                            values
                        )
                    )

        return AsCompare(products, rows)

    ##### Метод не проверен,
    def category_fields(self, cat_id):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        catId = cat_id
                     )
        answer = self.client.service.categoryFields(**params).resultXml        
        tree = ET.fromstring(answer.encode('utf-8'))

        return list(
                    AsCompareProperty(
                        row.find('name').text if row.find('name') is not None else None,
                        list(
                            row_value.find('value').text \
                                if row_value.find('value') is not None else None \
                                for row_value in row.findall('value')                            
                        ) 
                    ) for row in tree.findall('category')
               )

    ##### Метод не проверен,
    def recall_order(self, id):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        id = id
                     )
        answer = self.client.service.recallOrder(**params)

        return answer.errorId is 0

    ##### Метод не проверен,
    def cancel_order(self, order_id, reason):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        orderId = order_id,
                        reason = reason
                     )
        answer = self.client.service.cancelOrder(**params)

        return answer.errorId is 0

    ##### Метод не проверен,
    def get_order_delivery_price(self, order_id, region_id, 
                                 delivery_type, payment_type):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        orderId = order_id,
                        regionId = region_id,
                        deliveryType = delivery_type,
                        paymentType = payment_type
                     )
        answer = self.client.service.getOrderDeliveryPrice(**params).resultXml        
        tree = ET.fromstring(answer.encode('utf-8'))

        return AsDeliveryPrice(
                    tree.find('totalSum').text if tree.find('totalSum') is not None else None,
                    tree.find('deliverySum').text if tree.find('deliverySum') is not None else None
               )

    ##### Метод не проверен,
    def confirm_order(self, order_id, region_id, mp3, delivery_type,
                      payment_type, self_delivery, name, email, phone1, phone2, 
                      addr_zip, addr_region, addr_zone, addr_city, addr_street_type, 
                      addr_street, addr_house, addr_struct, addr_housing, 
                      addr_room_type, addr_room, delivery_sum, comment):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        orderId = order_id,
                        regionId = region_id,
                        mp3 = mp3,
                        deliveryType = delivery_type,
                        paymentType = payment_type,
                        selfDelivery = self_delivery,
                        name = name,
                        email = email,
                        phone1 = phone1,
                        phone2 = phone2,
                        zip = addr_zip,
                        addrRegion = addr_region,
                        addrZone = addr_zone,
                        addrCity = addr_city,
                        addrStreetType = addr_street_type,
                        addrStreet = addr_street,
                        addrHouse = addr_house,
                        addrStruct = addr_struct,                        
                        addrRoomType = addr_room_type,
                        addrRoom = addr_room,
                        deliverySum = delivery_sum,
                        comment = comment
                     )
        answer = self.client.service.confirmOrder(**params)

        return answer.errorId is 0

    ##### Метод не проверен,
    def get_calls(self, order_id):
        params = dict(
                        login = self.login,
                        password = self.password,
                        site = self.site,
                        orderId = order_id                       
                     )
        answer = self.client.service.getCalls(**params).resultXml        
        tree = ET.fromstring(answer.encode('utf-8'))

        return list(
                    AsCall(
                        call.attrib.get('id'),
                        call.attrib.get('date'),
                        call.attrib.get('duration'),
                        call.attrib.get('phone'),
                        call.attrib.get('rate'),
                        call.find('mp3').text if call.find('mp3') is not None else None
                    ) for call in tree.find('calls').findall('call')
               )

    ##### Метод не проверен
    def rate_call(self, order_id, hash, rate):
        params = dict(
                        login = self.login,
                        password = self.password,                        
                        orderId = order_id,
                        hash = hash,
                        rate = rate                
                     )
        answer = self.client.service.rateCall(**params)

        return answer.errorId is 0




class AsCall(object):

    def __init__(self, id, date, duration, phone, rate, mp3):
        self.id = id
        self.date = date
        self.duration = duration
        self.phone = phone
        self.rate = rate
        self.mp3 = mp3


class AsDeliveryPrice(object):

    def __init__(self, total_sum, delivery_sum):
        self.total_sum = total_sum
        self.delivery_sum = delivery_sum


class AsCompare(object):

    def __init__(self, webmaster_products, values):
        self.webmaster_products = webmaster_products
        self.values = values        


class AsCompareProperty(object):

    def __init__(self, name, values):
        self.name = name
        self.values = values


class AsCompareWebmasterProduct(object):

    def __init__(self, id, name, image_url):
        self.id = id
        self.name = name
        self.image_url = image_url


class AsWebmasterProduct(object):

    def __init__(self, id, name, lat_name, articul, model, text,
                 short_name, price, webmaster_category_id, category_id,
                 website_id, product_id, producer_id, not_for_sale,
                 desc, keywords, sort_val, create_date, need_to_upload,
                 img_url, default_img, webmaster_product_picture_url,
                 webmaster_category_url, webmaster_category_name, 
                 webmaster_category_lat_name):
        self.id = id
        self.name = name
        self.lat_name = lat_name
        self.articul = articul
        self.model = model
        self.text = text
        self.short_name = short_name
        self.price = price
        self.webmaster_category_id = webmaster_category_id
        self.category_id = category_id
        self.website_id = website_id
        self.product_id = product_id
        self.producer_id = producer_id
        self.not_for_sale = not_for_sale
        self.desc = desc
        self.keywords = keywords
        self.sort_val = sort_val
        self.create_date = create_date
        self.need_to_upload = need_to_upload
        self.img_url = img_url
        self.default_img = default_img
        self.webmaster_product_picture_url = webmaster_product_picture_url
        self.webmaster_category_url = webmaster_category_url
        self.webmaster_category_name = webmaster_category_name
        self.webmaster_category_lat_name = webmaster_category_lat_name


class AsSelfDelivery(object):

    def __init__(self, id, region_id, name, address,
                 phone, work_time, delivery_time):
        self.id = id
        self.region_id = region_id
        self.name = name
        self.address = address
        self.phone = phone
        self.work_time = work_time
        self.delivery_time = delivery_time


class AsProductProducer(object):

    def __init__(self, id, product_producer_id, name,
                 lat_name, desc, meta_keywords, meta_description):
        self.id = id
        self.product_producer_id = product_producer_id
        self.name = name
        self.lat_name = lat_name
        self.desc = desc
        self.meta_keywords = meta_keywords
        self.meta_description = meta_description


class AsUserFinanceInfo(object):

    def __init__(self, balance, available, blocked,
                 campaign_expense24, website_profit24,
                 referral_profit24, profit24):
        self.balance = balance
        self.available = available
        self.blocked = blocked
        self.campaign_expense24 = campaign_expense24
        self.website_profit24 = website_profit24
        self.referral_profit24 = referral_profit24
        self.profit24 = profit24


class AsOrder(object):

    def __init__(self, id, confirmed, refuse_reason, post_id, 
                 address, address_city, phone1, email, 
                 source_ref, source_param, items):
        self.id = id
        self.confirmed = confirmed
        self.refuse_reason = refuse_reason
        self.post_id = post_id
        self.address = address
        self.address_city = address_city
        self.phone1 = phone1
        self.email = email
        self.source_ref = source_ref
        self.source_param = source_param
        self.items = items


class AsOrderItem(object):

    def __init__(self, id, status_id, product_id, articul, 
                 count, commission):
        self.id = id
        self.status_id = status_id
        self.product_id = product_id
        self.articul = articul
        self.count = count 
        self.commission = commission

                    
class AsCheckOrder(object):

    def __init__(self, order, cart, price, 
                 delivery, sum, days, date, items):
        self.order = order
        self.cart = cart
        self.price = price
        self.delivery = delivery
        self.sum = sum
        self.days = days
        self.date = date
        self.items = items


class AsCheckOrderItem(object):

    def __init__(self, pid, count, price, 
                 delivery, sum, days, date):
        self.pid = pid
        self.count = count
        self.price = price
        self.delivery = delivery
        self.sum = sum
        self.days = days
        self.date = date


class AsSubmitOrder(object):

    def __init__(self, order_id, cart, price, delivery,
                 sum, days, date, url, info1, info2, items):
        self.order_id = order_id
        self.cart = cart
        self.price = price
        self.delivery = delivery
        self.sum = sum
        self.days = days
        self.date = date
        self.url = url
        self.info1 = info1
        self.info2 = info2
        self.items = items


class AsCartDelivery(object):

    def __init__(self, pid, count, deliveries):
        self.pid = pid
        self.count = count
        self.deliveries = deliveries


    def get_deliveries_ids(self):
        delivery_ids = []
        payment_ids = []
        for delivery in self.deliveries:
            if delivery.id not in delivery_ids:
                delivery_ids.append(delivery.id)

            payments = []
            for payment in delivery.payments:
                if payment.id not in payment_ids:
                    payments.append(payment.id)

            payment_ids.append(set(payments))

        return delivery_ids, list(set.intersection(*payment_ids))


class AsCartItem(object):

    def __init__(self, pid, name, price, count):
        self.pid = pid
        self.name = name
        self.price = price
        self.count = count


class AsDelivery(object):

    def __init__(self, id, payments):
         self.id = id
         self.payments = payments


class AsDeliveryPayment(object):

    def __init__(self, id, sum):
        self.id = id
        self.sum = sum


class AsRecipient(object):

    def __init__(self, name, address, phone1, phone_time1, phone2, 
                 phone_time2, address_comment, org_address, org_bank, 
                 org_bankcity, org_bik, org_inn, org_kpp, org_ks, org_name,
                 org_okpo, org_okved, org_rs, org_type, email):
        self.name = name
        self.address = address
        self.phone1 = phone1
        self.phone_time1 = phone_time1
        self.phone2 = phone2
        self.phone_time2 = phone_time2
        self.address_comment = address_comment
        self.org_address = org_address
        self.org_bank = org_bank
        self.org_bankcity = org_bankcity
        self.org_bik = org_bik
        self.org_inn = org_inn
        self.org_kpp = org_kpp
        self.org_ks = org_ks
        self.org_name = org_name
        self.org_okpo = org_okpo
        self.org_okved = org_okved
        self.org_rs = org_rs
        self.org_type = org_type
        self.email = email


class AsProductBean(object):

    def __init__(self, id, pid, name, price, url):
        self.id = id
        self.pid = pid
        self.name = name
        self.price = price
        self.url = url        