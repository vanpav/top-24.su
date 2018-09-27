riot.tag('add-to-cart', '<span class="{ btn__added:true, btn__added--show: isadded }">{ text }</span> <yield></yield>', 'onclick="{ add }"', function(opts) {
        var self = this
        self.isadded = false
        self.text = 'В корзине'

        this.add = function(e) {
            if (self.isadded) {
                window.location.href = '/cart/'
            }
            if (!self.isadded) {
                var timer,
                    oldText=self.text;
                self.variant = opts.variant || null;
                self.qty = opts.qty || 1;
                self.text = 'Добавлено';
                cartStorage.update(opts.id, self.qty, self.variant)
                timer = setTimeout(function() {
                    self.text = oldText;
                    clearTimeout(timer);
                    self.update();
                }, 2000)
            }
            self.isadded = true
        }.bind(this);

        cartStorage.on('update', function() {
            var finded = this.offers.filter(function(offer) {
                return opts.id == offer.id
            })
            self.isadded = finded.length ? true : false
            self.update()
        })

    
});

riot.tag('quick-buy', '<yield></yield>', 'onclick="{ buy }"', function(opts) {
        this.buy = function(e) {
            content = {
                tag: 'modal-offer',
                offer_id: opts.id
            }
            window.modalWindow.open(content)
        }.bind(this);
    
});

riot.tag('offer-form', ' <div class="offer__count" if="{ variants.length }"> <div class="offer__field-label">Модель</div> <select name="variant" class="control__count" onchange="{ setVariant }"> <option each="{ variant in variants }" value="{ variant.id }" __disabled="{ !variant.count }" __selected="{ variant.id == choosedVariant ? selected : false }">{ variant.name }</option> </select> </div> <div class="offer__buttons"> <button riot-tag="add-to-cart" id="{ opts.offer_id }" variant="{ choosedVariant }" qty="{ quantity }" class="btn btn--large"><span class="btn__text"><i class="icon-16 icon--cart-white"></i>В корзину</span></button> <button riot-tag="quick-buy" id="{ opts.offer_id }" class="btn btn--grey btn--large"><span class="btn__text">Купить сейчас</span></button> </div>', function(opts) {
        var self = this

        self.quantity = 1

        this.send = function(e) {
            console.log('send')
        }.bind(this);

        this.setVariant = function(e) {
            self.choosedVariant = e.target.value
        }.bind(this);

        this.decrease = function(e) {
            if (self.quantity > 1) {
                self.quantity--
            }
        }.bind(this);

        this.increase = function(e) {
            self.quantity++
        }.bind(this);

        self.on('mount', function() {
            if (opts.hasvariants) {
                $.ajax({
                    method: 'post',
                    dataType: 'json',
                    url: '/cart/api/' + opts.offer_id + '/',
                    success: function(data) {
                        self.variants = data.variants
                        self.choosedVariant = self.variants[0]
                        self.update()
                    }
                })
            }
        })

    
});


riot.tag('modal-window', '<div class="modal {modal--hide: !opened}"> <div class="modal__hider" onclick="{ close }"></div> <div class="modal__window { modal__window--hide: !showed }"> <div class="modal__window-wrapper"> <span class="modal__window-close" onclick="{ close }"></span> <div id="mounter"></div> </div> </div> </div>', function(opts) {
        var self = this;

        self.on('mount', function() {
            var mounted;

            self.modal = modalWindow;
            self.opened = self.modal.opened || false;
            self.showed = self.modal.opened || false;

            self.modal.on('update', function() {

                self.opened = self.modal.opened;
                self.content = self.modal.content;

                if (self.opened && self.content) {
                    mounted = riot.mountTo(self.mounter, self.content.tag, self.content)[0];
                    showWindow();
                }

                self.update();
            });

            self.update();
        });

        function showWindow() {
            setTimeout(function() {
                self.showed = true;
                setPosition();
                self.modal.trigger('open');
                $(window).on('resize', setPosition);
                self.update();
            }, 5)
        }

        function setPosition() {
            var timer = setTimeout(function() {
                var win = $('.modal__window', self.root),
                    height = win.height(),
                    width = win.width(),
                    offsetTop = Math.round(height / 2),
                    offsetLeft = Math.round(width / 2);

                win.css({margin: '-' + offsetTop + 'px 0 0 -' + offsetLeft + 'px'});
                clearTimeout(timer);
            }, 0)
        }

        this.close = function() {
            self.modal.close();
            self.showed = false;
            $(window).off('resize', setPosition);
            self.update();
        }.bind(this);

    
});


riot.tag('modal-offer', '<div class="modal-offer"> <div class="modal-offer__info"> <div class="modal-offer__info-badges" if="{ !!offer.oldprice }"> <span class="badge-special">Акция</span> </div> <div class="modal-offer__category"><a href="{ offer.category.url }" class="link-plain link-grey text-small">{ offer.category.name }</a></div> <h2 class="modal-offer__name"><a href="{ offer.url }" class="link-plain">{ offer.name }</a></h2> <div class="modal-offer__image"> <a href="{ offer.url }" class="link-plain"><img riot-src="{ offer.picture }" alt="{ offer.name }" title="{ offer.name }"></a> <div class="modal-offer__countdown" if="{ offer.timer }"> <div id="countdown" class="countdown"></div> </div> </div> <div class="modal-offer__price { modal-offer__price--special: !!offer.oldprice }"><span if="{ offer.oldprice }">{ offer.oldprice }</span>{ offer.price } руб.</div> </div> <div class="modal-offer__form"> <div class="modal-offer__loading" if="{ loading }"> <div class="modal-offer__loading-spinner text-center"> <div class="spinner spinner--big"><span><span></span></span></div> <p>Оформляем заказ</p> </div> </div> <div class="modal-offer__form-line"> <label class="text-small">Количество</label> <span class="control__count"><span onclick="{ decrease }" class="{btn: true, btn--outline: true, btn--iconed: true, btn--icon-minus: true, control__count-minus:true, btn--dissabled: count == 1 }"></span><input type="text" class="input control__count-input" disabled value="{ count }"><span onclick="{ increase }" class="btn btn--outline btn--iconed btn--icon-plus control__count-plus"></span></span> </div> <div class="modal-offer__form-line" if="{ offer.variants.length }"> <label class="text-small">Модель</label> <select name="variant" class="control__count" style="width: 100%;" onchange="{ setVariant }"> <option each="{ variant in offer.variants }" value="{ variant.id }" __disabled="{ !variant.count }" __selected="{ variant.id == choosedVariant ? selected : false }">{ variant.name }</option> </select> </div> <div class="modal-offer__form-line {modal-offer__form-line--error: errors}"> <label class="text-small">Телефон</label> <input type="text" name="phone" placeholder="7 (495) 123-4567" class="input" id="phone"> </div> <div class="modal-offer__form-button"> <input type="submit" onclick="{ postOrder }" value="Оформить заказ" class="btn btn--large"> </div> </div> </div>', function(opts) {
        var self = this,
            phone_re = /^[78]{1}\s\([0-9]{3}\)\s[0-9]{3}[-]{1}[0-9]{4}$/;

        self.offer_id = opts.offer_id;
        self.count = 1;
        self.offer = {};
        self.loading = false;
        self.errors = false;

        this.decrease = function() {
            if (self.count > 1) {
                self.count--;
            }
        }.bind(this);

        this.increase = function() {
            self.count++;
        }.bind(this);

        this.setVariant = function(e) {
            self.choosedVariant = e.target.value
        }.bind(this);

        function validate() {
            var test = phone_re.test(self.phone.value);

            self.errors = !test;

            return test
        }

        this.postOrder = function() {
            if (!validate()) {
                $(self.phone).on('keyup', validate);
                return;
            }

            self.loading = true;

            $.ajax({
                method: 'post',
                dataType: 'json',
                url: '/cart/api/q/',
                data: {
                    count: self.count,
                    offer_id: self.offer_id,
                    variant: self.choosedVariant ? self.choosedVariant.id : undefined,
                    phone: self.phone.value
                },
                success: function(data) {
                    if (data.errors) {
                        self.loading = false;
                        self.update();
                        alert('Произошла ошибка')
                    }

                    if (data.order.order_id) {
                        window.location.href = data.order.url;
                    }
                }
            });
        }.bind(this);

        this.on('mount', function() {
            $(self.phone).mask("9 (999) 999-9999");

            $.ajax({
                method: 'get',
                dataType: 'json',
                url: '/cart/api/q/' + self.offer_id + '/',
                success: function(data) {
                    self.offer = data.offer;
                    self.choosedVariant = self.offer.variants[0];

                    if (self.offer.timer) {
                        $(self.countdown).countdown(self.offer.timer, function(event) {
                            var totalHours = event.offset.totalDays * 24 + event.offset.hours;
                            $(this).html(event.strftime(totalHours+':%M:%S'));
                        })
                    }
                    if (self.offer.user && self.offer.user.phone) {
                        self.phone.value = self.offer.user.phone;
                    }
                    self.update()
                }
            })
        })
    
});


riot.tag('offer-delivery', '<yield></yield>', function(opts) {
        var self = this;

        self.current_region = opts.current_region

        this.select = function(region) {
            self.current_region = region.id;
            fetch(region);
        }.bind(this);

        function fetch(region) {
            $.ajax({
                type: 'post',
                dataType: 'json',
                url: '/cart/api/d/paydel/',
                data: {region_id: region.id, aid: opts.aid},
                success: function(data) {
                    populate(data.data, region);
                }
            })
        }

        function populate(data, region) {
            self.link.text(region.text);
            self.list.html('');
            if (data.length) {
                data.forEach(function(method) {
                    var tpl = self.litpl.clone();
                    tpl.find('.offer__deliveries-method').text(method.method + ':');
                    tpl.find('.offer__deliveries-price').text('от ' + method.price + ' руб.');
                    self.list.append(tpl);
                })
            } else {
                var tpl = self.litpl.clone();
                tpl.find('.offer__deliveries-method').text('Уточняйте у оператора');
                self.list.append(tpl);
            }
            self.update();
        }

        self.on('mount', function() {
            self.el = $(self.root)
            self.link = self.el.find('.pseudo');
            self.list = self.el.find('.offer__deliveries-list');
            self.litpl = $('<li class="offer__deliveries-item"><div class="offer__deliveries-method"></div><span class="offer__deliveries-price"></span></li>');

            self.link.on('click', function() {
                window.modalWindow.open({tag: 'modal-delivery',
                                         current_region: self.current_region,
                                         parent: self})
            })
        })
    
});

riot.tag('modal-delivery', '<div class="modal-delivery"> <div class="modal-delivery__search"><input type="text" class="input" name="searchinp" oninput="{ search }" placeholder="Введите название города"></div> <ul class="modal-delivery__founded"> <li class="modal-delivery__founded-error" if="{ !regions.length }">Городов не найдено</li> <li class="modal-delivery__founded-item" onclick="{ choose }" each="{ region in regions }" region_id="{ region.id }">{ region.text }</li> </ul> </div>', function(opts) {
        var self = this,
            search_timer;

        self.regions = [];

        this.choose = function(e) {
            if (opts.current_region != e.item.region.id) opts.parent.select(e.item.region);
            window.modalWindow.close();
        }.bind(this);

        this.search = function(e) {
            var query = e.target.value;
            if (query.length >= 2) {
                clearTimeout(search_timer);
                search_timer = setTimeout(function() {
                    fetch(e.target.value)
                }, 500)
            }
        }.bind(this);

        function fetch(query) {
            var query = query || '';

            $.ajax({
                type: 'post',
                dataType: 'json',
                url: '/cart/api/d/regions/',
                data: {q: query},
                success: function(data) {
                    self.regions = data.regions;
                    self.update();
                }
            })
        }

        self.on('mount', function() {
            fetch();
            window.modalWindow.on('open', function() {
                self.searchinp.focus()
            })
        })
    
});

riot.tag('offer-articul', '<div class="offer__articul" if="{ articul }">Артикул: <strong>#{ articul }</strong></div>', function(opts) {
        var self = this;

        self.on('mount', function() {
            $.ajax({
                type: 'post',
                dataType: 'json',
                url: '/cart/api/aul/',
                data: {offer_id: opts.offer_id},
                success: function(data) {
                    self.articul = data.articul;
                    self.update();
                }
            })
        })
    
});
riot.tag('cart', '<div class="cart-page__loading" if="{ loading }"> <div class="cart-page__spinner text-center"> <div class="spinner spinner--big"><span><span></span></span></div> <p>Оформляем заказ</p> </div> </div> <div if="{ !offers.length }"> <p>В корзине пока нет товаров. Возможно вы захотите добавить эти:</p> <br > </div> <ul class="cart-offers" if="{ offers.length }"> <li each="{ offer, idx in offers }" idx="{ idx }" offer="{ offer }" class="cart-offers__item" riot-tag="cart-item"></li> </ul> <cart-form if="{ offers.length }" total="{ cartStorage.total }" userinfo="{ userinfo }"></cart-form> <cart-related></cart-related>', function(opts) {
        var self = this

        self.loading = false

        cartStorage.on('update', function() {
            self.offers = cartStorage.offers
            if (!self.userinfo && cartStorage.userinfo != {}) self.userinfo = cartStorage.userinfo
            self.update()
        });

    
});

riot.tag('cart-item', '<div class="cart-offers__item-picture"> <a href="{ opts.offer.url }" class="link-plain"><img riot-src="{ opts.offer.image }" alt="{ opts.offer.name }" title="{ opts.offer.name }" class="cart-offers__item-image"></a> </div> <div class="cart-offers__item-title"> <a href="{ opts.offer.url }">{ opts.offer.name } { opts.offer.variant.name.toLowerCase() }</a> </div> <div class="cart-offers__item-price {cart-offers__item-price--special: !!opts.offer.oldprice}"> <span if="{ opts.offer.oldprice }">{ opts.offer.oldprice } руб.</span> {{ opts.offer.price }} руб. </div> <div class="cart-offers__item-count"> <span class="{ control__count: true }"><span onclick="{ decrease }" class="{btn: true, btn--outline: true, btn--iconed: true, btn--icon-minus: true, control__count-minus:true, btn--dissabled: opts.offer.quantity == 1 }"></span><input type="text" class="input control__count-input" disabled value="{ opts.offer.quantity }"><span onclick="{ increase }" class="btn btn--outline btn--iconed btn--icon-plus control__count-plus"></span></span> </div> <div class="cart-offers__item-total"> { sum } руб.  </div> <div class="cart-offers__item-delete"> <a href="" class="icon icon-16 icon--delete link-plain cart-offers__item-remove" onclick="{ remove }"></a> </div>', function(opts) {
        var self = this

        this.remove = function(e) {
            self.cartUpdate(0, remove=true)
        }.bind(this);

        this.decrease = function(e) {
            if (opts.offer.quantity > 1) {
                opts.offer.quantity--
                self.cartUpdate(-1)

            }
        }.bind(this);

        this.increase = function(e) {
            opts.offer.quantity++
            self.cartUpdate(1)

        }.bind(this);

        this.cartUpdate = function(qty, remove) {
            var remove = remove || false,
                qty = qty || 1
            cartStorage.update(opts.offer.id, qty, opts.offer.variant ? opts.offer.variant.id : null, remove=remove)
        }.bind(this);

        self.on('update', function() {
            self.sum = smartRound(opts.offer.quantity * opts.offer.price)
        })
    
});

riot.tag('cart-related', '<div class="row--margin" if="{ len }"> <p class="h2-header"> Так же покупают <span class="cart-related__refresh" onclick="{ reload }" if="{ len >= 4 }">Показать другие</span> </p> <ul class="blocks-4 offers"> <li class="offers__item" each="{ offer in offers }"> <div class="offers__item-top"> <div class="offers__item-wrapper"> <div class="offers__item-picture"> <a href="{ offer.url }" class="link-plain"> <img riot-src="{ offer.picture }" alt="{ offer.name }" title="{ offer.name }"> </a> </div> <div class="offers__item-badges" if="{ offer.oldprice }"> <span class="badge-special">Акция</span><br> </div> <div class="offers__item-favorite {offers__item-favorite--added: offer.favorited}" oid="{ offer.id }" onclick="{ toggle }"> <span class="favorite-icon"><i class="icon-16 icon--heart-grey"></i></span> </div>  </div> </div> <div class="offers__item-info text-center"> <div class="offers__item-category"><a href="{ offer.category.url }" class="link-plain link-grey text-small">{ offer.category.name }</a></div> <div class="offers__item-name"><a href="{ offer.url }" class="offers__item-name__link">{ offer.name }</a></div> <div class="offers__item-price { offers__item-price--special: !!offer.oldprice }"><span class="offers__item-oldprice" if="{ offer.oldprice }">{ offer.oldprice }</span>{ offer.price } руб.</div> <div class="offers__item-buttons"> <button id="{ offer.id }" onclick="{ add }" class="btn"><span class="btn__text"><i class="icon-16 icon--cart-white"></i>Добавить</span></button> </div> <div class="offers__item-countdown" if="{ offer.timer }"> <span class="badge-special offers__item-countdown__until">До конца акции</span> <div class="countdown" id="countdown"></div> </div> </div> </li> </ul> </div>', 'class="cart-related"', function(opts) {
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

        this.add = function(e) {
            var el = $(e.target).parent().attr('id') != undefined ? $(e.target).parent() : $(e.target),
                id = el.attr('id');
            cartStorage.update(id, 1, null)
            fetch();
        }.bind(this);

        this.toggle = function(e) {
            var par = $(e.target).parent().parent(),
                id = par.attr('oid');

            for (var i=0; i<self.offers.length; i++) {
                if (self.offers[i].id == id) {
                    self.offers[i].favorited = !self.offers[i].favorited
                }
            }
            favoriteStorage.update(id);
            self.update();
        }.bind(this);

        this.reload = function() {
            fetch();
        }.bind(this);

        self.on('mount', function() {
            fetch();
        });

    
});

riot.tag('cart-form', '<div class="order-form"> <form action="" class="row" method="post" id="orderForm"> <div class="col-8"> <div class="order-form__wrapper"> <h2 class="order-form__title">Оформление заказа</h2>  <div class="order-form__group"> <h3 class="order-form__group-title">Контактная информация</h3> <div class="{ order-form__line:true, order-form__line--error: !!errors[\'fullname\'] }"> <label class="order-form__line-name order-form__line-name--required">ФИО</label> <div class="order-form__line-input"> <input type="text" name="fullname" onkeyup="{ edit }" class="input" placeholder="Иванов Федор Павлович"> <span class="order-form__line-error" if="{ errors[\'fullname\'] }" }>{ errors[\'fullname\'] }</span> </div> </div> <div class="{ order-form__line:true, order-form__line--error: !!errors[\'phone\'] }"> <label class="order-form__line-name order-form__line-name--required">Телефон</label> <div class="order-form__line-input"> <input type="text" name="phone" placeholder="7 (495) 123-4567" onkeyup="{ edit }" class="input" id="phone"> <span class="order-form__line-error" if="{ errors[\'phone\'] }">{{ errors[\'phone\'] }}</span> </div> </div> <div class="{ order-form__line:true, order-form__line--error: !!errors[\'email\'] }"> <label class="order-form__line-name">Электронная почта</label> <div class="order-form__line-input"> <input type="text" name="email" placeholder="ivanov.fedor@gmail.com" class="input" onkeyup="{ edit }"> <span class="order-form__line-error" if="{ errors[\'email\'] }">{{ errors[\'email\'] }}</span> </div> </div>  </div> <div class="order-form__group"> <h3 class="order-form__group-title">Информация о доставке, необязательно</h3> <p class="order-form__group-description">Доступные способы получения товара: курьерская доставка, самовывоз из пункта выдачи или доставка в отделение «Почты России». Способ доставки уточнит менеджер по телефону при подтверждении заказа.</p> <div class="order-form__line"> <label for="" class="order-form__line-name">Город</label> <div class="order-form__line-input" > <select style="width: 100%;" name="regions" onchange="{ look }" class="js-region-select"> <option value="" selected="selected">Не выбран</option> </select> </div> </div> <div class="order-form__line" if="{ selected_region && !!paydel.deliveries.length }"> <label for="" class="order-form__line-name">Тип доставки</label> <div class="order-form__line-input"> <select name="delivery_method" onchange="{ cart_info }"> <option each="{ delivery, idx in paydel.deliveries }" value="{ delivery.id }" __selected="{ idx == \'0\' }">{ delivery.name }</option> </select> </div> </div> <div class="order-form__line"> <label for="" class="order-form__line-name">Адрес доставки</label> <div class="order-form__line-input"> <textarea name="address" id="" rows="2" onkeyup="{ edit }" placeholder="Например: 3-й дегтярный переулок, дом 7"></textarea> </div> </div> <div class="order-form__line" if="{ selected_region && !!paydel.payments.length }"> <label for="" class="order-form__line-name">Метод оплаты</label> <div class="order-form__line-input"> <select name="payment_method" onchange="{ cart_info }"> <option each="{ payment, idx in paydel.payments }" value="{ payment.id }" __selected="{ idx == \'0\' }">{ payment.name }</option> </select> </div> </div> <div class="order-form__line"> <label for="" class="order-form__line-name">Комментарий</label> <div class="order-form__line-input"> <textarea name="comment" id="" rows="5" onkeyup="{ edit }" placeholder="Например: звоните с 9 до 12 утра"></textarea> </div> </div> </div> </div> </div> <div class="col-4 js-sticky"> <div class="order-form__right"> <div class="order-form__total">Сумма: <div class="order-form__total-price">{ opts.total.sum } руб.</div> <p if="{ delivery_info.delivery_price }">Доставка:<br ><b>{ delivery_info.delivery_price } руб.</b></p> <p if="{ delivery_info.order_sum }">Итого с доставкой:<br ><b>{ delivery_info.order_sum } руб.</b></p> </div>  <input type="submit" onclick="{ postOrder }" value="Оформить заказ" class="btn btn--large" __disabled="{ !validated }"> </div> </div> </form> </div>', function(opts) {
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

        this.edit = function(e) {
            self.values[e.target.name] = e.target.value
            self.validate()
        }.bind(this);

        this.look = function(e) {
            self.selected_region = e.target.value || 0;
            get_payment_and_delivery(self.selected_region);
        }.bind(this);

        this.cart_info = function(e) {
            get_cart_info();
        }.bind(this);

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

        this.validate = function() {
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
        }.bind(this);

        this.postOrder = function() {
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


        }.bind(this);

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




                    }
                }
                var region = self.values.region || false;
                if (region && region.id && region.name) {
                    $(self.regions).find('option:selected').val(region.id).text(region.name);
                    self.selected_region = region.id;

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

        });

    
});

riot.tag('minified-cart', '<a href="{{ opts.url }}" class="{ link-plain: true, link-active: opts.active }"> <span class="{ header__iconed-left:true, header__iconed-left--added: added && total.quantity }"> <i class="icon-32 icon--cart"></i> <span class="header__cart-count" if="{ total.quantity }">{ total.quantity }</span> </span> <span class="header__iconed-right"> Моя корзина<br > <span class="{ text-small: true, text-grey: !total.quantity }">{ message }&nbsp;</span> </span> </a>', 'class="{header__iconed: true}"', function(opts) {
        var self = this
        self.timer = null
        self.firstUpdate = true

        this.plural = function(amount, variants) {
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
        }.bind(this);

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
    
});
riot.tag('favorite', '<div class="offers__item-favorite {offers__item-favorite--added: favorited}" onclick="{ toggle }"> <span class="favorite-icon"><i class="icon-16 icon--heart-grey"></i></span> </div>', function(opts) {
        var self = this;

        self.id = self.opts.oid;
        self.favorited = self.opts.favorited == true || self.opts.favorited == 'true' || false;

        this.toggle = function(e) {
            self.favorited = !self.favorited;
            favoriteStorage.update(self.id);
        }.bind(this);

        favoriteStorage.on('update', function() {
            var is_in_list = this.favorites.indexOf(self.id) != -1;
            if (is_in_list && !self.favorited) {
                self.favorited = true;
                self.update();
            } else if (!is_in_list && self.favorited) {
                self.favorited = false;
                self.update();
            }
        });

    
});

riot.tag('favorites', '<span> <yield></yield> </span>', function(opts) {
        var self = this;

        favoriteStorage.on('update', function() {
            self.root.innerHTML = this.favorites.length || 0;
        })
    
});
riot.tag('order-upsale', '<div class="order__upsale" if="{ offers }"> <h2 class="order__upsale-header">Добавьте к заказу</h2> <div class="order__upsale-timer"><span id="timeto"></span></div> <ul class="blocks-3 offers order__offers"> <li class="offers__item" riot-tag="order-upsale-item" each="{ offer in offers }"></li> </ul> </div>', function(opts) {
        var self = this;

        self.offerTPL = $('.cart-offers .cart-offers__item').first();

        this.fetch = function() {
            $.ajax({
                type: 'get',
                dataType: 'json',
                url: '/order/' + self.order_id + '/api/upsale/',
                success: function(data) {
                    self.offers = data.offers;
                    self.update();
                }
            })
        }.bind(this);

        function plural(amount, variants) {
            if (variants.length < 3) return;
            var variant;

            if (amount % 10 == 1 && amount % 100 != 11) {
                variant = 0
            } else if (amount % 10 >=2 && amount % 10 <= 4 && (amount % 100 < 10 || amount % 100 >= 20)) {
                variant = 1
            } else {
                variant = 2
            }
            return variants[variant]
        }

        self.on('mount', function() {
            self.order_id = opts.order_id;
            $(document).ready(function() {
                self.timer_to = opts.timer_to !== 'False' ? opts.timer_to : false;
                if (self.timer_to) {
                    $(self.timeto).countdown(self.timer_to, function(event) {
                        var seconds_text = plural(event.offset.seconds, ['секунда', 'секунды', 'секунд']),
                            minutes_text = plural(event.offset.minutes, ['минута', 'минуты', 'минут']),
                            format = '%-M ' + minutes_text + ' %-S ' + seconds_text;

                        if (event.offset.minutes <= 0) {
                            format = '%-S ' + seconds_text;
                        }

                        $(this).html('Осталось ' + event.strftime(format))
                    }).on('finish.countdown', function() {
                        $(self.root).slideUp(500, function() { this.remove() });
                    });
                }
            });
            self.fetch();
        })
    
});

riot.tag('order-upsale-item', '<li> <div class="offers__item-top"> <div class="offers__item-wrapper"> <div class="offers__item-picture"> <a href="{ offer.url }" class="link-plain"> <img riot-src="{ offer.picture }" alt="{ offer.name }" title="{ offer.name }"> </a> </div> <div class="offers__item-badges" if="{ offer.oldprice }"> <span class="badge-special">Акция</span><br> </div> </div> </div> <div class="offers__item-info text-center"> <div class="offers__item-category"><a href="{ offer.category.url }" class="link-plain link-grey text-small">{ offer.category.name }</a></div> <div class="offers__item-name"><a href="{ offer.url }" class="offers__item-name__link">{ offer.name }</a></div> <div class="offers__item-price { offers__item-price--special: !!offer.oldprice }"><span class="offers__item-oldprice" if="{ offer.oldprice }">{ offer.oldprice }</span>{ offer.price } руб.</div> <div class="offers__item-buttons"> <button id="{ offer.id }" onclick="{ add }" class="btn"><span class="btn__text"><i class="icon-16 icon--cart-white"></i>Добавить</span></button> </div> <div class="offers__item-countdown" if="{ offer.timer }"> <span class="badge-special offers__item-countdown__until">До конца акции</span> <div class="countdown" id="countdown"></div> </div> </div> </li>', function(opts) {
        var self = this,
            offers = $('.cart-offers');

        function populateTpl(offer) {
            var tpl = self.parent.offerTPL.clone();

            tpl.find('.cart-offers__item-picture a, .cart-offers__item-title a').attr('href', offer.url);
            tpl.find('.cart-offers__item-picture img').attr('src', offer.picture).attr('alt', offer.name).attr('title', offer.name);
            tpl.find('.cart-offers__item-title a').text(offer.name);
            tpl.find('.cart-offers__item-price').text(offer.price + ' руб.');
            tpl.find('.cart-offers__item-quantity').text('X 1');
            tpl.find('.cart-offers__item-total').text(offer.price + ' руб.');

            return tpl;
        }

        this.add = function(e) {

            $.ajax({
                type: 'post',
                dataType: 'json',
                data: {offer_id: self.offer.id},
                url: '/order/' + self.parent.order_id + '/api/upsale/',
                success: function(data) {
                    var tpl = populateTpl(self.offer);
                    tpl.appendTo(offers);
                    self.parent.fetch();
                }
            })
        }.bind(this);
    
});
riot.tag('tabs', '<ul class="content__tabs"> <li class="content__tabs-item {\'content__tabs-item--active\': tab.active}" each="{tab in tabs}"><a href="" class="link-plain" onclick="{ activate }">{ tab.opts.heading }</a></li> </ul> <yield></yield>', function(opts) {
        var self = this
        this.tabs = this.tags['tab']

        var deselect = function() {
            self.tabs.forEach(function(tab) {
                tab.active = false
            })
        }

        this.activate = function(e) {
            var tab = e.item.tab
            deselect()
            tab.active = true
        }.bind(this);

        this.on('activateByIdx', function(index) {
            if (index > self.tabs.length - 1) return
            var tab = self.tabs[index]
            deselect()
            tab.active = true
            self.update()
        })

        window.thatOffer = this;

    
});


riot.tag('tab', '<div class="content__text content__text--padding-20 {\'content__text--hide\': !active}"> <yield></yield> </div>', function(opts) {
        this.route = opts.route
        this.active = opts.active == 'true'
    
});


riot.tag('comment-form', '<form action="post" onsubmit="{ submit }" enctype="multipart/form-data"> <div class="order-form__group order-form__group--comments"> <div class="cart-page__loading" if="{ sending }"> <div class="cart-page__spinner text-center"> <div class="spinner spinner--big"><span><span></span></span></div> <p>Отправляем отзыв</p> </div> </div> <div> <h3 class="order-form__group-title">Оставить отзыв</h3> <div class="order-form__line {order-form__line--error: !!errors[\'fullname\']}"> <label class="order-form__line-name">Имя</label> <div class="order-form__line-input order-form__line-input--short"> <input type="text" name="fullname" class="input" onblur="{ validateOne }" placeholder="Иванов Федор Павлович"> <span class="order-form__line-error">{ errors[\'fullname\'] }</span> </div> </div> <div class="order-form__line {order-form__line--error: !!errors[\'email\']}"> <label class="order-form__line-name">Электронная почта</label> <div class="order-form__line-input order-form__line-input--short"> <input type="text" name="email" class="input" onblur="{ validateOne }" placeholder="ivanov@fedor.pav"> <span class="order-form__line-error">{ errors[\'email\'] }</span> </div> </div> <div class="order-form__line"> <label class="order-form__line-name">Оценка</label> <div class="order-form__line-input order-form__line-rating-input"> <label for="rating_1"><input type="radio" name="rating" id="rating_1" value="1"><span>1</span></label> <label for="rating_2"><input type="radio" name="rating" id="rating_2" value="2"><span>2</span></label> <label for="rating_3"><input type="radio" name="rating" id="rating_3" value="3"><span>3</span></label> <label for="rating_4"><input type="radio" name="rating" id="rating_4" value="4"><span>4</span></label> <label for="rating_5"><input type="radio" name="rating" id="rating_5" value="5"><span>5</span></label> <label for="rating_6"><input type="radio" name="rating" id="rating_6" value="6"><span>6</span></label> <label for="rating_7"><input type="radio" name="rating" id="rating_7" value="7"><span>7</span></label> <label for="rating_8"><input type="radio" name="rating" id="rating_8" value="8"><span>8</span></label> <label for="rating_9"><input type="radio" name="rating" id="rating_9" value="9"><span>9</span></label> <label for="rating_10"><input type="radio" name="rating" id="rating_10" value="10"><span>10</span></label> </div> </div> <div class="order-form__line {order-form__line--error: !!errors[\'review\']}"> <label for="" class="order-form__line-name">Комментарий</label> <div class="order-form__line-input"> <textarea name="review" rows="4" onblur="{ validateOne }"></textarea> <span class="order-form__line-error">{ errors[\'review\'] }</span> </div> </div> <div class="order-form__line"> <div class="order-form__line-input"> <button class="btn btn--grey">Оставить отзыв</button> </div> </div> </div> <div class="cart-page__loading" if="{ sended }"> <div class="cart-page__spinner text-center"> <h1>Спасибо за отзыв</h1> <p>Ваш отзыв отправлен на модерацию. Можно&nbsp;<a href="" onclick="{ again }">оставить еще&nbsp;один</a></p> </div> </div> </div> </form>', function(opts) {
        var self = this,
            validators = {
                fullname: function(value) {
                    var value = value || ''
                    var msg = 'Обязательно и не менее 3 символов';
                    return {test: !!value.length && value.length >= 3, msg: msg}
                },
                review: function(value) {
                    var value = value || ''
                    var msg = 'Обязательно и не менее 15 символов';
                    return {test: !!value.length && value.length >= 15, msg: msg}
                },
                email: function(value) {
                    var msg = 'Неправильный формат электронной почты',
                        test
                    var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
                    test = re.test(value)
                    return {test: test, msg: msg}
                }
            }

        self.userinfo = opts.userinfo || {}
        self.errors = {}

        function getData(form) {
            var data = form.serializeArray(),
                formData = {};
            $.each(data, function(key) {
                formData[data[key].name] = data[key].value
            })
            return formData
        }

        function validate(data) {
            var validated = []
            $.each(data, function(key) {
                validated.push(validateField(key, data[key]))
            })
            return validated.every(Boolean)
        }

        function validateField(name, value) {
            if (validators[name] !== undefined) {
                var res = validators[name](value)
                self.errors[name] = !res.test ? res.msg : ''
                return res.test
            }
            return true
        }


        function sendReview(data) {
            self.sending = true
            data.offer_id = parseInt(opts.offerid)
            $.ajax({
                method: 'post',
                dataType: 'json',
                url: '/reviews/',
                data: data,
                success: function(data) {
                    self.sending = false
                    clearFields(data)
                    self.sended = true
                    self.update()
                },
                error: function() {
                    self.sending = false
                    alert('Невозможно отправить отзыв, попробуйте позже')
                    self.update()
                }
            })
        }

        function clearFields(data) {
            if (self.form) self.form[0].reset()
        }

        this.again = function(e) {
            self.sended = false
        }.bind(this);

        this.validateOne = function(e) {
            validateField(e.target.name, e.target.value)
        }.bind(this);

        this.submit = function(e) {
            var data = getData($(e.target))
            self.form = $(e.target)
            if (validate(data)) {
                sendReview(data)
            }
        }.bind(this);



    
});