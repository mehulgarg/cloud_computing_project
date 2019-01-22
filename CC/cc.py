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
		#return render_template("upload.html", filename="../"+src)

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
			l=[]
			tags=df['tags'][i]
			if(';' in tags):
				tags=tags.split(';')
			else:
				tags=[tags]
			for j in tags:
				if(search==j.strip()):
					l.append(df['image_src'][i])
					l.append(df['caption'][i])
					l.append(df['tags'][i])
					images.append(l)
					break
		return(render_template("feed.html",images=images))
		#print(search)
	return(render_template("upload.html"))


@app.route('/feed')
def display_grid():
	#images=os.listdir('static')
	df=pd.read_csv('database.csv')
	images=[]
	for i in range(0,len(df)):
		l=[]
		l.append("../"+os.path.join(app.config['UPLOAD_FOLDER'], (df.loc[df.index[i],"image_src"]).split('static/')[1]))
		l.append(df.loc[df.index[i],'caption'])
		l.append(df.loc[df.index[i],'tags'])
		images.append(l)
	return(render_template("feed.html",images=images))


@app.route('/tag', methods=['GET','POST'])
def tag_feed():
	if(request.method=='POST'):
		tags=request.form['tags']
		search=tags
		df=pd.read_csv('database.csv')
		images=[]
		for i in range(df.shape[0]):
			l=[]
			tags=df['tags'][i]
			if(';' in tags):
				tags=tags.split(';')
			else:
				tags=[tags]
			for j in tags:
				if(search==j.strip()):
					l.append(df['image_src'][i])
					l.append(df['caption'][i])
					l.append(df['tags'][i])
					images.append(l)
					break
		return(render_template("feed.html",images=images))
if __name__ == '__main__':
	app.run(debug = True)