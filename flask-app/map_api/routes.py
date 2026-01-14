from flask import Blueprint, jsonify, render_template
import json
import os

map_blueprint = Blueprint(
    "map",
    __name__,
    template_folder="../app/templates",
    static_folder="../app/static"
)

@map_blueprint.route("/")
def map_view():
    return render_template("map.html")

@map_blueprint.route("/data")
def map_data():
    data_dir = os.environ.get("MAP_DATA_DIR", "/app/flask-app/data")
    data_file = os.path.join(data_dir, "map.geojson")

    with open(data_file) as f:
        return jsonify(json.load(f))


#from flask import Blueprint, jsonify, render_template
#import os
#import json
#
#map_blueprint = Blueprint(
#    "map",
#    __name__,
#    template_folder="../templates",
#    static_folder="../static"
#)
#
#@map_blueprint.route("/")
#def map_view():
#    return render_template("map.html")
#
#@map_blueprint.route("/data")
#def map_data():
#    data_path = os.environ.get(
#        "MAP_DATA_DIR",
#        "/app/flask-app/data"
#    )
#
#    with open(os.path.join(data_path, "example.json")) as f:
#        return jsonify(json.load(f))
#
