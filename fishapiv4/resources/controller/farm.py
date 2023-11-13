import os
from flask import Flask, Response, request, current_app, url_for, send_from_directory
from fishapiv4.database.models import *
from flask_restful import Resource
from werkzeug.utils import secure_filename
from fishapiv4.resources.helper import *
from fishapiv4.resources.controller.authentication import *
import datetime
import json
from mongoengine import ObjectIdField
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from bson.objectid import ObjectId
from ...database import db
class FarmApi(Resource):
    def get(self):
        try:
            pipeline = [{"$sort": {"name": 1}},]
            # list_farm = Farm.objects.aggregate(pipeline)
            list_farm = db.aggregate('farm',pipeline)
            farm_list = list(list_farm)
            response = json.dumps(farm_list, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)