# -*- coding: utf-8 -*-

from ext import celery, mail

@celery.task(name='accounts.send_mail')
def send_security_mail(msg):
    mail.send(msg)