import os
import cgi
import datetime
import urllib
import wsgiref.handlers

from datetime import datetime, timedelta, tzinfo
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class Zone(tzinfo):
	def __init__(self, offset, isdst, name):
		self.offset=offset
		self.isdst=isdst
		self.name=name
	
	def utcoffset(self, dt):
		return timedelta(hours=self.offset) + self.dst(dt)

	def dst(self, dt):
		return timedelta(hours=1) if self.isdst else timedelta(0)

	def tzname(self, dt):
		return self.name


class Location(db.Model):
	name = db.StringProperty() #might change this to just be a string
	arrival = db.DateTimeProperty(auto_now_add=True)
#	arrival = db.DateTimeProperty()
	#length_stay = db.FloatProperty()	
	departure = db.DateTimeProperty()	
	#on display, this will convert to a time of day based on arrival time
	location = db.StringProperty()
	open_seats = db.IntegerProperty()
	other_bros = db.StringProperty(multiline=True)
	notes = db.StringProperty(multiline=True)


def location_key():
	return db.Key.from_path('Location', 'default_key')


class MainPage(webapp.RequestHandler):
	def get(self):
		locations_query = Location.all().ancestor(location_key()).order('-arrival')
		locations = locations_query.fetch(10)
		#remove brother entries who have already left
		currentlocs = []
		#EST = Zone(-5, False, 'EST')
		for loc in locations:
			if datetime.utcnow() < loc.departure:
				tzloc = {}
				tzloc['name'] = loc.name
				tzloc['arrival'] = loc.arrival - timedelta(hours=5)
				tzloc['departure'] = loc.departure - timedelta(hours=5)
				tzloc['location'] = loc.location
				tzloc['open_seats'] = loc.open_seats
				tzloc['other_bros'] = loc.other_bros
				tzloc['notes'] = loc.notes
				currentlocs.append(tzloc)

		url = self.request.relative_url('static/addloc.html')

		template_values = {
			'locations': currentlocs,
			'add_loc_url': url,
		}
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))



class ProcessLocation(webapp.RequestHandler):
	def post(self):
		EST = Zone(-5, False, 'EST')
		location = Location(parent=location_key())
	#	location.arrival = datetime.now(EST)	
		location.name = self.request.get('fname')
		duration = timedelta(hours=float(self.request.get('duration')))
#		length_stay = float(self.request.get('duration'))	
		location.departure = datetime.utcnow() + duration
		location.location = self.request.get('location')
		location.open_seats = int(self.request.get('openseats'))
		location.other_bros = self.request.get('other_bros')
		location.notes = self.request.get('notes')
		location.put()

		self.redirect('/') #TODO this is probably not correct to redirect to original page


application = webapp.WSGIApplication([
	('/', MainPage),
	('/results', ProcessLocation)], debug=True)

def main():
	run_wsgi_app(application)


if __name__ == '__main__':
	main()











