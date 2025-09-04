from fastapi import FastAPI, Response, Query
from fastapi.middleware.cors import CORSMiddleware
import xarray as xr
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import io
import os


app = FastAPI(title="ERA5 2m Temperature Plot API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


NETCDF_FILE = os.environ.get("NETCDF_FILE", "/data/file.nc")
VAR_NAME = "VAR_2T"
TIME_NAME = "time"
LAT_NAME = "latitude"
LON_NAME = "longitude"
FILL_THRESHOLD = 1.0e20 # treat >1e20 as missing


@app.get("/")
def root():
    return {"ok": True, "message": "GET /plot?t=0 returns a PNG map of VAR_2T at time index t."}


@app.get("/info")
def info():
    ds = xr.open_dataset(NETCDF_FILE)
    try:
        ntime = ds.dims[TIME_NAME]
        lat_shape = ds.dims[LAT_NAME]
        lon_shape = ds.dims[LON_NAME]
        return {
            "path": NETCDF_FILE,
            "variable": VAR_NAME,
            "time_len": int(ntime),
            "shape": [int(lat_shape), int(lon_shape)],
            "lat_range": [float(ds[LAT_NAME].values.min()), float(ds[LAT_NAME].values.max())],
            "lon_range": [float(ds[LON_NAME].values.min()), float(ds[LON_NAME].values.max())]
    }
    finally:
        ds.close()


@app.get("/plot", response_class=Response)
def plot_png(t: int = Query(0, ge=0)):
    ds = xr.open_dataset(NETCDF_FILE)
    try:
        da = ds[VAR_NAME]
        t = int(np.clip(t, 0, da.sizes[TIME_NAME]-1))
        slice2d = da.isel({TIME_NAME: t}).astype("float64")
        # mask fill values
        arr = slice2d.values
        arr = np.where(arr > FILL_THRESHOLD, np.nan, arr)


        lat = ds[LAT_NAME].values
        lon = ds[LON_NAME].values
        # Convert 0..360 -> -180..180 for nicer global view and sort longitudes
        lon_wrapped = ((lon + 180.0) % 360.0) - 180.0
        sort_idx = np.argsort(lon_wrapped)
        lon_sorted = lon_wrapped[sort_idx]
        arr_sorted = arr[:, sort_idx]


        fig = plt.figure(figsize=(9, 4.5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        try:
            ax.coastlines()
        except Exception:
            pass
        ax.set_global()
        mesh = ax.pcolormesh(lon_sorted, lat, arr_sorted, transform=ccrs.PlateCarree())
        plt.title(f"{VAR_NAME} (2 m temperature) — t={t}")
        plt.colorbar(mesh, ax=ax, orientation="horizontal", pad=0.05, label="K")
        plt.tight_layout()


        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return Response(content=buf.getvalue(), media_type="image/png")
    finally:
        ds.close()