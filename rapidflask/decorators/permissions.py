#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" All librarys are included in models/__init__.py
"""
__author__ = 'doj.ooo'

from functools import wraps

from flask import abort
from flask.ext.login import current_user

from app.models import Permission


def permission_required(permission):
	"""
	decorates functions to check user permissions
	for decorated route at views.py

	Usage::

		@permission_required(Permission.ADMINISTER)
		@app.route('/foo/bar')
		def foo:
			lalal...

	:param permission: required permissions
	:return: object
	"""

	def decorator(f):
		"""

		:param f:
		:return:
		"""

		@wraps(f)
		def decorated_function(*args, **kwargs):
			"""

			:param args:
			:param kwargs:
			:return:
			"""
			if not current_user.can(permission):
				abort(403)
			return f(*args, **kwargs)

		return decorated_function

	return decorator


def admin_required(f):
	"""
	Decorates route for admin access only.
	The decorated <app>.route object gets only assessable if user permission is ADMINSTER
	see:


	:param f:
	:return: decorated object if Permission.ADMINISTER
	"""
	return permission_required(Permission.ADMINISTER)(f)
