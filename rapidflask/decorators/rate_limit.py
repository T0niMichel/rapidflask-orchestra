#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Decorators
----------
to DRY out our code...

Listen to this guy https://www.youtube.com/watch?v=wFUkKgT8tFQ

...with the decorator from http://flask.pocoo.org/snippets/70/

Rate Limiting Decorator with Redis
++++++++++++++++++++++++++++++++++
http://flask.pocoo.org/snippets/70/

By Armin Ronacher filed in Decorators

Sometimes you want to rate limit a view (for example an API).
This is very simple to do with redis and a simple decorator.
The idea is that we limit a view for a certain period of time
and increment a counter in redis.
The key for this counter shall be the current IP (or userid)
plus the current endpoint plus the time when the rate limit
resets.


Connecting to Redis

In case you don't have a connection to redis yet, open with with those two simple lines:

from redis import Redis
redis = Redis()

A redis instance is thread safe so you can just keep this on
the global level and use it directly. If you want to connect
to a different redis instance just pass the address to the
constructor. More in the pyredis docs.

Rate Limit Code
+++++++++++++++

The actual rate limiting looks like this::

    class RateLimit(object):
        expiration_window = 10

        def __init__(self, key_prefix, limit, per, send_x_headers):
            self.reset = (int(time.time()) // per) * per + per
            self.key = key_prefix + str(self.reset)
            self.limit = limit
            self.per = per
            self.send_x_headers = send_x_headers
            p = redis.pipeline()
            p.incr(self.key)
            p.expireat(self.key, self.reset + self.expiration_window)
            self.current = min(p.execute()[0], limit)

        remaining = property(lambda x: x.limit - x.current)
        over_limit = property(lambda x: x.current >= x.limit)

    def get_view_rate_limit():
        return getattr(g, '_view_rate_limit', None)

    def on_over_limit(limit):
        return 'You hit the rate limit', 400

    def ratelimit(limit, per=300, send_x_headers=True,
                  over_limit=on_over_limit,
                  scope_func=lambda: request.remote_addr,
                  key_func=lambda: request.endpoint):
        def decorator(f):
            def rate_limited(*args, **kwargs):
                key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
                rlimit = RateLimit(key, limit, per, send_x_headers)
                g._view_rate_limit = rlimit
                if over_limit is not None and rlimit.over_limit:
                    return over_limit(rlimit)
                return f(*args, **kwargs)
            return update_wrapper(rate_limited, f)
        return decorator

The key is constructed by default from the remote address
and the current endpoint (name of the view function).
Before the function is executed it increments the rate limit
with the help of the RateLimit class and stores an instance
on g as g._view_rate_limit. Also if the view is indeed over
limit we automatically call a different function instead.

The view function itself can get hold of the current rate limit
by calling get_rate_limit().

We also give the key extra expiration_window seconds time
to expire in redis so that badly synchronized clocks between
the workers and the redis server do not cause problems.
Furthermore we use a pipeline (uses MULTI behind the scenes)
to make sure that we never increment a key without also
setting the key expiration in case an exception happens
between those lines (for instance if the process is killed).


X-RateLimit Headers

If we you to automatically emit X-RateLimit headers you can
attach this after-request function::

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
To use the decorator just apply it to a function::

    @app.route('/rate-limited')
    @rate_limit(300,60 *15)
    def index():
        return '<h1>This is a rate limited response</h1>'

This would limit the function to be called 300 times
per 15 minutes.

This snippet by Armin Ronacher can be used freely for anything
you like. Consider it public domain.

"""
__author__ = 'doj.ooo'

import time
from functools import update_wrapper
from flask import request, g
from app import redis


class RateLimit(object):
    """

	:param key_prefix:
	:param limit:
	:param per:
	:param send_x_headers:
	"""
    expiration_window = 10

    def __init__(self, key_prefix, limit, per, send_x_headers):
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        p = redis.pipeline()
        p.incr(self.key)
        p.expireat(self.key, self.reset + self.expiration_window)
        self.current = min(p.execute()[0], limit)

    remaining = property(lambda x: x.limit - x.current)
    over_limit = property(lambda x: x.current>=x.limit)


def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)


def on_over_limit(limit):
    return 'You hit the rate limit', 400


def ratelimit(limit, per=300, send_x_headers=True,
              over_limit=on_over_limit,
              scope_func=lambda: request.remote_addr,
              key_func=lambda: request.endpoint):
    def decorator(f):
        def rate_limited(*args, **kwargs):
            key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
            rlimit = RateLimit(key, limit, per, send_x_headers)
            g._view_rate_limit = rlimit
            if over_limit is not None and rlimit.over_limit:
                return over_limit(rlimit)
            return f(*args, **kwargs)

        return update_wrapper(rate_limited, f)

    return decorator
