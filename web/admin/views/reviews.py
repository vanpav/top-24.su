# -*- coding: utf-8 -*-

import json
from flask import request
from modules.catalog.models import Review
from ext import csrf
from ..helpers import AdminMethodView, render_template, admin_required

class ReviewsView(AdminMethodView):

    decorators = [csrf.exempt, admin_required]

    def get(self):
        reviews = Review.objects()
        return render_template('admin/reviews.html', reviews=reviews)

    def post(self):
        review_id = request.form.get('review_id', None)

        review = Review.objects(id=review_id).first()
        if review:
            command = request.form.get('command', None)

            if command == 'toggle_moderate':
                review.toggle_moderate()

            elif command == 'set_viewed':
                review.set_viewed()

            elif command == 'remove':
                review.delete()

            return json.dumps({'errors': None})