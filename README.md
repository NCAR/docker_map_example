# docker_map_example

1. Clone the repository
   
3. Add the NetCDF file

Place your ERA5 file in the data/ directory:

data/e5.oper.an.sfc.128_167_2t.ll025sc.2015050100_2015053123.nc

3. Build and run the app
   
docker compose up --build

4. Open in browser

Go to http://localhost:5173

Enter a time index (0–743, since this file has 744 hours = May 2015).

Click Generate Plot.
