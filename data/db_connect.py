"""
All interaction with MongoDB should be through this file!
We may be required to use a new database at any point.
"""
import os

import pymongo as pm

from functools import wraps
from pymongo.errors import AutoReconnect, NetworkTimeout

import certifi 

LOCAL = "0"
CLOUD = "1"

SE_DB = 'seDB'

client = None

MONGO_ID = '_id'

MIN_ID_LEN = 4

user_nm = os.getenv('MONGO_USER_NM', 'mattiasshularsson_db_user')
cloud_svc = os.getenv('MONGO_HOST', 'cluster0.nbhhiox.mongodb.net')
passwd = os.environ.get("MONGO_PASSWD", '')
cloud_mdb = "mongodb+srv"
db_params = "retryWrites=false&w=majority"

# parameter names of mongo client settings
SERVER_API_PARAM = 'server_api'
CONN_TIMEOUT = 'connectTimeoutMS'
SOCK_TIMEOUT = 'socketTimeoutMS'
CONNECT = 'connect'
MAX_POOL_SIZE = 'maxPoolSize'

# Recommended Python Anywhere settings.
PA_MONGO = os.getenv('PA_MONGO', True)
PA_SETTINGS = {
    CONN_TIMEOUT: os.getenv('MONGO_CONN_TIMEOUT', 30000),
    SOCK_TIMEOUT: os.getenv('MONGO_SOCK_TIMEOUT', None),
    CONNECT: os.getenv('MONGO_CONNECT', False),
    MAX_POOL_SIZE: os.getenv('MONGO_MAX_POOL_SIZE', 1),
}

def needs_db(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        global client
        if not client:
            connect_db()
        return fn(*args, **kwargs)
    return wrapper

def retry_mongo(retries=3):   
    def deco(fn):             
        @wraps(fn)
        def wrapper(*args, **kwargs):  
            for attempt in range(retries):
                try:
                    return fn(*args, **kwargs)
                except (AutoReconnect, NetworkTimeout):
                    if attempt == retries - 1:
                        raise
        return wrapper
    return deco

class DBError(Exception):
    pass

def handle_errors(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except pm.errors.PyMongoError as e:
            raise DBError(str(e)) from e
    return wrapper

def connect_db():
    """
    This provides a uniform way to connect to the DB across all uses.
    Returns a mongo client object... maybe we shouldn't?
    Also set global client variable.
    We should probably either return a client OR set a
    client global.
    """
    global client
    if client is None:  # not connected yet!
        if os.environ.get('CLOUD_MONGO', LOCAL) == CLOUD:
            password = os.environ.get('MONGO_PASSWD')
            if not password:
                raise ValueError('You must set your password '
                                 + 'to use Mongo in the cloud.')
            print('Connecting to Mongo in the cloud.')
            client = pm.MongoClient(f'{cloud_mdb}://{user_nm}:{password}'
                                    + f'@{cloud_svc}/{SE_DB}'
                                    + f'?{db_params}',
                                    tlsCAFile=certifi.where(), **PA_SETTINGS)
            client.admin.command("ping")
            print("MongoDB ping successful")
        else:
            print("Connecting to Mongo locally.")
            client = pm.MongoClient()
    return client


def convert_mongo_id(doc: dict | None):
    if not doc:
        return
    if MONGO_ID in doc:
        doc[MONGO_ID] = str(doc[MONGO_ID])

@handle_errors
@retry_mongo()
@needs_db
def create(collection, doc, db=SE_DB):
    """
    Insert a single doc into collection.
    """
    print(f'{db=}')
    ret = client[db][collection].insert_one(doc)
    doc.pop(MONGO_ID, None)
    return str(ret.inserted_id)

@handle_errors
@retry_mongo()
@needs_db
def read_one(collection, filt, db=SE_DB):
    """
    Find with a filter and return on the first doc found.
    Return None if not found.
    """
    doc = client[db][collection].find_one(filt)
    if doc:
        convert_mongo_id(doc) 
    return doc   

@handle_errors
@retry_mongo()
@needs_db
def delete(collection: str, filt: dict, db=SE_DB):
    """
    Find with a filter and return on the first doc found.
    """
    print(f'{filt=}')
    del_result = client[db][collection].delete_one(filt)
    return del_result.deleted_count

@handle_errors
@retry_mongo()
@needs_db
def update(collection, filters, update_dict, db=SE_DB):
    res = client[db][collection].update_one(filters, {'$set': update_dict})
    return res.modified_count

@handle_errors
@retry_mongo()
@needs_db
def read(collection, db=SE_DB, no_id=True) -> list:
    """
    Returns a list from the db.
    """
    ret = []
    for doc in client[db][collection].find():
        if no_id:
            del doc[MONGO_ID]
        else:
            convert_mongo_id(doc)
        ret.append(doc)
    return ret

@handle_errors
@retry_mongo
@needs_db
def read_dict(collection, key, db=SE_DB, no_id=True) -> dict:
    recs = read(collection, db=db, no_id=no_id)
    recs_as_dict = {}
    for rec in recs:
        recs_as_dict[rec[key]] = rec
    return recs_as_dict

@handle_errors
@retry_mongo
@needs_db
def fetch_all_as_dict(key, collection, db=SE_DB):
    ret = {}
    for doc in client[db][collection].find():
        del doc[MONGO_ID]
        ret[doc[key]] = doc
    return ret

def is_valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True

