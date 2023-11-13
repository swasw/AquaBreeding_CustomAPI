from flask import Response, json, request, current_app, Flask, flash, request, redirect, url_for
import urllib.request
import os
from werkzeug.utils import secure_filename
from fishapiv4.database.models import *
from flask_restful import Resource
from fishapiv4.database.db import db
from bson.json_util import dumps
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity  
from ..helper import * 
from bson.objectid import ObjectId
from ...database import db
class UploadImageApi(Resource):
    def post(self):
        try:
            # image
            file = request.files['image']
            if 'image' not in request.files:
                return {"message": "No file detected"}, 400
            if file.filename == '':
                return {"message": "No image selected for uploading"}, 400
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_DIR'], filename))
            
            return Response('Image ' + str(filename) + ' added', mimetype="application/json", status=200)
        except Exception as e:
            print(str(e))
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)