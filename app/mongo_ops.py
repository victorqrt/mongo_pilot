import app, json
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
                + conf["mongodb"]["auth_db"],
                connect=False
            )

    # Some basic mongoDB functions

    get_dbs = lambda self: list(
        filter(
            lambda db: db not in app.conf["blacklisted_dbs"],
            self.client.database_names()
        )
    )

    get_db_colls = lambda self, db: self.client[db].collection_names()

    get_coll_docs = lambda self, db, coll: deserialize_oids(list(self.client[db][coll].find()))

    get_document_by_oid = lambda self, db, coll, oid: deserialize_oids(
            self.client[db][coll].find_one({
                "_id": ObjectId(oid)
            })
        )

    def insert_documents(self, db, coll, req_json):
        try:
            _ids = self.client[db][coll].insert_many(objectify_ids(req_json["documents"])).inserted_ids
            res = list(map(lambda x: "Inserted document at ObjectId " + str(x), _ids))
        except:
            res = "Insert failed; are all documents valid ?"
        return res

    def custom_find_filter(self, db, coll, req_json):
        try:
            _filter = objectify_ids(req_json["filter"])
            res = deserialize_oids(list(self.client[db][coll].find(_filter)))
        except:
            res = "Invalid request filter."
        return res

    def delete_documents_by_filter(self, db, coll, req_json):
        try:
            _filter = objectify_ids(req_json["filter"])
            res = "Deleted " + str(self.client[db][coll].delete_many(_filter).deleted_count) + " documents."
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

    def _aggregate(self, db, coll, req_json):
        try:
            res = deserialize_oids(list(self.client[db][coll].aggregate(req_json["pipeline"])))
        except:
            res = "Invalid aggregation pipeline."
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
