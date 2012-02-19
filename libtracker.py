import os
import cgi
import datetime
import urllib
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.ext import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class Location(db.model):
	creator = db.StringProperty #might change this to just be a string
	arrival = db.DateTimeProperty(auto_now_add=True)
	departure = db.DateTimeProperty()	#on display, this will convert to a time of day based on arrival time
	location = db.StringProperty()
	open_seats = db.IntegerProperty()
	other_bros = db.StringProperty(multiline=true)
	notes = db.StringProperty(multiline=true)


def location_key():
	return db.Key.from_path('Location', 'default_key')


class MainPage(webapp.RequestHandler):
	def get(self):
		locations_query = Location.all().ancestor(location_key()).order('-arrival')
		locations = locations_query.fetch(10)
		
		url = self.request.relative_url('add_location')

		template_values = {
			'locations': locations,
			'add_loc_url': url,
		}

		path = os.path.join.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))

class AddLocation(webapp.RequestHandler):
	def post(self):
		location = Location(parent=location_key())
		location.creator = self.request.get('creator')
		duration = timedelta(hours=self.request.get('duration'))
		
		location.departure = datetime.now() + duration
		location.location = self.request.get('location')
		location.open_seats = self.request.get('open_seats')
		location.other_bros = self.request.get('other_bros')
		location.notes = self.request.get('notes')
		location.put()

		self.redirect('/') #TODO this is probably not correct to redirect to original page
