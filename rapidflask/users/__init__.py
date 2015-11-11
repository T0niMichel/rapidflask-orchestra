#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'doj.ooo'

from flask import Blueprint

usersbp = Blueprint('users', __name__, template_folder='templates', static_folder='static')
from . import decorators
