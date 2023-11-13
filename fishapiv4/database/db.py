from flask_mongoengine import MongoEngine
from flask import current_app
from pymongo import MongoClient

db = MongoEngine()
alias_connection = 'new_connection'

def initialize_db(app):
    db.init_app(app)

def get_db():
    
    mongocon = current_app.config['MONGO_CON']
    dbclient = MongoClient(mongocon)
    
    dbs = dbclient[current_app.config['MONGODB_DB']]
    
    return dbs

def get_collection(name):
    dbs = get_db()
    return dbs[name]

def aggregate(name, pipeline):
    collection = get_collection(name)
    data = collection.aggregate(pipeline)
    return data