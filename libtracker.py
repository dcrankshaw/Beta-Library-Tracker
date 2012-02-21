import os
import cgi
import datetime
import urllib
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class Location(db.Model):
	creator = db.StringProperty #might change this to just be a string
	arrival = db.DateTimeProperty(auto_now_add=True)
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
		for loc in locations:
			if loc.departure > datetime.now:
				currentlocs.add(loc)

		url = self.request.relative_url('add_loc')

		template_values = {
			'locations': currentlocs,
			'add_loc_url': url,
		}
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))


class ProcessLocation(webapp.RequestHandler):
	def post(self):
		location = Location(parent=location_key())
		location.creator = self.request.get('creator')
		duration = timedelta(hours=self.request.get('duration'))
		
		location.departure = datetime.now() + float(duration)
		location.location = self.request.get('location')
		location.open_seats = self.request.get('open_seats')
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











