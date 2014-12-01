# -*- coding: utf-8 -*-
# Attitude Poller
# schluchc - 2014-12-01
# schluchter@mailbox.org

import webapp2

from user import APSignup, APLogin, APLogout
from poll import APFront, APPoll, APGuessPoll, APEditPoll
DEBUG = True

POLL_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
application = webapp2.WSGIApplication([(r'/?',                  APFront),
                                       (r'/signup/?',           APSignup),
                                       (r'/login/?',            APLogin),
                                       (r'/logout/?',           APLogout),
                                       (r'/_edit/?' + POLL_RE,  APEditPoll),
                                       (r'/_guess/?' + POLL_RE, APGuessPoll),
                                       (POLL_RE,                APPoll),
                                      ], debug=True)
