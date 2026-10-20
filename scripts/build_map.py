"""Build map.json (pre-projected SVG paths) from Open Alberta's
"Provincial Electoral Division - Current 2019" boundaries (Open Government Licence - Alberta).
Run once: python3 scripts/build_map.py map.json"""
import json, math, subprocess, sys

SVC = ("https://geospatial.alberta.ca/titan/rest/services/boundary/"
       "goa_administrative_area_10tm_nad83_aep/MapServer/3/query"
       "?where={w}&outFields=EDNUMBER,EDNAME&outSR=4326&f=geojson&maxAllowableOffset={o}")

def get(where, offset):
    url = SVC.format(w=where.replace(" ", "%20").replace("'", "%27").replace("=", "%3D").replace("<", "%3C").replace(">", "%3E"), o=offset)
    return json.loads(subprocess.run(["curl", "-sS", "-m", "90", "--fail", url], capture_output=True, check=True).stdout)

def rings(geom):
    if geom["type"] == "Polygon":
        return geom["coordinates"]
    return [r for poly in geom["coordinates"] for r in poly]

def build(features, width, pad=4, min_area=0.0):
    pts = [p for f in features for r in rings(f["geometry"]) for p in r]
    lon0 = min(p[0] for p in pts); lon1 = max(p[0] for p in pts)
    lat0 = min(p[1] for p in pts); lat1 = max(p[1] for p in pts)
    c = math.cos(math.radians((lat0 + lat1) / 2))
    k = (width - 2 * pad) / ((lon1 - lon0) * c)
    height = (lat1 - lat0) * k + 2 * pad
    out = {}
    for f in features:
        num = f["properties"]["EDNUMBER"].zfill(2)
        parts = []
        for r in rings(f["geometry"]):
            xy = [((x - lon0) * c * k + pad, (lat1 - y) * k + pad) for x, y in r]
            # drop sub-pixel rings (tiny islands) and consecutive duplicate points
            xs = [p[0] for p in xy]; ys = [p[1] for p in xy]
            if (max(xs) - min(xs)) * (max(ys) - min(ys)) < min_area:
                continue
            seg, last = [], None
            for x, y in xy:
                q = (round(x, 1), round(y, 1))
                if q != last:
                    seg.append(q); last = q
            if len(seg) >= 3:
                parts.append("M" + "L".join(f"{x:g},{y:g}" for x, y in seg) + "Z")
        out[num] = "".join(parts)
    return {"w": width, "h": round(height, 1), "d": out}

ab = get("1=1", 0.004)["features"]
fine = get("1=1", 0.0004)["features"]
cal = [f for f in fine if 1 <= int(f["properties"]["EDNUMBER"]) <= 26]
edm = [f for f in fine if 27 <= int(f["properties"]["EDNUMBER"]) <= 46]
for name, fs, n in [("ab", ab, 87), ("cal", cal, 26), ("edm", edm, 20)]:
    assert len(fs) == n, (name, len(fs))
names = {f["properties"]["EDNUMBER"].zfill(2): f["properties"]["EDNAME"] for f in ab}
names["17"] = "Calgary-Bhullar-McCall"  # renamed since the 2019 boundary file; matches the results feed
m = {"ab": build(ab, 300, min_area=0.2), "cal": build(cal, 220, min_area=0.5), "edm": build(edm, 220, min_area=0.5), "names": names}
json.dump(m, open(sys.argv[1] if len(sys.argv) > 1 else "map.json", "w"), separators=(",", ":"))
print({k: len(json.dumps(v)) for k, v in m.items()})
