#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contact views
--------------

Manages views for our contact form.
Sends an email to the admin and a notification email to the user,
if he/she has submitted an valid email address as well.

Rate limiting is of importance since this method could DOS us in several ways!

General Information
++++++++++++++++++++

Defines available routes!
Most likely we will find reusable code here.
**IMPLEMENT THEM AS A DECORATOR!**


Rate limiting
+++++++++++++

Following http://flask.pocoo.org/snippets/70/

We do automatically emit X-RateLimit headers
by attaching this after-request function:

.. code: python
@app.after_request
    def inject_x_rate_headers(response):
        limit = get_view_rate_limit()
        if limit and limit.send_x_headers:
            h = response.headers
            h.add('X-RateLimit-Remaining', str(limit.remaining))
            h.add('X-RateLimit-Limit', str(limit.limit))
            h.add('X-RateLimit-Reset', str(limit.reset))
        return response

Using the Decorator
+++++++++++++++++++
To use the decorator just apply it to a function:

.. code: python
    @app.route('/rate-limited')
    @rate_limit(23,60 *15)
    def index():
        return '<h1>This is a rate limited response</h1>'

This would limit the function to be called 23 times
per 15 minutes.
"""
__author__ = 'doj.ooo'

from flask import render_template, request, flash

from . import contact
from .forms import ContactForm
from app.email import send_email
from app.decorators import *


@contact.route('/', methods=['GET', 'POST'])
@rate_limit(5, 60 * 60)
def contact():
	'''

	Contact view function

	.. function::
		renders cantact_base.html
		sends Emails to Admin and
		a Notification to the contact email address



	:return: redirect on submit, else logintemplate
	'''
	form = ContactForm()

	if request.method == 'POST' and form.validate_on_submit():
		send_email(form.contact_email.data,
		           'Notification',
		           'email/contact_notify')

		send_email('evilt0ne@gyrosbu.de',
		           'You Got a Message',
		           'email/contact_admin',
		           contact_email=form.contact_email,
		           contact_message=form.contact_message)
		flash('Email was sent!')
	# return redirect('/')

	return render_template('contact_base.html', contact_form=form)
