'use strict';

(function($) {

    $('.js-category-sort').on('change', function() {
        $(this).parent().submit();
    });

    var csrftoken = $('meta[name=csrf-token]').attr('content');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    (function(exports) {
        function CartStorage() {
            var self = riot.observable(this);

            self.offers = [];
            self.total = {quantity: 0, sum: 0};
            self.userinfo = {};

            self.set = function(offers) {
                self.offers = offers;
                calculateTotal();
                self.trigger('update');
            };

            self.update = function(offer_id, qty, variant_id, remove) {
                var remove = remove == true ? true : false;

                $.ajax({
                    method: 'post',
                    dataType: 'json',
                    url: '/cart/api/',
                    data: {offer_id: offer_id, quantity: qty, variant_id: variant_id, remove: remove},
                    success: function(data) {
                        self.set(data.offers)
                    }
                });
            };

            self.fetch = function() {
                $.ajax({
                    method: 'post',
                    dataType: 'json',
                    url: '/cart/api/',
                    success: function(data) {
                        self.userinfo = data.userinfo;
                        for (var key in self.userinfo) {
                            if (!localStorage.getItem(key)) localStorage.setItem(key, self.userinfo[key]);
                        }
                        self.set(data.offers);
                    }
                })
            };

            function calculateTotal() {
                self.total = {quantity: 0, sum: 0};

                self.offers.forEach(function(offer) {
                    self.total.quantity += offer.quantity;
                    self.total.sum += offer.quantity * offer.price;
                });

                self.total.sum = smartRound(self.total.sum);
            }
        }

        function FavoriteStorage() {
            var self = riot.observable(this);

            self.favorites = [];

            function request(offer_id) {
                $.ajax({
                    method: 'post',
                    dataType: 'json',
                    url: '/favorites/',
                    data: {offer_id: offer_id},
                    success: function(data) {
                        self.favorites = data.favorites;
                        self.trigger('update');
                    }
                })
            };

            self.fetch = function() {
                request();
            };

            self.update = function(offer_id) {
                request(offer_id);
            };

        }

        function ModalWindow() {
            var self = riot.observable(this);

            self.opened = false;

            function toggleBodyOverflow() {
                var curr = $('body').css('overflow-y');
                $('body').css({'overflow-y': curr == 'hidden' ? 'auto' : 'hidden' })
            }

            self.open = function(content) {
                self.opened = true;
                self.content = content;
                toggleBodyOverflow();
                self.trigger('update');
            };

            self.close = function() {
                self.opened = false;
                self.content = null;
                toggleBodyOverflow();
                self.trigger('update');
            };
        }

        function smartRound(value) {
            var spl = value.toString().split('.');
            if (spl.length > 1) return parseFloat(value.toFixed(2));

            return parseInt(value)

        }

        exports.cartStorage = new CartStorage();
        exports.cartStorage.fetch();
        exports.smartRound = smartRound;

        exports.favoriteStorage = new FavoriteStorage();
        exports.favoriteStorage.fetch();

        exports.modalWindow = new ModalWindow();

    })(window);



    var cart = riot.mount('cart');

    //riot.mount('cart-related');
    riot.mount('add-to-cart');
    riot.mount('quick-buy');
    riot.mount('minified-cart');
    riot.mount('offer-form');
    riot.mount('offer-delivery');
    riot.mount('offer-articul');


    riot.mount('order-upsale');


    riot.mount('tabs');

    riot.mount('favorite');
    riot.mount('favorites');

    riot.mount('modal-window');


    // Delete THIS
    //modalWindow.open({tag: 'modal-offer', offer_id: '12'});


    $('.js-offers-special').owlCarousel({
        items: 3,
        itemsCustom: [[0, 1], [400, 2], [700, 3], [1000, 3], [1240, 4], [1600, 4]],
        navigation: true,
        navigationText : false,
        scrollPerPage: true,
        rewindNav: false
    });

    $('.js-offers-four').owlCarousel({
        items: 4,
        itemsCustom: [[0, 1], [400, 2], [700, 4], [1000, 4], [1240, 4], [1600, 4]],
        navigation: true,
        navigationText : false,
        scrollPerPage: true,
        rewindNav: false
    });

    $('.js-offers-visited').owlCarousel({
        items: 4,
        navigation: true,
        navigationText : false,
        scrollPerPage: true,
        rewindNav: false
    });

    $('[data-countdown]').each(function() {
        var $this = $(this), finalDate = $(this).data('countdown');
        $this.countdown(finalDate, function(event) {
            var totalHours = event.offset.totalDays * 24 + event.offset.hours;
            $this.html(event.strftime(totalHours+':%M:%S'));
        });
    })

    $('.js-sticky').Stickyfill();


    $('.offer__text').on('click', function(e) {
        e.preventDefault();
        var tabs = $("[riot-tag=tabs]");
        window.thatOffer.trigger('activateByIdx', 0)
        $('html, body').animate({
            scrollTop: tabs.offset().top - 30
        }, 300);
    });

    $('.offer__reviews a').on('click', function(e) {
        e.preventDefault();
        var tabs = $("[riot-tag=tabs]");
        window.thatOffer.trigger('activateByIdx', 1)
        $('html, body').animate({
            scrollTop: tabs.offset().top - 30
        }, 300);
    });

    var subscribe = $('.subscribe');

    if (!!subscribe.length) {
        var form = subscribe.find('form');

        form.on('submit', function(e) {
            e.preventDefault();

            function serializeForm(form) {
                var o = {},
                    s = form.serializeArray();

                $.each(s, function (k, v) {
                    o[v.name] = v.value;
                });
                return o;
            }

            $.ajax({
                type: 'POST',
                dataType: 'JSON',
                url: '/subscribe/',
                data: serializeForm(form),
                success: function(data) {
                    var errors = form.find('.subscribe__errors').html('');

                    if (data.errors) {
                        $.each(data.errors, function(k, v) {
                            var li = $('<li/>').text(v).appendTo(errors);
                        })
                    } else {
                        form.siblings('.subscribe__overlay').removeClass('subscribe__overlay--hide');

                        setTimeout(function() {
                            var el;
                            if (subscribe.parent().hasClass('row')) el = subscribe.parent();
                            else el = subscribe;
                            el.slideUp(500, function() {
                                subscribe.remove();
                            })
                        }, 5000)
                    }
                }
            })

        })
    }

})(jQuery);