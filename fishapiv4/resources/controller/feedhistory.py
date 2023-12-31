from flask import Response, request, current_app
from fishapiv4.database.models import *
from flask_restful import Resource
from fishapiv4.database.db import db
import calendar
from datetime import timedelta, datetime
import json
from bson.json_util import dumps
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from bson.objectid import ObjectId
from dateutil.relativedelta import relativedelta
from ...database import db

class FeedHistorysApi(Resource):
    @jwt_required()

    def get(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            farm_id = ObjectId(farm)
            # filter date
            # get args with default input "all"
            filter_date = request.args.get("filter_date", "all")
            # handle input "today"
            if filter_date == "today":
                date = datetime.today().strftime('%Y-%m-%d')
                date_equation = {'$eq': [date, {'$dateToString': {
                    'format': "%Y-%m-%d", 'date': "$feed_history_time"}}]}
            # handle input "all"
            elif filter_date == "all":
                date_equation = {}
            # handle input date with format like "2022-02-18"
            else:
                # convert string to datetime
                filter_date = datetime.strptime(
                    filter_date, "%Y-%m-%d")
                date_equation = {'$eq': [date, {'$dateToString': {
                    'format': "%Y-%m-%d", 'date': "$feed_history_time"}}]}

            pipeline = [
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$pond_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$and': [{'$eq': ['$_id', '$$pondid']}]}, 
                            "farm_id": farm_id,

                            }},
                        {"$project": {
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'pond'
                }},
                {'$lookup': {
                    'from': 'feed_type',
                    'let': {"feedid": "$feed_type_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$feedid']}}},
                        {"$project": {
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'feed_type'
                }},
                {"$project": {
                    "pond_id": 0,
                    "feed_type_id": 0,
                    "created_at": 0,
                    "updated_at": 0,
                }}
            ]
            # feedhistory = FeedHistory.objects.aggregate(pipeline)
            feedhistory = db.aggregate('feed_history',pipeline)
            list_feedhistory = list(feedhistory)
            response = json.dumps(list_feedhistory, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    @jwt_required()
    def post(self):
        try:
            pond_id = request.form.get("pond_id", None)
            print(pond_id)
            fish_feed_id = request.form.get("fish_feed_id", None)
            pipline=[{"$match":{"_id": pond_id}}]
            pond = db.aggregate('pond',pipline)
            # pond = Pond.objects.get(id=pond_id)
            if pond['isActive'] == False:
                response = {"message": "pond is not active"}
                response = json.dumps(response, default=str)
                return Response(response, mimetype="application/json", status=400)
            pipeline=[
                {"$match":{"pond_id":pond_id}},
                {"$sort":{"activated_at": -1}},
                {"$limit": 1},
            ]
            pond_activation = db.aggregate('pond_activation',pipeline)
            # pond_activation = PondActivation.objects(
            #     pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
            # feed_type = FeedType.objects.get(id=feed_type_id)
            feed_history_time = request.form.get("feed_history_time", None)
            if feed_history_time != None:
                feed_history_time = datetime.fromisoformat(
                    feed_history_time)
                
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])

            theDate = request.form.get('created_at', None)
            print("created_at", theDate)

            body = {
                "pond_id": pond_id,
                "farm_id": farm,
                "pond_activation_id": pond_activation.id,
                "fish_feed_id": fish_feed_id,
                "feed_dose": request.form.get("feed_dose", None),
            }

            if theDate != '':
                body['created_at'] = datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z")
                body['feed_history_time'] = datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
            else :
                three_months_ago = datetime.now() - timedelta(days=3 * 30)
                body['created_at'] = three_months_ago
                body['feed_history_time'] = three_months_ago

            # # update feed inventory table
            # get_feed_by_id = FeedInventory.objects.get(id=request.form.get('fish_feed_id', None))
            # get_feed_by_id.amount -= float(request.form.get('feed_dose', None))
            # get_feed_by_id.save()

            # feedhistory = FeedHistory(**body).save(using=current_app.config['CONNECTION'])
            collection = db.get_collection('feed_history')
            feedhistory = collection.insert_one(body)
            id = feedhistory.id
            return {'id': str(id), 'message': 'success input'}, 200
        except Exception as e:
            print(str(e))
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FeedHistoryApi(Resource):
    def put(self, id):
        try:
            body = request.form.to_dict(flat=True)
            # FeedHistory.objects.get(id=id).update(**body)
            collection = db.get_collection('feed_history')
            macthFilter = {
                "_id" : ObjectId(id)
            }
            updateFilter = {
                "$set" : body
            }
            collection.update_one(macthFilter, updateFilter)
            response = {"message": "success change data feedhistory", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def delete(self, id):
        try:
            # feedhistory = FeedHistory.objects.get(id=id).delete()
            collection = db.get_collection('feed_history')
            matchfilter={
                "_id" : ObjectId(id)
            }
            collection.delete_one(matchfilter)
            response = {"message": "success"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def get(self, id):
        try:
            pipeline=[{"$match":{"_id": id}}]
            feedhistory= db.aggregate('feed_history',pipeline)
            # feedhistory = FeedHistory.objects.get(id=id)
            pipline = [
                {'$match': {'$expr': {'$eq': ['$_id', {'$toObjectId': id}]}}},
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$pond_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$and': [{'$eq': ['$_id', '$$pondid']}]}}},
                        {"$project": {
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'pond'
                }},
                {'$lookup': {
                    'from': 'feed_type',
                    'let': {"feedid": "$feed_type_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$feedid']}}},
                        {"$project": {
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'feed_type'
                }},
                {"$addFields": {
                    "pond": {"$first": "$pond"},
                    "feed_type": {"$first": "$feed_type"}
                }},
                {"$project": {
                    "pond_id": 0,
                    "feed_type_id": 0,
                    "created_at": 0,
                    "updated_at": 0,
                }}
            ]
            # feedhistory = FeedHistory.objects.aggregate(pipline)
            feedhistory = db.aggregate('feed_history',pipline)
            list_feedhistory = list(feedhistory)
            response = dict(list_feedhistory[0])
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FeedHistoryByPond(Resource):
    def get(self):
        try:
            # Filter Date
            # DATE FIELD
            # make variable for default field
            default = datetime.today().strftime('%Y-%m-%d')
            # get args with default input today
            date = request.args.get("date", default)
            date = datetime.strptime(date, '%Y-%m-%d')  # datetime
            # RANGE FIELD
            # get args with default input daily
            date_range = request.args.get("range", "daily")
            if date_range == "monthly":
                month_format = '%Y-%m'
                month_date = date.strftime(month_format)
                date_query = {'$eq': [month_date, {'$dateToString': {
                    'format': month_format, 'date': "$feed_history_time"}}]}
            else:
                daily_format = '%Y-%m-%d'
                daily_date = date.strftime(daily_format)
                date_query = {'$eq': [daily_date, {'$dateToString': {
                    'format': daily_format, 'date': "$feed_history_time"}}]}
            # Filter Pond
            # LIST POND FIELD
            # make variable for default field
            list_pond = request.args.get("list_pond", default="[]")
            list_pond = json.loads(list_pond)
            list_pond_query = {}
            if len(list_pond) >= 1:
                list_pond_query = {"$match": {
                    "$expr": {"$in": [{"$toString": "$_id"}, list_pond]}}}
            pipline = [
                list_pond_query,
                {'$lookup': {
                    'from': 'feed_history',
                    'let': {"pondid": "$_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_id', '$$pondid']},
                            date_query
                        ]}}},
                        {'$lookup': {
                            'from': 'feed_type',
                            'let': {"feedid": "$feed_type_id"},
                            'pipeline': [
                                {'$match': {
                                    '$expr': {'$eq': ['$_id', '$$feedid']}}},
                                {"$project": {
                                    "created_at": 0,
                                    "updated_at": 0,
                                }}
                            ],
                            'as': 'feed_type'
                        }},
                        {"$addFields": {
                            "feed_type": {"$first": "$feed_type"}
                        }},
                        {"$project": {
                            "pond_id": 0,
                            "feed_type_id": 0,
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'feed_historys_list'
                }},
                {"$addFields": {
                    "total_feed_dose": {"$sum": "$feed_historys_list.feed_dose"},
                    "feed_historys_list": '$feed_historys_list'
                }},
                {"$project": {
                    "created_at": 0,
                    "updated_at": 0,
                }}
            ]
            # ponds = Pond.objects().aggregate(pipline)
            ponds = db.aggregate('pond',pipline)
            response = list(ponds)
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FeedHistoryByOnePond(Resource):
    def get(self, id):
        try:
            objects = Pond.objects.get(id=id)
           # make variable for default field
            default = datetime.today().strftime('%Y-%m-%d')
            # get args with default input today
            date = request.args.get("date", default)
            date = datetime.strptime(date, '%Y-%m-%d')  # datetime
            # get args with default input daily
            date_range = request.args.get("range", "daily")
            if date_range == "monthly":
                month_format = '%Y-%m'
                month_date = date.strftime(month_format)
                date_query = {'$eq': [month_date, {'$dateToString': {
                    'format': month_format, 'date': "$feed_history_time"}}]}
            else:
                daily_format = '%Y-%m-%d'
                daily_date = date.strftime(daily_format)
                date_query = {'$eq': [daily_date, {'$dateToString': {
                    'format': daily_format, 'date': "$feed_history_time"}}]}
            pipeline = [
                {'$match': {'$expr': {'$eq': ['$_id', {'$toObjectId': id}]}}},
                {'$lookup': {
                    'from': 'feed_history',
                    'let': {"pondid": "$_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_id', '$$pondid']},
                            date_query
                        ]}}},
                        {'$lookup': {
                            'from': 'feed_type',
                            'let': {"feedid": "$feed_type_id"},
                            'pipeline': [
                                {'$match': {
                                    '$expr': {'$eq': ['$_id', '$$feedid']}}},
                                {"$project": {
                                    "created_at": 0,
                                    "updated_at": 0,
                                }}
                            ],
                            'as': 'feed_type'
                        }},
                        {"$addFields": {
                            "feed_type": {"$first": "$feed_type"}
                        }},
                        {"$project": {
                            "pond_id": 0,
                            "feed_type_id": 0,
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'feed_historys_list'
                }},
                {"$addFields": {
                    "total_feed_dose": {"$sum": "$feed_historys_list.feed_dose"},
                    "feed_historys_list": '$feed_historys_list'
                }},
                {"$project": {
                    "created_at": 0,
                    "updated_at": 0,
                }}
            ]
            data = Pond.objects.aggregate(pipeline)
            data = list(data)
            data = dict(data[0])
            response = json.dumps(data, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FeedHistoryMonthByActivation(Resource):

    def get(self, activation_id):
        try:
            pipeline = [
                {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_activation_id', {
                                '$toObjectId': activation_id}]},
                            ]}}},
                {"$addFields": {
                    "month": {"$month": "$feed_history_time"},
                    "year": {"$year": "$feed_history_time"},
                }},
                {"$group": {
                    "_id": "$month",
                    "year": {"$first": "$year"},
                    "total_feed": {"$sum": "$feed_dose"},
                    "total_feedhistory": {"$sum": 1}
                }},
            ]
            feedHistorys = FeedHistory.objects.aggregate(pipeline)
            response = list(feedHistorys)
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FeedHistoryWeekByActivation(Resource):

    def get(self, activation_id, month):
        try:
            # get weeks
            weeks = []
            dateStart = datetime.strptime(month, "%Y-%m")
            # xx = "test"
            daysInMonth = calendar.monthrange(
                dateStart.year, dateStart.month)[1]
            daysDelta = timedelta(days=daysInMonth)
            dateEnd = dateStart + daysDelta
            for i in range(daysInMonth+1):
                day = dateStart + timedelta(days=i)
                week = day.strftime("%W")
                if int(week) not in weeks:
                    weeks.append(int(week))
            print(weeks)
            pipeline = [
                {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_activation_id', {
                                '$toObjectId': activation_id}]},
                            {"$in": [{"$week": "$feed_history_time"}, weeks]},
                            ]}}},
                {"$addFields": {
                    "week": {"$week": "$feed_history_time"},
                    "month": {"$month": "$feed_history_time"},
                    "year": {"$year": "$feed_history_time"},
                }},
                {"$group": {
                    "_id": "$week",
                    "month": {"$first": "$month"},
                    "year": {"$first": "$year"},
                    "total_feed": {"$sum": "$feed_dose"},
                    "total_feedhistory": {"$sum": 1}
                }},
                {"$sort": {"year": 1, "_id": 1}},
            ]
            feedHistorys = FeedHistory.objects.aggregate(pipeline)
            response = list(feedHistorys)
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FeedHistoryDayByActivation(Resource):

    def get(self, activation_id, week):
        try:
            pipeline = [
                {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_activation_id', {
                                '$toObjectId': activation_id}]},
                            {"$eq": [
                                {"$week": "$feed_history_time"}, int(week)]},
                            ]}}},
                {"$addFields": {
                    "week": {"$week": "$feed_history_time"},
                    "day": {"$dayOfMonth": "$feed_history_time"},
                    "month": {"$month": "$feed_history_time"},
                    "year": {"$year": "$feed_history_time"},
                }},
                {"$group": {
                    "_id": "$day",
                    "month": {"$first": "$month"},
                    "year": {"$first": "$year"},
                    "total_feed": {"$sum": "$feed_dose"},
                    "total_feedhistory": {"$sum": 1}
                }},
                {"$sort": {"year": 1, "month": 1, "_id": 1}},
            ]
            feedHistorys = FeedHistory.objects.aggregate(pipeline)
            response = list(feedHistorys)
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FeedHistoryHourByActivation(Resource):

    def get(self, activation_id, day):
        try:
            pipeline = [
                {'$match': {'$expr': {'$and': [
                            {'$eq': ['$pond_activation_id', {
                                '$toObjectId': activation_id}]},
                            {"$eq": [
                                {'$dateToString': {
                                    'format': "%Y-%m-%d", 'date': "$feed_history_time"}}, day]},
                            ]}}},
                {"$addFields": {
                    "week": {"$week": "$feed_history_time"},
                    "day": {"$dayOfMonth": "$feed_history_time"},
                    "month": {"$month": "$feed_history_time"},
                    "year": {"$year": "$feed_history_time"},
                }},
                {"$sort": {"year": 1, "month": 1, "_id": 1}},
                {'$lookup': {
                    'from': 'feed_inventory',
                    'let': {"fishfeedid": "$fish_feed_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$fishfeedid']}}},
                        {"$project": {
                            "_id": 1,
                            "id_int": 1,
                            "feed_category": 1,
                            "brand_name": 1,
                            "description": 1,
                            "price": 1,
                            "amount": 1,
                            "producer": 1,
                            "protein": 1,
                            "carbohydrate": 1,
                            "min_expired_period": 1,
                            "max_expired_period": 1,
                            "image": 1,
                            "created_at": 1,
                        }}
                    ],
                    'as': 'feed'
                }},
                {"$addFields": {
                    "feed": {"$first": "$feed"},
                }},
            ]
            feedHistorys = FeedHistory.objects.aggregate(pipeline)
            response = list(feedHistorys)
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

# class FeedHistoryForChart(Resource):

#     def get(self, activation_id):
#         try:
#             pipeline = [
#                 {'$match': {'$expr': {'$and': [
#                             {'$eq': ['$pond_activation_id', {
#                                 '$toObjectId': activation_id}]},
#                             ]}}},
#                 {"$addFields": {
#                     "week": {"$week": "$feed_history_time"},
#                     "day": {"$dayOfMonth": "$feed_history_time"},
#                     "month": {"$month": "$feed_history_time"},
#                     "year": {"$year": "$feed_history_time"},
#                 }},
#                 {"$sort": {"year": 1, "month": 1, "_id": 1}},
#                 # {'$lookup': {
#                 #     'from': 'feed_type',
#                 #             'let': {"feedid": "$feed_type_id"},
#                 #             'pipeline': [
#                 #                 {'$match': {
#                 #                     '$expr': {'$eq': ['$_id', '$$feedid']}}},
#                 #                 {"$project": {
#                 #                     "created_at": 0,
#                 #                     "updated_at": 0,
#                 #                 }}
#                 #             ],
#                 #     'as': 'feed_type'
#                 # }},
#             ]
#             feedHistorys = FeedHistory.objects.aggregate(pipeline)
#             response = list(feedHistorys)
#             feed = []
#             dateIndicator = None
#             feeddose = 0
#             getlogic = 200
#             samedate = datetime.now()
#             yesterday = samedate - timedelta(days = 2)
#             samedate = samedate - samedate
#             # print(response)
#             for fish in response:
#                 date = fish["feed_history_time"].strftime('%d-%m-%Y')
#                 if (dateIndicator != None):
#                     if (getlogic == samedate) :
#                         feeddose += float(fish["feed_dose"])
#                         feed.pop()
#                         data = {
#                             "pond_id": fish['pond_id'],
#                             "pond_activation_id": fish['pond_activation_id'],
#                             "fish_feed_id": fish['fish_feed_id'],
#                             "date": fish['feed_history_time'],
#                             "feed_dose": feeddose,
#                             # "feed_used": fish['feed_used'],
#                         }
#                         dateIndicator = date
#                         date_object = datetime.strptime(date, '%d-%m-%Y').date()
#                         datecompar_object = datetime.strptime(dateIndicator, '%d-%m-%Y').date()
#                         getlogic = datecompar_object - date_object
#                         feed.append(data)
#                     if (getlogic != samedate) :
#                         feeddose = 0
#                         data = {
#                             "pond_id": fish['pond_id'],
#                             "pond_activation_id": fish['pond_activation_id'],
#                             "fish_feed_id": fish['fish_feed_id'],
#                             "date": fish['feed_history_time'],
#                             "feed_dose": fish["feed_dose"],
#                             # "feed_used": fish['feed_used'],
#                         }
#                         dateIndicator = date
#                         date_object = datetime.strptime(date, '%d-%m-%Y').date()
#                         datecompar_object = datetime.strptime(dateIndicator, '%d-%m-%Y').date()
#                         getlogic = datecompar_object - date_object
#                         feeddose += float(fish["feed_dose"])
#                         feed.append(data)
#                 else :
#                     data = {
#                         "pond_id": fish['pond_id'],
#                         "pond_activation_id": fish['pond_activation_id'],
#                         "fish_feed_id": fish['fish_feed_id'],
#                         "date": fish['feed_history_time'],
#                         "feed_dose": fish["feed_dose"],
#                         # "feed_used": fish['feed_used'],
#                     }
                    
#                     date_object = datetime.strptime(date, '%d-%m-%Y').date()
#                     feed.append(data)
#                     feeddose += int(fish["feed_dose"])
#                     getlogic =  date_object - yesterday.date()
#                     dateIndicator = date
#             response = json.dumps(feed, default=str)
#             return Response(response, mimetype="application/json", status=200)
#         except Exception as e:
#             response = {"message": e}
#             response = json.dumps(response, default=str)
#             return Response(response, mimetype="application/json", status=400)

class FeedHistoryForChart(Resource):
    def get(self):
        try:
            type = request.args.get('type') if request.args.get('type') else ""

            pipeline = [
                {'$lookup': {
                    'from': 'feed_inventory',
                    'let': {"fishfeedid": "$fish_feed_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$fishfeedid']},
                                    'feed_category': type,
                            }
                        },
                        {"$project": {
                            "_id": 1,
                            "id_int": 1,
                            "feed_category": 1,
                            "brand_name": 1,
                            "description": 1,
                            "price": 1,
                            "amount": 1,
                            "producer": 1,
                            "protein": 1,
                            "carbohydrate": 1,
                            "min_expired_period": 1,
                            "max_expired_period": 1,
                            "image": 1,
                            "created_at": 1,
                        }}
                    ],
                    'as': 'feed'
                }},
                # {"$addFields": {
                #     "feed": {"$first": "$feed"},
                # }},
                {
                    '$unwind': '$feed'
                },
                # {
                #     '$match': {
                #         'feed.feed_category': 'alami'
                #     }
                # },
                {
                    '$group': {
                        '_id': {
                            'created_at': {
                                '$dateToString': {
                                    'format': '%Y-%m-%d',
                                    'date': '$created_at'
                                }
                            }
                        },
                        'total_usage': { '$sum': '$usage' },
                        'feed_data': { '$push': '$feed' }
                    }
                },
                {
                    '$sort': {
                        '_id.created_at': 1  # 1 for ascending order, -1 for descending order
                    }
                }
            ]

            testing = FeedUsed.objects.aggregate(pipeline)
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