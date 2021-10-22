#!/usr/bin/env python3
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
# from sqlalchemy import create_engine
import json
from flask import jsonify
from html import escape
from wikidata import WikiData
from short_desc import ShortDescription
from infobox import InfoboxGenerator

app = Flask(__name__)
app.config["FLASK_ENV"] = "development"

html_header = "<!DOCTYPE html><html><head><meta charset=\"utf-8\"> </head><body>"
default_language = "en"


@app.route("/")
def api():
	# Parse and sanitize parameters
	parser = reqparse.RequestParser()
	parser.add_argument("q", type=str)
	parser.add_argument("lang", type=str, default=default_language)
	parser.add_argument("mode", type=str, default="short")  # short/long
	parser.add_argument("links", type=str, default="text")  # text/wikidata/wikipedia/wiki/reasonator
	parser.add_argument("redlinks", type=str, default="")  # ""/autodesc/reasonator
	parser.add_argument("format", type=str, default="jsonfm")  # jsonfm/json/html
	parser.add_argument("get_infobox", type=str, default="yes")  # yes/""
	parser.add_argument("infobox_template", type=str, default="")
	parser.add_argument("callback", type=str, default=None)
	args = parser.parse_args()
	original_args = args.copy()
	if args["lang"] == "any" or args["lang"] == "":
		args["lang"] = default_language
	if args["q"] is None or args["q"] == "":
		return index_html()

	if args["q"].isnumeric():
		q = f"Q{args['q']}"
	else:
		q = args["q"].upper()
	args["q"] = q
	# TODO check pattern Qxxx

	try:
		wd = WikiData()
		sd = ShortDescription(wd)
		result = sd.loadItem(q, args)
	except:
		result = [q, "<i>Automatic description is not available</i>"]

	output = str(result[1])
	if args["links"] == "wiki" and args["get_infobox"] == "yes":
		ig = InfoboxGenerator(wd)
		infobox = ig.get_filled_infobox(args)
		output = infobox + output

	j = {
		"call": original_args,
		"q": args["q"],
		"label": wd.items[q].getLabel(args["lang"]),
		"manual_description": wd.items[q].getDesc(args["lang"]),
		"result": output
	}

	if args["format"] == "html":
		html = html_header
		html += "<style>a.redlink { color:red }</style>"
		html += "<h1>" + j["label"] + " (<a href='//www.wikidata.org/wiki/" + q + "'>" + q + "</a>)</h1>"
		if args.links == 'wiki':
			html += "<pre style='white-space:pre-wrap;font-size:11pt'>" + j["result"] + "</pre>"
		else:
			html += "<p>" + j["result"] + "</p>"
		html += "<hr/><div style='font-size:8pt;'>This text was generated automatically from Wikidata using <a href='/autodesc/?'>AutoDesc</a>.</div>"
		html += "</body></html>"
		return html
	elif args["format"] == "jsonfm":
		json_link = []
		for (k, v) in args.items():
			json_link.append(k + "=" + escape("json" if k == "format" else str(v)))
		json_link = "<a href='?" + "&".join(json_link) + "'>format=json</a>"
		html = html_header
		html += "<p>You are looking at the HTML representation of the JSON format. HTML is good for debugging, but is unsuitable for application use.</p>"
		html += "<p>Specify the format parameter to change the output format. To see the non-HTML representation of the JSON format, set " + json_link + ".</p>"
		html += "<hr/><pre style=\"white-space:pre-wrap\">"
		html += json.dumps(j, indent=4);
		html += "</pre>"
		html += "</body></html>"
		return html
	else:
		if "callback" in args:
			return args["callback"] + "(" + json.dumps(j) + ")"
		else:
			return jsonify(j)


def index_html():
	with open("index.html", "r") as file:
		data = file.read()
		return data


if __name__ == "__main__":
	app.run(debug=True)
