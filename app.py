import json
from functools import wraps
from mongo_ops import MongoOps
from flask import Flask, jsonify, request

# Global conf

conf = json.loads(open("config.json").read())
mops = MongoOps(conf)
app = Flask(__name__)

# Some basic security

def require_api_token(f):
    """Some simple token-based auth"""
    @wraps(f)
    def validate_token(*args, **kwargs):
        if "token" not in request.headers or request.headers["token"] not in conf["tokens"]:
            return jsonify("Access denied.")

        return f(*args, **kwargs)

    return validate_token

def restrain_db_access(f):
    """We want to disallow access to some dbs from the routes"""
    @wraps(f)
    def check_args(*args, **kwargs):
        if kwargs["db"] in conf["blacklisted_dbs"]:
            return jsonify("Access denied.")

        return f(*args, **kwargs)

    return check_args

# API endpoints routes

@app.route("/")
@require_api_token
def main_route():
    return jsonify(mops.get_dbs())

@app.route("/<db>", strict_slashes=False)
@app.route("/<db>/<coll>", strict_slashes=False)
@require_api_token
@restrain_db_access
def db_route(db="", coll=None):
    if coll is None:
        return jsonify(mops.get_db_colls(db))
    else:
        return jsonify(mops.get_coll_docs(db, coll))

@app.route("/<db>/<coll>/oid/<doc_oid>", strict_slashes=False)
@app.route("/<db>/<coll>/oid/<doc_oid>/<op>", strict_slashes=False)
@require_api_token
@restrain_db_access
def document_by_oid_route(db, coll, doc_oid, op=None):
    if op is None:
        return jsonify(mops.get_document_by_oid(db, coll, doc_oid))
    else:
        if op == "delete":
            return jsonify(mops.delete_by_oid(db, coll, doc_oid))

@app.route("/<db>/<coll>/custom_filter", strict_slashes=False, methods=["POST"])
@require_api_token
@restrain_db_access
def custom_filter_route(db, coll):
    return jsonify(mops.custom_find_filter(db, coll, request.get_json()))

@app.route("/<db>/<coll>/insert", strict_slashes=False, methods=["POST"])
@require_api_token
@restrain_db_access
def insert_document(db, coll):
    return jsonify(mops.insert_document(db, coll, request.get_json()))

@app.route("/<db>/<coll>/update", strict_slashes=False, methods=["POST"])
@require_api_token
@restrain_db_access
def update_documents(db, coll):
    return jsonify(mops.update_documents_by_filter(db, coll, request.get_json()))
