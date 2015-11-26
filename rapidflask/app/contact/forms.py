#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Toni Michel'

from flask.ext.wtf import Form, RecaptchaField
from wtforms.validators import DataRequired, Email, Length
from wtforms import StringField, TextAreaField, SubmitField


class ContactForm(Form):
    contact_message = TextAreaField('Message', validators=[DataRequired()])
    contact_email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                                     Email()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Send')
