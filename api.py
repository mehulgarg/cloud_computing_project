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
timestamp_validate = re.compile(r'\b((0[1-9]|[1-2][0-9]|30)-(0[469]|11)-([1-2][0-9][0-9][0-9])|(0[1-9]|[1-2][0-9]|3[0-1])-(0[13578]|1[02])-([1-2][0-9][0-9][0-9])|((0[1-9]|[1-2][0-8])-(02)-([1-2][0-9][0-9][0-9]))|((29)-(02)-([1-2][0-9]([02468][48]|[13579][260])))|((29)-(02)-(1200|1600|2000|2400|2800))):[0-5][0-9]-[0-5][0-9]-[0-2][0-4]\b')


app = Flask(__name__)
api = Api(app)

class Authenticate(Resource):
	def post(self):
		request_json = request.get_json()
		username = request_json['username']
		password = request_json['password']

		client = MongoClient("mongodb://localhost:27017/")
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

		client = MongoClient("mongodb://127.0.0.1:27017/?gssapiServiceName=mongodb")
		db = client.sla
		col = db.users

		match = re.match(pwd_validate, password)
		if(col.find_one({"username" : username})==None and match!=None):
			user_id=col.insert_one({"username" : username, "password" : password})
			return(Response(status=201)) #Created

		return(Response(status=400)) #Bad request: password/username error
	
	def get(self):
		'''Method not allowed'''
		return(Response(status=405))

class ListNumActsForCat(Resource):
	def get(self,category):
		client = MongoClient("mongodb://127.0.0.1:27017/?gssapiServiceName=mongodb")
		db=client.sla
		col=db.categories
		cat = col.find_one({"category":category})
		if(cat!=None):
			response= jsonify(cat['count'])
			response.status_code=200 
			return(response)
		else:
			response= Response()
			response.status_code=204
			return(response)	

	def post(self,category):
		response= Response()
		response.status_code=405
		return(response)

	def delete(self,category):
		response= Response()
		response.status_code=405
		return(response)


class DelUser(Resource):
	def delete(self, username):
		client = MongoClient("mongodb://127.0.0.1:27017/?gssapiServiceName=mongodb")
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

class AddCategory(Resource):
	def post(self):
		request_json = request.get_json()
		cat = request_json[0]

		client = MongoClient("mongodb://127.0.0.1:27017/?gssapiServiceName=mongodb")
		db = client.sla
		col = db.categories

		valid_cat = col.find_one({"category":cat})
		if(valid_cat==None):
			cat_id=col.insert_one({"category" : cat, "count" : 0})
			response=Response()
			response.status_code=201
			return(response)

		response=Response()
		response.status_code=400
		return(response)

	def delete(self):
		response=Response()
		response.status_code=405
		return(response)

	def get(self):
		client = MongoClient("mongodb://127.0.0.1:27017/?gssapiServiceName=mongodb")
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

		response=Response()
		response.status_code=204
		return(response)
		
class DelCategory(Resource):
	def delete(self, category):
		client = MongoClient("mongodb://127.0.0.1:27017/?gssapiServiceName=mongodb")
		db = client.sla
		col = db.categories
		response=Response()

		if(col.find_one({"category" : category})!=None):
			cat_id = col.delete_one({"category" : category})
			response.status_code=200
			return(response)

		response.status_code=400
		return(response)

	def get(self,category):
		response=Response()
		response.status_code=405
		return(response)


	def post(self,category):
		response=Response()
		response.status_code=405
		return(response)

class AddAct(Resource):
	def post(self):
		request_json = request.get_json()

		client = MongoClient("mongodb://127.0.0.1:27017/?gssapiServiceName=mongodb")
		db = client.sla
		posts = db.posts
		users = db.users
		cat = db.categories

		# print(posts.find_one({"actId":request_json['actId']}), users.find_one({"username":request_json['username']}),not('upvotes' in request_json.keys()),cat.find_one({"category":request_json['categoryName']}),re.match(timestamp_validate, request_json['timestamp']))
		# print(request_json['timestamp'])
		response=Response()
		if(posts.find_one({"actId":request_json['actId']})==None and users.find_one({"username":request_json['username']})!=None and not('upvotes' in request_json.keys()) and cat.find_one({"category":request_json['categoryName']})!=None and re.match(timestamp_validate, request_json['timestamp'])!=None):
			try:
				img = base64.b64decode(request_json['imgB64'])
				input_to_mongo=request_json
				file=open('/Users/malaika/Desktop/cloud_computing_project/img_b64/'+str(input_to_mongo['actId'])+'.txt','w')
				file.write(request_json['imgB64'])
				input_to_mongo['imgB64']='/Users/malaika/Desktop/cloud_computing_project/img_b64/'+str(input_to_mongo['actId'])+'.txt'
				input_to_mongo['upvotes']=0
				posts.insert_one(input_to_mongo)
				cat_post =  cat.find_one({"category": request_json['categoryName']})
				update_cat = cat.update(cat_post,{"category": request_json['categoryName'],"count":cat_post['count']+1})
				response.status_code=201
				return(response)
			
			except Exception as e:
				# print('exception: ',e)
				response.status_code=400
				return(response)
			
		response.status_code=400
		return(response)
	def get(self):
		response=Response()
		response.status_code=405
		return(response)


class DelAct(Resource):
	def delete(self, actId):
		client = MongoClient("mongodb://127.0.0.1:27017/?gssapiServiceName=mongodb")
		db = client.sla
		posts = db.posts
		cat = db.categories
	
		act = posts.find_one({'actId':int(actId)})

		if(act!=None):
			act_cat = cat.find_one({"category":act['categoryName']})
			update_cat = cat.update(act_cat, {"category": act_cat['category'],'count':act_cat['count']-1})
			file_name=act['imgB64']
			os.remove(file_name)
			posts.delete_one({"actId":int(actId)})
			response=Response()
			response.status_code=200
			return(response)
		else:
			response=Response()
			response.status_code=400
			return(response)
	def get(self,actId):
		response=Response()
		response.status_code=405
		return(response)

	def post(self,actId):
		response=Response()
		response.status_code=405	
		return(response)

class getAct(Resource):
	def post(self):
		request_json = request.get_json()
		actId=int(request_json['actId'])
		username=request_json['username']
		client = MongoClient("mongodb://127.0.0.1:27017/?gssapiServiceName=mongodb")
		db = client.sla
		posts = db.posts

		r = posts.find_one({"actId":actId,"username":username})
		if(r!=None):
			response=Response()
			response.status_code=200
			return(response)
		else:
			response=Response()
			response.status_code=400
			return(response)

class ListCategory(Resource):
	def get(self,category,startRange=None,endRange=None):
		client = MongoClient("mongodb://127.0.0.1:27017/?gssapiServiceName=mongodb")
		db = client.sla
		col = db.posts
		startRange=request.args.get('start')
		endRange=request.args.get('end')
		record = col.find({"categoryName":category})
		records=copy.deepcopy(record)
		if(startRange!=None and endRange!=None):
			startRange=int(startRange)
			endRange=int(endRange)
			if(records.count()!=0):
				if(records.count()<(endRange-startRange+1) or startRange>endRange or endRange>records.count()):
					response= Response()
					response.status_code=204
					return(response)
				elif(endRange-startRange+1 >100):
					response= Response()
					response.status_code=413
					return(response)
				else:
					records=list(records)
					keys={'actId','username','timestamp','caption','upvotes','imgB64','_id'}
					
					temp={}
					for i in range(len(records)):
						all_k=set(records[i].keys())
						all_k=all_k-keys
						for j in all_k:
							del records[i][j]
						temp[records[i]['_id']]=records[i]

					list1=list(temp.keys())
					list1.sort(reverse=True)
					list1 = list1[startRange-1:endRange]
					final_list = [temp[i] for i in list1]
					for i in range(len(final_list)):
						del final_list[i]['_id']

					for i in final_list:
						final_list[i]['imgB64']=open(final_list[i]['imgB64']).read()

					response=jsonify(final_list)
					response.status_code=200
					return response

			else:
				response= Response()
				response.status_code=204
				return(response)
		else:
			#print(records)
			if(records.count()!=0):
				if(records.count()>100):
					return Response(413)
				else:
					records=list(records)
					keys={'actId','username','timestamp','caption','upvotes','imgB64'}
					for i in range(len(records)):
						all_k=set(records[i].keys())
						all_k=all_k-keys
						for j in all_k:
							del records[i][j]
						records[i]['imgB64']=open(records[i]['imgB64']).read()
					response=jsonify(records)
					response.status_code=200
					return response

			response=Response()
			response.status_code=204
			return response
	def post(self,category,startRange=None,endRange=None):
		response=Response()
		response.status_code=405
		return response

	def delete(self,category,startRange=None,endRange=None):
		response=Response()
		response.status_code=405
		return response

	def put(self,category,startRange=None,endRange=None):
		response=Response()
		response.status_code=405
		return response

class GetFeed(Resource):
	def get(self):
		client = MongoClient("mongodb://127.0.0.1:27017/?gssapiServiceName=mongodb")
		db = client.sla
		col = db.posts

		posts = list(col.find().limit(10))
		response_list=[]
		for i in posts:
			response_dict=i
			response_dict.pop('_id',None)
			url_b64=response_dict['imgB64']
			with open(url_b64,'r') as img:
				response_dict['imgB64']=img.read()
			response_list.append(response_dict)
		response=jsonify(response_list)
		response.status_code=200
		return(response)

class GetUserFeed(Resource):
	def post(self,username):
		client = MongoClient("mongodb://127.0.0.1:27017/?gssapiServiceName=mongodb")
		db = client.sla
		col = db.posts

		posts = col.find({"username":username})
		if(posts.count()==0):
			response=Response()
			response.status_code=204
			return(response)

		posts = list(posts)
		response_list=[]
		for i in posts:
			response_dict=i
			response_dict.pop('_id',None)
			url_b64=response_dict['imgB64']
			with open(url_b64,'r') as img:
				response_dict['imgB64']=img.read()
			response_list.append(response_dict)
		response=jsonify(response_list)
		response.status_code=200
		return(response)

class UpdateAct(Resource):
	def post(self,actId):
		client = MongoClient("mongodb://127.0.0.1:27017/?gssapiServiceName=mongodb")
		db = client.sla
		col = db.posts

		post = col.find_one_and_update({"actId":int(actId)} , {'$inc':{'upvotes':1}},return_document=ReturnDocument.AFTER)
		response=Response()
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.status_code=200
		return(response)


api.add_resource(GetFeed,'/api/v1/categories/feed/acts')
api.add_resource(ListCategory,'/api/v1/categories/<category>/acts')
api.add_resource(AddUser, '/api/v1/users')
api.add_resource(DelUser, '/api/v1/users/<username>')
api.add_resource(UpdateAct,'/api/v1/acts/update_act/<actId>')
api.add_resource(AddCategory, '/api/v1/categories')
api.add_resource(DelCategory, '/api/v1/categories/<category>')
api.add_resource(AddAct,'/api/v1/acts')
api.add_resource(DelAct, '/api/v1/acts/<actId>')
api.add_resource(ListNumActsForCat,'/api/v1/categories/<category>/acts/size')
api.add_resource(Authenticate,'/api/v1/users/authenticate')
api.add_resource(getAct,'/api/v1/users/acts/check_act')
api.add_resource(GetUserFeed,'/api/v1/users/acts/<username>')



if __name__ == '__main__':
	app.run(host='127.0.0.1',port=2000,debug = True)