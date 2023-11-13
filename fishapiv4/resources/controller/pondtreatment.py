from flask import Response, request, current_app
from fishapiv4.database.models import *
from flask_restful import Resource
import datetime
import json
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from bson.objectid import ObjectId
from dateutil.relativedelta import relativedelta
from ...database import db


class PondTreatmentsApi(Resource):
    @jwt_required()

    def get(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            farm_id = ObjectId(farm)
            
            pipeline = [
                {"$sort": {"created_at": -1}},
                {
                    '$match': {
                        "farm_id": farm_id,
                    }
                },
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$pond_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$pondid']}}},
                        {"$project": {
                            "_id": 1,
                            "alias": 1,
                            "location": 1,
                            "build_at": 1,
                            "isActive": 1,
                        }}
                    ],
                    'as': 'pond'
                }},
                {'$lookup': {
                    'from': 'pond_activation',
                    'let': {"activationid": "$pond_activation_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$eq': ['$_id', '$$activationid']}}},
                        {"$project": {
                            "_id": 1,
                            "isFinish": 1,
                            "isWaterPreparation": 1,
                            "water_level": 1,
                            "activated_at": 1
                        }}
                    ],
                    'as': 'pond_activation'
                }},
                {"$addFields": {
                    "pond": {"$first": "$pond"},
                    "pond_activation": {"$first": "$pond_activation"},
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}
            ]
            pondtreatment = PondTreatment.objects.aggregate(pipeline)
            list_pondtreatments = list(pondtreatment)
            response = json.dumps(list_pondtreatments, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            
            
            treatment_type = request.form.get("treatment_type", None)
            if treatment_type == "berat":
                pond_id = request.form.get("pond_id", None)
                theDate = request.form.get('created_at', None)

                pond = Pond.objects.get(id=pond_id)
                if pond['isActive'] == False:
                    response = {"message": "pond is not active"}
                    response = json.dumps(response, default=str)
                    return Response(response, mimetype="application/json", status=400)
                pond_activation = PondActivation.objects(
                pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
                fishes = request.form.get("fish", "[]")
                fishes = json.loads(fishes)
                body = {
                    "pond_id": pond_id,
                    "farm_id": farm,
                    "pond_activation_id": pond_activation.id,
                    "treatment_type": treatment_type,
                    "water_change": 100,
                    "description": request.form.get("description", None),
                }
                pondtreatment = PondTreatment(**body).save(using=current_app.config['CONNECTION'])
                id = pondtreatment.id
                # update activation and pond
                pond_deactivation_data = {
                    "isFinish": True,
                    "total_fish_harvested": request.form.get("total_fish_harvested", None),
                    "total_weight_harvested": request.form.get("total_weight_harvested", None),
                    "deactivated_description": "karantina total"
                }

                if theDate != '':
                    body['created_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
                    body['treatment_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
                    pond_deactivation_data['deactivation_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
                else :
                    three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)
                    body['created_at'] = three_months_ago
                    body['treatment_at'] = three_months_ago
                    pond_deactivation_data['deactivation_at'] = three_months_ago

                pond_activation = PondActivation.objects(
                    pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
                pond_activation.update(**pond_deactivation_data)
                pond.update(**{"isActive": False, "status": "Panen"})
                for fish in fishes:
            # save fish log
                    data = {
                        "pond_id": pond_id,
                        "pond_activation_id": pond_activation.id,
                        "type_log": "deactivation",
                        "fish_type": fish['type'],
                        "fish_amount": fish['amount'],
                        "fish_total_weight": fish['weight']
                    }
                    # total_fish_harvested += fish['amount']
                    # total_weight_harvested += fish['weight']
                    fishlog = FishLog(**data).save(using=current_app.config['CONNECTION'])
                    print(data)
            elif treatment_type == "ringan":
                theDate = request.form.get('created_at', None)

                body = {
                    "farm_id": farm,
                    "pond_activation_id": request.form.get("pond_activation_id", None),
                    "suplemen_id": request.form.get("suplemen_id", None),
                    "treatment_type": treatment_type,
                    "usage" : request.form.get("usage", None),
                    "description": request.form.get("description", None),
                }
                # get_suplemen_by_prob = SuplemenInventory.objects.get(id=body['suplemen_id'])
                # get_suplemen_by_prob.amount -= float(body['usage'])
                # get_suplemen_by_prob.save(using=current_app.config['CONNECTION'])

                if theDate != '':
                    body['created_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
                     
                else :
                    three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)
                    body['created_at'] = three_months_ago
                    

                pondtreatment = PondTreatment(**body).save(using=current_app.config['CONNECTION'])
                id = pondtreatment.id
            else:
                response = {
                    "message": "treatment type just allow ['ringan','berat']"}
                response = json.dumps(response, default=str)
                return Response(response, mimetype="application/json", status=400)
            response = {
                "message": "success add data pond treatment", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class PondTreatmentApi(Resource):
    def put(self, id):
        try:
            body = request.form.to_dict(flat=True)
            PondTreatment.objects.get(id=id).update(**body)
            response = {
                "message": "success change data pond treatment", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def delete(self, id):
        try:
            # pondtreatment = PondTreatment.objects.get(id=id).delete()
            collection = db.get_collection('pond_treatment')
            matchfilter={
                "_id" : ObjectId(id)
            }
            collection.delete_one(matchfilter)
            response = {"message": "success delete pond treatment"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def get(self, id):
        try:
            pipeline = [
                {'$match': {'$expr': {'$eq': ['$_id', {'$toObjectId': id}]}}},
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$pond_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$pondid']}}},
                        {"$project": {
                            "_id": 1,
                            "alias": 1,
                            "location": 1,
                            "build_at": 1,
                            "isActive": 1,
                        }}
                    ],
                    'as': 'pond'
                }},
                {'$lookup': {
                    'from': 'pond_activation',
                    'let': {"activationid": "$pond_activation_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$eq': ['$_id', '$$activationid']}}},
                        {"$project": {
                            "_id": 1,
                            "isFinish": 1,
                            "isWaterPreparation": 1,
                            "water_level": 1,
                            "activated_at": 1
                        }}
                    ],
                    'as': 'pond_activation'
                }},
                {"$addFields": {
                    "pond": {"$first": "$pond"},
                    "pond_activation": {"$first": "$pond_activation"},
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}
            ]
            pondtreatment = PondTreatment.objects.aggregate(pipeline)
            list_pondtreatments = list(pondtreatment)
            response = json.dumps(list_pondtreatments[0], default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
