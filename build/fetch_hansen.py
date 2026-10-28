"""Tree cover for the St Breock 3D page from Hansen et al. Global Forest Change (GFC-2023-v1.11), tile 60N_010W.
Reads only the map window over HTTP (no full-tile download): treecover2000 (% canopy, trees >5 m, 2000) and lossyear
(year of loss, 1 = 2001 ... 23 = 2023). Tree cover in 2018 is taken as treecover2000 with loss in 2001-2018 set to 0
(gain is not added; Hansen's gain layer is a 2000-2012 flag, not a percentage).
Saves the 30 m window to Z:/Data/st_breock_2018-07-24 and a 0.005 deg aggregate (mean % cover) here.
Source: Hansen, M.C. et al. (2013) Science 342, 850-853; data https://glad.earthengine.app/view/global-forest-change"""
import json
from pathlib import Path
import numpy as np
import rasterio
from rasterio.windows import from_bounds

BASE = "/vsicurl/https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_{}_60N_010W.tif"
W, S, E, N = -5.10, 50.25, -4.40, 50.80
ARCH = Path("Z:/Data/st_breock_2018-07-24")
HERE = Path(__file__).parent

layers = {}
for name in ("treecover2000", "lossyear"):
    with rasterio.open(BASE.format(name)) as src:
        win = from_bounds(W, S, E, N, src.transform).round_offsets().round_lengths()
        arr = src.read(1, window=win)
        tr = src.window_transform(win)
        prof = src.profile | {"height": arr.shape[0], "width": arr.shape[1], "transform": tr, "compress": "deflate", "tiled": False}
        with rasterio.open(ARCH / f"hansen_{name}_st_breock.tif", "w", **prof) as dst:
            dst.write(arr, 1)
        layers[name] = (arr, tr)
        print(name, arr.shape, "max", int(arr.max()))

tc, tr = layers["treecover2000"]
loss = layers["lossyear"][0]
tc2018 = np.where((loss >= 1) & (loss <= 18), 0, tc).astype(np.float32)

# aggregate to 0.005 deg cells (about 350 m x 560 m): mean canopy %, rows north -> south
step = 0.005
nlon, nlat = round((E - W) / step), round((N - S) / step)
px = abs(tr.a)
k = int(round(step / px))
H, Wd = tc2018.shape
agg = tc2018[: (H // k) * k, : (Wd // k) * k].reshape(H // k, k, Wd // k, k).mean(axis=(1, 3))
out = {"source": "Hansen et al. (2013), GFC-2023-v1.11, tile 60N_010W: treecover2000 with loss 2001-2018 removed; "
                  "mean canopy cover (%) per 0.005 deg cell, rows from north to south",
       "west": W, "north": float(tr.f), "step": step, "rows": agg.shape[0], "cols": agg.shape[1],
       "cover_pct": [[round(float(v), 1) for v in row] for row in agg],
       "loss_2001_2018_pixels": int(((loss >= 1) & (loss <= 18)).sum())}
(HERE / "hansen_cover_0005.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
print("aggregate", agg.shape, "mean cover %", round(float(agg.mean()), 1), "cells >30 %", int((agg > 30).sum()),
      "lost pixels 2001-18", out["loss_2001_2018_pixels"])
