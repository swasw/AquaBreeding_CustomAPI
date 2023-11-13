from flask import Response, request
from fishapiv4.database.models import DailyWaterQuality, Pond, PondActivation
from bson.objectid import ObjectId
from bson.json_util import dumps
from flask_restful import Resource
import datetime
import json
from ...database import db
from ...database import db
collection_name = 'daily_water_quality'
class DailyWaterQualitysApi(Resource):
    def get(self):
        try:
            pipeline = [
                {"$sort": {"created_at": -1}},
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
                    "ph_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {
                                        "case": {"$lt": ["$ph", 6]},
                                        "then": "berbahaya"
                                    },
                                    {
                                        "case": {"$gt": ["$ph", 8]},
                                        "then": "berbahaya"
                                    }
                                ],
                                "default": "normal"
                            }
                    },
                    "do_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {
                                        "case": {"$or": [
                                            {"$lt": ["$do", 3]},
                                            {"$gt": ["$do", 7.5]}
                                        ]},
                                        "then": "berbahaya"
                                    },
                                    {
                                        "case": {"$or": [
                                            {"$and": [{"$gte": ["$do", 3]}, {
                                                "$lte": ["$do", 4]}]},
                                            {"$and": [{"$gt": ["$do", 6]}, {
                                                "$lte": ["$do", 7.5]}]}
                                        ]},
                                        "then": "semi berbahaya"
                                    }
                                ],
                                "default": "normal"
                            }
                    }
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}
            ]
            # dailywaterquality = DailyWaterQuality.objects.aggregate(pipeline)
            dailywaterquality = db.aggregate(collection_name, pipeline)
            list_dailywaterqualitys = list(dailywaterquality)
            response = json.dumps(list_dailywaterqualitys, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def post(self):
        try:
            pond_id = request.form.get("pond_id", None)
            pipline=[{"$match":{"_id":pond_id}}]
            pond =db.aggregate('pond',pipline)
            # pond = Pond.objects.get(id=pond_id)
            if pond['isActive'] == False:
                response = {"message": "pond is not active"}
                response = json.dumps(response, default=str)
                return Response(response, mimetype="application/json", status=400)
            pipeline = [
    {"$match": {"pond_id": pond_id, "isFinish": False}},
    {"$sort": {"activated_at": -1}},
    {"$limit": 1}
]
            pond_activation = db.aggregate('pond_activation',pipeline)
            # pond_activation = PondActivation.objects(
            #     pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
            body = {
                "pond_id": ObjectId(pond.id),
                "pond_activation_id": ObjectId(pond_activation.id),
                "ph": int(request.form.get("ph", None)),
                "do": int(request.form.get("do", None)),
                "temperature": int(request.form.get("temperature", None)),
                "dailywater_at": request.form.get("dailywater_at", datetime.datetime.now())
            }
            print(body)
            # if float(request.form.get("ph")) < 6 or float(request.form.get("ph")) > 8:
            #     pond.update(**{"pondPhDesc": "berbahaya", "pondPh": float(request.form.get("ph"))})
            # else:
            #     pond.update(**{"pondPhDesc": "normal", "pondPh": float(request.form.get("ph"))})
            # if float(request.form.get("do")) < 3 or float(request.form.get("do")) > 7.5:
            #     pond.update(**{"pondDoDesc": "berbahaya", "pondDo": float(request.form.get("do"))})
            # elif float(request.form.get("do")) >= 3 and float(request.form.get("do")) <= 4 or float(request.form.get("do")) >= 6 and float(request.form.get("Do")) <= 7.5:
            #     pond.update(**{"pondDoDesc": "semi berbahaya", "pondDo": float(request.form.get("do"))})
            # else:
            #     pond.update(**{"pondDoDesc": "normal", "pondDo": float(request.form.get("do"))})
            # pond.update(**{"pondTemp": float(request.form.get("temperature"))})
            # dailywaterquality = DailyWaterQuality(**body).save()

            collection = db.get_collection('daily_water_quality')
            
            id = collection.insert_one(body)
            response = {
                "message": "success add data daily water quality", "id": id.inserted_id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class DailyWaterQualityApi(Resource):
    def put(self, id):
        try:
            body = request.form.to_dict(flat=True)
            print(body)
            collection = db.get_collection(collection_name)
            macthFilter = {
                "_id" : ObjectId(id)
            }
            updateFilter = {
                "$set" : body
            }
            collection.update_one(macthFilter, updateFilter)
            # DailyWaterQuality.objects.get(id=id).update(**body)
            response = {
                "message": "success change data daily water quality", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def delete(self, id):
        try:
            #dailywaterquality = DailyWaterQuality.objects.get(id=id).delete()
            collection = db.get_collection(collection_name)
            matchfilter={
                "_id" : ObjectId(id)
            }
            collection.delete_one(matchfilter)
            response = {"message": "success delete daily water quality"}
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
                    "ph_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {
                                        "case": {"$lt": ["$ph", 6]},
                                        "then": "berbahaya"
                                    },
                                    {
                                        "case": {"$gt": ["$ph", 8]},
                                        "then": "berbahaya"
                                    }
                                ],
                                "default": "normal"
                            }
                    },
                    "do_desc": {
                        "$switch":
                            {
                                "branches": [
                                    {
                                        "case": {"$or": [
                                            {"$lt": ["$do", 3]},
                                            {"$gt": ["$do", 7.5]}
                                        ]},
                                        "then": "berbahaya"
                                    },
                                    {
                                        "case": {"$or": [
                                            {"$and": [{"$gte": ["$do", 3]}, {
                                                "$lte": ["$do", 4]}]},
                                            {"$and": [{"$gt": ["$do", 6]}, {
                                                "$lte": ["$do", 7.5]}]}
                                        ]},
                                        "then": "semi berbahaya"
                                    }
                                ],
                                "default": "normal"
                            }
                    }
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}
            ]
            # dailywaterquality = DailyWaterQuality.objects.aggregate(pipeline)
            dailywaterquality = db.aggregate('daily_water_quality',pipeline)
            list_dailywaterqualitys = list(dailywaterquality)
            response = json.dumps(list_dailywaterqualitys[0], default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
