import os
from flask import Flask, Response, request, jsonify, current_app, url_for, send_from_directory, make_response
from fishapiv4.database.models import *
from flask_restful import Resource
import jwt
from functools import wraps
from werkzeug.utils import secure_filename
from fishapiv4.resources.helper import *
import datetime
import json
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from ...database import db
class Login(Resource): 
    def post(self):
        try:
            username = request.form.get("username")
            password = request.form.get("password")
            pipline=[{"$match":{"username":username}}]
            data = db.aggregate('breeder',pipline)
            # data = Breeder.objects.get(username=username)
            pipeline=[{"$match":{"_id":data.farm_id.id}}]
            farm = db.aggregate('farm',pipeline)
            # farm = Farm.objects.get(id=data.farm_id.id)
            user = {
                "id": str(data.id),
                "farm_id": str(data.farm_id.id),
                "username": data.username,
                "name": data.name,
                "nik": data.nik,
                "phone": data.phone,
                "farm_name":farm.farm_name
            }
            passwordcheck = check_password_hash(data.password, password)
            if passwordcheck == True:
                access_token = create_access_token(identity=user)
            return jsonify(access_token=access_token, identity=user)
        except Exception as e:
            response = {"message": "Breeder ID/Password Salah"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        # return make_response('could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Req"'})

class Register(Resource):
    def post(self):
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            name = request.form.get('name')
            nik = request.form.get('nik')
            phone = request.form.get('phone')
            hasFarm = request.form.get('hasFarm')
            pipeline_user = [
                {"$match": {"username": username}},
            ]
            # check_breeder = Breeder.objects.aggregate(pipeline_user)
            check_breeder = db.aggregate('breeder',pipeline_user)
            checking_breeder = list(check_breeder)
            if len(checking_breeder) > 0:
                response = {"message": "BreederID Sudah Digunakan"}
                response = json.dumps(response, default=str)
                return Response(response, mimetype="application/json", status=400)
            password_hash = generate_password_hash(password, method='sha256')
            if hasFarm == "Belum":
                farm_name = request.form.get('farm_name')
                breeder = request.form.get('breeder')
                address = request.form.get('address')
                coordinate = request.form.get('coordinate')
                farm_body = {
                    "farm_name": farm_name,
                    "breeder": breeder,
                    "address": address,
                    "coordinate": coordinate
                }
                # farm = Farm(**farm_body).save()
                collection = db.get_collection('farm')
                farm = collection.insert_one(farm_body)
                farm_id = farm.id
            if hasFarm == "Sudah":
                farm_id = request.form.get('farm_id')
                # farm = Farm.objects.get(id=farm_id)
                pipline=[{"$match":{"_id":farm_id}}]
                farm = db.aggregate('farm',pipline)
                farm_name = farm.farm_name
            body = {
                "farm_id": farm_id,
                "username": username,
                "password": password_hash,
                "name": name,
                "nik": nik,
                "phone": phone
            }
            collection = db.get_collection('breeder')
            breeder= collection.insert_one(body)
            # breeder = Breeder(**body).save()
            user = {
                "id": str(breeder.id),
                "farm_id": str(breeder.farm_id.id),
                "farm_name": farm_name,
                "username": breeder.username,
                "name": breeder.name,
                "nik": breeder.nik,
                "phone": breeder.phone
            }
            access_token = create_access_token(identity=user)
            return jsonify(access_token=access_token, identity=user)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


