"""ERA5 hourly 10 m wind on its 0.25 deg grid over the St Breock map, 24 July 2018 (UTC), via the Open-Meteo
historical archive (models=era5, commercial key from OPEN_METEO_API_KEY). Reanalysis, not measurement.
Archive on Z:/Data/st_breock_2018-07-24, working copy here."""
import json, os, urllib.request
from pathlib import Path

LAT = [50.25, 50.5, 50.75]
LON = [-5.25, -5.0, -4.75, -4.5, -4.25]
pts = [(la, lo) for la in LAT for lo in LON]
url = ("https://customer-archive-api.open-meteo.com/v1/archive?apikey=" + os.environ["OPEN_METEO_API_KEY"]
       + "&latitude=" + ",".join(str(p[0]) for p in pts) + "&longitude=" + ",".join(str(p[1]) for p in pts)
       + "&start_date=2018-07-24&end_date=2018-07-24&models=era5&timezone=GMT&wind_speed_unit=ms"
       + "&hourly=wind_speed_10m,wind_direction_10m")
with urllib.request.urlopen(url, timeout=120) as r:
    d = json.load(r)
cells = [{"lat_req": la, "lon_req": lo, "lat": c["latitude"], "lon": c["longitude"],
          "time_utc": c["hourly"]["time"], "speed_ms": c["hourly"]["wind_speed_10m"], "dir_deg": c["hourly"]["wind_direction_10m"]}
         for (la, lo), c in zip(pts, d)]
out = {"source": "ERA5 (Hersbach et al. 2020) via Open-Meteo historical archive, models=era5, 10 m wind, hourly UTC, fetched 2026-10-27",
       "cells": cells}
for dd in (Path("Z:/Data/st_breock_2018-07-24"), Path(__file__).parent):
    (dd / "era5_wind_grid_2018-07-24.json").write_text(json.dumps(out), encoding="utf-8")
c = cells[7]
print(len(cells), "cells; e.g.", c["lat"], c["lon"], "15 UTC", c["speed_ms"][15], "m/s from", c["dir_deg"][15])
