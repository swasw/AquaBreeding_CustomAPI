import os
from flask import Flask, Response, request, current_app, url_for, send_from_directory
from fishapiv4.database.models import *
from flask_restful import Resource
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required
from fishapiv4.resources.helper import *
import datetime
import json
from bson.objectid import ObjectId
from ...database import db
class FishHarvestedPriceApi(Resource):
    @jwt_required()
    def get(self):
        try:
            print("get...")
            pipeline = [{"$sort": {"created_at": -1}},]
            list_fish_harvested_price = FishHarvestedPriceDetails.objects.aggregate(pipeline)
            fish_harvested_price = list(list_fish_harvested_price)
            print("fish harvested price list", fish_harvested_price)
            response = {"message": "sukses mendapatkan daftar harga ikan yang telah dipanen!", "fish_harvested_price" : fish_harvested_price }
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:  
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
    @jwt_required()
    def post(self):
        try:
            fish_harvested_id = request.form.get("fish_harvested_id")
            fishHarvested = FishHarvested.objects(id=fish_harvested_id).first()
            if (not fishHarvested):
                raise Exception('Fish Harvested Id Tidak ditemukan')
            asset_price =  request.form.get("asset_price")
            electric_price =  request.form.get("electric_price")
            seed_price =  request.form.get("seed_price")
            feed_price =  request.form.get("feed_price")
            suplement_price =  request.form.get("suplement_price")
            total_price =  request.form.get("total_price")
            body = {
                "fish_harvested_id" : fish_harvested_id,
                "asset_price" : asset_price,
                "electric_price" : electric_price,
                "seed_price" : seed_price,
                "feed_price" : feed_price,
                "suplement_price" : suplement_price,
                "total_price" : total_price,
            }
            isExist = FishHarvestedPriceDetails.objects.get(fish_harvested_id = fish_harvested_id)
            if isExist is None:
                fish_harvested_price = FishHarvestedPriceDetails(**body).save(using=current_app.config['CONNECTION'])
                response = {"message" : "success add to fish harvested price", "fish_harvested_price" : fish_harvested_price.id}
                response = json.dumps(response, default=str)
                return Response(response, mimetype="application/json", status=200)
            else:
                
                response = {"message" : "record already exist"}
                response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        except Exception as e:  
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        
class FishHarvestedPriceApibyId(Resource):
    @jwt_required()
    def get(self, id):
        try:
            print("get...")
            searchById = FishHarvestedPriceDetails.objects(fish_harvested_id = id).first()
            print("fish harvested price ", searchById.asset_price)
            body = {
                "id" : searchById.id,
                "fish_harvested_id" : searchById.fish_harvested_id.id,
                "asset_price" : searchById.asset_price,
                "electric_price" : searchById.electric_price,
                "seed_price" : searchById.seed_price,
                "feed_price" : searchById.feed_price,
                "suplement_price" : searchById.suplement_price,
                "total_price" : searchById.total_price,
            }
            response = {"message": "sukses mendapatkan daftar harga ikan yang telah dipanen!", "data" : body }
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:  
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
    