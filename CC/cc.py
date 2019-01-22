from flask import Flask, render_template,request
from werkzeug.utils import secure_filename
import os 
import pandas as pd
import datetime

app= Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET','POST'])
def upload():
	if(request.method=='POST' and request.files['upload']):
		file = request.files['upload']
		username=request.form['username']
		tags=request.form['tags']
		tags=tags.split(',')
		tags=';'.join(tags)
		caption=request.form['caption']
		print(username,tags,caption)
		filename = secure_filename(file.filename)
		src = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		print(src)
		time1=datetime.datetime.now()
		file.save(src)
		likes=0
		df=pd.read_csv('database.csv')
		print(type(df['user_name']))

		print(df.columns)
		#print(len(df.rows))
		print(type(df['time'][0]),)
		content=[username,src,likes,caption,tags,time1]
		#df2=pd.DataFrame(content,columns=df.columns)
		dictionary=dict(zip(df.columns,content))
		print(dictionary)
		df=df.append(dictionary,ignore_index=True)
		df['time'] = df['time'].astype('datetime64[ns]')

		#print(df['time'],type(df['time']))
		df.sort_values(by=['time'],axis=0,inplace=True,ascending=[False])
		df.to_csv('database.csv',index=False)
		return(render_template("upload.html", filename="../"+src))
	elif('Search' in request.args):
		print('entered ehre')
		print('entered')
		search=request.args['Search']
		df=pd.read_csv('database.csv')
		images=[]
		for i in range(df.shape[0]):
			if(search in df['tags'][i]):
				images.append(df['image_src'][i])
		return(render_template("feed.html",images=images))
		#print(search)
	return(render_template("upload.html"))


@app.route('/feed')
def display_grid():
	#images=os.listdir('static')
	df=pd.read_csv('database.csv')
	images=[i.split('static/')[1] for i in df['image_src']]
	images=["../"+os.path.join(app.config['UPLOAD_FOLDER'], file) for file in images]
	return(render_template("feed.html",images=images))


	
app.run(debug=True)