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

class AuthorizedUser(db.Model):
	user = db.UserProperty()
	auth = db.BooleanProperty()

def user_key():
	return db.Key.from_path('AuthorizedUser', 'default')

class Location(db.Model):
	name = db.StringProperty() #might change this to just be a string
	arrival = db.DateTimeProperty(auto_now_add=True)
	creator = db.UserProperty()
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
				fmat = '%I:%M %p'
				tzloc['name'] = loc.name
				arrivetime = loc.arrival - timedelta(hours=5)
				tzloc['arrival'] = arrivetime.strftime(fmat)
				deptime = loc.departure - timedelta(hours=5)
				tzloc['departure'] = deptime.strftime(fmat) 
				tzloc['location'] = loc.location
				tzloc['open_seats'] = loc.open_seats
				tzloc['other_bros'] = loc.other_bros
				tzloc['notes'] = loc.notes
				tzloc['creator'] = loc.creator
				currentlocs.append(tzloc)

		url = self.request.relative_url('static/addloc.html')
		logout = users.create_logout_url("/")
		template_values = {
			'locations': currentlocs,
			'add_loc_url': url,
			'logout_url': logout,	
		}
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))


class ProcessLocation(webapp.RequestHandler):
	def post(self):
		location = Location(parent=location_key())
	#	location.arrival = datetime.now(EST)	
		location.name = self.request.get('fname')
		location.creator = users.get_current_user()
		duration = timedelta(hours=float(self.request.get('duration')))
#		length_stay = float(self.request.get('duration'))	
		location.departure = datetime.utcnow() + duration
		location.location = self.request.get('location')
		location.open_seats = int(self.request.get('openseats'))
		location.other_bros = self.request.get('other_bros')
		location.notes = self.request.get('notes')
		location.put()

		self.redirect('/main') #TODO this is probably not correct to redirect to original page

class AuthenticateUser(webapp.RequestHandler):
	def get(self):
		auth_user_query = AuthorizedUser.all().ancestor(user_key())
		auth_user_query.filter('user = ', users.get_current_user())
		results = auth_user_query.fetch(1) #just need to know whether present or not
		if len(results) > 0:
			if results[0].auth == True:
				self.redirect('/main')
			else:
				self.redirect(users.create_logout_url("/"))
		elif users.is_current_user_admin(): 
				
			authuser = AuthorizedUser(parent=user_key())
			authuser.user = users.get_current_user()
			authuser.auth = True
			authuser.put()
			
			self.redirect('/main')
		else:
			authuser = AuthorizedUser(parent=user_key())
			authuser.user = users.get_current_user()
			authuser.auth = False 
			authuser.put()
			self.redirect(users.create_logout_url("/"))

application = webapp.WSGIApplication([
	('/', AuthenticateUser),
	('/main', MainPage),
	('/results', ProcessLocation)], debug=True)

def main():
	run_wsgi_app(application)


if __name__ == '__main__':
	main()




