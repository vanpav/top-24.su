# -*- coding: utf-8 -*-

from os import path as op

# Need to setup
DB_NAME = 'YOUR_DB_NAME'
DB_TEMP_NAME = '%s_temp' % DB_NAME

class Config(object):
    SITENAME = u'Админка'

    DEFAULT_TITLE = u'Магазин ТОП-24'
    DEFAULT_TITLE_SEPARATOR = u' | '

    PHONE_NUMBER = '+7 (499) 705-95-84'

    MINIFY_PAGE = True

    DEBUG = True
    SECRET_KEY = 'KEEP_IT_SECRET'
    CSRF_ENABLED = WTF_CSRF_ENABLED = True

    BASE_DIR = op.abspath(op.dirname(__file__))
    MEDIA_DIR = op.join(BASE_DIR, 'media')

    COLLECT_STATIC_ROOT = op.join(BASE_DIR, 'static')
    COLLECT_STORAGE = 'flask.ext.collect.storage.file'

    ALLOWED_FILE_EXTENSIONS = set(['pdf', 'txt'])
    ALLOWED_IMAGES_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'svg'])
    ALLOWED_EXTENSIONS = set(list(ALLOWED_FILE_EXTENSIONS) + list(ALLOWED_IMAGES_EXTENSIONS))

    RESIZE_ROOT = BASE_DIR
    RESIZE_URL = 'http://127.0.0.1:5000/'
    RESIZE_CACHE_DIR = 'media/cache'


    MONGODB_SETTINGS = {
        'db': DB_NAME,
        'alias': 'default'
    }

    # SECURITY
    SECURITY_PASSWORD_HASH = 'sha512_crypt'
    SECURITY_PASSWORD_SALT = SECRET_KEY

    SECURITY_LOGIN_URL = '/accounts/login/'
    SECURITY_LOGOUT_URL = '/accounts/logout/'
    SECURITY_REGISTER_URL = '/accounts/register/'

    SECURITY_REGISTERABLE = False

    SECURITY_LOGIN_USER_TEMPLATE = 'admin/security/login.html'
    SECURITY_REGISTER_USER_TEMPLATE = 'admin/security/register.html'

    SECURITY_MSG_INVALID_EMAIL_ADDRESS = (u'Неверный формат элетронной почты', 'error')
    SECURITY_MSG_USER_DOES_NOT_EXIST = (u'Пользователя не существует', 'error')
    SECURITY_MSG_PASSWORD_NOT_PROVIDED = (u'Не указан пароль', 'error')
    SECURITY_MSG_INVALID_PASSWORD = (u'Неправильный пароль', 'error')

    # CELERY
    CELERY_IMPORTS = (
        'modules.accounts.tasks',
        'modules.apishop.tasks',
        'modules.catalog.tasks',
        'utils.email'
    )
    CELERY_RESULT_BACKEND = "mongodb"
    CELERY_MONGODB_BACKEND_SETTINGS = {
        "host": 'localhost',
        "port": 27017,
        "database": '%s_celery' % DB_NAME
    }
    CELERY_BROKER_URL = 'mongodb://localhost:27017/%s' % CELERY_MONGODB_BACKEND_SETTINGS['database']
    from datetime import timedelta
    CELERYBEAT_SCHEDULE = {
        'test-every-second': {
            'task': 'apishop.autoupdate',
            'schedule': timedelta(minutes=5)
        }
    }

    # MAIL
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'YOUR_EMAIL@gmail.com'
    MAIL_DEFAULT_SENDER = (DEFAULT_TITLE, MAIL_USERNAME,)
    MAIL_PASSWORD = 'YOUR_EMAIL_PASSWORD'

    # APISHOP
    APISHOPS_WSDL_URL = 'http://api.apishops.com/services/API?wsdl'
    APISHOPS_YML_URL = 'http://www.apishops.com/websiteAction?action=getPrice&addPictures=1&id='

    # CACHE
    CACHE_TYPE = 'memcached'
    CACHE_DIR = 'cache'

    ###

    DEBUG_TB_PANELS = [
        'flask_debugtoolbar.panels.versions.VersionDebugPanel',
        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
        'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
        'flask_debugtoolbar.panels.logger.LoggingPanel',
        'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
        'flask_debugtoolbar_mongo.panel.MongoDebugPanel',
    ]
