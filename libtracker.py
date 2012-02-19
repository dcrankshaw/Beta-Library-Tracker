import cgi
import datetime
import urllib
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.ext import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class Location(db.model):
	creator = db.StringProperty #might change this to just be a string
	arrival = db.DateTimeProperty(auto_now_add=True)
	duration = db.FloatProperty()	#on display, this will convert to a time of day based on arrival time
	location = db.StringProperty()
	open_seats = db.IntegerProperty()
	other_bros = db.StringProperty(multiline=true)
	notes = db.StringProperty(multiline=true)


def location_key():
	return db.Key.from_path('Location', 'default_key')


class MainPage(webapp.RequestHandler):
	def get(self):
