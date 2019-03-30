import json
from functools import wraps
from mongo_ops import MongoOps
from flask import Flask, request, make_response

# Global conf

conf = json.loads(open("../config.json").read())
mops = MongoOps(conf)
application = Flask(__name__)

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

# Cache control

def jsonify(_json):
    resp = make_response(json.dumps(_json))
    resp.headers["Content-Type"] = "application/json"
    if "nocache" in request.args:
        resp.headers["Cache-Control"] = "no-cache, no-store"
    return resp

# API endpoints routes

@application.route("/")
@require_api_token
def main_route():
    return jsonify(mops.get_dbs())

@application.route("/<db>", strict_slashes=False)
@application.route("/<db>/<coll>", strict_slashes=False)
@require_api_token
@restrain_db_access
def db_route(db="", coll=None):
    if coll is None:
        return jsonify(mops.get_db_colls(db))
    else:
        return jsonify(mops.get_coll_docs(db, coll))

@application.route("/<db>/<coll>/oid/<doc_oid>", strict_slashes=False)
@require_api_token
@restrain_db_access
def document_by_oid_route(db, coll, doc_oid):
    return jsonify(mops.get_document_by_oid(db, coll, doc_oid))

@application.route("/<db>/<coll>/oid/<doc_oid>/delete", strict_slashes=False)
@require_api_token
@restrain_db_access
def del_document_by_oid(db, coll, doc_oid):
    return jsonify(mops.delete_documents_by_filter(
        db,
        coll,
        {"filter": {"_id": doc_oid}}
    ))

@application.route("/<db>/<coll>/oid/<doc_oid>/update", strict_slashes=False, methods=["POST"])
@require_api_token
@restrain_db_access
def update_document_by_oid(db, coll, doc_oid):
    return jsonify(mops.update_many_documents_by_filter(
        db,
        coll,
        {"updates": [{"filter": {"_id": doc_oid}, "op": request.get_json()["op"]}]}
    )[0])

@application.route("/<db>/<coll>/custom_filter", strict_slashes=False, methods=["POST"])
@require_api_token
@restrain_db_access
def custom_filter_route(db, coll):
    return jsonify(mops.custom_find_filter(db, coll, request.get_json()))

@application.route("/<db>/<coll>/insert", strict_slashes=False, methods=["POST"])
@require_api_token
@restrain_db_access
def insert_documents(db, coll):
    return jsonify(mops.insert_documents(db, coll, request.get_json()))

@application.route("/<db>/<coll>/update", strict_slashes=False, methods=["POST"])
@require_api_token
@restrain_db_access
def update_documents(db, coll):
    return jsonify(mops.update_many_documents_by_filter(db, coll, request.get_json()))

@application.route("/<db>/<coll>/delete", strict_slashes=False, methods=["POST"])
@require_api_token
@restrain_db_access
def delete_documents(db, coll):
    return jsonify(mops.delete_documents_by_filter(db, coll, request.get_json()))

@application.route("/<db>/<coll>/aggregate", strict_slashes=False, methods=["POST"])
@require_api_token
@restrain_db_access
def aggregate_route(db, coll):
    return jsonify(mops._aggregate(db, coll, request.get_json()))
