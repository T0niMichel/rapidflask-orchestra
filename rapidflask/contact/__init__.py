# coding=utf-8
__author__ = 'doj.ooo'

from flask import Blueprint

from app.decorators import etag, rate_limit

contact = Blueprint('contact', __name__, template_folder='templates', static_folder='static')


@contact.before_request
@rate_limit(5, 15)
def before_request():
    """All routes in this blueprint are rate limited by default."""
    pass


@contact.after_request
@etag
def after_request(rv):
    """Generate an ETag header for all routes in this blueprint.
	:param rv:
	"""
    return rv


from . import views, forms
