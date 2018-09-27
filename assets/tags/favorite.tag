<favorite>
    <div class="offers__item-favorite {offers__item-favorite--added: favorited}" onclick={ toggle }>
        <span class="favorite-icon"><i class="icon-16 icon--heart-grey"></i></span>
    </div>

    <script>
        var self = this;

        self.id = self.opts.oid;
        self.favorited = self.opts.favorited == true || self.opts.favorited == 'true' || false;

        toggle(e) {
            self.favorited = !self.favorited;
            favoriteStorage.update(self.id);
        }

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

    </script>
</favorite>

<favorites>
    <span>
        <yield/>
    </span>

    <script>
        var self = this;

        favoriteStorage.on('update', function() {
            self.root.innerHTML = this.favorites.length || 0;
        })
    </script>
</favorites>