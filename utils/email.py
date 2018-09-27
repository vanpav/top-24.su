# -*- coding: utf-8 -*-

from flask import render_template
from flask.ext.mail import Message

from ext import celery, mail


def celery_is_running():
    inspect = celery.control.inspect()
    stats = inspect.stats()
    return stats is not None


def send_email(to, subject, text, template=None, **context):

    if not isinstance(to, (list, tuple)):
        to = [to]

    message = Message(recipients=to,
                      subject=subject)

    if template:
        message.html = render_template(template,
                                       text=text,
                                       **context)
    else:
        message.body = text

    if celery_is_running():
        task = send_async_mail.delay(message)
    else:
        mail.send(message)


@celery.task(name='email.send_async')
def send_async_mail(message):
    mail.send(message)