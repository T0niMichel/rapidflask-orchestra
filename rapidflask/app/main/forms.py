#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Toni Michel'

from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField, \
    SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
