"""Fetch Elections Alberta 2026 referendum results and write data.json.
Prints CHANGED when the numbers differ from the existing file, else SAME."""
import datetime, json, os, re, subprocess, sys

PAGE = "https://results.elections.ab.ca/8400"
WARDS = ",".join(f"{i:02d}" for i in range(1, 88))
DATA = "https://results.elections.ab.ca/data/8400?version={v}&questions=1,2,3,4,5,6,7,8,9,11&wards=" + WARDS
OUT = sys.argv[1] if len(sys.argv) > 1 else "data.json"
VER_FILE = "/tmp/ab_version"
UA = "Mozilla/5.0 (referendum dashboard)"

def get(url):
    return subprocess.run(["curl", "-sS", "-m", "25", "--fail", "-A", UA, url],
                          capture_output=True, check=True).stdout.decode()

def version(refresh=False):
    if not refresh and os.path.exists(VER_FILE):
        return open(VER_FILE).read().strip()
    v = re.search(r"version: '([^']+)'", get(PAGE)).group(1)
    open(VER_FILE, "w").write(v)
    return v

d = json.loads(get(DATA.format(v=version())))
if d.get("forceFullRefresh") or "referendumResults" not in d:
    d = json.loads(get(DATA.format(v=version(refresh=True))))

rr = d["referendumResults"]
w = rr["widgets"]
types = []
for key, name in [("advance", "Advance"), ("votingDay", "Election day"), ("vbm", "Mail-in"), ("mobile", "Mobile")]:
    x = w.get(key) or {}
    types.append({"name": name, "valid": x.get("valid"), "pct": x.get("percentageOfAllVotes"),
                  "rep": x.get("pollsReporting"), "tot": x.get("totalPolls")})
num = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 11: 10}
qs = sorted([{"n": num.get(q["questionID"], q["questionID"]), "yes": q["yesVotes"], "no": q["noVotes"]}
             for q in rr["votes"]["questionStats"]], key=lambda q: q["n"])
# per electoral division: reporting and [yes, no] for questions 1..10 (Q10 = Remain, Referendum)
wards = {x["ward"]: {"r": x.get("pollsReporting"), "t": x.get("totalPolls"), "v": [None] * 10} for x in rr.get("wards") or []}
for q in rr["votes"]["questionStats"]:
    i = num.get(q["questionID"], q["questionID"]) - 1
    for ws in q.get("wardStats") or []:
        if ws["ward"] in wards and 0 <= i < 10:
            wards[ws["ward"]]["v"][i] = [ws.get("yesVotes") or 0, ws.get("noVotes") or 0]
s = w["summary"]
core = {"sourceUpdated": d.get("lastUpdated"),
        "summary": {"valid": s.get("valid"), "rep": s.get("pollsReporting"), "tot": s.get("totalPolls")},
        "types": types, "questions": qs, "wards": wards}

try:
    old = json.load(open(OUT))
except Exception:          # missing or unreadable file: treat as changed
    old = {}
changed = {k: old.get(k) for k in core} != core
out = dict(core, fetchedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
json.dump(out, open(OUT, "w"), separators=(",", ":"))
print("CHANGED" if changed else "SAME", out["summary"]["rep"], "of", out["summary"]["tot"])
