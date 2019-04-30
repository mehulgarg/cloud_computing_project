from flask import Flask,request,jsonify,make_response,Response, redirect
from flask_restful import Resource, reqparse
from pymongo import MongoClient,ReturnDocument
from datetime import datetime
import os
import requests
import json


instance_ip='http://54.172.183.151'

client = MongoClient('localhost', 27017)
db = client.container_meta
col = db.containers


app = Flask(__name__)
app.secret_key = 'any random string'

def get_current_container():
	'''finds the container to which a request must be directed, updates is state to inactive,
	decides which container to try next based on port number, and updates the next container's 
	state to active
	'''

	current_container = col.find_one({"current":1})
	current_port = current_container['port']
	col.update_one({"port":current_port},{'$set': {'current':0}})
	next_port = col.find_one({"port":current_port+1})
	if(next_port):
		col.update_one({"port":current_port+1},{'$set': {'current':1}})
	else:
		col.update_one({"port":8000},{'$set': {'current':1}})

	return(int(current_port))

def get_next_port():
	container_count = col.count({})
	port_alloc = 8000+container_count
	return(port_alloc)

def update_round_robin():
	col.update({"port":8000},{'$set': {'current':1}})
	return

@app.route('/api/v1/categories')
@app.route('/api/v1/acts/upvote')
@app.route('/api/v1/acts')
@app.route('/api/v1/categories/feed/acts')
@app.route('/api/v1/_count')
@app.route('/api/v1/acts/count')
def forward_requests_no_param():
	'''replace the port number with the current container port and forwards the 
	request to that container'''
	url = request.url
	request.url = url.replace(':5000',':{}'.format(get_current_container()))
	print(request.url)
	# return(redirect(request.url))	

@app.route('/api/v1/categories/<category>/acts')
@app.route('/api/v1/categories/<category>')
@app.route('/api/v1/categories/<category>/acts/size')
def forward_requests_param_category(category):
	'''replace the port number with the current container port and forwards the 
	request to that container'''
	url = request.url
	request.url = url.replace(':5000',':{}'.format(get_current_container()))
	print(request.url)
	# return(redirect(request.url))


@app.route('/api/v1/acts/<actId>')
def forward_requests_param_actId(actId):
	'''replace the port number with the current container port and forwards the 
	request to that container'''
	url = request.url
	request.url = url.replace(':5000',':{}'.format(get_current_container()))
	print(request.url)
	# return(redirect(request.url))


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000,debug = True)
