#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""All librarys are included in models/__init__.py
"""
__author__ = 'doj.ooo'

import hashlib
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request

from flask.ext.login import UserMixin, AnonymousUserMixin

from app.models import *
from app import db, login_manager


class Permission():
    """Define Your User permissions here!"""

    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

    def __repr__(self):
        return '<Role %r>' % self.name


class Role(db.Model):
    """Define User Roles here!

    .. function::
    Referencing to Permissions

    .. highlight:: python
        :linenos:
        roles = {
                 'User': (0x01 |
                 0x02 |
                 0x04, True),

                 'Moderator': (0x01 |
                          0x02 |
                          0x04 |
                          0x08, False),
        'Administrator': (0xff, False)
        }

        0x01 Follow users
        0x02 Comment on post made by others
        0x04 Write original articles
        0x08 Supress offensive comments made by others
        0x80 Administrative access to the

        :param kwargs: SQLAlchemy Database Moddel
        """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        """ inserts available roles into the database  """
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)

        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    """
    UserMixin Class has default implementations for authentication

    he model also inherits from UserMixin from Flask-Login,
    as that gives it the methods required by that extension.
    The user_loader callback function, also required by Flask-Login,
    loads a user by its primary key.

    :param social_id: a string that defines a unique identifier from the third party authentication service used
    tologin.
    :param nickname: a nickname for the user. Must be defined for all users, and does not need to be unique.
    :param email: the email address of the user.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    # this implements the helpertable which is used to implement a twitter like following
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    @staticmethod
    def generate_fake(count=100):
        """

        :param count:
        """
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def add_self_follows():
        """add_self_follows
        """
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def __init__(self, **kwargs):
        """init

        .. function::
            User init, sets the User role
            since it uses current_app.config['SYSTEM_ADMIN'] the User object hst to be created via app.route('foo').
            This user object will be associated with a default permission if the email is not equal to SYSTEM_ADMIN.

        :param kwargs:
        :return: None
        """
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['SYSTEM_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        self.followed.append(Follow(followed=self))

    def __repr__(self):
        """
        Since oauth implementation requires that current_user() returns the user,
        i decided to let the user object return int self.
        so for if a current_user object ist initialized, it still behaves like its not!

        :return: User Object
        """
        return self

    @property
    def password(self):
        """only raises an error if someone tries to read the pw (which is not stored)

        :return: AttributeError
        """
        raise AttributeError('Password is not a Readable Attribute')

    @password.setter
    def password(self, password):
        """
        .. function::
            sets password for user

        :param password: Password String
        :return:
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        .. function::
            checks the password against the stored hash
            :param password:
            :return: True if match, False if not
        """
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        """
        :param expiration:
        .. function::
            creates json web signatures
        :return: serialized json
        """
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        """
        .. function::
        verifies the token and checks if the user is logged in

        :param token: the token from generate_confirmation_token
        :return: True if okay, else False
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_token(self, expiration=3600):
        """
        Generates a reset Token for auth.views.password_reset_request
        Called by route @auth.route('/reset', methods=['GET', 'POST'])

        :param expiration: Expiration time in seconds default is 3600
        :return: serialized dictionary {'reset': self.id}
        """
        s = Serializer(current_app.config['SECRET_KEY'], int(expiration))
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        """ resets userpassword with the usertoken

        :param token:
        :param new_password:
        :return:
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        """To change an email address needs verification of that new address.

           Therefor this methode generates an token for secondary validation of the user.
           This token expires by default after 3600 seconds.
           this function calls (in return ;-) change_email with that generated validation token.

        :param new_email: new email address
        :param expiration: time until token expires in seconds
        :return: calls change_email with that generated validation token
        """
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        """changes the emailaddress for a current user

        :param token:
        :return:
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        db.session.commit()
        return True

    def can(self, permissions):
        """ this methode returns the actual permissions of an user.

        .. function::
            performs bitwise AND with the User permissions

        :param permissions: permissions as int
        :return: True, if all requested Bits are present in the User role
        """
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        """If the User is Admin this methode returns TRUE
        :return: True if user is admin
        """
        return self.can(Permission.ADMINISTER)

    def ping(self):
        """ ping updates the timestamp of a user ...
        used to do such nice things as last seen at...

        :return: has no return val
        """
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar(self, size=100, default='identicon', rating='g'):
        """This Methode generates a hash that should be uniqe for each user.
        this hash is used to generate an random avatar via gravatar's api.

        :param size: size in pixel
        :param default: type of generated pic
        :param rating:
        :return: returns a url to secure.gravatar.com
        """
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'https://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self, user):
        """
        :param user:
        """
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        """

        :param user:
        """
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self, user):
        """
        :param user:
        :return:
        """
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        """
        :param user:
        :return:
        """
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    def generate_auth_token(self, expiration):
        """

        :param expiration:
        :return:
        """
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        """

        :param token:
        :return:
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])


class AnonymousUser(AnonymousUserMixin):
    """
    class that represents anonymous users.
    not in db.
    """

    def can(self, permissions):
        """Anonymous users cant do shit!

        :param permissions:
        :return: False
        """
        return False

    def is_administrator(self):
        """Anonymous users cant be admins!

        :return: False
        """
        return False


login_manager.anonymous_user = AnonymousUser
"""tells current_user to be an object of AnonymousUser"""


@login_manager.user_loader
def load_user(user_id):
    """
    User loader Callback function

    :param user_id: User Identifier as Unicode String
    :return: User object or None
    """
    return User.query.get(int(user_id))

# we use flask-login's current_user
# def current_user():
# if 'id' in session:
# uid = session['id']
# return User.query.get(uid)
# return None
