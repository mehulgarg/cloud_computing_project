from flask import Flask, render_template,request
from werkzeug.utils import secure_filename
import os 

app= Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET','POST'])
def upload():
	if(request.method=='POST'):
		file = request.files['upload']
		filename = secure_filename(file.filename)
		src = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		print(src)
		file.save(src)
		return render_template("upload.html", filename="../"+src)
	return	render_template("upload.html")


@app.route('/feed')
def display_grid():
	images=os.listdir('static')
	images=["../"+os.path.join(app.config['UPLOAD_FOLDER'], file) for file in images]
	return render_template("feed.html",images=images)

if __name__ == '__main__':
	app.run(debug = True)