import json
from pymongo import MongoClient
from bson.objectid import ObjectId

class MongoOps:

    def __init__(self, conf):
        self.client = MongoClient("mongodb://"
                + conf["mongodb"]["user"]
                + ":"
                + conf["mongodb"]["pass"]
                + "@"
                + conf["mongodb"]["host"]
                + "/"
                + conf["mongodb"]["auth_db"]
            )

    # Some basic mongoDB functions

    get_dbs = lambda self: self.client.database_names()

    get_db_colls = lambda self, db: self.client[db].collection_names()

    get_coll_docs = lambda self, db, coll: deserialize_oids(list(self.client[db][coll].find()))

    get_document_by_oid = lambda self, db, coll, oid: deserialize_oids(
            self.client[db][coll].find_one({
                "_id": ObjectId(oid)
            })
        )

    def delete_by_oid(self, db, coll, oid):
        self.client[db][coll].delete_one({
            "_id": ObjectId(oid)
        })

        return "Document with oid " + oid +" deleted (if found)."

    def insert_document(self, db, coll, req_json):
        try:
            _id = self.client[db][coll].insert_one(req_json["document"]).inserted_id
            res = "Inserted document " + str(_id) + "."
        except:
            res = "Invalid document."
        return res

    def custom_find_filter(self, db, coll, req_json):
        try:
            _filter = objectify_ids(req_json["filter"])
            res = deserialize_oids(list(self.client[db][coll].find(_filter)))
        except:
            res = "Invalid request filter."
        return res

    def update_many_documents_by_filter(self, db, coll, req_json):
        res = []
        for update in req_json["updates"]:
            try:
                _filter = objectify_ids(update["filter"])
                update_op = objectify_ids(update["op"])
                res.append(self.client[db][coll].update_many(_filter, update_op).raw_result)
            except:
                res.append("Invalid request filter.")
        return res

def deserialize_oids(document):
    """Flask cannot serialize "ObjectID" type fields, so we recursively stringify them"""
    if isinstance(document, list):
        for e in document:
            deserialize_oids(e)

    elif isinstance(document, dict):
        if "_id" in document:
            document["_id"] = str(document["_id"])
        for k,v in document.items():
            deserialize_oids(v)

    return document

def objectify_ids(document):
    """Incoming filters will contain ObjectIds as strings"""
    if isinstance(document, list):
        for e in document:
            objectify_ids(e)

    elif isinstance(document, dict):
        if "_id" in document:
            document["_id"] = ObjectId(document["_id"])
        for k,v in document.items():
            objectify_ids(v)

    return document
