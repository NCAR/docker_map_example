from flask import Blueprint, jsonify, render_template, render_template_string, request, send_file
from .era5_plot import plot_png, NETCDF_FILE, VAR_NAME, TIME_NAME, LEV_NAME, LAT_NAME, LON_NAME
from pathlib import Path
import xarray as xr
import json
import os

NTIME = 0
VARS_2D = []
VARS_3D = []

def openDataset1():
    with xr.open_mfdataset(NETCDF_FILE, engine="netcdf4", autoclose=True) as ds:
        NTIME = int(ds.sizes[TIME_NAME])
        # Filter variables to only 2D spatial (lat/lon) variables
        VARIABLES = []
        for var_name, da in ds.data_vars.items():
            dims = da.dims
            # Remove time dimension if present
            spatial_dims = [d for d in dims if d != TIME_NAME]
            if len(spatial_dims) == dimension and LAT_NAME in spatial_dims and LON_NAME in spatial_dims:
                    VARIABLES.append(var_name)

    ds = xr.open_mfdataset(
        NETCDF_FILE,
        engine="netcdf4",
        combine="by_coords"
    )

def openDataset():
    with xr.open_mfdataset(NETCDF_FILE, engine="netcdf4", autoclose=True) as ds:
        try:
            NTIME = int(ds.sizes.get(TIME_NAME, 1))

            for var_name, da in ds.data_vars.items():
                dims = da.dims
                if len(dims) == 2 and LAT_NAME in dims and LON_NAME in dims:
                    VARS_2D.append(var_name)
                elif (
                    len(dims) == 3
                    and LEV_NAME in dims
                    and LAT_NAME in dims
                    and LON_NAME in dims
                ):
                    VARS_3D.append(var_name)
            VARS_2D.sort()
            VARS_3D.sort()
            #return (
            #    NTIME,
            #    sorted(VARS_2D),
            #    sorted(VARS_3D),
            #)

        finally:
            ds.close()

openDataset()
print("VARS2D")
PRINT(VARS_2D)
print("VARS3D")
PRINT(VARS_3D)

map_blueprint = Blueprint(
    "map",
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static")
    #template_folder="../templates",
    #static_folder="../static"
)

@map_blueprint.route("/files")
def list_files():
    data_dir = os.environ.get("MAP_DATA_DIR", "/app/flask-app/data")
    local_dir = "/Users/vapor/docker_map_example/flask-app/data"
    if os.path.isdir(local_dir):
        append="local"
        data_dir = os.environ.get("MAP_DATA_DIR", local_dir)
    else:
        append="remote"
        data_dir = os.environ.get("MAP_DATA_DIR", "/output")
    #data_dir = os.environ.get("/output")

    files = os.listdir(data_dir)
    files.sort()
    files.append(append)
    files.append(data_dir)
    #files=["foo", "bar", "baz", "boo"]

    outputFileDir = os.listdir(data_dir + "/model_predict")
    files.append(outputFileDir)
    #outputFiles = os.listdir(data_dir + "/model_predict/2025-12-03T12Z")
    #files.append(outputFiles)

    html = """
    <h1>PVC Contents</h1>
    <ul>
    {% for f in files %}
      <li>{{ f }}</li>
    {% endfor %}
    </ul>
    """

    return render_template_string(html, files=files)

@map_blueprint.route("/model_predict")
def list_model_predict():
    data_dir = os.environ.get("fooMAP_DATA_DIR", "/app/flask-app/data/model_predict")

    files = os.listdir(data_dir)
    files.sort()
    #files=["foo", "bar", "baz", "boo"]

    predictFiles = os.listdir("/app/flask-app/data/model_predict/2026-01-28T06Z")
    files.append(predictFiles)

    html = """
    <h1>model_predict Contents</h1>
    <ul>
    {% for f in files %}
      <li>{{ f }}</li>
    {% endfor %}
    </ul>
    """

    return render_template_string(html, files=files)

#@map_blueprint.route("/data")
#def map_data():
#    #data_dir = os.environ.get("MAP_DATA_DIR", "/app/flask-app/data")
#    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#    data_dir = os.environ.get("MAP_DATA_DIR", os.path.join(BASE_DIR, "data"))
#    data_file = os.path.join(data_dir, "map.geojson")
#
#    with open(data_file) as f:
#        return jsonify(json.load(f))

@map_blueprint.route("/era5")
def era5_root():
    return jsonify(
        ok=True,
        message="GET /era5/plot?t=0 returns a PNG map of VAR_2T"
    )


@map_blueprint.route("/era5/info")
def era5_info():
    ds = xr.open_dataset(NETCDF_FILE)
    try:
        return jsonify({
            "path": NETCDF_FILE,
            "variable": VAR_NAME,
            "time_len": int(ds.dims[TIME_NAME]),
            "shape": [
                int(ds.dims[LAT_NAME]),
                int(ds.dims[LON_NAME])
            ],
            "lat_range": [
                float(ds[LAT_NAME].values.min()),
                float(ds[LAT_NAME].values.max())
            ],
            "lon_range": [
                float(ds[LON_NAME].values.min()),
                float(ds[LON_NAME].values.max())
            ]
        })
    finally:
        ds.close()

@map_blueprint.route("/era5/plot")
def era5_plot():
    t = request.args.get("t", default=0, type=int)
    var_name = request.args.get("var", default="t2m")
    buf = plot_png(t, var_name)
    return send_file(buf, mimetype="image/png")

@map_blueprint.route("/credit-map")
def map_view():
    return render_template(
        "map.html", 
        ntime=NTIME,
        vars_2d=VARS_2D,
        vars_3d=VARS_3D,
        default_var="t2m"
    )
    #return render_template(
    #    "map.html", 
    #    ntime=NTIME,
    #    variables=VARIABLES,
    #    default_var="t2m"
    #)

#@map_blueprint.route("/map")
#def map_view():
#    return render_template("openStreetMap.html")
#
