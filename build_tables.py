"""Builds the VAKYR calibration tables from the frozen pre-match predictions (read-only)."""
import sqlite3, csv, json, math, os
os.makedirs(os.environ.get('OUT', 'out'), exist_ok=True)
c = sqlite3.connect('file:' + os.environ.get('VAKYR_DB', 'scommesse.db') + '?mode=ro', uri=True)
q = """select substr(match_date,1,7), prob_home,prob_draw,prob_away,prob_over15,prob_over25,prob_over35,prob_btts,home_goals,away_goals
       from prediction_tracking where home_goals is not null and away_goals is not null
       and substr(match_date,1,10) >= '2026-09-01' and substr(match_date,1,10) < '2026-11-19'"""
M = ["1X2_home", "1X2_draw", "1X2_away", "over_1_5", "over_2_5", "over_3_5", "btts_yes"]
agg = {}; tot = {m: [0, 0.0, 0.0, 0] for m in M}; n_partite = 0; mesi = set()
def add(mese, m, p, y):
    if p is None: return
    p = float(p); p = p / 100 if p > 1 else p
    if not (0 <= p <= 1): return
    y = 1 if y else 0
    b = min(9, int(p * 10)); a = agg.setdefault((mese, m, b), [0, 0.0, 0])
    a[0] += 1; a[1] += p; a[2] += y
    t = tot[m]; t[0] += 1; t[1] += (p - y) ** 2; t[2] += -math.log(max(1e-6, p if y else 1 - p)); t[3] += y
for mese, ph, pd, pa, o15, o25, o35, bt, hg, ag in c.execute(q):
    n_partite += 1; mesi.add(mese); g = hg + ag
    r = "H" if hg > ag else ("D" if hg == ag else "A")
    add(mese, "1X2_home", ph, r == "H"); add(mese, "1X2_draw", pd, r == "D"); add(mese, "1X2_away", pa, r == "A")
    add(mese, "over_1_5", o15, g >= 2); add(mese, "over_2_5", o25, g >= 3); add(mese, "over_3_5", o35, g >= 4)
    add(mese, "btts_yes", bt, hg > 0 and ag > 0)
with open(os.path.join(os.environ.get('OUT', 'out'), 'calibration_by_month.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(["month", "market", "bin_low", "bin_high", "n", "mean_predicted", "observed_rate"])
    for (mese, m, b), (n, sp, sy) in sorted(agg.items()):
        w.writerow([mese, m, b / 10, (b + 1) / 10, n, round(sp / n, 4), round(sy / n, 4)])
tutti = {}
for (mese, m, b), (n, sp, sy) in agg.items():
    a = tutti.setdefault((m, b), [0, 0.0, 0]); a[0] += n; a[1] += sp; a[2] += sy
with open(os.path.join(os.environ.get('OUT', 'out'), 'calibration_overall.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(["market", "bin_low", "bin_high", "n", "mean_predicted", "observed_rate"])
    for (m, b), (n, sp, sy) in sorted(tutti.items()):
        w.writerow([m, b / 10, (b + 1) / 10, n, round(sp / n, 4), round(sy / n, 4)])
somm = {"period": "2026-09-01..2026-11-18", "matches": n_partite, "months": sorted(mesi), "markets": {}}
for m, (n, br, ll, ys) in tot.items():
    base = ys / n if n else 0
    somm["markets"][m] = {"n": n, "brier": round(br / n, 4) if n else None, "log_loss": round(ll / n, 4) if n else None,
                         "base_rate": round(base, 4), "brier_climatology": round(base * (1 - base), 4)}
json.dump(somm, open(os.path.join(os.environ.get('OUT', 'out'), 'summary.json'), 'w'), indent=1)
print(json.dumps(somm, indent=1))
