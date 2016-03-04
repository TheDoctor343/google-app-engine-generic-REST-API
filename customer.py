import webapp2
import models
import logging
from google.appengine.ext import ndb
import json

class CustomerRoute(webapp2.RequestHandler):
    def get(self):

    	"""
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write("Hello, Customer!")

        logging.info("____")
        logging.info(models.Customer.state)
        logging.info(type(models.Customer.state))
        logging.info("____")
        q = getattr(models.Customer, "state")
        logging.info(q)
        logging.info(type(q))
        t = models.Customer
        qry = t.query(q == "The Moon")
        for customer in qry.iter():
        	logging.info(customer)
        logging.info("____")

        """
        def key_method(KIND, ID, BODY):
        	return ndb.Key("Customer", int(ID))

        obj = models.API_GET(model_type=models.Customer, key_method=key_method, request=self.request, kind="Customer")

        self.response.content_type = 'application/json'
        self.response.out.write(json.dumps(obj))
        

app = webapp2.WSGIApplication([
    ('/customer', CustomerRoute),
], debug=True)