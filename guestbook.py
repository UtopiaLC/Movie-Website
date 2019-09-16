#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_CATEGORY_NAME = 'Action'
flag=True
fflag=True
cflag=True
ctitle=''
cdirector=''
cactor=''
cyear=''
# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def category_key(category_name=DEFAULT_CATEGORY_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('category_name', category_name)


# [START greeting]
class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    title = ndb.StringProperty(indexed=False)
    director = ndb.StringProperty(indexed=False)
    actor1 = ndb.StringProperty(indexed=False)
    actor2= ndb.StringProperty(indexed=False)
    year = ndb.StringProperty(indexed=False)
    duration = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END greeting]


# [START main_page]
class MainPage(webapp2.RequestHandler):
    def get(self):
        global flag, cflag, ctitle, cdirector, cactor, cyear, fflag
        template = JINJA_ENVIRONMENT.get_template('ondex.html')
        self.response.write(template.render())
        flag = True
        cflag = True
        fflag = True
        ctitle=''
        cdirector=''
        cactor=''
        cyear=''
# [END main_page]


# [START guestbook]
class Displaydata(webapp2.RequestHandler):

    def get(self):
        category_name = self.request.get('category_name',
                                          DEFAULT_CATEGORY_NAME)
        greetings_query = Greeting.query(
            ancestor=category_key(category_name.lower())).order(-Greeting.date)
        greetings = greetings_query.fetch()
        template_values = {
            'greetings': greetings,
            'category_name': urllib.quote_plus(category_name),
        }
                                                                          
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
# [END guestbook]

class SearchData(webapp2.RequestHandler):
    
    def get(self):
        erf=True
        global ctitle, cdirector, cactor, cyear, cflag, fflag
        print(ctitle, cdirector, cactor, cyear)
        category_name = self.request.get('category_name',
                                         DEFAULT_CATEGORY_NAME)
        greetings_query = Greeting.query(
            ancestor=category_key(category_name.lower())).order(-Greeting.date)
        greetings = greetings_query.fetch()
        cgree = greetings_query.fetch()
        for greeting in cgree:
            if not ((ctitle.lower() in greeting.title.lower() ) and (cdirector.lower() in greeting.director.lower() ) and ((cactor.lower() in greeting.actor1.lower()) or (cactor.lower() in greeting.actor2.lower())) and (greeting.year.lower() == cyear.lower() or cyear == '')):
                greetings.remove(greeting)
        if greetings == []:
            erf = False
        template_values = {
            'erf': erf,
            'fflag':fflag,
            'cflag':cflag,
            'greetings': greetings,
            'category_name': urllib.quote_plus(category_name),
        }
        template = JINJA_ENVIRONMENT.get_template('sedex.html')
        self.response.write(template.render(template_values))
        ctitle=''
        cdirector=''
        cactor=''
        cyear=''
        cflag=True
        fflag=True

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        global ctitle, cdirector, cactor, cyear, cflag, fflag
        fflag=False
        category_name = self.request.get('category_name',
                                         DEFAULT_CATEGORY_NAME)
        ctitle = self.request.get('title')
        cdirector = self.request.get('director')
        cactor = self.request.get('actor')
        cyear = self.request.get('year')
        if ctitle == '' and cdirector=='' and cactor=='' and cyear=='':
            cflag = False
        else:
            cflag = True
        query_params = {'category_name': category_name}
        self.redirect('/search?' + urllib.urlencode(query_params))


class Guestbook(webapp2.RequestHandler):
    
    def get(self):
        category_name = self.request.get('category_name',
                                          DEFAULT_CATEGORY_NAME)
        template_values = {
                        'flag':flag,
                        'category_name': urllib.quote_plus(category_name),}
        template = JINJA_ENVIRONMENT.get_template('endex.html')
        self.response.write(template.render(template_values))

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        global flag
        category_name = self.request.get('category_name',
                                          DEFAULT_CATEGORY_NAME)
        greeting = Greeting(parent=category_key(category_name.lower()))
        greeting.title = self.request.get('title')
        greeting.director = self.request.get('director')
        greeting.actor1 = self.request.get('actor1')
        greeting.actor2= self.request.get('actor2')
        greeting.year = self.request.get('year')
        greeting.duration = self.request.get('duration')
        flag=True
        if greeting.title=='' or greeting.director=='' or greeting.actor1=='' or greeting.actor2=='' or greeting.year=='' or greeting.duration=='':
                flag=False
        if flag==False:
            query_params = {'category_name': category_name}
            self.redirect('/enter?' + urllib.urlencode(query_params))
        else:
            greeting.put()
            query_params = {'category_name': category_name}
            self.redirect('/?' + urllib.urlencode(query_params))

# [START app]
app = webapp2.WSGIApplication([
                               ('/', MainPage),
                               ('/display', Displaydata),
                               ('/search', SearchData),
                               ('/enter', Guestbook),
                               ], debug=True)
# [END app]
