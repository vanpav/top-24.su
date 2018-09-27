# -*- coding: utf-8 -*-

from api import AsApi
from models import ApishopConfig, ApishopCategory, ApishopOffer
from parser import parse
from tasks import download_yml_task, parse_yml_task

api_connect = lambda conf: AsApi(conf.login,
                             conf.password,
                             'http://api.apishops.com/services/API?wsdl',
                             conf.shop_id)