import xarray as xr
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import io
import os

from pathlib import Path

def newest_directory(parent: str) -> Path | None:
    parent_path = Path(parent)

    dirs = [d for d in parent_path.iterdir() if d.is_dir()]
    if not dirs:
        return None

    return max(dirs, key=lambda d: d.stat().st_mtime)

#NETCDF_FILE = os.environ.get("NETCDF_FILE", "/data/file.nc")
#NETCDF_FILE = os.environ.get("NETCDF_FILE", "/output/*.nc")
#NETCDF_FILE = os.environ.get("NETCDF_FILE", "/app/flask-app/data/model_predict/2026-01-28T06Z/*.nc")
#NETCDF_FILE = os.environ.get("NETCDF_FILE", "/app/flask-app/data/model_predict/2026-01-28T06Z/pred_2026-01-28T06Z_003.nc")
#NETCDF_FILE = os.environ.get("NETCDF_FILE", "/app/flask-app/data/model_predict/2026-01-28T06Z/*.nc")
print("NEWEST " + str(newest_directory("/app/flask-app/data/model_predict")))
NETCDF_FILE = os.environ.get("NETCDF_FILE", str(newest_directory("/app/flask-app/data/model_predict")) + "/*.nc")
#VAR_NAME = "VAR_2T"
VAR_NAME = "t2m"
TIME_NAME = "time"
LAT_NAME = "latitude"
LON_NAME = "longitude"
FILL_THRESHOLD = 1.0e20


def plot_png(t: int):
    #ds = xr.open_dataset(NETCDF_FILE)
    print("plot time" + str(t))
    ds = xr.open_mfdataset(NETCDF_FILE)
    try:
        da = ds[VAR_NAME]
        t = int(np.clip(t, 0, da.sizes[TIME_NAME] - 1))

        slice2d = da.isel({TIME_NAME: t}).astype("float64")
        arr = slice2d.values
        arr = np.where(arr > FILL_THRESHOLD, np.nan, arr)

        lat = ds[LAT_NAME].values
        lon = ds[LON_NAME].values

        lon_wrapped = ((lon + 180.0) % 360.0) - 180.0
        sort_idx = np.argsort(lon_wrapped)
        lon_sorted = lon_wrapped[sort_idx]
        arr_sorted = arr[:, sort_idx]

        fig = plt.figure(figsize=(9, 4.5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())

        #ax.coastlines()
        # skip coastlines if cartopy data isn't available
        try:
            ax.coastlines()
            ax.set_global()
        except Exception:
            pass

        vmin, vmax = da.min().values.item(), da.max().values.item()
        ax.imshow(arr_sorted, origin='lower', 
            extent=[lon_sorted.min(), lon_sorted.max(), lat.min(), lat.max()],
            transform=ccrs.PlateCarree(), 
            vmin=vmin, vmax=vmax)
        #mesh = ax.pcolormesh(
        #    lon_sorted, lat, arr_sorted,
        #    transform=ccrs.PlateCarree(),
        #    vmin=vmin,
        #    vmax=vmax
        #)
        time_val = da[TIME_NAME].isel({TIME_NAME: t}).values
        time_str = pd.Timestamp(time_val).strftime("%Y-%m-%d %H:%M UTC")
        plt.title(f"{VAR_NAME} (2 m temperature) - t={t} - {time_str}")
        plt.colorbar(mesh, ax=ax, orientation="horizontal",
                     pad=0.05, label="K")
        fig.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.10)
        #plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)

        return buf
    finally:
        ds.close()

