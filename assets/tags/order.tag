<order-upsale>
    <div class="order__upsale" if={ offers }>
        <h2 class="order__upsale-header">Добавьте к заказу</h2>
        <div class="order__upsale-timer"><span id="timeto"></span></div>
        <ul class="blocks-3 offers order__offers">
            <li class="offers__item" riot-tag="order-upsale-item" each={ offer in offers }></li>
        </ul>
    </div>

    <script>
        var self = this;

        self.offerTPL = $('.cart-offers .cart-offers__item').first();

        fetch() {
            $.ajax({
                type: 'get',
                dataType: 'json',
                url: '/order/' + self.order_id + '/api/upsale/',
                success: function(data) {
                    self.offers = data.offers;
                    self.update();
                }
            })
        }

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
    </script>
</order-upsale>

<order-upsale-item>
    <li>
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

    <script>
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

        add(e) {

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
        }
    </script>
</order-upsale-item>