<cart>
    <div class="cart-page__loading" if={ loading }>
        <div class="cart-page__spinner text-center">
            <div class="spinner spinner--big"><span><span></span></span></div>
            <p>Оформляем заказ</p>
        </div>
    </div>

    <div if={ !offers.length }>
        <p>В корзине пока нет товаров. Возможно вы захотите добавить эти:</p>
        <br />
    </div>

    <ul class="cart-offers" if={ offers.length }>
        <li each={ offer, idx in offers } idx={ idx } offer={ offer } class="cart-offers__item" riot-tag="cart-item"></li>
    </ul>

    <cart-form if={ offers.length } total={ cartStorage.total } userinfo={ userinfo }></cart-form>

    <cart-related></cart-related>

    <script>
        var self = this

        self.loading = false

        cartStorage.on('update', function() {
            self.offers = cartStorage.offers
            if (!self.userinfo && cartStorage.userinfo != {}) self.userinfo = cartStorage.userinfo
            self.update()
        });

    </script>
</cart>

<cart-item>
    <div class="cart-offers__item-picture">
        <a href="{ opts.offer.url }" class="link-plain"><img src="{ opts.offer.image }" alt="{ opts.offer.name }" title="{ opts.offer.name }" class="cart-offers__item-image"></a>
    </div>
    <div class="cart-offers__item-title">
        <a href="{ opts.offer.url }">{ opts.offer.name } { opts.offer.variant.name.toLowerCase() }</a>
    </div>
    <div class="cart-offers__item-price {cart-offers__item-price--special: !!opts.offer.oldprice}">
        <span if={ opts.offer.oldprice }>{ opts.offer.oldprice } руб.</span>
        {{ opts.offer.price }} руб.
    </div>
    <div class="cart-offers__item-count">
        <span class={ control__count: true }><span onclick={ decrease } class={btn: true, btn--outline: true, btn--iconed: true, btn--icon-minus: true, control__count-minus:true, btn--dissabled: opts.offer.quantity == 1 }></span><input type="text" class="input control__count-input" disabled value="{ opts.offer.quantity }"><span onclick={ increase } class="btn btn--outline btn--iconed btn--icon-plus control__count-plus"></span></span>
    </div>
    <div class="cart-offers__item-total">
        { sum } руб.
        <!--<a href="" class="icon icon-16 icon--delete link-plain cart-offers__item-delete" onclick={ remove }></a>-->
    </div>
    <div class="cart-offers__item-delete">
        <a href="" class="icon icon-16 icon--delete link-plain cart-offers__item-remove" onclick={ remove }></a>
    </div>

    <script>
        var self = this

        remove(e) {
            self.cartUpdate(0, remove=true)
        }

        decrease(e) {
            if (opts.offer.quantity > 1) {
                opts.offer.quantity--
                self.cartUpdate(-1)
              //  cartStorage.update(opts.offer.id, -1, opts.offer.variant ? opts.offer.variant.id : null )
            }
        }

        increase(e) {
            opts.offer.quantity++
            self.cartUpdate(1)
            //cartStorage.update(opts.offer.id, 1, opts.offer.variant ? opts.offer.variant.id : null )
        }

        cartUpdate(qty, remove) {
            var remove = remove || false,
                qty = qty || 1
            cartStorage.update(opts.offer.id, qty, opts.offer.variant ? opts.offer.variant.id : null, remove=remove)
        }

        self.on('update', function() {
            self.sum = smartRound(opts.offer.quantity * opts.offer.price)
        })
    </script>

</cart-item>

<cart-related class="cart-related">
    <div class="row--margin" if={ len }>
        <p class="h2-header">
            Так же покупают
            <span class="cart-related__refresh" onclick={ reload } if={ len >= 4 }>Показать другие</span>
        </p>
        <ul class="blocks-4 offers">
            <li class="offers__item" each={ offer in offers }>
                <div class="offers__item-top">
                    <div class="offers__item-wrapper">
                        <div class="offers__item-picture">
                            <a href={ offer.url } class="link-plain">
                                <img src={ offer.picture }  alt={ offer.name } title={ offer.name }>
                            </a>
                        </div>
                        <div class="offers__item-badges" if={ offer.oldprice }>
                            <span class="badge-special">Акция</span><br>
                        </div>
                        <div class="offers__item-favorite {offers__item-favorite--added: offer.favorited}" oid={ offer.id } onclick={ toggle }>
                            <span class="favorite-icon"><i class="icon-16 icon--heart-grey"></i></span>
                        </div>
                        <!--<favorite oid={ offer.id } favorited={ offer.favorited }></favorite>-->
                    </div>
                </div>
                <div class="offers__item-info text-center">
                    <div class="offers__item-category"><a href={ offer.category.url } class="link-plain link-grey text-small">{ offer.category.name }</a></div>
                    <div class="offers__item-name"><a href={ offer.url } class="offers__item-name__link">{ offer.name }</a></div>
                    <div class="offers__item-price { offers__item-price--special: !!offer.oldprice }"><span class="offers__item-oldprice" if={ offer.oldprice }>{ offer.oldprice }</span>{ offer.price } руб.</div>
                    <div class="offers__item-buttons">
                    <button id={ offer.id } onclick={ add } class="btn"><span class="btn__text"><i class="icon-16 icon--cart-white"></i>Добавить</span></button>
                    </div>

                    <div class="offers__item-countdown" if={ offer.timer }>
                        <span class="badge-special offers__item-countdown__until">До конца акции</span>
                        <div class="countdown" id="countdown"></div>
                    </div>
                </div>
            </li>
        </ul>
    </div>

    <script>
        var self = this;

        self.offers = [];
        self.len = true;

        function fetch() {
            $.ajax({
                type: 'get',
                dataType: 'json',
                url: '/cart/api/r/',
                success: function(data) {
                    self.offers = data.offers;
                    self.len = self.offers.length > 0 ? self.offers.length : false;
                    self.update()
                }
            })
        }

        add(e) {
            var el = $(e.target).parent().attr('id') != undefined ? $(e.target).parent() : $(e.target),
                id = el.attr('id');
            cartStorage.update(id, 1, null)
            fetch();
        }

        toggle(e) {
            var par = $(e.target).parent().parent(),
                id = par.attr('oid');

            for (var i=0; i<self.offers.length; i++) {
                if (self.offers[i].id == id) {
                    self.offers[i].favorited = !self.offers[i].favorited
                }
            }
            favoriteStorage.update(id);
            self.update();
        }

        reload() {
            fetch();
        }

        self.on('mount', function() {
            fetch();
        });

    </script>
</cart-related>

<cart-form>
    <div class="order-form">
        <form action="" class="row" method="post" id="orderForm">
            <div class="col-8">
                <div class="order-form__wrapper">
                    <h2 class="order-form__title">Оформление заказа</h2>
                    <!--<a href="#" class="order-form__hasaccount link-blue">У меня есть аккаунт</a>-->
                    <div class="order-form__group">
                        <h3 class="order-form__group-title">Контактная информация</h3>
                        <div class={ order-form__line:true, order-form__line--error: !!errors['fullname'] }>
                            <label class="order-form__line-name order-form__line-name--required">ФИО</label>
                            <div class="order-form__line-input">
                                <input type="text" name="fullname" onkeyup={ edit } class="input" placeholder="Иванов Федор Павлович">
                                <span class="order-form__line-error" if={ errors['fullname'] }  }>{ errors['fullname'] }</span>
                            </div>
                        </div>
                        <div class={ order-form__line:true, order-form__line--error: !!errors['phone'] }>
                            <label class="order-form__line-name order-form__line-name--required">Телефон</label>
                            <div class="order-form__line-input">
                                <input type="text" name="phone" placeholder="7 (495) 123-4567" onkeyup={ edit } class="input" id="phone">
                                <span class="order-form__line-error" if={ errors['phone'] }>{{ errors['phone'] }}</span>
                            </div>
                        </div>
                        <div class={ order-form__line:true, order-form__line--error: !!errors['email'] }>
                            <label class="order-form__line-name">Электронная почта</label>
                            <div class="order-form__line-input">
                                <input type="text" name="email" placeholder="ivanov.fedor@gmail.com" class="input" onkeyup={ edit }>
                                <span class="order-form__line-error" if={ errors['email'] }>{{ errors['email'] }}</span>
                            </div>
                        </div>
                        <!--<div class="order-form__line">
                            <div class="order-form__line-input">
                                <label for="account" class="checkbox__label"><input type="checkbox" class="checkbox" id="account"> Создать аккаунт</label>
                            </div>
                        </div>-->
                    </div>
                    <div class="order-form__group">
                        <h3 class="order-form__group-title">Информация о доставке, необязательно</h3>
                        <p class="order-form__group-description">Доступные способы получения товара: курьерская доставка, самовывоз из пункта выдачи или доставка в отделение «Почты России». Способ доставки уточнит менеджер по телефону при подтверждении заказа.</p>
                        <div class="order-form__line">
                            <label for="" class="order-form__line-name">Город</label>
                            <div class="order-form__line-input" >
                                <select style="width: 100%;" name="regions" onchange={ look } class="js-region-select">
                                    <option value="" selected="selected">Не выбран</option>
                                </select>
                            </div>
                        </div>
                        <div class="order-form__line" if={ selected_region && !!paydel.deliveries.length }>
                            <label for="" class="order-form__line-name">Тип доставки</label>
                            <div class="order-form__line-input">
                                <select name="delivery_method" onchange={ cart_info }>
                                    <option each={ delivery, idx in paydel.deliveries } value={ delivery.id } selected={ idx == '0' }>{ delivery.name }</option>
                                </select>
                            </div>
                        </div>
                        <div class="order-form__line">
                            <label for="" class="order-form__line-name">Адрес доставки</label>
                            <div class="order-form__line-input">
                                <textarea name="address" id="" rows="2" onkeyup={ edit } placeholder="Например: 3-й дегтярный переулок, дом 7"></textarea>
                            </div>
                        </div>
                        <div class="order-form__line" if={ selected_region && !!paydel.payments.length }>
                            <label for="" class="order-form__line-name">Метод оплаты</label>
                            <div class="order-form__line-input">
                                <select name="payment_method" onchange={ cart_info }>
                                    <option each={ payment, idx in paydel.payments } value={ payment.id } selected={ idx == '0' }>{ payment.name }</option>
                                </select>
                            </div>
                        </div>
                        <div class="order-form__line">
                            <label for="" class="order-form__line-name">Комментарий</label>
                            <div class="order-form__line-input">
                                <textarea name="comment" id="" rows="5" onkeyup={ edit } placeholder="Например: звоните с 9 до 12 утра"></textarea>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-4 js-sticky">
                <div class="order-form__right">
                    <div class="order-form__total">Сумма:
                        <div class="order-form__total-price">{ opts.total.sum } руб.</div>
                        <p if={ delivery_info.delivery_price }>Доставка:<br /><b>{ delivery_info.delivery_price } руб.</b></p>
                        <p if={ delivery_info.order_sum }>Итого с доставкой:<br /><b>{ delivery_info.order_sum } руб.</b></p>
                    </div>
                    <!--<div class="order-form__delivery-tip"></div>-->
                    <input type="submit" onclick={ postOrder } value="Оформить заказ" class="btn btn--large" disabled={ !validated }>
                </div>
            </div>
        </form>
    </div>

    <script>
        var self = this,
            validators = {
                fullname: function(value) {
                    var value = value || ''
                    var msg = 'Обязательно и не менее 3 символов';
                    return {test: !!value.length && value.length >= 3, msg: msg}
                },
                phone: function(value) {
                    var value = value || ''
                    var msg = 'Обязательно в формате 7 (123) 456-7890'
                        re = /^[78]{1}\s\([0-9]{3}\)\s[0-9]{3}[-]{1}[0-9]{4}$/
                    return {test: re.test(value), msg: msg}
                },
                email: function(value) {
                    var msg = 'Неправильный формат электронной почты',
                        test
                    var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
                    test = !value || value == '' ? true : re.test(value)
                    return {test: test, msg: msg}
                }
            }

        var timer;

        self.validated = false
        self.values = {}
        self.errors = {}
        self.userinfo = opts.userinfo || {}

        self.selected_region = null;
        self.paydel = {}
        self.delivery_info = {}

        edit(e) {
            self.values[e.target.name] = e.target.value
            self.validate()
        }

        look(e) {
            self.selected_region = e.target.value || 0;
            get_payment_and_delivery(self.selected_region);
        }

        cart_info(e) {
            get_cart_info();
        }

        function get_cart_info() {
            if (!!self.selected_region && !!self.payment_method.value && !!self.delivery_method.value) {
                $.ajax({
                    type: 'post',
                    dataType: 'json',
                    data: {region_id: self.selected_region,
                           payment_method: self.payment_method.value,
                           delivery_method: self.delivery_method.value},
                    url: '/cart/api/d/check/',
                    success: function(data) {
                        if (!data.error) {
                            self.delivery_info = data.data;
                            self.update();
                            Stickyfill.rebuild();
                            return;
                        }
                        self.delivery_info = {}
                        return;
                    }
                })
            } else {
                self.delivery_info = {}
                self.update()
            }
        }

        validate() {
            var validated = [];
            for (key in validators) {
                var validator = validators[key], res;
                if (validator) {
                    res = validator(self.values[key]);
                    self.errors[key] = !res.test ? res.msg : '';
                    validated.push(res.test)
                }
            }
            self.validated = validated.every(Boolean)
        }

        postOrder() {
            var data = $.extend({}, self.values, {payment: self.payment_method.value, delivery: self.delivery_method.value})

            if (self.delivery_info != {}) {
                data['delivery_info'] = self.delivery_info;
            }

            self.parent.loading = true
            self.parent.update()


            $.ajax({
                type: 'post',
                dataType: 'json',
                data: data,
                url: '/order/',
                success: function(data) {
                    if (!data.error) {
                        window.location.href = data.backurl;
                        return;
                    }

                    self.parent.loading = false
                    self.parent.update()
                    alert(data.error)
                }
            })


        }

        function get_payment_and_delivery(region_id) {
            var data = {region_id: region_id};
            if (region_id === 0 || !!region_id) {
                $.ajax({
                    type: 'post',
                    dataType: 'json',
                    data: data,
                    url: '/cart/api/d/paydel/',
                    success: function(data) {
                        if ((data.data.deliveries && data.data.deliveries.length) || (data.data.payments && data.data.payments.length)) {
                            self.paydel = data.data;
                            self.update();
                            get_cart_info();
                            return;
                        }

                        self.paydel = {}
                        self.delivery_info = {}
                        self.update();
                        return;
                    }
                })
            }
        }



        self.on('mount', function() {
            $(self.phone).mask("9 (999) 999-9999");
            self.sticky = $('.js-sticky').Stickyfill();

            if (opts.userinfo) {
                self.values = opts.userinfo
                for (key in self.values) {
                    if (self[key]) {
                        self[key].value = self.values[key]
                        //if (key == 'address' && self.values[key].toLowerCase() == 'уточнить при звонке') {
                          //  console.log('here')
                            //self[key].value = ''
                        //}
                    }
                }
                var region = self.values.region || false;
                if (region && region.id && region.name) {
                    $(self.regions).find('option:selected').val(region.id).text(region.name);
                    self.selected_region = region.id;
                    //get_payment_and_delivery(region.id);
                }
                self.validate()
                self.update()
            }

            $('.js-region-select').select2({
                ajax: {
                    url: '/cart/api/d/regions/',
                    dataType: 'json',
                    type: 'post',
                    delay: 250,
                    data: function(params) {
                        return {
                            q: params.term,
                            page: params.page
                        }
                    },
                    processResults: function(data, params) {
                        return {
                            results: data.regions
                        }
                    },
                    cache: true,
                },
                escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
                minimumInputLength: 2,
                searching: function () {
                    return 'Поиск…';
                }
            });

            cartStorage.on('update', function() {
                clearTimeout(timer);
                if (this.offers.length) {
                    timer = setTimeout(function() {
                        get_payment_and_delivery(self.selected_region);
                        clearTimeout(timer);
                    }, 1000)

                }
            })

            //get_payment_and_delivery();
        });

    </script>
</cart-form>

<minified-cart class={header__iconed: true}>
    <a href="{{ opts.url }}" class={ link-plain: true, link-active: opts.active }>
        <span class={ header__iconed-left:true, header__iconed-left--added: added && total.quantity }>
            <i class="icon-32 icon--cart"></i>
            <span class="header__cart-count" if={ total.quantity }>{ total.quantity }</span>
        </span>
        <span class="header__iconed-right">
            Моя корзина<br />
            <span class={ text-small: true, text-grey: !total.quantity }>{ message }&nbsp;</span>
        </span>
    </a>


    <script>
        var self = this
        self.timer = null
        self.firstUpdate = true

        plural(amount, variants) {
            if (variants.length < 3) return

            var variant;

            if (amount % 10 == 1 && amount % 100 != 11) {
                variant = 0
            } else if (amount % 10 >=2 && amount % 10 <= 4 && (amount % 100 < 10 || amount % 100 >= 20)) {
                variant = 1
            } else {
                variant = 2
            }

            return amount + ' ' + variants[variant]
        }

        self.on('mount', function() {
            self.added = false
        })

        cartStorage.on('update', function() {
            self.total= cartStorage.total
            self.message = !self.total.quantity ? 'пока пуста' : self.plural(self.total.quantity, ['товар', 'товара', 'товаров']) + ' на ' + self.total.sum + ' руб.'

            if (!self.firstUpdate) {
                clearTimeout(self.timer)
                self.added = true
                self.timer = setTimeout(function() {
                    self.added = false
                    self.update()
                }, 200)
            }

            self.firstUpdate = false
            self.update()
        })
    </script>
</minified-cart>