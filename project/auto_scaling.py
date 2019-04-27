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
client = MongoClient('mongo', 27017)

#sudo docker run --link mongo:mongo --net my-network -d -p 8080:80 -e TEAM_ID="CC_189_206_229_232​" users:latest

#adding another container:	docker.containers.run('image',auto_remove=1,detach=1,environment=["TEAM_ID=CC_189_206_229_232​"],links={'mongo':'mongo'},network='my-network',ports={'80/tcp':get_next_port()},publish_all_ports=1)
#removing a container: doc
#update_round_robin()
def get_next_port():
	container_count = col.count({})
	port_alloc = 8000+container_count
	return(port_alloc)

def update_round_robin():
	col.update({"port":8000},{'$set': {'current':1}})
	return

def check_status():
	threading.Timer(120.0, check_status).start()
    client = MongoClient('mongo', 27017)

	db=client.container_meta
	col=db.containers
	#{id:}
	requests=db.counts
	counts=requests.find()
	counts=counts[0]
	value_required=counts//20+1
	# There has to be a database which says the number of containers that are running.
	#Let that be variable c
	while(value_required>counts):
		#adding containers
		port_allocated=get_next_port()
		new_container=docker.containers.run('image',auto_remove=1,detach=1,environment=["TEAM_ID=CC_189_206_229_232​"],links={'mongo':'mongo'},network='my-network',ports={'80/tcp':port_allocated},publish_all_ports=1)
		counts+=1
		col.insert_one({'id':new_container,'current':0,'port':port_allocated})
	while(value_required<counts):
		#removing containers
		container_present=list(col.find()['port'])
		container_to_be_removed=max(container_present)
		current_val=col.find_one({'port':container_to_be_removed})['current']
		if(current_val==1):
			update_round_robin()
		id_of_container=col.find({'port':container_to_be_removed})['id']
		container_remove=docker.containers.get(id_of_container)
		container_remove.remove(v=1,link=1,force=1)
		counts-=1
	#requests collections are of type {'counts':<value_of_counts>}
	#update c in the database to the value of k
	requests.update_one({},{'$set':{'counts':counts}})

check_status()


