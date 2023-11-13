from flask import Response, json, request, current_app, Flask, flash, request, redirect, url_for
import urllib.request
import os
from os.path import join, dirname, realpath
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
class FeedDistributionApi(Resource):
    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            farm_id = str(current_user['farm_id'])
            fish_feed_id = request.form.get("fish_feed_id", None)
            feed_dose = float(request.form.get("feed_dose", None))

            # Hitung jumlah kolam aktif
            pipeline = [
    {"$match": {"farm_id": farm_id, "isActive": True}}
]
            active_ponds =  db.aggregate('pond',pipeline)
            # active_ponds = Pond.objects(farm_id=farm_id, isActive=True)
            if not active_ponds:
                response = {"message": "No active ponds found"}
                return response, 400
            
            dose_per_pond = feed_dose / len(active_ponds)

            UPLOADS_PATH = join(dirname(realpath(__file__)), 'instance/uploads/..')
            # image
            file = request.files['image']
            if 'image' not in request.files:
                return {"message": "No file detected"}, 400
            if file.filename == '':
                return {"message": "No image selected for uploading"}, 400
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # image_path = os.path.join(current_app.config['UPLOAD_DIR'], filename)
                image_path = UPLOADS_PATH
                print(image_path)
                file.save(image_path)

            for pond in active_ponds:
                pipeline = [
    {"$match": {"pond_id": pond_id, "isFinish": False}},
    {"$sort": {"activated_at": -1}},
    {"$limit": 1}
]
                pond_activation = db.aggregate('pond_activation',pipeline)
                # pond_activation = PondActivation.objects(
                #     pond_id=pond.id, isFinish=False).order_by('-activated_at').first()
                bodyEntry = {
                    "pond_id": pond.id,
                    "farm_id": farm_id,
                    "pond_activation_id": pond_activation.id,
                    "fish_feed_id": fish_feed_id,
                    "feed_dose": dose_per_pond,
                }
                # print(bodyEntry)
                # feedhistory = FeedHistory(**bodyEntry).save(using=current_app.config['CONNECTION'])
                collection = db.get_collection('feed_history')
                feedhistory = collection.insert_one(bodyEntry)

            body = {
                "farm_id": farm_id,
                "fish_feed_id": fish_feed_id,
                "pond_activation_id": pond_activation.id,
                "feed_dose": feed_dose,
                "feed_dose_per_pond": dose_per_pond,
                "image": filename,
            }

            # feed_distribution = FeedDistribution(**body).save(using=current_app.config['CONNECTION'])
            collection = db.get_collection('feed_distribution')
            feed_distribution = collection.insert_one(body)
            return Response(dumps(body), mimetype="application/json", status=200)

        except Exception as e:
            print(str(e))
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)