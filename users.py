from flask import Flask,request,jsonify,make_response,Response
from flask_restful import Resource, Api
from pymongo import MongoClient,ReturnDocument
import re
import base64
from datetime import datetime
from flask_restful import reqparse
import os
import copy

pwd_validate = re.compile(r'\b[0-9a-f]{40}\b')
timestamp_validate = re.compile(r'\b((0[1-9]|[1-2][0-9]|30)-(0[469]|11)-([1-2][0-9][0-9][0-9])|(0[1-9]|[1-2][0-9]|3[0-1])-(0[13578]|1[02])-([1-2][0-9][0-9][0-9])|((0[1-9]|[1-2][0-8])-(02)-([1-2][0-9][0-9][0-9]))|((29)-(02)-([1-2][0-9]([02468][48]|[13579][260])))|((29)-(02)-(1200|1600|2000|2400|2800))):[0-5][0-9]-[0-5][0-9]-[0-1][0-9]|[2][0-4]\b')
#timestamp_validate= re.compile(r'\b())
app = Flask(__name__)
api = Api(app)
instance_ip='54.224.139.61'
client=MongoClient("mongodb://mongo:27017/?gssapiServiceName=mongodb")
class Authenticate(Resource):
	def post(self):
		request_json = request.get_json()
		username = request_json['username']
		password = request_json['password']

		db = client.sla
		users = db.users

		response=Response()
		user_doc=users.find_one({"username":username,"password":password})
		if(user_doc!=None):
			response.status_code=200
		else:
			response.status_code=403
		return(response)

class AddUser(Resource):
	def post(self):
		request_json = request.get_json()
		username = request_json['username']
		password = request_json['password']

		db = client.sla
		col = db.users

		match = re.match(pwd_validate, password)
		if(col.find_one({"username" : username})==None and match!=None):
			user_id=col.insert_one({"username" : username, "password" : password})
			return(Response(status=201)) #Created

		return(Response(status=400)) #Bad request: password/username error
	
	def get(self):
		'''Method not allowed'''
		db=client.sla
		col=db.users
		a=col.distinct('username')
		print(a)
		if(len(a)==0):
			response.status_code=204
			return(response)	
		else:
			response= jsonify(a)
			response.status_code=200 
			return(response)

		return(Response(status=405))
class DelUser(Resource):	
	def delete(self, username):
		db = client.sla
		col = db.users

		query = {"username" : username}
		if(col.find_one(query)!=None):
			user_id = col.delete_one(query)
			return(Response(status=200)) #Success

		return(Response(status=400)) #Bad request (username not found)
	
	def get(self,username):
		'''Method not allowed'''
		return(Response(status=405))

	def post(self,username):
		'''Method not allowed'''
		return(Response(status=405))

api.add_resource(AddUser, '/api/v1/users')
api.add_resource(DelUser, '/api/v1/users/<username>')
api.add_resource(Authenticate,'/api/v1/users/authenticate')
if __name__ == '__main__':
	app.run(host='0.0.0.0',port=80,debug = True)