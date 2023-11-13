from bson import ObjectId
from flask import Response, request, current_app
from fishapiv4.database.models import *
from flask_restful import Resource, reqparse
from fishapiv4.database.db import db
from fishapiv4.resources.helper import getYearToday
import datetime
import json
from bson.json_util import dumps
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from bson.objectid import ObjectId
from dateutil.relativedelta import relativedelta
from ...database import db
from ...database import db
class PondsStatusApi(Resource):
    def get(self):
        pipline = [
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"pondid": "$_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', '$$pondid']},
                    ]}}},
                    {'$lookup': {
                        'from': 'water_preparation',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id', '$$pond_activation_id']}}},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }}
                        ],
                        'as': 'water_preparation'
                    }},
                    {"$addFields": {
                        "water_preparation": {"$first": "$water_preparation"}
                    }},
                    {"$project": {
                        "pond_id": 0,
                        "feed_type_id": 0,
                        "created_at": 0,
                        "updated_at": 0,
                    }}
                ],
                'as': 'pond_activation_list'
            }},
            {"$addFields": {
                "total_activation": {"$size": "$pond_activation_list"},
            }},
            {"$project": {
                "location": 0,
                "shape": 0,
                "material": 0,
                "length": 0,
                "width": 0,
                "diameter": 0,
                "height": 0,
                "image_name": 0,
                "pond_activation_list": 0,
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        ponds = Pond.objects().aggregate(pipline)
        response = list(ponds)
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=200)


class PondStatusApi(Resource):
    def get(self, pond_id):
        pond_objects = Pond.objects.get(id=pond_id)
        pipline = [
            {'$match': {'$expr': {'$eq': ['$_id', {'$toObjectId': pond_id}]}}},
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"pondid": "$_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', '$$pondid']},
                    ]}}},
                    {"$sort": {"activated_at": -1}},
                    # {'$lookup': {
                    #     'from': 'fish_log',
                    #     'let': {"pond_activation_id": "$_id"},
                    #     'pipeline': [
                    #         {'$match': {
                    #             '$expr': {'$and': [
                    #                 {'$eq': ['$pond_activation_id',
                    #                  '$$pond_activation_id']},
                    #                 {'$eq': ['$type_log', 'activation']},
                    #             ]}
                    #         }},
                    #         {"$project": {
                    #             "created_at": 0,
                    #             "updated_at": 0,
                    #         }},
                    #         {"$group": {
                    #             "_id": "$fish_type",
                    #             "fish_type": {"$first": "$fish_type"},
                    #             "fish_amount": {"$sum": "$fish_amount"},
                    #             "fish_total_weight": {"$sum": "$fish_total_weight"}
                    #         }},
                    #         {"$sort": {"fish_type": -1}},
                    #         {"$project": {
                    #             "_id": 0,
                    #         }},
                    #     ],
                    #     'as': 'fish_stock'
                    # }},
                    {'$lookup': {
                        'from': 'fish_grading',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']}
                            }},
                            {"$sort": {"_id": -1}},
                        ],
                        'as': 'list_grading'
                    }},
                    {'$lookup': {
                        'from': 'fish_harvested',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']}
                            }},
                            {"$sort": {"_id": -1}},
                        ],
                        'as': 'list_fish_harvested'
                    }},
                    {"$addFields": {
                        "first_fish_harvested": {"$first": "$list_fish_harvested"},
                    }},
                    {"$addFields": {
                        "fish_harvested": "$first_fish_harvested.fish",
                        "total_fish_harvested": "$first_fish_harvested.total_fish_harvested",
                        "total_weight_harvested": "$first_fish_harvested.total_weight_harvested"
                    }},
                    {"$project": {
                        "list_fish_harvested": 0,
                        # "first_fish_harvested": 0,
                    }},

                    # {'$lookup': {
                    #     'from': 'fish_log',
                    #     'let': {"pond_activation_id": "$_id"},
                    #     'pipeline': [
                    #         {'$match': {
                    #             '$expr': {'$and': [
                    #                 {'$eq': ['$pond_activation_id',
                    #                          '$$pond_activation_id']},
                    #                 {'$eq': ['$type_log', 'DEATH']},
                    #             ]}
                    #         }},
                    #         {"$group": {
                    #             "_id": "$fish_type",
                    #             "fish_type": {"$first": "$fish_type"},
                    #             "fish_amount": {"$sum": "$fish_amount"}
                    #         }},
                    #         {"$sort": {"fish_type": -1}},
                    #         {"$project": {
                    #             "_id": 0,
                    #         }},
                    #     ],
                    #     'as': 'fish_death'
                    # }},
                    # {'$lookup': {
                    #     'from': 'fish_log',
                    #     'let': {"pond_activation_id": "$_id"},
                    #     'pipeline': [
                    #         {'$match': {
                    #             '$expr': {'$and': [
                    #                 {'$eq': ['$pond_activation_id',
                    #                  '$$pond_activation_id']},
                    #                 {'$eq': ['$type_log', 'deactivation']},
                    #             ]}
                    #         }},
                    #         {"$group": {
                    #             "_id": "$fish_type",
                    #             "fish_type": {"$first": "$fish_type"},
                    #             "fish_amount": {"$sum": "$fish_amount"},
                    #             "fish_total_weight": {"$sum": "$fish_total_weight"},
                    #         }},
                    #         {"$sort": {"fish_type": -1}},
                    #         {"$project": {
                    #             "_id": 0,
                    #         }},
                    #     ],
                    #     'as': 'fish_harvested'
                    # }},
                    {'$lookup': {
                        'from': 'feed_history',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                             '$$pond_activation_id']},
                                ]}
                            }},
                        ],
                        'as': 'feed_history'
                    }},
                    {"$addFields": {
                        "fish_live": {"$first": "$list_grading.fish"},
                        "fish_death": [],
                        "fish_harvested": [],
                        "fish_stock": [],
                        "fcr": {"$first": "$list_grading.fcr"},
                        "fcr_update": {"$first": "$list_grading.created_at"},
                        "last_feed_dose": {"$first": "$feed_history.created_at"},
                        "feed_dose": {"$sum": "$feed_history.feed_dose"},
                    }},
                    {"$addFields": {
                        "total_fish": {"$sum": "$fish_live.amount"},
                        "survival_rate": {"$cond": [
                            {"$eq": [{"$sum": "$fish_stock.fish_amount"}, 0]},
                            0,
                            {"$multiply": [{"$divide": [{"$sum": "$fish_live.fish_amount"}, {
                                "$sum": "$fish_stock.fish_amount"}]}, 100]}
                        ]},
                        "weight_growth": {"$subtract": [{"$sum": "$fish_harvested.fish_total_weight"}, {"$sum": "$fish_stock.fish_total_weight"}]},
                    }},
                    {"$project": {
                        "pond_id": 0,
                        "feed_history": 0,
                        "feed_type_id": 0,
                        "list_grading": 0,
                        "created_at": 0,
                        "updated_at": 0,
                    }}
                ],
                'as': 'pond_activation_list'
            }},
            {"$addFields": {
                "total_activation": {"$size": "$pond_activation_list"},
                "pond_activation_list": '$pond_activation_list',

            }},
            {"$project": {
                "location": 0,
                "shape": 0,
                "material": 0,
                "length": 0,
                "width": 0,
                "diameter": 0,
                "height": 0,
                "image_name": 0,
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        ponds = Pond.objects().aggregate(pipline)
        ponds = list(ponds)
        ponds = dict(ponds[0])
        response = json.dumps(ponds, default=str)
        return Response(response, mimetype="application/json", status=200)

class PondActivationDetailApi(Resource):
    def get(self,id, pond):
        # log = FishLog.objects(pond_activation_id=id, type_log="deactivation").first()
        # response = json.dumps(ponds, default=str)
        activation = PondActivation.objects(id=id).first()
        pond_id = ObjectId(pond)
        # pond = Pond.objects(id=pond).first()
        pipline = [
            
            {'$match': {'$expr': {'$eq': ['$_id', pond_id]}}},
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"pondid": "$_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', '$$pondid']},
                    ]}}},
                    {"$sort": {"activated_at": -1}},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'activation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"},
                                "fish_total_weight": {"$sum": "$fish_total_weight"}
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_stock'
                    }},
                    {'$lookup': {
                        'from': 'fish_grading',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']}
                            }},
                            {"$sort": {"_id": -1}},
                        ],
                        'as': 'list_grading'
                    }},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                             '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'death']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"}
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_death'
                    }},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'deactivation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"},
                                "fish_total_weight": {"$sum": "$fish_total_weight"},
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_harvested'
                    }},
                    {'$lookup': {
                        'from': 'feed_history',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                             '$$pond_activation_id']},
                                ]}
                            }},
                        ],
                        'as': 'feed_history'
                    }},
                    {"$addFields": {
                        "last_grading": {"$first": "$list_grading"},
                    }},
                    {"$addFields": {
                        "total_fish": {"$sum": "$fish_live.amount"},
                        "survival_rate": {"$cond": [
                            {"$eq": [{"$sum": "$fish_stock.fish_amount"}, 0]},
                            0,
                            {"$multiply": [{"$divide": [{"$sum": "$fish_live.fish_amount"}, {
                                "$sum": "$fish_stock.fish_amount"}]}, 100]}
                        ]},
                        "weight_growth": {"$subtract": [{"$sum": "$fish_harvested.fish_total_weight"}, {"$sum": "$fish_stock.fish_total_weight"}]},
                        "total_dose": {"$sum": "$feed_history.feed_dose"},
                        # "fcr": {"$sum": {"$divide": [{"$sum": "$fish_live.fish_amount"}, {"$sum": "$fish_stock.fish_amount"}]}},
                    }},
                    {"$addFields": {
                        "fcr": {"$cond": [
                            {"$eq": [{"$sum": "$total_dose"}, 0]},
                            0,
                            {"$sum": {"$divide": [
                                "$weight_growth", "$total_dose"]}}
                        ]},
                    }},
                    {"$project": {
                        "pond_id": 0,
                        "feed_history": 0,
                        "feed_type_id": 0,
                        "created_at": 0,
                        "updated_at": 0,
                    }}
                ],
                'as': 'pond_activation_list'
            }},
            {"$addFields": {
                "total_activation": {"$size": "$pond_activation_list"},
                "pond_activation_list": '$pond_activation_list',

            }},
            {"$project": {
                "location": 0,
                "shape": 0,
                "material": 0,
                "length": 0,
                "width": 0,
                "diameter": 0,
                "height": 0,
                "image_name": 0,
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        ponds = Pond.objects().aggregate(pipline)
        ponds = list(ponds)
        activ = None
        for acti in ponds[0]["pond_activation_list"]:
            # activ = acti["_id"]
            if str(acti["_id"]) == id:
                activ = acti
        if activ == None:
            activ =0
        response =  {
            "id": activation.id,
            "pond_id": pond,
            # "pond_id": activation.pond_id,
            "is_finish": activation.isFinish,
            "water_level": activation.water_level,
            "total_fish_harvested": activation.total_fish_harvested,
            "total_weight_harvested": activation.total_weight_harvested,
            "activation_at": activation.activated_at,
            "deactivation_at": activation.deactivated_at,
            "deactivation_description": activation.deactivated_description,
            "fish_activated": activ["fish_stock"],
            "fish_alive": activ["fish_live"],
            "fish_harvested": activ["fish_harvested"],
            "fish_death": activ["fish_death"]
        }
        response = json.dumps(response, default=str)
        # response = jsonify(activation.__dict__)
        return Response(response, mimetype="application/json", status=200)

class PondActivationApi(Resource):

    def post(self, pond_id):

        def _activationValidation(pond_id , args):
            # pond id validation
            if (pond_id == None):
                raise Exception('Pond_id Tidak boleh kosong')
            pond = Pond.objects(id=pond_id).first()
            if (not pond):
                raise Exception('Pond_id Tidak ditemukan')
            if (pond.isActive == True):
                raise Exception('Pond masih dalam masa budidaya')
            # fish validation
            str_fish_list = args['fish']
            fish_list = json.loads(str_fish_list)
            if (len(fish_list)<1):
                raise Exception('list fish harus lebih dari atau sama dengan 1')
            return

        parser = reqparse.RequestParser()
        parser.add_argument('fish', type=str, required=True, location='form')
        parser.add_argument('water_level', type=str, required=True, location='form')
        parser.add_argument('fish_category', type=str, required=True, location='form')
        
        args = parser.parse_args()
        fish = json.loads(args.fish)
        print(args)
        print(fish)
        print(type(fish))
        _activationValidation(pond_id=pond_id, args=args)
        pond = Pond.objects(id=pond_id).first()
        pipeline_year = {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', {'$toObjectId': pond_id}]},
                        {'$eq': [{'$dateToString': {
                            'format': "%Y", 'date': "$created_at"}}, getYearToday()]},
        ]
        }}}
        list_pond_year = PondActivation.objects.aggregate(pipeline_year)
        list_pond_year = list(list_pond_year)
        id_int = len(list_pond_year) + 1
    
        pondActivationData = {
            "pond_id" : pond,
            "isFinish" : False,
            "fish_type" : fish[0]["type"],
            "fish_category" : args.fish_category,
            "total_fish_added" : fish[0]["amount"],
            "water_level" : args.water_level,
        }
        active_at = request.form.get('active_at')
        print("active_at", active_at)
        if active_at != '':
            pondActivationData['created_at'] = datetime.datetime.strptime(active_at, "%Y-%m-%dT%H:%M:%S.%f %z") 
            pondActivationData['activated_at'] = datetime.datetime.strptime(active_at, "%Y-%m-%dT%H:%M:%S.%f %z") 
        else :
            three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)
            pondActivationData['created_at'] = three_months_ago
            pondActivationData['activated_at'] = three_months_ago
        pondActivation = PondActivation(**pondActivationData).save(using=current_app.config['CONNECTION'])
        print("fish seed id", fish[0]['seed_id'])
        fishObj = Fish.objects.get(id=fish[0]['seed_id'])
        fishObj.update(**{"pond_activation_id": ObjectId(pondActivation.id)})
        # add fish to grading
        fishGradingData = {
            "pond_id" : pond,
            "pond_activation_id" : pondActivation,
            "event" : pondActivation,
            "event_desc" : 'ACTIVATION',
            "fish" : fish,
            "fcr" : 0,
        }
        fishLogData =  {
            "pond_id" : pond,
            "pond_activation_id" : pondActivation,
            "event_id" : pondActivation,
            "type_log" : 'ACTIVATION',
            "fish" : fish,
        }
        if active_at != '':
            fishLogData['created_at'] = datetime.datetime.strptime(active_at, "%Y-%m-%dT%H:%M:%S.%f %z")
            fishGradingData['grading_at'] = datetime.datetime.strptime(active_at, "%Y-%m-%dT%H:%M:%S.%f %z")
            fishGradingData['created_at'] = datetime.datetime.strptime(active_at, "%Y-%m-%dT%H:%M:%S.%f %z") 
            # fishLogData['activated_at'] = datetime.datetime.strptime(active_at, "%Y-%m-%dT%H:%M:%S.%f %z") 
        else :
            three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)
            fishLogData['created_at'] = three_months_ago
            fishGradingData['grading_at'] = three_months_ago
            fishGradingData['created_at'] = three_months_ago
            # fishLogData['activated_at'] = three_months_ago
        print("fishseed", fish[0]['seed_id'])
        # get_seed_by_id = SeedInventory.objects.get(id=fish[0]['seed_id'])
        # print("seed id", get_seed_by_id)
        # print("seed amount", get_seed_by_id.amount)
        # get_seed_by_id.amount -= int(fish[0]['amount'])
        # get_seed_by_id.save(using=current_app.config['CONNECTION'])  
        fishGrading =FishGrading(**fishGradingData).save(using=current_app.config['CONNECTION'])
        fishLog = FishLog(**fishLogData).save(using=current_app.config['CONNECTION'])
        pond.update(isActive=True)

        response = {"message": "success to activation pond"}
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=200)


class PondDeactivationApi(Resource):
    def post(self, pond_id):
        current_user = get_jwt_identity()
        farm = str(current_user['farm_id'])

        def _udpateFishWithNewWeight(fishes, total_fish_harvested, total_weight_harvested):
            newFishes = []
            for fish in fishes:
                fish['amount'] = int(fish['amount'])
                fish['weight'] = float(total_weight_harvested) / int(total_fish_harvested)
                newFishes.append(fish)
            return newFishes

        def _getTotalWeightFromListFishLastGrading(listFish):
                totalWeight = 0
                for fish in listFish:
                    print("fishweight", fish['weight'])
                    print("fishamount", fish['amount'])
                    weight = float(fish['amount'])*float(fish['weight'])
                    totalWeight += weight
                return totalWeight
        
        def _getFcr(pond_activation,total_weight_harvested):
            last_grading_activation = FishGrading.objects(pond_activation_id=pond_activation.id).order_by('-grading_at').first()
            print("last grading", last_grading_activation.fish)
            date_last_grading_activation = last_grading_activation.grading_at
            print("date last grading activation", date_last_grading_activation)
            date_now = datetime.datetime.now()
            print("date now", date_now)
            total_feed_dose_before_last_grading = FeedHistory.objects(
                pond_activation_id=pond_activation.id,
                feed_history_time__lt=date_last_grading_activation
            ).sum('feed_dose')
            total_feed_dose_before_now = FeedHistory.objects(
                pond_activation_id=pond_activation.id,
                feed_history_time__lt=date_now
            ).sum('feed_dose')
            print("total feed dose before last grading", total_feed_dose_before_last_grading)
            print("total feed dose before now", total_feed_dose_before_now)
            diff_feed_dose = total_feed_dose_before_now-total_feed_dose_before_last_grading
            total_fish_weight_last_grading = _getTotalWeightFromListFishLastGrading(list(last_grading_activation.fish))
            total_fish_weight_now = total_weight_harvested
            diff_fish_weight = float(total_fish_weight_now) - total_fish_weight_last_grading
            print("total fish weight last grading", total_fish_weight_last_grading)
            print("total fish weight now", total_fish_weight_now)
            print("diff feed dose", diff_feed_dose)
            print("diff fish weight", diff_fish_weight)
            fcr = diff_feed_dose / diff_fish_weight
            print("fcr", fcr)
            return fcr

        pond = Pond.objects.get(id=pond_id)
        if pond.isActive == False:
            response = {"message": "status pond is already not active"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        # get last pond_activation
        pond_activation = PondActivation.objects(
            pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
        fishes = request.form.get("fish", "[]")
        fishes = json.loads(fishes)
        print("fishes", fishes)
        total_fish_harvested = request.form.get("total_fish_harvested", None)
        sample_weight = request.form.get("sample_weight", None)
        sample_amount = request.form.get("sample_amount", None)
        sample_long = request.form.get("sample_long", None)
        total_weight_harvested = request.form.get("total_weight_harvested", None)
        deactive_at = request.form.get('deactive_at')
        print("active_at", deactive_at)
        newFishes = _udpateFishWithNewWeight(fishes,total_fish_harvested,total_weight_harvested)
        fcr = _getFcr(pond_activation=pond_activation,total_weight_harvested=total_weight_harvested)
        # return fish to stock

        seedInventoryData = {
                "farm_id": farm,
                "fish_seed_category": "Pembesaran",
                "fish_type": fishes[0]['type'],
                "brand_name": request.form.get('brand_name', None),
                "amount": fishes[0]['amount'],
                "weight": fishes[0]['weight'],
                "width": request.form.get('width', None),
                "price": request.form.get('price', None),
                "total_price": request.form.get('total_price', None),
                "image": request.form.get('image', None)
        }
        collection = db.get_collection('seed_inventory')
        id = collection.insert_one(seedInventoryData)
        # save fish harvested
        fishHarvestedData = {
            "pond_id" : pond,
            "pond_activation_id" : pond_activation,
            "fish" : fishes,
            "fcr" : fcr,
            "total_weight_harvested" : total_weight_harvested,
            "total_fish_harvested" : total_fish_harvested,
        }
        if deactive_at != '':
            fishHarvestedData['harvested_at'] = datetime.datetime.strptime(deactive_at, "%Y-%m-%dT%H:%M:%S.%f %z")
            fishHarvestedData['created_at'] = datetime.datetime.strptime(deactive_at, "%Y-%m-%dT%H:%M:%S.%f %z")
            # fishLogData['activated_at'] = datetime.datetime.strptime(active_at, "%Y-%m-%dT%H:%M:%S.%f %z") 
        else :
            three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)
            fishHarvestedData['harvested_at'] = three_months_ago
            fishHarvestedData['created_at'] = three_months_ago
        fishHarvested = FishHarvested(**fishHarvestedData).save(using=current_app.config['CONNECTION'])
        # save fish grading
        fish_gradingData = {
            "pond_id" : pond,
            "pond_activation_id" : pond_activation,
            "event" : fishHarvested,
            "event_desc" : 'DEACTIVATION',
            "fish" : fishes,
            "fcr" : fcr,
            "sample_amount" : total_fish_harvested,
            "sample_weight" : total_weight_harvested,
            "sample_long" : sample_long,
        }
       
        if deactive_at != '':
            fish_gradingData['grading_at'] = datetime.datetime.strptime(deactive_at, "%Y-%m-%dT%H:%M:%S.%f %z")
            fish_gradingData['created_at'] = datetime.datetime.strptime(deactive_at, "%Y-%m-%dT%H:%M:%S.%f %z")
            # fishLogData['activated_at'] = datetime.datetime.strptime(active_at, "%Y-%m-%dT%H:%M:%S.%f %z") 
        else :
            three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)
            fish_gradingData['grading_at'] = three_months_ago
            fish_gradingData['created_at'] = three_months_ago
        fish_grading = FishGrading(**fish_gradingData).save(using=current_app.config['CONNECTION'])
        # update activation
        pond_activation.update(
            isFinish=True,
            deactivated_at = request.form.get("deactivated_at", datetime.datetime.now()),
        )
        # updat pond
        pond.update(
            isActive = False
        )

        response = {"message": "success to deactivation pond", "id" : fishHarvested.id}
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=200)

class GetPricesApi(Resource):
    @jwt_required()
    def get(self, activation_id):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            farm_id = ObjectId(farm)
            print("farm_id", farm_id)
            ## get list of active ponds
            active_pond_pipeline = [
                {"$sort": {"status": 1,"alias": 1}},
                {"$match": {"farm_id": farm_id, "isActive": True}},]
            # active_pond = Pond.objects(isActive=True)
            active_pond = Pond.objects.aggregate(active_pond_pipeline)
            list_active_ponds = list(active_pond)
            total_active_pond = len(list_active_ponds)
            start_date = datetime.datetime.strptime(request.args.get('start_date'), '%Y-%m-%d') if request.args.get('start_date') else datetime.datetime.strptime("2023-01-01", '%Y-%m-%d')
            
            end_date = datetime.datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + datetime.timedelta(days=1) if request.args.get('end_date') else datetime.datetime.strptime("2030-01-01", '%Y-%m-%d')
            type = request.args.get('type') if request.args.get('type') else ""

  ## get seed price
            pipeline = [
                        {
                            "$lookup":
                            {
                                "from": "pond_activation",
                                "localField": "pond_activation_id",
                                "foreignField": "_id",
                                "as": "view",
                            },
                        },
                        {
                            "$match":
                            {
                                "pond_activation_id": {
                                "$exists": True,
                                },
                            },
                        },
                        {
                            "$unwind":
                            {
                                "path": "$view",
                                "includeArrayIndex": "string",
                                "preserveNullAndEmptyArrays": False,
                            },
                        },
                        {
                            "$project": {
                            "pond_activation_id": 1,
                            "amount": 1,
                            "price": 1,
                            "brand_name": 1,
                            "view.total_fish_added": 1,
                            "result": {
                                "$subtract": [
                                "$amount",
                                "$view.total_fish_added",
                                ],
                            },
                            "type": "Benih",
                            },
                        },
                        {
                            "$addFields": {
                            "newPrice": {
                                "$multiply": ["$result", "$price"],
                            },
                            },
                        },
                        {
                            "$project":
                            {
                                "price": 0,
                                "view": 0,
                                "result": 0,
                            },
                        },
                        {
                            "$addFields":
                            {
                                "fish_id": "$_id",
                            },
                        },
                        {
                            "$project":
                            {
                                "_id": 0,
                            },
                        },
                        {
                            "$lookup":
                            {
                                "from": "fish_grading",
                                "localField": "pond_activation_id",
                                "foreignField": "pond_activation_id",
                                "as": "grading",
                            },
                        },
                        {
                            "$addFields":
                            {
                                "grading_id": {
                                "$first": "$grading._id",
                                },
                                "fish_price": "$newPrice",
                            },
                        },
                        {
                            "$project":
                            {
                                "grading": 0,
                                "newPrice": 0,
                            },
                        },
                        {
                            "$out":
                            "price_accumulator",
                        },
                        ]

            testing = Fish.objects.aggregate(pipeline)
            temp = list(testing)
            print("temp", temp)
            tempSeedPrice = 0
            if len(temp) != 0:
                tempSeedPrice = temp[0]['newPrice']

            ## get electric price
            pipeline = [
                {"$sort": {"id_int": 1}},
                {
                    '$match': {
                        'created_at': {
                            '$gte': start_date,
                            '$lte': end_date,
                        }
                    }
                },
                {
                    '$match': {
                        "farm_id": farm_id,
                        'type': {
                            '$regex': type,
                            '$options': 'i'
                        }
                    }
                }
            ]
           
            # testing = ElectricInventory.objects.aggregate(pipeline)
            # electricResult = list(testing)
            # print("electricResult", electricResult)
            tempElectricPrice = 0
            # for item in electricResult:
            #     print("price", item['price'])
            #     tempElectricPrice+=item['price']
            finalElectricPrice = 0
            ## get asset price

            pipeline = [
                    {
                        "$project":
                        {
                            "finalDate": {
                            "$dateAdd": {
                                "startDate": "$created_at",
                                "unit": "year",
                                "amount": 5,
                                "timezone": "Asia/Jakarta",
                            },
                            },
                            "created_at": 1,
                            "price": 1,
                            "name": 1,
                        },
                    },
                    {
                        "$addFields":
                        {
                            "monthNum": {
                            "$dateDiff": {
                                "startDate": "$created_at",
                                "endDate": "$finalDate",
                                "unit": "month",
                                "timezone": "Asia/Jakarta",
                                "startOfWeek": "Monday",
                            },
                            },
                        },
                    },
                    {
                        "$addFields":
                        {
                            "unitPrice": {
                            "$divide": ["$price", "$monthNum"],
                            },
                        },
                    },
                    {
                        "$merge": {
                        "into": "asset_inventory_monthly",
                        },
                    },
                    ]
           
            # testing = AssetInventory.objects.aggregate(pipeline)
            # assetResult = list(testing)

            tempAssetPrice = 0
            # for item in assetResult:
            #     tempAssetPrice+=item['price']
            # finalAssetPrice = tempAssetPrice/total_active_pond
            finalAssetPrice = 0



            ## get suplement price

            name = request.args.get('name') if request.args.get('name') else ""
            pond_name = request.args.get('pond_name') if request.args.get('pond_name') else ""

            pipeline = [
                        {
                            "$match": {
                            "created_at": {
                                "$gte": start_date,
                                "$lte": end_date,
                            },
                            },
                        },
                        {
                            "$match": {
                            "farm_id": farm_id
                            },
                        },
                        {
                            "$match":
                            {
                                "suplemen_id": {
                                "$exists": True,
                                },
                            },
                        },
                        {
                            "$match": {
                            "pond_activation_id": ObjectId(
                                activation_id
                            ),
                            },
                        },
                        {
                            "$lookup": {
                            "from": "suplemen_inventory",
                            "localField": "suplemen_id",
                            "foreignField": "_id",
                            "as": "suplemen",
                            },
                        },
                        {
                            "$unwind": {
                            "path": "$suplemen",
                            "includeArrayIndex": "string",
                            "preserveNullAndEmptyArrays": False,
                            },
                        },
                        {
                            "$project":
                            {
                                "usage": 1,
                                "pond_activation_id": 1,
                                "suplemen.name": 1,
                                "suplemen.amount": 1,
                                "suplemen.price": 1,
                                "result": {
                                "$subtract": [
                                    "$suplemen.amount",
                                    "$usage",
                                ],
                                },
                            },
                        },
                        {
                            "$addFields":
                            {
                                "newPrice": {
                                "$multiply": [
                                    "$result",
                                    "$suplemen.price",
                                ],
                                },
                            },
                        },
                        {
                            "$addFields":
                            {
                                "name": "$suplemen.name",
                            },
                        },
                        {
                            "$project":
                            {
                                "suplemen": 0,
                                "result": 0,
                            },
                        },
                        {
                            "$project":
                            {
                                "pond_activation_id": 1,
                                "amount": "$usage",
                                "newPrice": 1,
                                "name": 1,
                                "type": "Suplemen",
                            },
                        },
                        {
                            "$addFields":
                            {
                                "suplemen_id": "$_id",
                                "suplemen_price": "$newPrice",
                            },
                        },
                        {
                            "$project":
                            {
                                "_id": 0,
                                "newPrice": 0,
                            },
                        },
                        {
                            "$merge":
                            {
                                "into": "price_accumulator",
                            },
                        },
                        ]

            testing = PondTreatment.objects.aggregate(pipeline)
            suplementResult = list(testing)
            print("suplementResult", suplementResult)
            tempSuplementPrice = 0
            if len(suplementResult) != 0:
                tempSuplementPrice = suplementResult[0]['newPrice']

            ## get feed price
            print("activation_id", activation_id)
            pipeline = [
                    {
                            "$match": {
                            "pond_activation_id": ObjectId(activation_id),
                            "created_at": {
                                "$gte": start_date,
                                "$lte": end_date
                            },
                            "farm_id": farm_id,
                            
                            }
                        },
                    {
                        "$lookup":
                        {
                            "from": "feed_inventory",
                            "localField": "fish_feed_id",
                            "foreignField": "_id",
                            "as": "feed",
                        },
                    },
                    {
                        "$unwind": {
                        "path": "$feed",
                        "includeArrayIndex": "string",
                        "preserveNullAndEmptyArrays": False,
                        },
                    },
                    {
                        "$group": {
                        "_id": {
                            "pond_activation_id": ObjectId(activation_id),
                        },
                        "feedId": {
                            "$first": "$feed._id",
                        },
                        "totalFeedDose": {
                            "$sum": "$feed_dose",
                        },
                        "initialAmount": {
                            "$first": "$feed.amount",
                        },
                        "price": {
                            "$first": "$feed.price",
                        },
                        "name": {
                            "$first": "$feed.brand_name",
                        },
                        },
                    },
                    {
                        "$project": {
                        "totalFeedDose": 1,
                        "price": 1,
                        "initialAmount": 1,
                        "name": 1,
                        "feedId": 1,
                        "result": {
                            "$subtract": [
                            "$initialAmount",
                            "$totalFeedDose",
                            ],
                        },
                        },
                    },
                    {
                        "$addFields": {
                        "newPrice": {
                            "$multiply": ["$result", "$price"],
                        },
                        },
                    },
                    {
                        "$project":
                        {
                            "price": 0,
                            "result": 0,
                            "totalFeedDose": 0,
                        },
                    },
                    {
                        "$project":
                        {
                            "amount": "$initialAmount",
                            "newPrice": 1,
                            "name": 1,
                            "feedId": 1,
                            "type": "Pakan",
                        },
                    },
                    {
                        "$addFields":
                        {
                            "pond_activation_id":
                            "$_id.pond_activation_id",
                            "feed_price": "$newPrice",
                        },
                    },
                    {
                        "$project":
                        {
                            "_id": 0,
                            "newPrice": 0,
                        },
                    },
                    {
                        "$merge": {
                        "into": "price_accumulator",
                        },
                    },
                    ]

            testing = FeedHistory.objects.aggregate(pipeline)
            print("testing", testing)
            feedResult = list(testing)
            print("feedresult", feedResult)
            tempFeedPrice = 0
            if len(feedResult) != 0:
                tempFeedPrice = feedResult[0]['newPrice']
      
            ## get fish amount
            last_fish_grading = FishGrading.objects(pond_activation_id=activation_id).order_by('-grading_at').first()
            print("last grading amount", last_fish_grading.fish[0]['amount'])
            
            # print("amount", lastFishGrading[0]['amount'])
            finalTotalPrice = (finalAssetPrice + finalElectricPrice + tempSeedPrice + tempFeedPrice + tempSuplementPrice) / last_fish_grading.fish[0]['amount']

            ## merge to harvest tabel

            pipeline = [
                            {
                                "$match": {
                                "pond_activation_id": {
                                    "$exists": True,
                                },
                                },
                            },
                            {
                                "$match":
                                {
                                    "pond_activation_id": ObjectId(activation_id),
                                },
                            },
                            {
                                "$group": {
                                "_id": "$pond_activation_id",
                                "pond_activation_id": {
                                    "$first": "$pond_activation_id",
                                },
                                "feed_id": {
                                    "$max": "$feedId",
                                },
                                "feed_price": {
                                    "$sum": {
                                    "$cond": [
                                        {
                                        "$eq": ["$type", "Pakan"],
                                        },
                                        "$feed_price",
                                        0,
                                    ],
                                    },
                                },
                                "fish_id": {
                                    "$first": "$fish_id",
                                },
                                "fish_price": {
                                    "$first": "$fish_price",
                                },
                                "suplemen_id": {
                                    "$max": "$suplemen_id",
                                },
                                "suplemen_price": {
                                    "$sum": {
                                    "$cond": [
                                        {
                                        "$eq": ["$type", "Suplemen"],
                                        },
                                        "$suplemen_price",
                                        0,
                                    ],
                                    },
                                },
                                "grading_id": {
                                    "$first": "$grading_id",
                                },
                                },
                            },
                            {
                                "$merge":
                                {
                                    "into": "harvest",
                                },
                            },
                        ]
            harvest = db.aggregate("price_accumulator", pipeline)
            print("harvest", harvest)

            response = json.dumps({
                'status': 'success',
                'electricPrice' : round(finalElectricPrice, 3),
                'asset_price': round(finalAssetPrice, 3),
                'suplemen_price' : round(tempSuplementPrice, 3),
                'feed_price' : round(tempFeedPrice, 3),
                'seed_price' : round(tempSeedPrice, 3),
                "fish_amount" : last_fish_grading.fish[0]['amount'],
                'total_price' : round(finalTotalPrice, 3)
            }, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)



# class PondDeactivationApi(Resource):
#     def post(self, pond_id):
#         pond = Pond.objects.get(id=pond_id)
#         deactivation_at = request.form.get("deactivated_at",None)

#         print(deactivation_at)

#         if pond.isActive == False:
#             response = {"message": "status pond is already not active"}
#             response = json.dumps(response, default=str)
#             return Response(response, mimetype="application/json", status=400)
#         # get last pond_activation
#         pond_activation = PondActivation.objects(
#             pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
#         fishes = request.form.get("fish", "[]")
#         fishes = json.loads(fishes)
#         total_fish_harvested = request.form.get("total_fish_harvested", None)
#         amount_undersize = request.form.get("amount_undersize", None)
#         amount_oversize = request.form.get("amount_oversize", None)
#         amount_normal = request.form.get("amount_normal", None)
#         sample_weight = request.form.get("sample_weight", None)
#         sample_amount = request.form.get("sample_amount", None)
#         sample_long = request.form.get("sample_long", None)
#         total_weight_harvested = request.form.get("total_weight_harvested", None)
#         # fish_harvested = request.form.get("fish_harvested", None)
#         for fish in fishes:
#             # save fish log
#             data = {
#                 "pond_id": pond_id,
#                 "pond_activation_id": pond_activation.id,
#                 "type_log": "deactivation",
#                 "fish_type": fish['type'],
#                 "fish_amount": fish['amount'],
#                 "fish_total_weight": fish['weight'],
#                 "fish_seed_id": fish['fish_seed_id'],
#                 "fish_category": fish['fish_category'],
#             }
#             # total_fish_harvested += fish['amount']
#             # total_weight_harvested += fish['weight']
#             fishlog = FishLog(**data).save()
#             print(data)
#         print(total_fish_harvested)
#         print(total_weight_harvested)
        

#         # get args form data
#         # update pond_activation
#         pond_deactivation_data = {
#             "isFinish": True,
#             "total_fish_harvested": total_fish_harvested,
#             "total_weight_harvested": total_weight_harvested,
#             "deactivated_description": "Normal",
#             "amount_undersize_fish":amount_undersize,
#             "amount_oversize_fish":amount_oversize,
#             "amount_normal_fish":amount_normal,
#             "sample_amount":sample_amount,
#             "sample_long":sample_long,
#             "sample_weight": sample_weight
#         }

#         if deactivation_at != '':
#             pond_deactivation_data['deactivated_at'] = datetime.datetime.strptime(deactivation_at, "%Y-%m-%dT%H:%M:%S.%f %z") 
#         else :
#             three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)
#             pond_deactivation_data['deactivated_at'] = three_months_ago

#         pond_activation.update(**pond_deactivation_data)
#         # update pond isActive
#         pond.update(**{"isActive": False,"status": "Panen"})
#         response = {"message": "success to deactivation pond"}
#         response = json.dumps(response, default=str)
#         return Response(response, mimetype="application/json", status=200)

class DeactivationRecapApi(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            farm_id = ObjectId(farm)
    
            start_date = datetime.datetime.strptime(request.args.get('start_date'), '%Y-%m-%d') if request.args.get('start_date') else datetime.datetime.strptime("2023-01-01", '%Y-%m-%d')
            end_date = datetime.datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + datetime.timedelta(days=1) if request.args.get('end_date') else datetime.datetime.strptime("2030-01-01", '%Y-%m-%d')
    
            pipeline = [
                {
                    '$match': {
                        'created_at': {
                            '$gte': start_date,
                            '$lte': end_date,
                        },
                        "farm_id": farm_id,
                    }
                },
                {"$sort": {"created_at": 1}},
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$pond_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$pondid']}}, },
                        {"$project": {
                            "_id": 1,
                            "alias": 1,
                            "location": 1,
                            "created_at": 1,
                        }}
                    ],
                    'as': 'pond_detail'
                }},
                {"$addFields": {
                    "pond_detail": {"$first": "$pond_detail"},
                }},
            ]

            testing = DeactivationRecap.objects.aggregate(pipeline)
            temp = list(testing)
            
            response = json.dumps({
                'status': 'success',
                'data': temp,
            }, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
    
    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])

            deactivation_at = request.form.get("deactivated_at", datetime.datetime.now())

            body = {
                "pond_id": request.form.get('pond_id'),
                "farm_id": farm,
                "fish_seed_id": request.form.get('fish_seed_id'),
                "fish_weight": request.form.get('fish_weight'),
                "fish_amount": request.form.get('fish_amount'),
                "fish_type": request.form.get('fish_type'),
                "fish_category": request.form.get('fish_category'),
                "fish_price": request.form.get('fish_price'),
            }

            if deactivation_at != '':
                body['created_at'] = datetime.datetime.strptime(deactivation_at, "%Y-%m-%dT%H:%M:%S.%f %z") 
            else :
                three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)
                body['created_at'] = three_months_ago

            DeactivationRecap(**body).save()
            res = {"message": "success add deactivation recap"}
            response = json.dumps(res, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)