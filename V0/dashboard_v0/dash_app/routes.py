"""Routes for main Flask app."""
from flask import render_template, make_response, redirect, request
from flask import current_app as app
from google.cloud import storage
import os
import uuid
import datetime

def upload_blob(bucket_name, content, name):
    """Uploads a file to a bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(name)
    blob.upload_from_string(content)

    return blob.exists()

@app.route('/')
def home():
    """First page."""
    return redirect("/dashapp/", code=302)

@app.route('/upload/', methods=['POST'])
def uploader():
    """Upload helper page."""
    session_id = str(uuid.uuid4())

    content = request.form["content"]
    bucket = os.environ["STORAGE_BUCKET"]
    name = session_id + "_json.json"

    result = upload_blob(bucket, content, name)

    if result:
        response = redirect("/dashapp/", code=302)
        response.set_cookie('sessionID', session_id)
    else:
        response = make_response('''
        <!doctype html>
        <html>
        <head>
            <title>Upload error</title>
        </head>
        <body>
            <h1>You tried to upload a file but something's gone wrong</h1>
            <p>Please, chat to me so we can fix it. email: myshopdash@kutilov.com.au</p>
            <p>Include this: SessionID: {}, ts: {}, content.length: {}, content.type: {}</p>
        </body>
        </html>''').format(session_id, datetime.today(),
                            len(content), type(content))

    return response

#for debug purposes, won't work on production
@app.route('/form/', methods=['GET'])
def form():
    return render_template('form.jinja2')
