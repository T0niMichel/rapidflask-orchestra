#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Miguel Grinberg'

from flask.ext.mail import Message
from threading import Thread
from flask import current_app, render_template
from app import mail


def _send_async_email(app, msg):
    '''_send_async_email

    .. function::
        sends an email with falsk.ext.mail

    used by send_email


    :param app:
    :param msg:
    :return:
    '''
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    ''' send emails

    .. function::
        process gets threaded

    :param to: recipient
    :param subject:
    :param template: path to template (without .txt)
    :param kwargs: user=user (vars for the template)
    :return: thread which sends the email
    '''
    app = current_app._get_current_object()
    msg = Message(app.config['SYSTEM_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['SYSTEM_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=_send_async_email, args=[app, msg])
    thr.start()
    return thr
