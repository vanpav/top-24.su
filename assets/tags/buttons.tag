<add-to-cart onclick={ add }>
    <span class={ btn__added:true, btn__added--show: isadded }>{ text }</span>
    <yield/>

    <script>
        var self = this
        self.isadded = false
        self.text = 'В корзине'

        add(e) {
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
        }

        cartStorage.on('update', function() {
            var finded = this.offers.filter(function(offer) {
                return opts.id == offer.id
            })
            self.isadded = finded.length ? true : false
            self.update()
        })

    </script>
</add-to-cart>

<quick-buy onclick={ buy }>
    <yield/>

    <script>
        buy(e) {
            content = {
                tag: 'modal-offer',
                offer_id: opts.id
            }
            window.modalWindow.open(content)
        }
    </script>
</quick-buy>

<offer-form>
    <!--<div class="offer__count">
        <div class="offer__field-label">Количество</div>
        <span class="control__count"><span onclick={ decrease } class={btn: true, btn--outline: true, btn--iconed: true, btn--icon-minus: true, control__count-minus:true, btn--dissabled: quantity == 1 } ></span><input type="text" class="input control__count-input" value="{ quantity }" disabled><span onclick={ increase } class="btn btn--outline btn--iconed btn--icon-plus control__count-plus"></span></span>
    </div>-->
    <div class="offer__count" if={ variants.length }>
        <div class="offer__field-label">Модель</div>
        <select name="variant" class="control__count" onchange={ setVariant }>
            <option each={ variant in variants } value="{ variant.id }" disabled={ !variant.count } selected={ variant.id == choosedVariant ? selected : false }>{ variant.name }</option>
        </select>
    </div>
    <div class="offer__buttons">
        <button riot-tag="add-to-cart" id={ opts.offer_id } variant={ choosedVariant } qty={ quantity } class="btn btn--large"><span class="btn__text"><i class="icon-16 icon--cart-white"></i>В корзину</span></button>
        <button riot-tag="quick-buy" id={ opts.offer_id } class="btn btn--grey btn--large"><span class="btn__text">Купить сейчас</span></button>
    </div>

    <script>
        var self = this

        self.quantity = 1

        send(e) {
            console.log('send')
        }

        setVariant(e) {
            self.choosedVariant = e.target.value
        }

        decrease(e) {
            if (self.quantity > 1) {
                self.quantity--
            }
        }

        increase(e) {
            self.quantity++
        }

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

    </script>
</offer-form>


<modal-window>
    <div class="modal {modal--hide: !opened}">
        <div class="modal__hider" onclick={ close }></div>
        <div class="modal__window { modal__window--hide: !showed }">
            <div class="modal__window-wrapper">
                <span class="modal__window-close" onclick={ close }></span>
                <div id="mounter"></div>
            </div>
        </div>
    </div>

    <script>
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

        close() {
            self.modal.close();
            self.showed = false;
            $(window).off('resize', setPosition);
            self.update();
        }

    </script>
</modal-window>


<modal-offer>
    <div class="modal-offer">
        <div class="modal-offer__info">
            <div class="modal-offer__info-badges" if={ !!offer.oldprice }>
                <span class="badge-special">Акция</span>
            </div>
            <div class="modal-offer__category"><a href={ offer.category.url } class="link-plain link-grey text-small">{ offer.category.name }</a></div>
            <h2 class="modal-offer__name"><a href={ offer.url } class="link-plain">{ offer.name }</a></h2>
            <div class="modal-offer__image">
                <a href={ offer.url } class="link-plain"><img src={ offer.picture } alt={ offer.name } title={ offer.name }></a>
                <div class="modal-offer__countdown" if={ offer.timer }>
                    <div id="countdown" class="countdown"></div>
                </div>
            </div>
            <div class="modal-offer__price { modal-offer__price--special: !!offer.oldprice }"><span if={ offer.oldprice }>{ offer.oldprice }</span>{ offer.price } руб.</div>
        </div>
        <div class="modal-offer__form">
            <div class="modal-offer__loading" if={ loading }>
                <div class="modal-offer__loading-spinner text-center">
                    <div class="spinner spinner--big"><span><span></span></span></div>
                    <p>Оформляем заказ</p>
                </div>
            </div>
            <div class="modal-offer__form-line">
                <label class="text-small">Количество</label>
                <span class="control__count"><span onclick={ decrease } class={btn: true, btn--outline: true, btn--iconed: true, btn--icon-minus: true, control__count-minus:true, btn--dissabled: count == 1 }></span><input type="text" class="input control__count-input" disabled value="{ count }"><span onclick={ increase } class="btn btn--outline btn--iconed btn--icon-plus control__count-plus"></span></span>
            </div>
            <div class="modal-offer__form-line" if={ offer.variants.length }>
                <label class="text-small">Модель</label>
                <select name="variant" class="control__count" style="width: 100%;" onchange={ setVariant }>
                    <option each={ variant in offer.variants } value="{ variant.id }" disabled={ !variant.count } selected={ variant.id == choosedVariant ? selected : false }>{ variant.name }</option>
                </select>
            </div>
            <div class="modal-offer__form-line {modal-offer__form-line--error: errors}">
                <label class="text-small">Телефон</label>
                <input type="text" name="phone" placeholder="7 (495) 123-4567" class="input" id="phone">
            </div>
            <div class="modal-offer__form-button">
                <input type="submit" onclick={ postOrder } value="Оформить заказ" class="btn btn--large">
            </div>
        </div>
    </div>

    <script>
        var self = this,
            phone_re = /^[78]{1}\s\([0-9]{3}\)\s[0-9]{3}[-]{1}[0-9]{4}$/;

        self.offer_id = opts.offer_id;
        self.count = 1;
        self.offer = {};
        self.loading = false;
        self.errors = false;

        decrease() {
            if (self.count > 1) {
                self.count--;
            }
        }

        increase() {
            self.count++;
        }

        setVariant(e) {
            self.choosedVariant = e.target.value
        }

        function validate() {
            var test = phone_re.test(self.phone.value);

            self.errors = !test;

            return test
        }

        postOrder() {
            if (!validate()) {
                $(self.phone).on('keyup', validate);
                return;
            }

            self.loading = true;
            // Should block window while order processing
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
        }

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
    </script>
</modal-offer>


<offer-delivery>
    <yield/>

    <script>
        var self = this;

        self.current_region = opts.current_region

        select(region) {
            self.current_region = region.id;
            fetch(region);
        }

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
    </script>
</offer-delivery>

<modal-delivery>
    <div class="modal-delivery">
        <div class="modal-delivery__search"><input type="text" class="input" name="searchinp" oninput={ search } placeholder="Введите название города" /></div>
        <ul class="modal-delivery__founded">
            <li class="modal-delivery__founded-error" if={ !regions.length }>Городов не найдено</li>
            <li class="modal-delivery__founded-item" onclick={ choose } each={ region in regions } region_id={ region.id }>{ region.text }</li>
        </ul>

    </div>

    <script>
        var self = this,
            search_timer;

        self.regions = [];

        choose(e) {
            if (opts.current_region != e.item.region.id) opts.parent.select(e.item.region);
            window.modalWindow.close();
        }

        search(e) {
            var query = e.target.value;
            if (query.length >= 2) {
                clearTimeout(search_timer);
                search_timer = setTimeout(function() {
                    fetch(e.target.value)
                }, 500)
            }
        }

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
    </script>
</modal-delivery>

<offer-articul>
    <div class="offer__articul" if={ articul }>Артикул: <strong>#{ articul }</strong></div>

    <script>
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
    </script>
</offer-articul>