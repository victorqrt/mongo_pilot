mongo_pilot
===========

An API to do simple ops on mongoDB

Synopsis
--------

This API comes in handy when you need to perform simple CRUD operations on mongoDB databases using http requests.
It was designed to avoid using any client driver when accessing the DB (via Excel spreadsheets or scripts
for instance).

For now, it does not expose endpoints to use the aggregate or map/reduce framework, but it might in the future.

Usage
-----

- Prerequisites: make, bash, python, virtualenv

- Generate the environmnent with its dependencies: `make`

- Fill in the `config.json` file

- Start the API: `./run`

Documentation
-------------

All requests need an authentication token in their http header as the `token` field.
The API will not allow access to DBs that are specified in the `blacklisted_dbs` field of the config JSON file.

- Endpoints

    - `/` (GET)
      Lists all DBs on your mongo server instance. Will list blacklisted DBs.

    - `/<db>` (GET)
      Lists all collections in the specified db.

    - `/<db>/<coll>` (GET)
      Lists all documents in the specified collection.

    - `/<db>/<coll>/custom_filter` (POST)
      Performs a `find()` operation on the specified collection, applying the given filter.
      The filter is to be sent in the request payload's `filter` JSON field.

    - `/<db>/<coll>/insert` (POST)
      Inserts documents in the specified collection.
      The documents are to be sent as a list in the request payload's `documents` JSON field.

    - `/<db>/<coll>/update` (POST)
      Updates documents in the specified collection.
      The payload has to contain an `updates` field containing a list of updates to perform.
      The mongoDB update operation specified in the `op` field of each of the updates will be applied to all
      documents in the collection matching the filter specified in the `filter` field.
      The response will contain the update reports in the same order as in the sent request.

    - `/<db>/<coll>/delete` (GET)
      Deletes all documents matching the `filter` field in the collection.

    - `/<db>/<coll>/oid/<doc_oid>` (GET)
      Returns the document corresponding to the specified ObjectId (if it exists).

    - `/<db>/<coll>/oid/<doc_oid>/delete` (GET)
      Deletes the document corresponding to the specified ObjectId (if it exists).

    - `/<db>/<coll>/oid/<doc_oid>/update` (POST)
      Performs an update operation on the document corresponding to the specified ObjectId. The operation
      is to be specified as the `op` field of the payload.

- Misc

    - Passing the `?nocache` parameter to the query string will send back a response containing a
      `Cache-Control` header to avoid caching from your client when performing the same query multiple times.

WSGI
----

The API supports deployment through uwsgi for production use through unix sockets and the uwsgi protocol. This deployment mode is meant to be used with a web server such as nginx.

Run `make wsgi` to prepare the environment for uwsgi deployment. You will need a C compiler such as gcc or clang as well
as the python headers (the `python3-dev` package on Debian 9 for instance).
