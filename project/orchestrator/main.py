#!encoding=utf-8
from flask import Flask,request,jsonify,make_response,Response, redirect
from flask_restful import Api, Resource, reqparse
from pymongo import MongoClient,ReturnDocument
from datetime import datetime
import os
import requests
import json
import docker 
import threading
import math
import time

instance_ip='http://54.172.183.151'

client = MongoClient('localhost', 27017)
db = client.container_meta
col = db.containers

flags=0
app = Flask(__name__)
app.secret_key = 'any random string'
api = Api(app)

def get_current_container():
	current_container = col.find_one({"current":1})
	if(current_container==None):
		col.update_one({"port":8000},{'$set': {'current':1}})
	current_container = col.find_one({"current":1})
	current_port = current_container['port']
	col.update_one({"port":current_port},{'$set': {'current':0}})

	all_containers = col.find()
	i=0
	global flags
	global another
	if(flags==0 and another==1):
		flags=1
		#fault_check()
		threading.Timer(1.0, fault_check).start()
		check_status()
	

	n_cont = all_containers.count()
	while(all_containers[i]['port']!=current_port):
		i+=1

	i = (i+1)%n_cont
	while(all_containers[i]['active']!=1):
		i=(i+1)%n_cont

	next_port = all_containers[i]['port']
	col.update_one({"port":next_port},{'$set': {'current':1}})
	f = open('log.txt','w+')
	f.write(str(current_port))
	return(current_port)



def fault_check():
	threading.Timer(1.0, fault_check).start()
	while True:
		client = MongoClient('mongodb://127.0.0.1', 27017)
		db = client.container_meta
		col = db.containers

		client2 = docker.from_env()

		container_list = list(col.find())
		for i in range(len(container_list)):
			time.sleep(1)
			port_no = col.find()[i]['port']
			port_no = int(port_no)
			active_status = col.find()[i]['active']
			active_status = int(active_status)
			if(active_status==0):
			    continue
			while(1):
				try:
					res = requests.get('http://localhost:'+str(port_no)+'/api/v1/_health')
					break
				except:
					pass
			if(res.status_code == 200):
			    continue
			elif(res.status_code != 200):
				col.update_one({"port":port_no},{'$set': {'active':0}})
				#to replace this container with a new one
				id_of_container=col.find_one({'port':port_no})['id']
				container_remove=client2.containers.get(id_of_container)
				container_remove.kill()
				#container_remove.restart()
				#container_remove.stop(timeout=1)
				time.sleep(5)
				#                client2.containers.prune()
				new_container=client2.containers.run('acts',detach=1,volumes={"/home/ubuntu/project": {"bind": "/home/ubuntu/","mode": "rw"}},environment=["TEAM_ID=CC_189_206_229_232"],links={'mongo':'mongo'},network='my-network',ports={'80/tcp':port_no})
				time.sleep(5)
				print('finished adding and the id is',new_container.id)
				col.update_one({"port":port_no},{'$set': {'id':new_container.id}})
				col.update_one({"port":port_no},{'$set':{'active':1}})
		time.sleep(1)

    
        
threading.Timer(1.0, fault_check).start()

def get_next_port():
	container_count = col.count({})
	port_alloc = 8000+container_count

	return(port_alloc)


def update_round_robin():
	col.update({"port":8000},{'$set': {'current':1}})
	return

def check_status():
	threading.Timer(120.0, check_status).start()

	client = MongoClient('mongodb://127.0.0.1', 27017)
	db=client.container_meta
	col=db.containers
	#f{id:}
	#container_counts=db.counts
	#counts=container_counts.find_one()
	requests=db.requests
	value_required=requests.find_one()
	value_required=value_required['requests']
	counts=col.find({}).count()

	value_required=math.floor(value_required/20)+1
	requests.update_one({},{'$set':{'requests':0}})

	client = docker.from_env()
	# There has to be a database which says the number of containers that are running.
	#Let that be variable c
	while(value_required>counts):
		#adding containers
		port_allocated=get_next_port()
		new_container=client.containers.run('acts',detach=1,volumes={"/home/ubuntu/project": {"bind": "/home/ubuntu/","mode": "rw"}},environment=["TEAM_ID=CC_189_206_229_232​"],links={'mongo':'mongo'},network='my-network',ports={'80/tcp':port_allocated})
		#fp.write('finished adding and the id is'+str(new_container.id))
		counts+=1
		col=db.containers


		col.insert_one({'id':new_container.id,'current':0,'port':port_allocated,'active':1})
	while(value_required<counts):
		#removing containers
		container_present=col.find()
		print('present_container',container_present)
		# container_present=list(container_present['port'])
		all_containers=[]
		for i in container_present:
			all_containers.append(i['port'])
		container_to_be_removed=max(all_containers)
		col=db.containers
		current_val=col.find_one({'port':container_to_be_removed})['current']
		if(current_val==1):
			update_round_robin()
		print('container to be removed')

		id_of_container=col.find_one({'port':container_to_be_removed})['id']
		container_remove=client.containers.get(id_of_container)
		col.update_one({'port':container_to_be_removed},{'$set':{'active':0}})
		container_remove.stop(timeout=1)
		client.containers.prune()
		col.delete_one({'port':container_to_be_removed})
		counts-=1
	#requests collections are of type {'counts':<value_of_counts>}
	#update c in the database to the value of k
	#container_counts.update_one({},{'$set':{'counts':counts}})
another=0

class Route(Resource):
	def delete(self,catch_all):
		
		url = request.url
		if(('/api/v1/_health' not in url) and ('/api/v1/_crash' not in url) and ('api' in url)):
			global another
			another=1
			
		url = url.split('/')
		url[2] = '0.0.0.0:'+str(get_current_container())
		
		url = '/'.join(url)
		resp= requests.delete(url,data = request.get_json())
		if(('/api/v1/_health' not in url) and ('/api/v1/_crash' not in url) and ('api' in url)):
			client = MongoClient('mongodb://127.0.0.1', 27017)
			db=client.container_meta
			req=db.requests
			req.find_one_and_update({} , {'$inc':{'requests':1}})

		return(Response(resp))
		#return(resp.json, resp.status_code, resp.headers.items())
	def get(self,catch_all):
		url = request.url
		if(('/api/v1/_health' not in url) and ('/api/v1/_crash' not in url) and ('api' in url)):
			global another
			another=1
		
		url = url.split('/')
		url[2] = '0.0.0.0:'+str(get_current_container())
		url = '/'.join(url)
		resp= requests.get(url,data = request.get_json())
		if(('/api/v1/_health' not in url) and ('/api/v1/_crash' not in url) and ('api' in url)):
			client = MongoClient('mongodb://127.0.0.1', 27017)
			db=client.container_meta
			req=db.requests
			req.find_one_and_update({} , {'$inc':{'requests':1}})
		return(Response(resp))
		#return(resp.content, resp.status_code, resp.headers.items())
	def post(self,catch_all):
		url = request.url
		if(('/api/v1/_health' not in url) and ('/api/v1/_crash' not in url) and ('api' in url)):
			global another
			another=1
		
		url = url.split('/')
		url[2] = '0.0.0.0:'+str(get_current_container())
		url = '/'.join(url)
		resp= requests.post(url,data = request.get_json())
		if(('/api/v1/_health' not in url) and ('/api/v1/_crash' not in url) and ('api' in url)):
			client = MongoClient('mongodb://127.0.0.1', 27017)
			db=client.container_meta
			req=db.requests
			req.find_one_and_update({} , {'$inc':{'requests':1}})

		return(resp.json, resp.status_code, resp.headers.items())
	def put(self,catch_all):
		url = request.url
		if(('/api/v1/_health' not in url) and ('/api/v1/_crash' not in url) and ('api' in url)):
			global another
			another=1
		
		url = url.split('/')
		url[2] = '0.0.0.0:'+str(get_current_container())
		url = '/'.join(url)
		resp= requests.put(url,data = request.get_json())
		if(('/api/v1/_health' not in url) and ('/api/v1/_crash' not in url) and ('api' in url)):
			client = MongoClient('mongodb://127.0.0.1', 27017)
			db=client.container_meta
			req=db.requests
			req.find_one_and_update({} , {'$inc':{'requests':1}})

		return(Response(resp))
		#return(resp.json, resp.status_code, resp.headers.items())


api.add_resource(Route,'{}<path:catch_all>'.format("/api/v1/"))

if __name__ == '__main__':
	app.run(host='0.0.0.0',port= 80,debug = True)
