#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tryed to import it as a blueprint...
but lets keep them out off our context...

https://github.com/micheles/decorator/blob/3.4.2/documentation3.rst

"""
# from flask import Blueprint
# deco = Blueprint('deco', __name__)

from .permissions import permission_required, admin_required
from .json import json
from .paginate import paginate
from .caching import cache_control, no_cache, etag
from .rate_limit import ratelimit, get_view_rate_limit, on_over_limit, RateLimit
#from .rate_limit import rate_limit, MemRateLimit
#from .background import Async

# usage : async = decorator(Async(threading.Thread))
