from .db import db
import datetime
from bson import json_util
from mongoengine import connect, disconnect

disconnect()

_meta = {
    'db_alias' : 'new_connection',
}
class Farm(db.Document):
    meta = _meta
    farm_name = db.StringField(required=True)
    address = db.StringField(required=True)
    breeder = db.StringField(required=True)
    coordinate = db.StringField()


class Breeder(db.Document):
    meta = _meta
    farm_id = db.ReferenceField(Farm, required=True)
    username = db.StringField(required=True)
    password = db.StringField(required=True)
    name = db.StringField(required=True)
    nik = db.StringField(required=True)
    phone = db.StringField(required=True)


class Pond(db.Document):
    meta = _meta
    shape_option = ("bundar", "persegi")

    farm_id = db.ReferenceField(Farm, required=True)
    id_int = db.SequenceField(required=True)
    alias = db.StringField(required=True)
    location = db.StringField(required=True)
    shape = db.StringField(required=True, choices=shape_option)
    material = db.StringField(required=True)
    length = db.FloatField(required=True, default=0)
    width = db.FloatField(required=True, default=0)
    diameter = db.FloatField(required=True, default=0)
    height = db.FloatField(required=True, default=0)
    image_name = db.StringField(required=True, default='default.jpg')
    isActive = db.BooleanField(required=True, default=False)
    build_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class PondActivation(db.Document):
    meta = _meta
    pond_id = db.ReferenceField(Pond, required=True)
    isFinish = db.BooleanField(required=True, default=False)
    fish_type = db.StringField(required = True, default='')
    fish_category = db.StringField(required = True)
    total_fish_added = db.IntField(default = 0)
    water_level = db.FloatField(required=True, default=0)
    activated_at = db.DateTimeField(default=datetime.datetime.now)
    deactivated_at = db.DateTimeField(default=None)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class WaterPreparation(db.Document):
    meta = _meta
    carbohydrate_type_option = ("gula", "molase", "terigu", "tapioka")

    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    carbohydrate = db.IntField(required=True)
    carbohydrate_type = db.StringField(
        required=True, choices=carbohydrate_type_option)
    salt = db.IntField(required=True)
    calcium = db.IntField(required=True)


class FishDeath(db.Document):
    meta = _meta
    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    fish = db.ListField()
    image_name = db.StringField(required=True)
    diagnosis = db.StringField(default=datetime.datetime.now)
    death_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class SeedInventory(db.Document):
    meta = _meta
    id_int = db.SequenceField(required=True)
    farm_id = db.ReferenceField(Farm, required=True)
    fish_seed_category = db.StringField(required=True)
    fish_type = db.StringField(required=True)
    brand_name = db.StringField(required=True)
    amount = db.IntField(required=True)
    weight = db.FloatField(default=0)
    # length = db.IntField()
    width = db.StringField()
    price = db.IntField(required=True)
    total_price = db.IntField(required=True)
    image = db.StringField(required=True)
    fish_origin_category = db.StringField()
    # fish_added_date = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class Fish(db.Document):
    meta = _meta
    id_int = db.SequenceField(required=True)
    farm_id = db.ReferenceField(Farm, required=True)
    # seed_id = db.ReferenceField(SeedInventory, required=True)
    pond_activation_id = db.ReferenceField(PondActivation)
    fish_seed_category = db.StringField(required=True)
    fish_type = db.StringField(required=True)
    brand_name = db.StringField(required=True)
    amount = db.IntField(required=True)
    weight = db.FloatField(default=0)
    # length = db.IntField()
    width = db.StringField()
    price = db.IntField(required=True)
    total_price = db.IntField(required=True)
    image = db.StringField(required=True)
    fish_origin_category = db.StringField()
    # fish_added_date = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)  

class FishTransfer(db.Document):
    meta = _meta
    transfer_method_option = ("basah", "kering")
    transfer_type_option = ("", "oversized_transfer", "undersized_transfer")

    origin_pond_id = db.ReferenceField(Pond, required=True)
    destination_pond_id = db.ReferenceField(Pond, required=True)
    origin_activation_id = db.ReferenceField(PondActivation, required=True)
    destination_activation_id = db.ReferenceField(
        PondActivation, required=True)
    # fish_grading_id = db.ObjectIdField(required=True, default=None)
    transfer_type = db.StringField(choices=transfer_type_option, default="")
    fish_seed_id= db.ReferenceField(SeedInventory, required=True)
    fish_category = db.StringField(required=True)
    transfer_method = db.StringField(
        required=True, choices=transfer_method_option)
    sample_weight = db.FloatField(required=True)
    sample_long = db.FloatField(default=None)
    transfer_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class FishLog(db.Document):
    meta = _meta
    type_log = ('ACTIVATION', 'DEACTIVATION', 'TRANSFER_IN', 'TRANSFER_OUT', 'DEATH')

    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    event_id = db.GenericReferenceField()
    type_log = db.StringField(required=True)
    fish = db.ListField()
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class FishGrading(db.Document):
    meta = _meta
    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    event = db.GenericReferenceField()
    event_desc = db.StringField(required=True)
    fish = db.ListField()
    fcr = db.FloatField(defauit=0)
    sample_amount = db.IntField(default=0)
    sample_weight = db.FloatField(default=0)
    sample_long = db.FloatField(default = 0)
    grading_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class DailyWaterQuality(db.Document):
    meta = _meta
    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    ph = db.FloatField(required=True)
    do = db.FloatField(required=True)
    temperature = db.FloatField(required=True)
    week = db.IntField(defauit=None)
    dailywater_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class WeeklyWaterQuality(db.Document):
    meta = _meta
    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    floc = db.FloatField(required=True)
    nitrite = db.FloatField(Default=None)
    nitrate = db.FloatField(Default=None)
    ammonia = db.FloatField(Default=None)
    hardness = db.FloatField(Default=None)
    week = db.IntField(Default=None)
    weeklywater_at= db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class OptionTable(db.Document):
    meta = _meta
    type = db.StringField(required=True)
    option = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class Breeder(db.Document):
    meta = _meta
    farm_id = db.ReferenceField(Farm, required=True)
    username = db.StringField(required=True)
    password = db.StringField(required=True)
    name = db.StringField(required=True)
    nik = db.StringField(required=True)
    phone = db.StringField(required=True)

class SeedUsed(db.Document):
    meta = _meta
    fish_seed_id = db.ReferenceField(SeedInventory, required=True)
    farm_id = db.ReferenceField(Farm, required=True)
    original_amount = db.IntField(required=True)
    usage = db.IntField(required=True)
    pond = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class FeedName(db.Document):
    meta = _meta
    id_int = db.SequenceField(required=True)
    farm_id = db.ReferenceField(Farm, required=True)
    type = db.StringField(required=True)
    name = db.StringField(required=True)
    description = db.StringField(required=True)
    producer = db.StringField(required=True)
    protein = db.IntField(required=True)
    carbohydrate = db.IntField(required=True)
    min_expired_period = db.IntField(required=True)
    max_expired_period = db.IntField(required=True)
    image = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class FeedInventory(db.Document):
    meta = _meta
    feed_name_id = db.ReferenceField(FeedName, required=False)
    farm_id = db.ReferenceField(Farm, required=True)
    id_int = db.SequenceField(required=True)
    feed_category = db.StringField(required=True)
    brand_name = db.StringField(required=True)
    price = db.IntField(required=True)
    amount = db.FloatField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class FeedUsed(db.Document):
    meta = _meta
    fish_feed_id = db.ReferenceField(FeedInventory, required=True)
    farm_id = db.ReferenceField(Farm, required=True)
    original_amount = db.FloatField(required=True)
    usage = db.FloatField(required=True)
    pond = db.StringField(required=False)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class FeedAccumulation(db.Document):
    meta = _meta
    fish_feed_id = db.ReferenceField(FeedInventory, required=True)
    

class FeedHistory(db.Document):
    meta = _meta
    fish_feed_id = db.ReferenceField(FeedInventory, required=True)
    pond_id = db.ReferenceField(Pond, required=True)
    farm_id = db.ReferenceField(Farm, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=False)
    feed_dose = db.FloatField(required=True)
    feed_history_time = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class FeedDistribution(db.Document):
    meta = _meta
    farm_id = db.ReferenceField(Farm, required=True)
    fish_feed_id = db.ReferenceField(FeedInventory, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=False)
    feed_dose = db.FloatField(required=True)
    feed_dose_per_pond = db.FloatField(required=True)
    feed_history_time = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)
    image = db.StringField(required=True)

class SuplemenInventory(db.Document):
    meta = _meta
    id_int = db.SequenceField(required=True)
    farm_id = db.ReferenceField(Farm, required=True)
    function = db.StringField(required=True)
    name = db.StringField(required=True)
    description = db.StringField(required=True)
    price = db.IntField(required=True)
    amount = db.FloatField(required=True)
    type = db.StringField(required=True)
    min_expired_period = db.IntField(required=True)
    max_expired_period = db.IntField(required=True)
    image = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class SuplemenUsed(db.Document):
    meta = _meta
    fish_suplemen_id = db.ReferenceField(SuplemenInventory, required=True)
    farm_id = db.ReferenceField(Farm, required=True)
    original_amount = db.FloatField(required=True)
    usage = db.FloatField(required=True)
    pond = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class PondTreatment(db.Document):
    meta = _meta
    treatment_type_option = ("ringan", "berat", "pergantian air")
    farm_id = db.ReferenceField(Farm, required=True)
    suplemen_id = db.ReferenceField(SuplemenInventory, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    treatment_type = db.StringField(
        required=True, choices=treatment_type_option)
    usage = db.FloatField()
    description = db.StringField(default="")
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class TreatmentDistribution(db.Document):
    meta = _meta
    farm_id = db.ReferenceField(Farm, required=True)
    treatment_type = db.StringField()
    suplemen_id = db.ReferenceField(SuplemenInventory, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    usage = db.FloatField()
    usage_per_pond = db.FloatField()
    image = db.StringField(required=True)
    description = db.StringField(default="")
    created_at = db.DateTimeField(default=datetime.datetime.now)

class ElectricInventory(db.Document):
    meta = _meta
    id_int = db.SequenceField(required=True)
    farm_id = db.ReferenceField(Farm, required=True)
    type = db.StringField(required=True)
    name = db.StringField(required=True)
    daya = db.StringField()
    price = db.IntField(required=True)
    id_token = db.StringField()
    month = db.StringField()
    image = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class AssetInventory(db.Document):
    meta = _meta
    id_int = db.SequenceField(required=True)
    farm_id = db.ReferenceField(Farm, required=True)
    asset_category = db.StringField(required=True)
    name = db.StringField(required=True)
    description = db.StringField(required=True)
    amount = db.IntField(required=True)
    price = db.IntField(required=True)
    image = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class DeactivationRecap(db.Document):
    meta = _meta
    id_int = db.SequenceField(required=True)
    pond_id = db.ReferenceField(Pond, required=True)
    farm_id = db.ReferenceField(Farm, required=True)
    fish_seed_id = db.ReferenceField(SeedInventory, required=True)
    fish_weight = db.FloatField(required=True)
    fish_amount = db.IntField(required=True)
    fish_type = db.StringField(required=True)
    fish_category = db.StringField(required=True)
    fish_price = db.IntField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class Logging(db.Document):
    meta = _meta
    farm_id = db.ReferenceField(Farm)
    breeder_id = db.ReferenceField(Breeder)
    farm_name = db.StringField()
    breeder_name = db.StringField()
    start_at = db.DateTimeField()
    end_at = db.DateTimeField()
    duration = db.StringField()
    feature_name = db.StringField()

class FishHarvested(db.Document):
    meta = _meta
    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    fish = db.ListField()
    fcr = db.FloatField(defauit=0)
    total_fish_harvested = db.IntField(default=0)
    total_weight_harvested = db.FloatField(default=0)
    sample_amount = db.IntField(default=0)
    sample_weight = db.FloatField(default=0)
    sample_long = db.FloatField(default = 0)
    harvested_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class FishHarvestedPriceDetails(db.Document):
    meta = _meta
    fish_harvested_id = db.ReferenceField(FishHarvested, required=True)
    asset_price = db.IntField(required=True, default = 0)
    electric_price = db.IntField(required=True, default = 0)
    seed_price = db.IntField(required=True, default = 0)
    feed_price = db.IntField(required=True, default = 0)
    suplement_price = db.IntField(required=True, default = 0)
    total_price = db.IntField(required=True, default = 0)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class PriceAccumulator(db.Document):
    meta = _meta
    amount = db.IntField(required=True, default = 0)
    newPrice = db.IntField(required=True, default = 0)
    type = db.IntField(required=True, default = 0)

class AssetMonthlyPrice(db.Document):
    meta = _meta
    month = db.StringField(required=True)
    unitPrice = db.IntField(required=True)
    asetName = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

# class FeedType(db.Document):
#     fish_feed_id = db.ReferenceField(FeedInventory, required=True)
#     feed_type = db.StringField(required=True)
#     name = db.StringField(required=True)
#     protein = db.IntField(required=True)
#     carbohydrate = db.IntField(required=True)
#     created_at = db.DateTimeField(default=datetime.datetime.now)
#     updated_at = db.DateTimeField(default=datetime.datetime.now)
