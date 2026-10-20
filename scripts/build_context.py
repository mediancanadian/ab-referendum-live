"""Build context.json (one record per electoral division) from the verified CSVs in context/.
Run: python3 scripts/build_context.py"""
import csv, json, itertools

def rows(f): return list(csv.DictReader(open(f"context/{f}", encoding="utf-8")))
def num(x):
    try: return round(float(x), 2)
    except (TypeError, ValueError): return None

out = {}
for r in rows("ab_2023_pge_results_by_ed.csv"):
    out[r["ed_num"]] = {"p23": {"ucp": num(r["ucp_pct"]), "ndp": num(r["ndp_pct"]), "oth": num(r["other_pct"]),
                                "win": r["winner"], "turnout": num(r["turnout_pct"])}}
for r in rows("fed_2025_transposed_to_ab_ed.csv"):
    out[r["ed_num"]]["f25"] = {"cpc": num(r["cpc_pct"]), "lpc": num(r["lpc_pct"]), "ndp": num(r["ndp_pct"]),
                               "ppc": num(r["ppc_pct"]), "win": r["winner"]}
by = sorted(rows("ab_byelections_since_2023_candidates.csv"), key=lambda r: (r["ed_num"], r["election_date"]))
for (ed, date), g in itertools.groupby(by, key=lambda r: (r["ed_num"], r["election_date"])):
    g = sorted(g, key=lambda r: -float(r["votes"]))
    out[ed]["by"] = {"date": date, "win": next(r["party"] for r in g if r["elected"] == "1"),
                     "res": [[r["party"], num(r["pct"])] for r in g[:3]], "turnout": num(g[0]["turnout_pct"])}  # latest kept (sorted by date)
for r in rows("ab_census_2021_by_ed.csv"):
    out[r["ed_num"]]["c21"] = {
        "pop": num(r["population_2021"]), "age": num(r["avg_age"]), "p65": num(r["pct_age_65_plus"]),
        "inc": num(r["median_household_income_2020"]), "imm": num(r["pct_immigrants"]), "rimm": num(r["pct_recent_immigrants"]),
        "vm": num(r["pct_visible_minority"]), "ind": num(r["pct_indigenous_identity"]), "deg": num(r["pct_bachelors_or_higher_25_64"]),
        "unemp": num(r["unemployment_rate"]), "lowinc": num(r["pct_low_income_limat"]),
        "occ": r["top1_occ"], "occp": num(r["top1_occ_pct"]), "indus": r["top1_ind"], "indusp": num(r["top1_ind_pct"])}
assert len(out) == 87 and all({"p23", "f25", "c21"} <= set(v) for v in out.values())
json.dump(out, open("context.json", "w"), separators=(",", ":"))
print("divisions", len(out), "with by-election", sum("by" in v for v in out.values()))
