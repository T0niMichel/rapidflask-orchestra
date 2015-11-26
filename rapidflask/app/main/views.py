#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Toni Michel'

from datetime import datetime

from flask import render_template, redirect, url_for, abort, flash, make_response, jsonify, session, g

from . import main
from app import db
from .forms import *
from app.decorators import *


@main.route('/', methods=["GET", "POST"])
def index():
    return render_template('main_index.html', current_time=datetime.utcnow())
