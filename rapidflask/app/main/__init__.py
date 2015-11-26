#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Toni Michel'

from flask import Blueprint

from app.models import Permission

main = Blueprint('main', __name__, template_folder='templates', static_folder='static')
from . import views, errors, forms

from app.decorators import rate_limit


@main.before_request
@rate_limit(42, 10)
def before_request():
    """All routes in this blueprint require rate limiting."""
    pass
