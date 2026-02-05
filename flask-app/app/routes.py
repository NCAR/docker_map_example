from flask import Blueprint, jsonify, render_template, render_template_string, request, send_file
from .era5_plot import plot_png, NETCDF_FILE, VAR_NAME, TIME_NAME, LEV_NAME, PRES_NAME, LAT_NAME, LON_NAME
from pathlib import Path
import xarray as xr
import json
import os

#from .era5_plot import VARS_2D, VARS_3D, NTIME, nlev

NTIME = 0
NLEV = 0
NPLEV = 0
LATS = 0
LONS = 0
STIME = ""
ETIME = ""
VARS_2D = []
VARS_3D = []


# Store metadata for each dataset
DATASET_METADATA = {}

def scan_datasets():
    data_dir = Path(os.environ.get("MAP_DATA_DIR", "/output/model_predict"))
    print(data_dir)
    for d in data_dir.iterdir():
        print(d)
        if d.is_dir():
            #nc_file = d / "*.nc" # Assuming standard naming
            nc_file = f"{d}/*.nc"
            #if nc_file.exists():
            with xr.open_mfdataset(nc_file, engine="netcdf4", autoclose=True) as ds:
                DATASET_METADATA[d.name] = {
                    "ntime": len(ds.time),
                    "nlev": len(ds.get(LEV_NAME, [])),
                    "nplev": int(ds.sizes[PRES_NAME]),
                    "lats": int(ds.sizes[LAT_NAME]),
                    "lons": int(ds.sizes[LON_NAME]),
                    "stime": str(ds.time.values[0].astype("datetime64[s]")),
                    "etime": str(ds.time.values[-1].astype("datetime64[s]")),
                    "vars_2d": [v for v in ds.data_vars if len(ds[v].dims) <= 3],
                    "vars_3d": [v for v in ds.data_vars if len(ds[v].dims) > 3]
                }

scan_datasets()
print(DATASET_METADATA)

def openDataset():
    global NTIME, NLEV, NPLEV, LATS, LONS, STIME, ETIME, VARS_2D, VARS_3D
    with xr.open_mfdataset(NETCDF_FILE, engine="netcdf4", autoclose=True) as ds:
        try:
            NTIME = int(ds.sizes.get(TIME_NAME))
            NLEV = int(ds.sizes[LEV_NAME])
            NPLEV = int(ds.sizes[PRES_NAME])
            LATS = int(ds.sizes[LAT_NAME])
            LONS = int(ds.sizes[LON_NAME])
            STIME = str(ds.time.values[0].astype("datetime64[s]"))
            ETIME = str(ds.time.values[-1].astype("datetime64[s]"))
            
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
)

@map_blueprint.route("/")
def index():
    data_dir = Path(os.environ.get("MAP_DATA_DIR", "/output/model_predict"))
    dirs_with_mtime = [(d, d.stat().st_mtime) for d in data_dir.iterdir() if d.is_dir()]
    dirs_with_mtime.sort(key=lambda x: x[1], reverse=True)
    datasets = [d.name for d, _ in dirs_with_mtime]

    #datasets = [d.name for d in data_dir.iterdir() if d.is_dir()]

    return render_template(
        "map.html",
        datasets=datasets,
        metadata=DATASET_METADATA,
        vars_2d=VARS_2D,
        vars_3d=VARS_3D,
        ntime=NTIME,
        nlev=NLEV,
        nplev=NPLEV,
        nlat=LATS,
        nlon=LONS,
        stime=STIME,
        etime=ETIME
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
    data_dir = os.environ.get("fooMAP_DATA_DIR", "/output/model_predict")

    # Dictionary mapping directory -> list of files
    dir_files = {}

    for subdir in sorted(os.listdir(data_dir)):
        subdir_path = os.path.join(data_dir, subdir)
        if os.path.isdir(subdir_path):
            # List all files in this subdirectory
            files = sorted(os.listdir(subdir_path))
            dir_files[subdir] = files

    html = """
    <h1>model_predict Contents</h1>
    <ul>
    {% for dir, files in dir_files.items() %}
      <li>{{ dir }}
        <ul>
          {% for f in files %}
            <li>{{ f }}</li>
          {% endfor %}
        </ul>
      </li>
    {% endfor %}
    </ul>
    """

    return render_template_string(html, dir_files=dir_files)
    ##data_dir = os.environ.get("fooMAP_DATA_DIR", "/app/flask-app/data/model_predict")
    #data_dir = os.environ.get("fooMAP_DATA_DIR", "/output/model_predict")

    #files = os.listdir(data_dir)
    #files.sort()
    ##files=["foo", "bar", "baz", "boo"]

    ##predictFiles = os.listdir("/app/flask-app/data/model_predict/2026-01-28T06Z")
    ##predictFiles = os.listdir("/output/model_predict/2026-01-29T06Z")
    #predictFiles = os.listdir("/output/model_predict/2026-02-02T00Z")
    #files.append(predictFiles)

    #html = """
    #<h1>model_predict Contents</h1>
    #<ul>
    #{% for f in files %}
    #  <li>{{ f }}</li>
    #{% endfor %}
    #</ul>
    #"""

    #return render_template_string(html, files=files)

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
    dataset = request.args.get("dataset", default="")
    print("PLOT REQUEST DATASET =", dataset)
    buf = plot_png(dataset, t, lev, var_name)
    return send_file(buf, mimetype="image/png")
