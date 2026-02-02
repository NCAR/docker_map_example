from flask import Blueprint, jsonify, render_template, render_template_string, request, send_file
from .era5_plot import plot_png, NETCDF_FILE, VAR_NAME, TIME_NAME, LEV_NAME, PRES_NAME, LAT_NAME, LON_NAME
from pathlib import Path
import xarray as xr
import json
import os

#from .era5_plot import VARS_2D, VARS_3D, NTIME, nlev

NTIME = 0
NLEV = 0
VARS_2D = []
VARS_3D = []

def openDataset():
    global NTIME, NLEV, VARS_2D, VARS_3D
    with xr.open_mfdataset(NETCDF_FILE, engine="netcdf4", autoclose=True) as ds:
        try:
            NTIME = int(ds.sizes.get(TIME_NAME))
            NLEV = int(ds.sizes[LEV_NAME])
            print(NTIME)
            print(NLEV)
            for var_name, da in ds.data_vars.items():
                dims = da.dims
                if TIME_NAME in dims and (LEV_NAME in dims or PRES_NAME in dims) and LAT_NAME in dims and LON_NAME in dims:
                    VARS_3D.append(var_name)
                elif TIME_NAME in dims and LAT_NAME in dims and LON_NAME in dims:
                    VARS_2D.append(var_name)
            VARS_2D.sort()
            VARS_3D.sort()
        finally:
            ds.close()

openDataset()

map_blueprint = Blueprint(
    "map",
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static")
    #template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    #static_folder=os.path.join(os.path.dirname(__file__), "static")
    #template_folder="../templates",
    #static_folder="../static"
)

@map_blueprint.route("/")
def index():
    #datasets = [d.name for d in DATA_ROOT.iterdir() if d.is_dir()]
    data_dir = Path(os.environ.get("MAP_DATA_DIR", "/output/model_predict"))
    datasets = [d.name for d in data_dir.iterdir() if d.is_dir()]
    print("datasets :")
    print(datasets)

    return render_template(
        "map.html",
        datasets=datasets,
        vars_2d=VARS_2D,
        vars_3d=VARS_3D,
        ntime=NTIME,
        nlev=NLEV
    )

@map_blueprint.route("/files")
def list_files():
    #data_dir = os.environ.get("MAP_DATA_DIR", "/app/flask-app/data")
    data_dir = os.environ.get("MAP_DATA_DIR", "/output")
    #local_dir = "/Users/vapor/docker_map_example/flask-app/data"
    #if os.path.isdir(local_dir):
    #    append="local"
    #    data_dir = os.environ.get("MAP_DATA_DIR", local_dir)
    #else:
    #    append="remote"
    #    data_dir = os.environ.get("MAP_DATA_DIR", "/output")

    print("DATA DIR" + data_dir)
    files = os.listdir(data_dir)
    files.sort()
    #files.append(append)
    files.append(data_dir)

    outputFileDir = os.listdir(data_dir + "/model_predict")
    files.append(outputFileDir)
    #outputFiles = os.listdir(data_dir + "/model_predict/2025-12-03T12Z")
    #files.append(outputFiles)

    html = """
    <h1>PVC Contents!</h1>
    <ul>
    {% for f in files %}
      <li>{{ f }}</li>
    {% endfor %}
    </ul>
    """

    return render_template_string(html, files=files)

@map_blueprint.route("/model_predict")
def list_model_predict():
    #data_dir = os.environ.get("fooMAP_DATA_DIR", "/app/flask-app/data/model_predict")
    data_dir = os.environ.get("fooMAP_DATA_DIR", "/output/model_predict")

    files = os.listdir(data_dir)
    files.sort()
    #files=["foo", "bar", "baz", "boo"]

    #predictFiles = os.listdir("/app/flask-app/data/model_predict/2026-01-28T06Z")
    #predictFiles = os.listdir("/output/model_predict/2026-01-29T06Z")
    predictFiles = os.listdir("/output/model_predict/2026-02-02T00Z")
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
    lev = request.args.get("lev", default=0, type=int)
    var_name = request.args.get("var", default="t2m")
    buf = plot_png(t, lev, var_name)
    return send_file(buf, mimetype="image/png")

@map_blueprint.route("/credit-map")
def map_view():
    return render_template(
        "map.html", 
        ntime=int(NTIME),
        nlev=int(NLEV),
        vars_2d=VARS_2D,
        vars_3d=VARS_3D,
        default_var="t2m"
    )
