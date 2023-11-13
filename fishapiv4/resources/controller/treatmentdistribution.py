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
class TreatmentDistributionApi(Resource):
    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            farm_id = str(current_user['farm_id'])

            # Form Request for Treatment 'Berat' and 'Ringan'
            treatment_type = request.form.get("treatment_type", None)
            file = request.files['image']
            theDate = request.form.get('created_at', None)
            description = request.form.get("description", None)

            # image Handling
            if 'image' not in request.files:
                return {"message": "No file detected"}, 400
            if file.filename == '':
                return {"message": "No image selected for uploading"}, 400
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(current_app.config['UPLOAD_DIR'], filename)
                # print(image_path)
                file.save(image_path)
            
            # Hitung jumlah kolam aktif
            active_ponds = Pond.objects(farm_id=farm_id, isActive=True)
            if not active_ponds:
                response = {"message": "No active ponds found"}
                return response, 400
            
            listPondActivation = []
            for pond in active_ponds:
                pond_activation = PondActivation.objects(
                    pond_id=pond.id, isFinish=False).order_by('-activated_at').first()
                pond_id = pond.id

                if treatment_type == "berat":
                    # Form Request 'Berat'
                    fishes = request.form.get("fish", "[]")
                    fishes = json.loads(fishes)

                    bodyTreatment = {
                        "pond_id": pond_id,
                        "farm_id": farm_id,
                        "pond_activation_id": pond_activation.id,
                        "treatment_type": treatment_type,
                        "water_change": 100,
                        "description": request.form.get("description", None),
                    }
                    # pondtreatment = PondTreatment(**body).save(using=current_app.config['CONNECTION'])

                    for fish in fishes:
                        pond_activation = PondActivation.objects(
                            pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
                        bodyFish = {
                            "pond_id": pond.id,
                            "pond_activation_id": pond_activation.id,
                            "type_log": "deactivation",
                            "fish_type": fish['type'],
                            "fish_amount": fish['amount'],
                            "fish_total_weight": fish['weight']
                        }
                        print(bodyFish)
                        # fishLog = FishLog(**bodyFish).save(using=current_app.config['CONNECTION'])
                    
                    pond_deactivation_data = {
                        "isFinish": True,
                        "total_fish_harvested": request.form.get("total_fish_harvested", None),
                        "total_weight_harvested": request.form.get("total_weight_harvested", None),
                        "deactivated_description": "karantina total"
                    }

                    if theDate != '':
                        bodyTreatment['created_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
                        bodyTreatment['treatment_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
                        pond_deactivation_data['deactivation_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
                    else :
                        three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)
                        bodyTreatment['created_at'] = three_months_ago
                        bodyTreatment['treatment_at'] = three_months_ago
                        pond_deactivation_data['deactivation_at'] = three_months_ago

                elif treatment_type == "ringan":
                    suplemen_id = request.form.get("suplemen_id", None)
                    usage = float(request.form.get("usage", None))

                    bodyTreatment = {
                        "farm_id": farm_id,
                        "pond_activation_id": pond_activation.id,
                        "suplemen_id": suplemen_id,
                        "treatment_type": treatment_type,
                        "usage" : usage,
                        "description": description,
                    }

                    if theDate != '':
                        bodyTreatment['created_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
                    else :
                        three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)
                        bodyTreatment['created_at'] = three_months_ago
                    
                    # print(bodyTreatment)
                    pondtreatment = PondTreatment(**bodyTreatment).save(using=current_app.config['CONNECTION'])

            usage_per_pond = usage / len(active_ponds)
            if treatment_type == "ringan": 
                body = {
                    "farm_id": farm_id,
                    "suplemen_id": suplemen_id,
                    "pond_activation_id": listPondActivation,
                    "usage": usage,
                    "usage_per_pond": usage_per_pond,
                    "image": filename,
                    "description": description
                }
                treatment_distribution = TreatmentDistribution(**body).save(using=current_app.config['CONNECTION'])
                print(listPondActivation)
                return Response(dumps(body), mimetype="application/json", status=200)
            
        except Exception as e:
            print(str(e))
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)