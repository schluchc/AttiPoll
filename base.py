# -*- coding: utf-8 -*-
# Attitude Poller
# schluchc - 2014-12-01
# schluchter@mailbox.org

import webapp2
import os
import jinja2
import logging

# enable jinja2 file system loader, note that html-escaping is activated
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
autoescape = True)


def render_str(template, **params):
  t = jinja_env.get_template(template)
  return t.render(params)

class BaseHandler(webapp2.RequestHandler):
  # write html to screen
  # *a: dictionary of all unnamed parameters
  # **kw: dictionary of all named parameters
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  # write html-template to screen
  # template: html template file
  # **kw: dictionary of all named parameters accessed by the template
  def render(self, template, **kw):
    self.write(render_str(template, **kw))
