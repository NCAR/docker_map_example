import xarray as xr
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import io
import os

#NETCDF_FILE = os.environ.get("NETCDF_FILE", "/data/file.nc")
#NETCDF_FILE = os.environ.get("NETCDF_FILE", "/output/*.nc")
NETCDF_FILE = os.environ.get("NETCDF_FILE", "/app/flask-app/data/model_predict/2026-01-28T06Z/*.nc")
#VAR_NAME = "VAR_2T"
VAR_NAME = "t2m"
TIME_NAME = "time"
LAT_NAME = "latitude"
LON_NAME = "longitude"
FILL_THRESHOLD = 1.0e20


def plot_png(t: int):
    ds = xr.open_dataset(NETCDF_FILE)
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
        #ax.coastlines()
        # skip coastlines if cartopy data isn't available
        try:
            ax.coastlines()
            ax.set_global()
        except Exception:
            pass

        mesh = ax.pcolormesh(
            lon_sorted, lat, arr_sorted,
            transform=ccrs.PlateCarree()
        )

        plt.title(f"{VAR_NAME} (2 m temperature) — t={t}")
        plt.colorbar(mesh, ax=ax, orientation="horizontal",
                     pad=0.05, label="K")
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)

        return buf
    finally:
        ds.close()

