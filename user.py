# -*- coding: utf-8 -*-
# Attitude Poller
# schluchc - 2014-12-01
# schluchter@mailbox.org

import re
import hmac
import random
import string
import hashlib
import json
import logging
from datetime import datetime
from google.appengine.ext import db

from base import BaseHandler

secret = 'blu2345-.,197/()' #TODO: move to different file

def validateUser(username):
	USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
	return username and USER_RE.match(username)

def validatePw(password):
	PW_RE = re.compile(r"^.{3,20}$")
	return password and PW_RE.match(password)

def validateVerifyPw(password, verify):
	return password == verify

def validateEmail(email):
	EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
	return not email or EMAIL_RE.match(email)


def make_salt():
	return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(pw, salt=None):
	if not salt:
		salt = make_salt()
	#h = hashlib.bcrypt(pw + salt).hexdigest()
	h = hmac.new(salt, pw, hashlib.sha256).hexdigest()
	return '%s|%s' % (h, salt)

def make_secure_val(s):
    return "%s|%s" % (s, hmac.new(secret, s).hexdigest())

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val




class APSignup(BaseHandler):
	def get(self):
		self.render('signup.html')

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		verify = self.request.get('verify')
		email = self.request.get('email')

		params = dict(username = username,
		              email = email)

		has_error = False

		if not validateUser(username):
			params['error_username'] = "That's not a valid username."
			has_error = True

		if not validatePw(password):
			params['error_password'] = "That's not a valid password."
			has_error = True

		if not validateVerifyPw(password, verify):
			params['error_verify'] = "Your passwords didn't match."
			has_error = True

		if not validateEmail(email):
			params['error_email'] = "That's not a valid email address."
			has_error = True

		if self.user_exists(username):
			params['error_username'] = "Username already exists."
			has_error = True

		if has_error:
			self.render('signup.html', **params)
		else:
			user = User(name=username, pw=str(make_pw_hash(password)))
			user.put()
			self.response.headers.add_header('Set-Cookie', 'name=%s; Path=/' % str(make_secure_val(username)))
			self.redirect('/')

	def user_exists(self, username):
		user = db.GqlQuery("SELECT * FROM User WHERE name = '%s'" % username).get()
		if user:
			return True
		else:
			return False


class APLogin(BaseHandler):
	def get(self):
		self.render('login.html')

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		params = dict()

		if self.valid_login(username, password):
			#TODO: better to just put user id into the cookie
			self.response.headers.add_header('Set-Cookie', 'name=%s; Path=/' % str(make_secure_val(username)))
			self.redirect('/')
		else:
			params['error_login'] = "Invalid login."
			self.render('login.html', **params)

	def valid_login(self, username, password):
		user = db.GqlQuery("SELECT * FROM User WHERE name = '%s'" % username).get()
		if user:
			salt = user.pw.split('|')[1]
			if user.pw == make_pw_hash(password, str(salt)):
				return True
		return False

class APLogout(BaseHandler):
	def get(self):
		self.response.headers.add_header('Set-Cookie', 'name=%s; Path=/' % "")
		self.redirect("signup")




class User(db.Model):
	name = db.StringProperty(required = True)
	pw = db.StringProperty(required = True)
