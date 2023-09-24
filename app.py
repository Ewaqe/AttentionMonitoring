import os
from flask import Flask, Response, request, redirect, jsonify, render_template
from werkzeug.utils import secure_filename
from markupsafe import escape

from db import *

UPLOAD_FOLDER = 'static/videos/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET'])
def index():
	return render_template("index.html", value="aaa")

@app.route('/uploadVideo', methods=['POST'])
def upload_video():
	if 'file' not in request.files:
		response = '{"error": "No file part"}'
		return redirect('/', Response=Response(response=response))
	file = request.files['file']
	if file.filename == '':
		response = '{"error": "No video selected for uploading"}'
		return redirect('/', Response=Response(response=response))
	else:
		filename = secure_filename(file.filename)
		videPath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		file.save(videPath)
		
		reportPath = get_report_path()
		
		connection = get_db_connection()
		connection.execute('INSERT INTO videos (videoPath, reportPath) VALUES (?, ?)', (videPath, reportPath))
		connection.commit()
		connection.close()
		
		response = '{"success": "Video successfully uploaded"}'
		return redirect('/videos')

@app.route('/videos', methods=['GET'])
def get_videos():
	query = 'SELECT * FROM videos'
	connection = get_db_connection()
	if 'query' in request.args:
		search_value = '%' + request.args["query"] + '%'
		print(search_value)
		videos = connection.execute(query + ' WHERE videoPath LIKE ?', (search_value,)).fetchall()
	else:
		videos = connection.execute(query).fetchall()
	connection.close()

	videos = [tuple(row) for row in videos]
	response = dict()
	response["videos"] = list()
	for video in videos:
		head, tail = os.path.split(video[2])
		response["videos"].append({"id": video[0], "timestamp": video[1], "videoPath": video[2], "reportPath": video[3], "fileName": tail})

	return render_template('videos.html', response=response)

@app.route('/videos/<int:id>', methods=['GET'])
def get_video(id):
    connection = get_db_connection()
    video = list(connection.execute("SELECT * FROM videos WHERE id = ?", (id,)).fetchone())
    connection.close()
    
    head, tail = os.path.split(video[2])
 
    return render_template('video.html', video=video, file=tail)

	
def get_report_path():
	return 'reports/base.json'
