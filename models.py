"""
Data-Store Models
and a couple things to basically automatically create an API from a Model
"""
from google.appengine.ext import ndb
import datetime
import json
import logging

#Example
class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Customer(ndb.Model):
 	"""Model for customers"""
 	# String properties
 	company = ndb.StringProperty()
 	address = ndb.StringProperty()
 	city = ndb.StringProperty()
 	state = ndb.StringProperty()
 	zip_code = ndb.StringProperty()

 	#Date Time Properties
 	created_at = ndb.DateTimeProperty(auto_now_add=True)
 	updated_at = ndb.DateTimeProperty(auto_now=True)


class Project(ndb.Model):
 	"""Model for Projects"""
 	# Customer Key
 	customer_id = ndb.KeyProperty()

 	project_name = ndb.StringProperty()

 	created_at = ndb.DateTimeProperty()
 	updated_at = ndb.DateTimeProperty(auto_now=True)


class Task(ndb.Model):
	"""Model for Tasks"""
	# Keys
	project_id = ndb.KeyProperty()

	# Strings
	task_name = ndb.StringProperty()
	user_id = ndb.StringProperty(indexed=True)

	"""
	#GETSOMETHINGWORKING
	So this whole project is crazy; I'm just going to try to get the simplest thing working that's possible"""
	project_name = ndb.StringProperty()
	current_task_note = ndb.StringProperty()
	current_task_duration = ndb.IntegerProperty(default=0)
	current_task_created_at = ndb.DateTimeProperty(auto_now_add=True)
	current_task_updated_at = ndb.DateTimeProperty(auto_now=True)
	current_task_start = ndb.IntegerProperty(default=0)

	# CHANGE
	task_entries = ndb.KeyProperty(repeated=True)

	# Date-Time Properties
	created_at = ndb.DateTimeProperty(auto_now_add=True)
	updated_at = ndb.DateTimeProperty(auto_now=True)

class Task_Entry(ndb.Model):
	"""Model for task entries"""
	# Tasks
	# CHANGE
	#task_ids = ndb.KeyProperty(repeated=True)

	"""!!! I'm not sure what type this property should be!!!"""
	# seconds
	duration = ndb.IntegerProperty()

	note = ndb.StringProperty()

	#Date-Time Properties
	start_time = ndb.DateTimeProperty()
	created_at = ndb.DateTimeProperty()
	updated_at = ndb.DateTimeProperty(auto_now=True)


class User_Model(ndb.Model):
	"""Using the name "User" would almost certainly cause a name conflict"""
	username = ndb.StringProperty()

	"""I'm not storing the password here. Mostly, because I'll be using Google Apps Auth, 
	but also because storing passwords in plaintext is BAD"""
		
	email = ndb.StringProperty()

	# Obligatory Date-Time Properties
	created_at = ndb.DateTimeProperty()
	updated_at = ndb.DateTimeProperty(auto_now=True)


def encode_to_dict(obj):
	"""Encode a data-store model to a dictionary"""
	result = {}

	for attr in dir(obj):
		if not attr.startswith("_") and not callable(getattr(obj,attr)):
			value = getattr(obj, attr)
			if isinstance(value, datetime.datetime):
				value = encode_date_time(value)
			elif isinstance(value, ndb.key.Key):
				value = dict(kind=value.kind(), id=value.id())
			result[attr] = value

	return result


def encode_date_time(dt_obj):
	result = {}

	# get attributes, but only the int ones
	for attr in dir(dt_obj):
		if not attr.startswith("_") and not callable(getattr(dt_obj, attr)):
			value = getattr(dt_obj, attr)
			if isinstance(value, int):
				result[attr] = value

	return result

def prepare_body(obj, key_method):
	"""Takes a decoded JSON object and prepares it for the data-store"""
	for key in obj:
		val = obj[key]
		if isinstance(val, dict):
			if val.get('kind'): # is a key
				val = key_method(kind=val['kind'], ID=val['id'], body=None)
			elif val.get('year'): # is a date-time
				val = datetime.datetime(**val)
	return obj
        	


def API_GET(model_type, key_method, request, kind):
	"""One annoyance: for get: use key=id"""
	result_list = []

	if len(request.params) == 0: # no params, so return all stored objects -> "list mode"
		qry = model_type.query()
		for model in qry.iter():
				result_list.append(encode_to_dict(model))

	else:

		for param in request.params:
			if param == 'key':
				key = key_method(KIND=kind, ID=request.get("key"), BODY=None)
				result_list.append(encode_to_dict(key.get()))
			else:
				qry = model_type.query(getattr(model_type, param) == request.get(param))
				for model in qry.iter():
					result_list.append(encode_to_dict(model))

	#remove duplicates
	unique = []
	seen_id = {}
	for result in result_list:
		ID = result["key"]["id"]
		if not seen_id.get(ID):
			unique.append(result)
			seen_id[ID] = True


	return unique


def API_POST(model_type, key_method, request, kind):
	"""Return Success, Data
	Data is either an error message or the created key"""
	body = json.loads(request.body)

	#key = key_method(kind=kind, body=body, ID=None)

	#if key.get():
	#	return False, "Key already exists"
		# make new object in datastore
	body = prepare_body(obj=body, key_method=key_method)
	model = model_type(**body)

		#model.key = key
	model.put()

	return True, "key"


def API_PUT(model_type, key_method, request, kind):
	"""One pitfall: Whatever attribute defines the unique key CAN be changed by this method;
	these methods I'm creating put the responsibilty on the front end to ensure that
	bad things do not happen
	Return Success, MSg"""

	body = json.loads(request.body)

	if not body.get('key'):
		return False, "Required Arg Key not found"

	key = key_method(kind=body['key']['kind'], ID=body['key']['id'], body=None)

	model = key.get()

	if not model:
		return False, "Object Not Found in DB"
	else:
		del body['key']

		body = prepare_body(obj=body, key_method=key_method)

		for attr in body:
			setattr(model, attr, body[attr])

		model.put()

		return True, "Success"


def API_DELETE(model_type, key_method, request, kind):
	"Takes a 'key' in the query params"
	if request.get('key'):
		ID = request.get('key')

		key = key_method(kind=kind, ID=ID, body=None)

		key.delete()

		return True, "Successfully Deleted"
	else:
		return False, "Object not found"


"""For Now I'm not using Body"""
def Key_Method(kind, ID, body):
	if isinstance(ID, str):
		ID = int(str)
	if kind == 'Task':
		return ndb.Key('Task', ID)
	elif kind == 'Task_Entry':
		return ndb.Key('Task_Entry', ID)





		