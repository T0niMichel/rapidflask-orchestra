#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
>>> from app import create_app, db
>>> app = create_app('production')
>>> app_context = app.app_context()
>>> app_context.push()
>>> db.create_all()
>>> Role.insert_roles()
>>> User.generate_fake()
>>> db.session.commit()
>>> exit()

"""
__author__ = 'Toni Michel'

import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage

    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

# loading own nutshell
# if os.path.exists('.env'):
#    print('Importing environment from .env...')
#    for line in open('.env'):
#        var = line.strip().split('=')
#        if len(var) == 2:
#            os.environ[var[0]] = var[1]

import logging

from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from app import create_app, db
from app.models import User, Role, Permission, \
    Follow, AnonymousUser, Customer, Item, Order, Product, Url

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# sapp = SocketIO(app)
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    """	Creates a Dictionary with initialized objects and an app context.

    God bless we got our new json decorator ...
    we could even manage this type of initialisation remotely :)
    :return: Dictionary with initialized objects and an app context.
    """
    return dict(app=app,
                db=db,
                User=User,
                Role=Role,
                Permission=Permission,
                Follow=Follow,
                AnonymousUser=AnonymousUser,
                Customer=Customer,
                Item=Item,
                Order=Order,
                Product=Product,
                Url=Url)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys

        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


from flask import url_for


@manager.command
def deploy():
    """
	Deploy Command Implementation.
	++++++++++++++++++++++++++++++

	Note::

		These functions are all designed in a way that causes no problems if they are executed
		multiple times. Designing update functions in this way makes it possible to run just this
		deploy command every time an installation or upgrade is done.

	:return:
	"""
    from flask.ext.migrate import upgrade
    from app.models import Role, User
    # migrate database to latest revision
    #  upgrade()
    #  create user roles
    Role.insert_roles()
    # create self-follows for all users
    User.add_self_follows()


@manager.command
def list_routes():
    import urllib

    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print(line)


@manager.command
def list_routes2():
    import urllib

    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)

    for line in sorted(output):
        print(line)


if __name__ == '__main__':
    """
    | set the following environment variables before running:
    | FLASK_CONFIG(='development', 'testing', 'production'),
    | MAIL_USERNAME,
    | MAIL_PASSWORD,
    | SYSTEM_MAIL_SENDER
    """
    logging.basicConfig(filename='/tmp/myapp.log', level=logging.DEBUG)
    logging.info('Started')
    manager.run()
    logging.debug('Finished')
