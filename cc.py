from flask import Flask, render_template,request, redirect, url_for
import constants
from werkzeug.utils import secure_filename
import os 
import pandas as pd
import datetime

app= Flask(__name__)

def searching():
	print('entered ehre')
	print('entered')
	search=request.args['Search']
	df=pd.read_csv(constants.FLASK_PATH + "/cloud_computing_project/database.csv")
	images=[]
	for i in range(df.shape[0]):
		l=[]
		tags=df['tags'][i]
		if(';' in tags):
			tags=tags.split(';')
		else:
			tags=[tags]
		l_tags=[]
		for j in tags:
			l_tags.append(j)
			if(search==j.strip()):
				img_path = df['image_src'][i].split('static/')[1]
				l.append(img_path)
				l.append(df['caption'][i])
				l.append(l_tags)
				images.append(l)
				break
	return(render_template("feed.html",images=images))

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


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
		print(filename)
		src = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		print(src)
		time1=datetime.datetime.now()
		src = constants.FLASK_PATH + '/cloud_computing_project/'+src
		file.save(src)
		#return render_template("upload.html", filename="../"+src)

		likes=0
		df=pd.read_csv(constants.FLASK_PATH + "/cloud_computing_project/database.csv")
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
		df.to_csv(constants.FLASK_PATH + "/cloud_computing_project/database.csv",index=False)
		return(render_template("upload.html", filename=filename))
	elif('Search' in request.args):
		return searching()
		#print(search)
	return(render_template("upload.html"))


@app.route('/feed')
def display_grid():
	#images=os.listdir('static')
	if('Search' not in request.args): 
		df=pd.read_csv(constants.FLASK_PATH + "/cloud_computing_project/database.csv")
		images=[]
		tags=[]
		for i in range(0,len(df)):

			l=[]
			l.append((df.loc[df.index[i],"image_src"]).split('static/')[1])
			print(l[0])
			l.append(df.loc[df.index[i],'caption'])
			tag_1=df.loc[df.index[i],'tags']
			l_tags=[]
			if(';' in tag_1):
				tag_1=tag_1.split(';')
				for j in tag_1:
					l_tags.append(j)
			else:
				l_tags.append(tag_1)
			l.append(l_tags)

			images.append(l)
		return(render_template("feed.html",images=images,tags=tags))
	else:
		return searching()


@app.route('/tag', methods=['GET','POST'])
def tag_feed():
	if(request.method=='POST'):
		tags=request.form['tags']
		search=tags
		df=pd.read_csv(constants.FLASK_PATH + "/cloud_computing_project/database.csv")
		images=[]
		for i in range(df.shape[0]):
			l=[]
			tags=df['tags'][i]
			if(';' in tags):
				tags=tags.split(';')
			else:
				tags=[tags]
			l_tags=[]
			for j in tags:
				l_tags.append(j)
				if(search==j.strip()):
					img_path = df['image_src'][i].split('static/')[1]
					l.append(img_path)
					l.append(df['caption'][i])
					l.append(l_tags)
					images.append(l)
					break
		return(render_template("feed.html",images=images))

@app.route('/delete/<img_source>')
def delete_images(img_source=""):
	img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_source)
	full_path = constants.FLASK_PATH + '/cloud_computing_project/'+img_path
	print("Image Path ", img_path)
	os.remove(full_path)
	df = pd.read_csv(constants.FLASK_PATH + "/cloud_computing_project/database.csv")
	df = df[~df.image_src.str.contains(str(img_path))]
	df.to_csv(constants.FLASK_PATH + "/cloud_computing_project/database.csv", sep=',', encoding='utf-8', index=False)
	return redirect(url_for('display_grid'))


if __name__ == '__main__':
	app.run(debug = True)
