#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'doj.ooo'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Below you can see how the example application is configured
    """
    #app.config['SECRET_KEY']
    SECRET_KEY = os.environ.get('SECRET_KEY')
    PREFERRED_URL_SCHEME = 'https'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    POSTS_PER_PAGE = os.environ.get('POSTS_PER_PAGE')

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    #they referenced to an easy to use extension
    #https://pythonhosted.org/Flask-Uploads/
    #http://flask-uploads.readthedocs.org/en/latest/
    DEFAULT_FILE_STORAGE = 'filesystem'
    UPLOAD_FOLDER = os.path.realpath('.') + '/app/static/uploads'
    FILE_SYSTEM_STORAGE_FILE_VIEW = 'static'
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    SYSTEM_MAIL_SUBJECT_PREFIX = os.environ.get('SYSTEM_MAIL_SUBJECT_PREFIX')
    SYSTEM_MAIL_SENDER = os.environ.get('SYSTEM_MAIL_SENDER')
    SYSTEM_ADMIN = os.environ.get('SYSTEM_ADMIN')

    RECAPTCHA_USE_SSL = False
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')
    RECAPTCHA_OPTIONS = {'theme': 'white'}

    #REDIS CONFIG
    REDIS_URL = 'redis://{0}:{1}'
    REDIS_DATABASE = 5

    GOOGLE_CONSUMER_KEY = os.environ.get('GOOGLE_CONSUMER_KEY')
    GOOGLE_CONSUMER_SECRET = os.environ.get('GOOGLE_CONSUMER_SECRET')
    SECRET_KEY = os.environ.get('SECRET_KEY')


    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

    DB_NAME_DEV = os.environ.get('DB_NAME_DEV')
    DB_USER_DEV = os.environ.get('DB_USER_DEV')
    DB_PASS_DEV = os.environ.get('DB_PASS_DEV')
    DB_SERVICE_DEV = os.environ.get('DB_SERVICE_DEV')
    DB_PORT_DEV = os.environ.get('DB_PORT_DEV')

    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(basedir, "data-devel.sqlite")
#    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
#        DB_USER_DEV, DB_PASS_DEV, DB_SERVICE_DEV, DB_PORT_DEV, DB_NAME_DEV
#    )

class TestingConfig(Config):
    TESTING = True

    DB_NAME_TESTS = os.environ.get('DB_NAME_TESTS')
    DB_USER_TESTS = os.environ.get('DB_USER_TESTS')
    DB_PASS_TESTS = os.environ.get('DB_PASS_TESTS')
    DB_SERVICE_TESTS = os.environ.get('DB_SERVICE_TESTS')
    DB_PORT_TESTS = os.environ.get('DB_PORT_TESTS')

    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(basedir, "data-test.sqlite")
#    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
#        DB_USER_TESTS, DB_PASS_TESTS, DB_SERVICE_TESTS, DB_PORT_TESTS, DB_NAME_TESTS
#    )

class ProductionConfig(Config):
    DEBUG = False

    DB_NAME_PROD = os.environ.get('DB_NAME_PROD')
    DB_USER_PROD = os.environ.get('DB_USER_PROD')
    DB_PASS_PROD = os.environ.get('DB_PASS_PROD')
    DB_SERVICE_PROD = os.environ.get('DB_SERVICE_PROD')
    DB_PORT_PROD = os.environ.get('DB_PORT_PROD')

    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(basedir, "data-prod.sqlite")
#    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
#        DB_USER_PROD, DB_PASS_PROD, DB_SERVICE_PROD, DB_PORT_PROD, DB_NAME_PROD
#    )

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.SYSTEM_MAIL_SENDER,
            toaddrs=[cls.SYSTEM_ADMIN],
            subject=cls.SYSTEM_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': os.environ.get('DEFAULT_RUN_MODE'),
}
