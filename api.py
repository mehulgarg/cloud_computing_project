from flask import Flask,request,jsonify,make_response,Response
from flask_restful import Resource, Api
from pymongo import MongoClient
import re

pwd_validate = re.compile(r'\b[0-9a-f]{40}\b')
timestamp_validate = re.compile(r'\b[0-2][0-9]-(0[1-9]|1[0-2])-[0-9][0-9][0-9][0-9]:[0-6][0-9]-[0-6][0-9]-[0-2][0-4]\b')


app = Flask(__name__)
api = Api(app)



class AddUser(Resource):
	def post(self):
		request_json = request.get_json()
		username = request_json['username']
		password = request_json['password']

		client = MongoClient("mongodb://localhost:27017/")
		db = client.sla
		col = db.user

		match = re.match(pwd_validate, password)
		if(col.find_one({"username" : username})==None and match!=None):
			user_id=col.insert_one({"username" : username, "password" : password})
			return(Response(status=201)) #Created

		return(Response(status=400)) #Bad request: password/username error
	
	def get(self):
		'''Method not allowed'''
		return(Response(status=405))

class DelUser(Resource):
	def delete(self, username):
		client = MongoClient("mongodb://localhost:27017/")
		db = client.sla
		col = db.user

		query = {"username" : username}
		if(col.find_one(query)!=None):
			user_id = col.delete_one(query)
			return(Response(status=200)) #Success

		return(Response(status=400)) #Bad request (username not found)
	
	def get(self):
		'''Method not allowed'''
		return(Response(status=405))

	def post(self):
		'''Method not allowed'''
		return(Response(status=405))

class AddCategory(Resource):
	def post(self):
		request_json = request.get_json()
		cat = request_json[0]

		client = MongoClient("mongodb://localhost:27017/")
		db = client.sla
		col = db.categories

		valid_cat = col.find_one({"category":cat})
		if(valid_cat==None):
			cat_id=col.insert_one({"category" : cat, "count" : 0})
			return(Response(status=201)) #Created

		return(Response(status=400)) #Bad request

	def delete(self):
		return(Response(405))

	def get(self):
		client = MongoClient("mongodb://localhost:27017/")
		db = client.sla
		col = db.categories


		records = col.find()
		if(records!=None):		
			keys=[]
			vals=[]
			for record in records:
				keys.append(record['category'])
				vals.append(record['count'])
			response = jsonify(dict(zip(keys,vals)))
			response.status_code=200
			return(response) #Found and returned
		return(Response(204)) #No categories found
		



class DelCategory(Resource):
	def delete(self, category):
		client = MongoClient("mongodb://localhost:27017/")
		db = client.sla
		col = db.categories

		if(col.find_one({"category" : category})!=None):
			cat_id = col.delete_one({"category" : category})
			return(Response(200))

		return(Response(400))

	def get(self,category):
		return(Response(405))
	def post(self,category):
		return(Response(405))

# class AddAct(Resource):
# 	def post(self):
# 		request_json = request.get_json()

# 		print(request_json)
# 		client = MongoClient("mongodb://localhost:27017/")
# 		db = client.sla
# 		posts = db.posts
# 		users = db.users
# 		cat = db.categories



# 		if(posts.find_one({"actID":request_json['actId']})!=None or users.find_one({"username":request_json['username']})==None or 'upvotes' in request_json.keys() or categories.find_one({"category":categoryName})==None or re.match(timestamp_validate, request_json['timestamp']==None)):
# 			return(Response(201))
# 			# try:
# 			# 	img = base64.b64decode(request_json['imgB64'])
# 			# 	posts.insert_one(request_json)
# 			# 	return(201)
# 			# except:
# 			# 	return(Response(400))
# 			# return(Response(400))





api.add_resource(AddUser, '/api/v1/users')
api.add_resource(DelUser, '/api/v1/users/<username>')
api.add_resource(AddCategory, '/api/v1/categories')
api.add_resource(DelCategory, '/api/v1/categories/<category>')
# api.add_resource(AddAct,'/api/v1/acts')


if __name__ == '__main__':
	app.run(debug = True)
