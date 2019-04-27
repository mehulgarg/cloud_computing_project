from flask import Flask,request,jsonify,make_response,Response
from flask_restful import Resource, Api
from pymongo import MongoClient,ReturnDocument
import re
import base64
from datetime import datetime
from flask_restful import reqparse
import os
import copy
import requests
import json
pwd_validate = re.compile(r'\b[0-9a-f]{40}\b')
timestamp_validate = re.compile(r'\b((0[1-9]|[1-2][0-9]|30)-(0[469]|11)-([1-2][0-9][0-9][0-9])|(0[1-9]|[1-2][0-9]|3[0-1])-(0[13578]|1[02])-([1-2][0-9][0-9][0-9])|((0[1-9]|[1-2][0-8])-(02)-([1-2][0-9][0-9][0-9]))|((29)-(02)-([1-2][0-9]([02468][48]|[13579][260])))|((29)-(02)-(1200|1600|2000|2400|2800))):[0-5][0-9]-[0-5][0-9]-[0-1][0-9]|[2][0-4]\b')

path=''
instance_ip='http://35.174.114.194'
client = MongoClient('mongo', 27017)
db=client.sla
print(db.list_collection_names())
col=db.categories
print(col.distinct('category'))
# client = MongoClient('localhost', 27017)
app = Flask(__name__)
api = Api(app)


class ListNumActsForCat(Resource):
	def get(self,category):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

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
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response= Response()
		response.status_code=405
		return(response)

	def delete(self,category):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response= Response()
		response.status_code=405
		return(response)



class AddCategory(Resource):
	def post(self):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		request_json = request.get_json()
		cat = request_json[0]

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
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response=Response()
		response.status_code=405
		return(response)

	def get(self):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

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
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		col = db.categories
		response=Response()

		if(col.find_one({"category" : category})!=None):
			cat_id = col.delete_one({"category" : category})
			response.status_code=200
			return(response)

		response.status_code=400
		return(response)

	def get(self,category):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response=Response()
		response.status_code=405
		return(response)


	def post(self,category):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response=Response()
		response.status_code=405
		return(response)

class AddAct(Resource):
	def post(self):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		request_json = request.get_json()

		posts = db.posts
		url=instance_ip+':80/api/v1/users'
		print(url)
		r = requests.get(url,allow_redirects=False)
		print('finished')
		r = json.loads(r.text)
		print(r)

		cat = db.categories
		response=Response()
		print(posts.find_one({"actId":request_json['actId']}))
		print(request_json['username'] in r)
		print(not('upvotes' in request_json.keys()))
		print(cat.find_one({"category":request_json['categoryName']})!=None)
		print(re.match(timestamp_validate, request_json['timestamp'])!=None)
		if(posts.find_one({"actId":request_json['actId']})==None and request_json['username'] in r and not('upvotes' in request_json.keys()) and cat.find_one({"category":request_json['categoryName']})!=None and re.match(timestamp_validate, request_json['timestamp'])!=None):
			try:
				img = base64.b64decode(request_json['imgB64'])
				input_to_mongo=request_json
				
				file=open(str(input_to_mongo['actId'])+'.txt','w')
				file.write(request_json['imgB64'])
				input_to_mongo['imgB64']=str(input_to_mongo['actId'])+'.txt'
				input_to_mongo['upvotes']=0
				posts.insert_one(input_to_mongo)
				cat_post =  cat.find_one({"category": request_json['categoryName']})
				update_cat = cat.update(cat_post,{"category": request_json['categoryName'],"count":cat_post['count']+1})
				response.status_code=201
				response.headers['Access-Control-Allow-Origin'] = '*'
				#file=open('/home/ubuntu/flask/cloud_computing_project/check.txt','w')
				file.close()
				return(response)
			
			except Exception as e:
				print('exception: ',e)
				
				response.status_code=400
				return(response)
		print('entered here directly')
		response.status_code=400
		return(response)
	
	def get(self):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response=Response()
		response.status_code=405
		return(response)

	def delete(self):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response=Response()
		response.status_code=405
		return response



class DelAct(Resource):
	def delete(self, actId):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

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
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response=Response()
		response.status_code=405
		return(response)

	def post(self,actId):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response=Response()
		response.status_code=405	
		return(response)

class getAct(Resource):
	def post(self):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		request_json = request.get_json()
		actId=int(request_json['actId'])
		username=request_json['username']

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

	def get(self):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response=Response()
		response.status_code=405
		return response

	def delete(self):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response=Response()
		response.status_code=405
		return response


class ListCategory(Resource):
	def get(self,category,startRange=None,endRange=None):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		col = db.posts
		startRange=request.args.get('start')
		endRange=request.args.get('end')
		record = col.find({"categoryName":category})
		records=copy.deepcopy(record)
		if(startRange!=None and endRange!=None):
			file=open("a.txt","w")
			file.write(str(records.count()))
			file.close()
			
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
					print(temp)
					list1=list(temp.keys())
					list1.sort(reverse=True)
					list1 = list1[startRange-1:endRange]
					final_list = [temp[i] for i in list1]
					for i in range(len(final_list)):
						del final_list[i]['_id']

					for i in range(len(final_list)):
						final_list[i]['imgB64']=open(final_list[i]['imgB64']).read()

					response=jsonify(final_list)
					response.status_code=200
					return response

			else:
				response= Response()
				response.status_code=204
				return(response)
		else:
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
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response=Response()
		response.status_code=405
		return response

	def delete(self,category,startRange=None,endRange=None):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response=Response()
		response.status_code=405
		return response

	def put(self,category,startRange=None,endRange=None):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response=Response()
		response.status_code=405
		return response

class GetFeed(Resource):
	def get(self):
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
	def post(self):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		col = db.posts
		request_json = request.get_json()
		actId=request_json[0]
		post = col.find_one_and_update({"actId":int(actId)} , {'$inc':{'upvotes':1}},return_document=ReturnDocument.AFTER)
		if(post==None):
			response=Response()
			response.headers['Access-Control-Allow-Origin'] = '*'
			response.status_code=400
			return(response)
		response=Response()
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.status_code=200
		return(response)

	def get(self):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response=Response()
		response.status_code=405
		return(response)
	
	def delete(self):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response=Response()
		response.status_code=405
		return(response)


class RequestsCount(Resource):
	def get(self):
		db=client.sla
		counter = db.requestCount.find()[0]['count']

		col = db.requestCount
		response = jsonify([col.find()[0]['count']])
		response.status_code=200 
		return(response)

	def post(self):
		return(Response(status=405))

	def delete(self):
		db=client.sla
		col = db.requestCount
		col.update({},{'count': 0});
		counter =0
		return(Response(status=200))

class ActsCount(Resource):
	def get(self):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		col=db.posts
		a=col.distinct('actId')
		
		response=jsonify([len(a)])
		response.status_code=200
		return(response)

	def post(self):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response= Response()
		response.status_code=405
		return(response)

	def delete(self):
		db=client.sla
		counter = db.requestCount.find()[0]['count']
		counter+=1
		col = db.requestCount
		col.update({},{'count': counter})

		response= Response()
		response.status_code=405
		return(response)



api.add_resource(AddCategory, '/api/v1/categories')
api.add_resource(DelCategory, '/api/v1/categories/<category>')
api.add_resource(ListCategory,'/api/v1/categories/<category>/acts')
api.add_resource(ListNumActsForCat,'/api/v1/categories/<category>/acts/size')
api.add_resource(UpdateAct,'/api/v1/acts/upvote')
api.add_resource(DelAct, '/api/v1/acts/<actId>')
api.add_resource(AddAct,'/api/v1/acts')


api.add_resource(GetFeed,'/api/v1/categories/feed/acts')
api.add_resource(getAct,'/api/v1/users/acts/check_act')
api.add_resource(GetUserFeed,'/api/v1/users/acts/<username>')
api.add_resource(RequestsCount,'/api/v1/_count')
api.add_resource(ActsCount,'/api/v1/acts/count')



	
if __name__ == '__main__':
	app.run(host='0.0.0.0',port=80,debug = True)
	# app.run(debug=True)
