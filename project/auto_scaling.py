import os
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
import docker
import threading

dockers = docker.from_env()
path=''
#dockers.containers.run-> to run an image
#dockers.containers.get get(id_or_name)
#dockers.containers.list -> docker ps
#dockers.containers.prune prune(filters=None)  Delete stopped containers
#

instance_ip='http://18.215.245.30'
# client=MongoClient("mongodb://mongo:27017/?gssapiServiceName=mongodb")
client = MongoClient('mongodb://127.0.0.1', 27017)

#sudo docker run --link mongo:mongo --net my-network -d -p 8080:80 -e TEAM_ID="CC_189_206_229_232​" users:latest

#adding another container:	docker.containers.run('image',auto_remove=1,detach=1,environment=["TEAM_ID=CC_189_206_229_232​"],links={'mongo':'mongo'},network='my-network',ports={'80/tcp':get_next_port()},publish_all_ports=1)
#removing a container: doc
#update_round_robin()
def get_next_port():
	client = MongoClient('mongodb://127.0.0.1', 27017)
	db=client.container_meta
	col=db.containers
	container_count = col.count({})
	port_alloc = 8000+container_count
	return(port_alloc)

def update_round_robin():
	client = MongoClient('mongodb://127.0.0.1', 27017)
	db=client.container_meta
	col=db.containers
	col.update({"port":8000},{'$set': {'current':1}})
	return

def check_status():
	threading.Timer(10.0, check_status).start()
	client = MongoClient('mongodb://127.0.0.1', 27017)
	print('routine started')
	db=client.container_meta
	col=db.containers

	#{id:}
	print('col done')
	container_counts=db.counts
	print('requests done')
	counts=container_counts.find_one()
	requests=db.requests
	value_required=requests.find_one()
	value_required=value_required['requests']
	print('done',value_required)
	counts=int(counts['counts'])
	print('counts is ',counts)
	value_required=value_required//20+1
	print('value_required',value_required)
	client = docker.from_env()
	# There has to be a database which says the number of containers that are running.
	#Let that be variable c
	while(value_required>counts):
		#adding containers
		port_allocated=get_next_port()
		new_container=client.containers.run('cc_acts_web',detach=1,environment=["TEAM_ID=CC_189_206_229_232​"],links={'mongo':'mongo'},network='my-network',ports={'80/tcp':port_allocated})
		print('finished adding and the id is',new_container.id)
		counts+=1
		col=db.containers


		col.insert_one({'id':new_container.id,'current':0,'port':port_allocated})
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
		container_remove.stop(timeout=1)
		client.containers.prune()
		print('finished removing')
		col.delete_one({'port':container_to_be_removed})
		counts-=1
	#requests collections are of type {'counts':<value_of_counts>}
	#update c in the database to the value of k
	container_counts.update_one({},{'$set':{'counts':counts}})

check_status()


