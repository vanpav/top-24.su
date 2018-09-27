<tabs>
    <ul class="content__tabs">
        <li class="content__tabs-item {'content__tabs-item--active': tab.active}" each={tab in tabs}><a href="" class="link-plain" onclick={ activate }>{ tab.opts.heading }</a></li>
    </ul>

    <yield/>

    <script>
        var self = this
        this.tabs = this.tags['tab']

        var deselect = function() {
            self.tabs.forEach(function(tab) {
                tab.active = false
            })
        }

        activate(e) {
            var tab = e.item.tab
            deselect()
            tab.active = true
        }

        this.on('activateByIdx', function(index) {
            if (index > self.tabs.length - 1) return
            var tab = self.tabs[index]
            deselect()
            tab.active = true
            self.update()
        })

        window.thatOffer = this;

    </script>
</tabs>


<tab>
    <div class="content__text content__text--padding-20 {'content__text--hide': !active}">
        <yield/>
    </div>

    <script>
        this.route = opts.route
        this.active = opts.active == 'true'
    </script>
</tab>


<comment-form>
    <form action="post" onsubmit={ submit } enctype="multipart/form-data">
        <div class="order-form__group order-form__group--comments">
            <div class="cart-page__loading" if={ sending }>
                <div class="cart-page__spinner text-center">
                    <div class="spinner spinner--big"><span><span></span></span></div>
                    <p>Отправляем отзыв</p>
                </div>
            </div>
            <div>
                <h3 class="order-form__group-title">Оставить отзыв</h3>
                <div class="order-form__line {order-form__line--error: !!errors['fullname']}">
                    <label class="order-form__line-name">Имя</label>
                    <div class="order-form__line-input order-form__line-input--short">
                        <input type="text" name="fullname" class="input" onblur={ validateOne } placeholder="Иванов Федор Павлович">
                        <span class="order-form__line-error">{ errors['fullname'] }</span>
                    </div>
                </div>
                <div class="order-form__line {order-form__line--error: !!errors['email']}">
                    <label class="order-form__line-name">Электронная почта</label>
                    <div class="order-form__line-input order-form__line-input--short">
                        <input type="text" name="email" class="input" onblur={ validateOne } placeholder="ivanov@fedor.pav">
                        <span class="order-form__line-error">{ errors['email'] }</span>
                    </div>
                </div>
                <div class="order-form__line">
                    <label class="order-form__line-name">Оценка</label>
                    <div class="order-form__line-input order-form__line-rating-input">
                        <label for="rating_1"><input type="radio" name="rating" id="rating_1" value="1"><span>1</span></label>
                        <label for="rating_2"><input type="radio" name="rating" id="rating_2" value="2"><span>2</span></label>
                        <label for="rating_3"><input type="radio" name="rating" id="rating_3" value="3"><span>3</span></label>
                        <label for="rating_4"><input type="radio" name="rating" id="rating_4" value="4"><span>4</span></label>
                        <label for="rating_5"><input type="radio" name="rating" id="rating_5" value="5"><span>5</span></label>
                        <label for="rating_6"><input type="radio" name="rating" id="rating_6" value="6"><span>6</span></label>
                        <label for="rating_7"><input type="radio" name="rating" id="rating_7" value="7"><span>7</span></label>
                        <label for="rating_8"><input type="radio" name="rating" id="rating_8" value="8"><span>8</span></label>
                        <label for="rating_9"><input type="radio" name="rating" id="rating_9" value="9"><span>9</span></label>
                        <label for="rating_10"><input type="radio" name="rating" id="rating_10" value="10"><span>10</span></label>
                    </div>
                </div>
                <div class="order-form__line {order-form__line--error: !!errors['review']}">
                    <label for="" class="order-form__line-name">Комментарий</label>
                    <div class="order-form__line-input">
                        <textarea name="review" rows="4" onblur={ validateOne }></textarea>
                        <span class="order-form__line-error">{ errors['review'] }</span>
                    </div>
                </div>
                <div class="order-form__line">
                    <div class="order-form__line-input">
                        <button class="btn btn--grey">Оставить отзыв</button>
                    </div>
                </div>
            </div>
            <div class="cart-page__loading" if={ sended }>
                <div class="cart-page__spinner text-center">
                    <h1>Спасибо за отзыв</h1>
                    <p>Ваш отзыв отправлен на модерацию. Можно&nbsp;<a href="" onclick={ again }>оставить еще&nbsp;один</a></p>
                </div>
            </div>
        </div>
    </form>

    <script>
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

        again(e) {
            self.sended = false
        }

        validateOne(e) {
            validateField(e.target.name, e.target.value)
        }

        submit(e) {
            var data = getData($(e.target))
            self.form = $(e.target)
            if (validate(data)) {
                sendReview(data)
            }
        }



    </script>
</comment-form>