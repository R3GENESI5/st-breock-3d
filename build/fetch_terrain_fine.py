"""Terrain at 0.01 deg for the 3D St Breock page (Copernicus DEM GLO-90 via the Open-Meteo elevation API,
commercial key from OPEN_METEO_API_KEY). Archive on Z:/Data/st_breock_2018-07-24, working copy here."""
import json, os, time, urllib.request
from pathlib import Path

LON = [round(-5.10 + 0.01 * i, 3) for i in range(71)]   # -5.10 .. -4.40
LAT = [round(50.25 + 0.01 * j, 3) for j in range(56)]   # 50.25 .. 50.80
pts = [(la, lo) for la in LAT for lo in LON]
elev = []
for i in range(0, len(pts), 100):
    chunk = pts[i:i + 100]
    url = ("https://customer-api.open-meteo.com/v1/elevation?apikey=" + os.environ["OPEN_METEO_API_KEY"]
           + "&latitude=" + ",".join(str(p[0]) for p in chunk) + "&longitude=" + ",".join(str(p[1]) for p in chunk))
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                elev += json.load(r)["elevation"]
            break
        except Exception:
            time.sleep(5 * (attempt + 1))
    else:
        raise SystemExit("elevation request failed")
    time.sleep(0.3)
out = {"source": "Open-Meteo elevation API (Copernicus DEM GLO-90), 0.01 deg, fetched 2026-10-27",
       "lat": LAT, "lon": LON, "elevation_m": [elev[j * len(LON):(j + 1) * len(LON)] for j in range(len(LAT))]}
for d in (Path("Z:/Data/st_breock_2018-07-24"), Path(__file__).parent):
    (d / "terrain_grid_001.json").write_text(json.dumps(out), encoding="utf-8")
print(len(elev), "points; max", max(elev), "m")
