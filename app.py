#!/usr/bin/env python3
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
#from sqlalchemy import create_engine
#from json import dumps
from flask import jsonify
from wikidata import WikiData

app = Flask(__name__)
#api = Api(app)

default_language = "en"
wd = WikiData()

@app.route("/")
def api():
    # Parse and sanitize parameters
    parser = reqparse.RequestParser()
    parser.add_argument("q", type=str)
    parser.add_argument("lang", type=str, default=default_language)
    parser.add_argument("mode", type=str, default="short" ) # short/long
    parser.add_argument("links", type=str, default="text" ) # text/wikidata/wikipedia/wiki/reasonator
    parser.add_argument("redlinks", type=str, default="" ) # ""/autodesc/reasonator
    parser.add_argument("format", type=str, default="jsonfm" ) # jsonfm/json/html
    parser.add_argument("get_infobox", type=str, default="yes" ) # yes/""
    parser.add_argument("infobox_template", type=str, default="" )
    args = parser.parse_args()
    if args["lang"] == "any" or args["lang"] == "":
        args["lang"] = default_language
    if args["q"] is None or args["q"] == "":
        return html()
    if args["q"].isnumeric():
        args["q"] = f"Q{args['q']}"
    else:
        args["q"] = args["q"].upper()
    # TODO check pattern Qxxx



    return jsonify(args)

def html():
    with open("index.html", "r") as file:
        data = file.read()
        return data


#api.add_resource(All, "/")

if __name__ == "__main__":
    app.run(port="5002")
