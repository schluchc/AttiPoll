# -*- coding: utf-8 -*-
# Attitude Poller
# schluchc - 2014-12-01
# schluchter@mailbox.org

import logging
from google.appengine.ext import db
from google.appengine.api import memcache
from base import BaseHandler, render_str
from user import validateUser, check_secure_val


def poll_key(name = 'default'):
    return db.Key.from_path('polls', name)


def get_cache(poll_name, update=False):
  poll = memcache.get(poll_name)
  if poll is None or update:
    poll = get_db(poll_name)
    if poll is not None:
      memcache.set(poll_name, poll)
  return poll

def get_db(poll_name):
  logging.warning("poll DB read")
  polls = db.GqlQuery("SELECT * FROM PollModel WHERE ANCESTOR IS :1 AND name = :2", poll_key(), poll_name)
  polls = list(polls)
  if len(polls) > 0:
    return polls[0]
  else:
    return None

def get_guesses(poll_name):
  all_guesses = GuessModel.all().order('-created') #"SELECT * FROM BlogPost ORDER BY created DESC limit 10"
  guesses = []

  for guess in all_guesses:
    logging.info("get guesses for pollname%s" % guess.pollname)
    logging.info("guess%s" % guess.guess)
    if guess.pollname == poll_name:
      guesses.append(guess)
  return guesses

class APFront(BaseHandler):
  def get(self):
    polls = PollModel.all().order('-created') #"SELECT * FROM BlogPost ORDER BY created DESC limit 10"

    params = dict()
    params['title'] = "Resultateraten"
    params['header'] = "Wilkommen zum heiteren Resultateraten"
    params['description'] = "Hier kannst du Longchamp spielen"
    params['polls'] = polls

    #username = check_secure_val(self.request.cookies.get('name', ''))
    #if not validateUser(username):
    #  params['error'] = 'you need to login to guess'

    self.render("front.html", **params)

  def post(self):
    logging.info("post new poll")

    username = check_secure_val(self.request.cookies.get('name', ''))
    if not validateUser(username):
      self.redirect('/login')
      return

    poll_name = self.request.get('poll_name')
    if poll_name:
      self.redirect(str(poll_name))
      return
    else:
      logging.error('NEW POLL WITHOUT NAME, FRONT:post')

class APPoll(BaseHandler):
  def get(self, poll_name):
    logging.warning("get poll %s" % poll_name)
    poll = get_cache(poll_name)
    if poll is None:
      logging.info("new poll: %s" % poll_name)
      return self.redirect('/_edit%s' % poll_name)
    else:
      params = dict()
      params['p'] = poll
      params['guesses'] = get_guesses(poll_name)
      self.render("poll.html", **params)

class APGuessPoll(BaseHandler):
  def get(self, poll_name):
    logging.warning("get poll %s" % poll_name)
    poll = get_cache(poll_name)
    if poll is None:
      logging.info("new poll: %s" % poll_name)
      return self.redirect('/_edit%s' % poll_name)
    else:
      params = dict()
      params['p'] = poll
      params['guesses'] = get_guesses(poll_name)
      self.render("pollguess.html", **params)

  def post(self, poll_name):
    logging.info("post poll guess %s" % poll_name)
    content = self.request.get('content')

    if poll_name:
      username = check_secure_val(self.request.cookies.get('name', ''))
      if not validateUser(username):
        self.redirect('../../login')
        return
      guess = float(self.request.get('guess'))
      guess = GuessModel(parent = poll_key(), guess = guess, username = username, pollname=poll_name)
      guess.put()
      self.redirect(poll_name)
      return
    else:
      logging.error('POLL WITHOUT NAME, EditPoll:post')

class APEditPoll(BaseHandler):
  def get(self, poll_name):
    logging.info("get poll edit %s" % poll_name)
    username = check_secure_val(self.request.cookies.get('name', ''))
    if not validateUser(username):
      self.redirect('../../login')
      return
    if poll_name:
      poll = get_cache(poll_name)
      if poll is None:
        poll = PollModel(name = poll_name, content='')
      self.render("polledit.html", p = poll)
    else:
      logging.error('POLL WITHOUT NAME, APEditPoll:get')

  def post(self, poll_name):
    logging.info("post poll edit %s" % poll_name)
    content = self.request.get('content')

    if poll_name:
      poll = PollModel(parent = poll_key(), name = poll_name, content = content)
      poll.put()
      get_cache(poll_name, True)
      self.redirect(poll_name)
      return
    else:
      logging.error('POLL WITHOUT NAME, EditPoll:post')



class PollModel(db.Model):
  name = db.StringProperty(required=True)
  content = db.TextProperty(required=False)
  created = db.DateTimeProperty(auto_now_add = True)
  last_modified = db.DateTimeProperty(auto_now = True)

  def render(self):
    logging.info("render poll %s" % self.name)
    self._render_content = self.content.replace('\n', '<br>')
    return render_str("poll.html", p = self)

class GuessModel(db.Model):
  guess = db.FloatProperty(required=True)
  username = db.StringProperty(required=True)
  pollname = db.StringProperty(required=True)
  created = db.DateTimeProperty(auto_now_add = True)
  last_modified = db.DateTimeProperty(auto_now = True)

  def render(self):
    return render_str("guess.html", g = self)
