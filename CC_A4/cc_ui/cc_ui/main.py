from flask import Flask, render_template,request, redirect, url_for,session
from werkzeug.utils import secure_filename
from hashlib import sha1
import os 
import pandas as pd
import datetime
import requests
import json
import datetime
import base64
import random

# FLASK_PATH = '/Users/malaika/Desktop/CC_A2/static/'

FLASK_PATH='/home/ubuntu/CC_A2/CC_A2/static/'
app= Flask(__name__)
app.secret_key = 'any random string'

# api_url='http://127.0.0.1:2000/'
# api_url='http://3.81.102.242/'

api_acts_url = 'http://3.81.102.242:80/'
api_users_url = 'http://3.1.10.242:80/'


@app.route('/', methods=['GET','POST'])
def enterSite():
	# r = requests.get(api_url+'api/v1/categories')
	# categories = json.loads(r.text)
	try:
		if(session['username']):
			session.pop('username', None)
	except:
		pass
	if(request.method=='POST'):
		if(request.form['btn']=='login'):
			pwd_sha1 = sha1(request.form['password'].encode())
			r = requests.post(api_users_url+'api/v1/users/authenticate',json={"username":request.form['username'],"password":pwd_sha1.hexdigest()})
			if(r.status_code==200):
				session['username']=request.form['username']
				return(redirect(url_for('dbUpdate')))
			else:
				return(render_template("index.html"))

		else:
			pwd_sha1 = sha1(request.form['password'].encode())
			r = requests.post(api_users_url+'api/v1/users',json={"username":request.form['username'],"password":pwd_sha1.hexdigest()})
			if(r.status_code==201):
				session['username']=request.form['username']
				return(redirect(url_for('dbUpdate')))
			else:
				return(render_template("index.html"))
	return(render_template("index.html"))



@app.route('/feed', methods=['GET','POST','DELETE'])
def dbUpdate():
	r = requests.get(api_acts_url+'api/v1/categories')
	categories = json.loads(r.text)

	r= requests.get(api_acts_url+'api/v1/categories/feed/acts')
	posts = json.loads(r.text)
	posts.reverse()

	# print(request.method)
	if(request.method=='POST'):
		try:
			if(request.form['btn']=='add_cat'):
				r = requests.post(api_acts_url+'api/v1/categories',json=[request.form['category']])
				return(render_template("alerts.html",userid=session['username'],status_code=r.status_code,act=1,categories=categories,posts=posts))
			
			if(request.form['btn']=='rem_cat'):
				url_format = 'api/v1/categories/{}'.format(request.form['category'])
				r = requests.delete(api_acts_url+url_format)
				return(render_template("alerts.html",userid=session['username'],status_code=r.status_code,act=2,categories=categories,posts=posts))
			
			if(request.form['btn'] == 'upload'):
				url_format = '/api/v1/acts'
				timestamp = datetime.datetime.now().strftime("%d-%m-%Y:%S-%M-%H")
				img = base64.b64encode(request.files['image'].read()).decode('utf-8')
				caption = request.form['caption']
				tag = request.form['category']
				actId = random.randint(1,102931)
				request_body={"actId":actId,"username":session['username'],"timestamp":timestamp,"caption":caption,"categoryName":tag,"imgB64":img}
				r = requests.post(api_acts_url+'api/v1/acts',json=request_body)
				return(redirect(url_for('dbUpdate')))
				
			# if(request.form['btn']== 'signout'):
			# 	session.pop('username', None)
			# 	return(redirect(url_for('enterSite')))

			if(request.form['btn'] == 'unsubscribe'):
				url_format='api/v1/users/{}'.format(session['username'])
				session.pop('username', None)
				r = requests.delete(api_users_url+url_format)
				return(redirect(url_for('enterSite')))
		except Exception as e:
			print(e)
			if(request.form['btn_del']):
				url_format = 'api/v1/users/acts/check_act'
				r = requests.post(api_acts_url+url_format,json={"actId":int(request.form['btn_del']),"username":session['username']})
				if(r.status_code==200):
					url_format='api/v1/acts/{}'.format(request.form['btn_del'])
					del_act = requests.delete(api_acts_url+url_format)
					return(redirect(url_for('dbUpdate')))
				else:
					return(render_template("alerts.html",userid=session['username'],status_code=r.status_code,act=3,categories=categories,posts=posts))

	if(session['username']):
		return(render_template("feed.html",userid=session['username'],categories=categories,posts=posts))

@app.route('/feed/<username>', methods=['GET','POST'])
def updateFeed(username):
	api_format='api/v1/users/acts/{}'.format(username)
	r= requests.post(api_acts_url+api_format)
	if(r.status_code==200):
		posts = json.loads(r.text)
	else:
		posts=[]

	r = requests.get(api_acts_url+api_format)
	categories = json.loads(r.text)

	
	return(render_template("feed.html",userid=session['username'],posts=posts,categories=categories))

	
@app.route('/feed/category/<category>', methods=['GET','POST'])
def catFeed(category):
	print("here")
	api_format='api/v1/categories/{}/acts'.format(category)
	r= requests.get(api_acts_url+api_format)
	if(r.status_code==200):
		posts = json.loads(r.text)
	else:
		posts=[]

	r = requests.get(api_acts_url+'api/v1/categories')
	categories = json.loads(r.text)

	print(posts)
	
	return(render_template("feed.html",userid=session['username'],posts=posts,categories=categories))


if __name__ == '__main__':
	#app.run(host='0.0.0.0',port=1000,debug = True)
	app.run(debug=True)