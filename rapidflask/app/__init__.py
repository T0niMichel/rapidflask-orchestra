#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Application
===========

This File initializes the app package
by calling


Here an app instance is created

code::

    app = Flask(__name__)
    app.config.from_object(config[config_name])

Every needed librarys hate to be initialized with this app object,
else the imported librarys will not be accessable within
an app context.
code::

    oauth2p.init_app(app)

this is needed for gunicorn::

    app.wsgi_app = ProxyFix(app.wsgi_app)

Blueprint and their prefixes are registered as well
in this function.

:param config_name:
:return: returns an app object

"""
__author__ = 'doj.ooo'

from flask import Flask, render_template, jsonify, g
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail

# moment.js for ltc of consumers browser
from flask.ext.moment import Moment

# sqlalchemy is going to complete Our Flask(view/controller) with the Model part
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import config

from flask_redis import FlaskRedis

redis = FlaskRedis()

# gunicorn proxyfix
from werkzeug.contrib.fixers import ProxyFix


# mail logging of errors
import logging
from logging.handlers import SMTPHandler


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'  # endpoint for login
from flask.ext.pagedown import PageDown

pagedown = PageDown()

# http://flask-wtf.readthedocs.org/en/latest/csrf.html
from flask_wtf.csrf import CsrfProtect

csrf = CsrfProtect()


def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    login_manager.init_app(app)
    redis.init_app(app)
    pagedown.init_app(app)
    # To enable CSRF protection for all your view handlers, you need to enable the CsrfProtect module:
    #    csrf.init_app(app)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .users import usersbp as users
    app.register_blueprint(users)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .contact import contact as contact_blueprint
    app.register_blueprint(contact_blueprint, url_prefix='/contact')

    db.init_app(app)
    # register an after request handler

    @app.after_request
    def after_request(rv):
        """
        This enables to set the after_request globally to be dynamic for what decorators you are using

        for example the decorators/rate_limit.py decorator does set this Headers::

            # set the rate limit headers in g, so that they are picked up
            # by the after_request handler and attached to the response
            g.headers = {
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Limit': str(limit),
                'X-RateLimit-Reset': str(reset)
            }

        Or the decorators/caching.py is using the Headers to realizie Etags an HTTP-Caching.
        IT also uses the request-headers to identify the need of sending Information::

            # set the rate limit headers in g, so that they are picked up
            # by the after_request handler and attached to the response
            g.headers = {
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Limit': str(limit),
                'X-RateLimit-Reset': str(reset)
            }

        Usage::

            # authentication token route
            from .auth import auth
            @app.route('/get-auth-token')
            @auth.login_required
            @rate_limit(42, 60*15)  # 42 call per 15 minute period
            @no_cache
            @json
            def get_auth_token():
                return {'token': g.user.generate_auth_token()}



        :param rv: Function that is going to be wrapped
        :return: wrapped function object
        """
        headers = getattr(g, 'headers', {})
        rv.headers.extend(headers)
        return rv

    return app
