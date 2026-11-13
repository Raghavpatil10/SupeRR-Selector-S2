#!/usr/bin/env python3
"""
RR IPL 2027 Auction - CORRECTED Pressure Player Analysis
Key fix: extras1_runs is delivery type code (6=regular, 1=no-ball, 2=wide, etc.)
         Actual runs are in 'runs' column only. Wide=+1 extra, Overstep=+1 extra.
         Dot ball = runs==0 AND extras_type=='None' (legal, no runs)
"""

import csv
import math
import re
from collections import defaultdict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
BASE = str(DATA_DIR)

# ============================================================
# 1. LOAD DATA
# ============================================================
print("Loading data...")

with open(f"{BASE}/matches.csv") as f:
    matches = {r['match_id']: r for r in csv.DictReader(f)}

with open(f"{BASE}/competitions.csv") as f:
    competitions = {r['comp_id']: r for r in csv.DictReader(f)}

# Get IPL matches only (2022-2026)
ipl_comp_ids = {cid for cid, c in competitions.items() if 'IPL' in c['comp_name']}
ipl_matches = {mid: m for mid, m in matches.items() if m['comp_id'] in ipl_comp_ids}
ipl_match_ids = set(ipl_matches.keys())

print(f"IPL competitions: IPL 2022-2026")
print(f"Total IPL matches: {len(ipl_matches)}")

# Load ball by ball - only IPL
print("Loading ball_by_ball.csv...")
bbb_rows = []
with open(f"{BASE}/ball_by_ball.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['match_id'] in ipl_match_ids:
            bbb_rows.append(row)
print(f"IPL deliveries: {len(bbb_rows)}")

# ============================================================
# 2. MATCH METADATA
# ============================================================

def total_runs_ball(row):
    """Total runs off a delivery including extras penalty"""
    runs = int(row['runs'])
    ex = row['extras_type']
    if ex == 'wide':
        runs += 1
    elif ex == 'Overstep':
        runs += 1
    elif ex == 'byes':
        pass  # byes don't count as batsman runs but DO count in total
    elif ex == 'legbyes':
        pass  # same
    return runs

def is_dot_ball(row):
    """A dot ball: legal delivery (not wide/no-ball) with 0 runs"""
    return int(row['runs']) == 0 and row['extras_type'] == 'None'

def is_legal_delivery(row):
    """Counts as a ball faced by batsman and bowled by bowler"""
    return row['extras_type'] not in ('wide', 'Overstep')

def is_bowler_wicket(row):
    """Wicket credited to bowler (not run-out)"""
    if row['is_wicket'] != 'true':
        return False
    dismissal = row.get('dismissal_type', '').lower()
    return 'run out' not in dismissal and row.get('dismissal_type', '') != ''

# Compute match targets from innings 1 totals
match_inn1_total = defaultdict(int)
match_inn1_balls = defaultdict(list)
match_inn2_balls = defaultdict(list)
match_all_balls = defaultdict(list)

for row in bbb_rows:
    mid = row['match_id']
    inn = int(row['innings'])
    rval = total_runs_ball(row)
    if inn == 1:
        match_inn1_total[mid] += rval
        match_inn1_balls[mid].append(row)
    elif inn == 2:
        match_inn2_balls[mid].append(row)
    match_all_balls[mid].append(row)

# Match metadata helper
def parse_margin(result_str):
    """Returns (is_close, margin_runs, margin_wkts)"""
    if not result_str:
        return False
    result_lower = result_str.lower()
    m = re.search(r'by (\d+) run', result_lower)
    if m and int(m.group(1)) <= 9:
        return True
    m = re.search(r'by (\d+) wk', result_lower)
    if m and int(m.group(1)) <= 2:
        return True
    return False

match_meta = {}
for mid, m in ipl_matches.items():
    inn1_total = match_inn1_total.get(mid, 0)
    target = inn1_total + 1 if inn1_total > 0 else None
    stage = m['stage']
    is_ko = (m['knock_out'] == '1' or stage in ('Qualifier', 'Eliminator', 'Final', 'Semi Final'))
    is_close = parse_margin(m['result'])
    match_meta[mid] = {
        'target': target,
        'inn1_total': inn1_total,
        'is_knockout': is_ko,
        'is_close': is_close,
        'stage': stage,
        'comp_id': m['comp_id'],
    }

print(f"Knockout matches: {sum(1 for v in match_meta.values() if v['is_knockout'])}")
print(f"Close matches: {sum(1 for v in match_meta.values() if v['is_close'])}")

# ============================================================
# 3. BATTER METRICS
# ============================================================
print("\nComputing batter metrics...")

class BatterStats:
    def __init__(self):
        self.name = ""
        # Overall (all IPL)
        self.all_runs = 0; self.all_balls = 0
        self.all_fours = 0; self.all_sixes = 0
        self.all_dismissals = 0
        
        # Death (overs 16-20, both innings)
        self.death_runs = 0; self.death_balls = 0
        self.death_fours = 0; self.death_sixes = 0
        self.death_dots = 0; self.death_dismissals = 0
        self.death_innings_set = set()  # for innings count
        self.death_innings_runs = defaultdict(int)   # (mid,inn)->runs for consistency
        self.death_innings_balls = defaultdict(int)
        
        # Chase pressure: inn2, RRR > 10
        self.chase_p_runs = 0; self.chase_p_balls = 0
        self.chase_p_dismissals = 0
        
        # Knockout
        self.ko_runs = 0; self.ko_balls = 0; self.ko_dismissals = 0

batter_stats = defaultdict(BatterStats)

for mid in ipl_match_ids:
    target = match_meta.get(mid, {}).get('target')
    is_ko = match_meta.get(mid, {}).get('is_knockout', False)
    
    # Process innings 2 (chasing) with RRR tracking
    inn2 = sorted(match_inn2_balls.get(mid, []),
                  key=lambda x: (int(x['overid']), int(x['over_ball_num'])))
    
    cum_runs = 0; cum_wkts = 0; legal_balls = 0
    for ball in inn2:
        over_num = int(ball['overid'])
        pid = ball['striker_id']
        bs = batter_stats[pid]
        bs.name = ball['striker_name']
        
        legal = is_legal_delivery(ball)
        brun = int(ball['runs'])
        is4 = ball['is_four'] == 'true'
        is6 = ball['is_six'] == 'true'
        iswkt = ball['is_wicket'] == 'true'
        dis_id = ball.get('dismissed_player_id', '')
        striker_out = iswkt and (dis_id == pid or dis_id == '')
        is_dot = is_dot_ball(ball)
        
        # Compute RRR before this delivery
        if target and legal_balls > 0:
            balls_rem = max(1, 120 - legal_balls)
            runs_needed = max(0, target - cum_runs)
            rrr = runs_needed / (balls_rem / 6.0)
        else:
            rrr = 0
        
        # Overall
        if legal:
            bs.all_runs += brun; bs.all_balls += 1
            bs.all_fours += (1 if is4 else 0); bs.all_sixes += (1 if is6 else 0)
            if striker_out: bs.all_dismissals += 1
        
        # Death overs
        if over_num >= 16 and legal:
            bs.death_runs += brun; bs.death_balls += 1
            bs.death_fours += (1 if is4 else 0); bs.death_sixes += (1 if is6 else 0)
            bs.death_dots += (1 if is_dot else 0)
            if striker_out: bs.death_dismissals += 1
            bs.death_innings_set.add((mid, 2))
            bs.death_innings_runs[(mid,2)] += brun
            bs.death_innings_balls[(mid,2)] += 1
        
        # Chase pressure (RRR > 10)
        if rrr > 10 and legal:
            bs.chase_p_runs += brun; bs.chase_p_balls += 1
            if striker_out: bs.chase_p_dismissals += 1
        
        # Knockout
        if is_ko and legal:
            bs.ko_runs += brun; bs.ko_balls += 1
            if striker_out: bs.ko_dismissals += 1
        
        # Update running totals
        rval = total_runs_ball(ball)
        cum_runs += rval
        if iswkt: cum_wkts += 1
        if legal: legal_balls += 1
    
    # Process innings 1 (setting innings) for death overs and consistency
    inn1 = sorted(match_inn1_balls.get(mid, []),
                  key=lambda x: (int(x['overid']), int(x['over_ball_num'])))
    
    for ball in inn1:
        over_num = int(ball['overid'])
        pid = ball['striker_id']
        bs = batter_stats[pid]
        bs.name = ball['striker_name']
        
        legal = is_legal_delivery(ball)
        brun = int(ball['runs'])
        is4 = ball['is_four'] == 'true'
        is6 = ball['is_six'] == 'true'
        iswkt = ball['is_wicket'] == 'true'
        dis_id = ball.get('dismissed_player_id', '')
        striker_out = iswkt and (dis_id == pid or dis_id == '')
        is_dot = is_dot_ball(ball)
        
        if legal:
            bs.all_runs += brun; bs.all_balls += 1
            bs.all_fours += (1 if is4 else 0); bs.all_sixes += (1 if is6 else 0)
            if striker_out: bs.all_dismissals += 1
        
        if over_num >= 16 and legal:
            bs.death_runs += brun; bs.death_balls += 1
            bs.death_fours += (1 if is4 else 0); bs.death_sixes += (1 if is6 else 0)
            bs.death_dots += (1 if is_dot else 0)
            if striker_out: bs.death_dismissals += 1
            bs.death_innings_set.add((mid, 1))
            bs.death_innings_runs[(mid,1)] += brun
            bs.death_innings_balls[(mid,1)] += 1
        
        if is_ko and legal:
            bs.ko_runs += brun; bs.ko_balls += 1
            if striker_out: bs.ko_dismissals += 1

# ============================================================
# 4. BOWLER METRICS
# ============================================================
print("Computing bowler metrics...")

class BowlerStats:
    def __init__(self):
        self.name = ""; self.pace_or_spin = ""; self.bowling_type = ""
        # Death (16-20)
        self.death_runs = 0; self.death_balls = 0; self.death_wkts = 0
        self.death_fours = 0; self.death_sixes = 0; self.death_dots = 0
        self.death_inn_set = set()
        self.death_inn_runs = defaultdict(int)
        self.death_inn_balls = defaultdict(int)
        self.death_inn_wkts = defaultdict(int)
        # Middle (7-15)
        self.mid_runs = 0; self.mid_balls = 0; self.mid_wkts = 0; self.mid_dots = 0
        self.mid_inn_set = set()
        # Overall
        self.all_runs = 0; self.all_balls = 0; self.all_wkts = 0
        # Knockout
        self.ko_runs = 0; self.ko_balls = 0; self.ko_wkts = 0

bowler_stats = defaultdict(BowlerStats)

for mid in ipl_match_ids:
    is_ko = match_meta.get(mid, {}).get('is_knockout', False)
    all_balls = match_inn1_balls.get(mid, []) + match_inn2_balls.get(mid, [])
    
    for ball in all_balls:
        over_num = int(ball['overid'])
        bid = ball['bowler_id']
        bs = bowler_stats[bid]
        bs.name = ball['bowler_name']
        bs.pace_or_spin = ball['pace_or_spin']
        bs.bowling_type = ball['bowling_type']
        
        legal = is_legal_delivery(ball)
        bwkt = is_bowler_wicket(ball)
        rval = total_runs_ball(ball)  # runs conceded by bowler
        is4 = ball['is_four'] == 'true'
        is6 = ball['is_six'] == 'true'
        is_dot = is_dot_ball(ball)
        inn_key = (mid, ball['innings'])
        
        if legal:
            bs.all_runs += rval; bs.all_balls += 1
            if bwkt: bs.all_wkts += 1
        
        if over_num >= 16 and legal:
            bs.death_runs += rval; bs.death_balls += 1
            if bwkt: bs.death_wkts += 1
            bs.death_fours += (1 if is4 else 0); bs.death_sixes += (1 if is6 else 0)
            bs.death_dots += (1 if is_dot else 0)
            bs.death_inn_set.add(inn_key)
            bs.death_inn_runs[inn_key] += rval
            bs.death_inn_balls[inn_key] += 1
            if bwkt: bs.death_inn_wkts[inn_key] += 1
        
        if 7 <= over_num <= 15 and legal:
            bs.mid_runs += rval; bs.mid_balls += 1
            if bwkt: bs.mid_wkts += 1
            if is_dot: bs.mid_dots += 1
            bs.mid_inn_set.add(inn_key)
        
        if is_ko and legal:
            bs.ko_runs += rval; bs.ko_balls += 1
            if bwkt: bs.ko_wkts += 1

# ============================================================
# 5. COMPOSITE INDICES
# ============================================================
print("Computing composite indices...")

MIN_DEATH_BALLS_BAT = 100
MIN_DEATH_BALLS_BWL = 60
MIN_MID_BALLS_BWL = 60

def normalize(val, min_val, max_val, invert=False):
    if max_val == min_val:
        return 0.5
    n = max(0.0, min(1.0, (val - min_val) / (max_val - min_val)))
    return 1.0 - n if invert else n

def cv(values):
    """Coefficient of variation"""
    if len(values) < 2:
        return 0.5
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.5
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(variance) / mean

# ---- BATTER SCORES ----
batter_rows = []
for pid, bs in batter_stats.items():
    if bs.death_balls < MIN_DEATH_BALLS_BAT:
        continue
    
    death_sr = bs.death_runs / bs.death_balls * 100
    death_avg = bs.death_runs / bs.death_dismissals if bs.death_dismissals > 0 else bs.death_runs * 2
    death_bdry_pct = (bs.death_fours + bs.death_sixes) / bs.death_balls * 100
    death_dot_pct = bs.death_dots / bs.death_balls * 100
    
    all_sr = bs.all_runs / bs.all_balls * 100 if bs.all_balls > 0 else 100
    delta_sr = death_sr - all_sr
    
    chase_sr = bs.chase_p_runs / bs.chase_p_balls * 100 if bs.chase_p_balls >= 20 else death_sr * 0.85
    chase_avg = bs.chase_p_runs / bs.chase_p_dismissals if bs.chase_p_dismissals > 0 else bs.chase_p_runs * 2
    
    # Consistency: CV of innings-level SR in death
    inn_srs = []
    for ik in bs.death_innings_set:
        b = bs.death_innings_balls.get(ik, 0)
        r = bs.death_innings_runs.get(ik, 0)
        if b >= 3:
            inn_srs.append(r / b * 100)
    consistency = 1.0 - min(1.0, cv(inn_srs)) if len(inn_srs) >= 3 else 0.5
    
    sample_conf = min(1.0, math.log(bs.death_balls + 1) / math.log(400))
    
    ko_sr = bs.ko_runs / bs.ko_balls * 100 if bs.ko_balls >= 10 else death_sr
    
    batter_rows.append({
        'pid': pid, 'name': bs.name,
        'death_balls': bs.death_balls, 'death_runs': bs.death_runs,
        'death_innings': len(bs.death_innings_set),
        'death_sr': death_sr, 'death_avg': death_avg,
        'death_bdry_pct': death_bdry_pct, 'death_dot_pct': death_dot_pct,
        'death_dismissals': bs.death_dismissals,
        'all_sr': all_sr, 'all_runs': bs.all_runs, 'all_balls': bs.all_balls,
        'delta_sr': delta_sr,
        'chase_p_balls': bs.chase_p_balls,
        'chase_sr': chase_sr, 'chase_avg': chase_avg,
        'ko_sr': ko_sr, 'ko_balls': bs.ko_balls,
        'consistency': consistency,
        'sample_conf': sample_conf,
    })

# Normalize
def norm_field(rows, field, invert=False):
    vals = [r[field] for r in rows]
    mn, mx = min(vals), max(vals)
    for r in rows:
        r[f'{field}_n'] = normalize(r[field], mn, mx, invert)

norm_field(batter_rows, 'death_sr')
norm_field(batter_rows, 'death_bdry_pct')
norm_field(batter_rows, 'death_dot_pct', invert=True)
norm_field(batter_rows, 'chase_sr')
norm_field(batter_rows, 'delta_sr')
norm_field(batter_rows, 'consistency')

for r in batter_rows:
    perf = 0.55 * r['death_sr_n'] + 0.30 * r['death_bdry_pct_n'] + 0.15 * r['death_dot_pct_n']
    r['composite'] = (0.40 * perf + 0.25 * r['chase_sr_n'] + 0.20 * r['consistency'] +
                      0.10 * r['delta_sr_n'] + 0.05 * r['sample_conf'])

batter_rows.sort(key=lambda x: x['composite'], reverse=True)

# ---- BOWLER SCORES ----
bowler_rows = []
for pid, bs in bowler_stats.items():
    if bs.death_balls < MIN_DEATH_BALLS_BWL:
        continue
    
    death_econ = bs.death_runs / bs.death_balls * 6
    death_dot_pct = bs.death_dots / bs.death_balls * 100
    death_bdry_pct = (bs.death_fours + bs.death_sixes) / bs.death_balls * 100
    death_wpi = bs.death_wkts / len(bs.death_inn_set) if bs.death_inn_set else 0
    
    all_econ = bs.all_runs / bs.all_balls * 6 if bs.all_balls > 0 else 9
    delta_econ = death_econ - all_econ  # negative = specializes in death
    
    # Consistency of death economy
    inn_econs = []
    for ik in bs.death_inn_set:
        b = bs.death_inn_balls.get(ik, 0)
        if b >= 3:
            inn_econs.append(bs.death_inn_runs[ik] / b * 6)
    cv_econ = cv(inn_econs)
    consistency = 1.0 - min(1.0, cv_econ)
    
    mid_econ = bs.mid_runs / bs.mid_balls * 6 if bs.mid_balls > 0 else 9
    mid_dot_pct = bs.mid_dots / bs.mid_balls * 100 if bs.mid_balls > 0 else 0
    mid_wpi = bs.mid_wkts / len(bs.mid_inn_set) if bs.mid_inn_set else 0
    
    sample_conf = min(1.0, math.log(bs.death_balls + 1) / math.log(400))
    
    ko_econ = bs.ko_runs / bs.ko_balls * 6 if bs.ko_balls >= 6 else death_econ
    
    bowler_rows.append({
        'pid': pid, 'name': bs.name,
        'pace_or_spin': bs.pace_or_spin, 'bowling_type': bs.bowling_type,
        'death_balls': bs.death_balls, 'death_runs': bs.death_runs,
        'death_innings': len(bs.death_inn_set),
        'death_econ': death_econ, 'death_dot_pct': death_dot_pct,
        'death_bdry_pct': death_bdry_pct, 'death_wkts': bs.death_wkts,
        'death_wpi': death_wpi, 'cv_econ': cv_econ,
        'consistency': consistency,
        'all_econ': all_econ, 'delta_econ': delta_econ,
        'mid_balls': bs.mid_balls, 'mid_econ': mid_econ,
        'mid_dot_pct': mid_dot_pct, 'mid_wkts': bs.mid_wkts,
        'mid_wpi': mid_wpi, 'mid_innings': len(bs.mid_inn_set),
        'ko_econ': ko_econ, 'ko_balls': bs.ko_balls, 'ko_wkts': bs.ko_wkts,
        'sample_conf': sample_conf,
        'all_wkts': bs.all_wkts, 'all_balls': bs.all_balls,
    })

def norm_field_b(rows, field, invert=False):
    vals = [r[field] for r in rows]
    mn, mx = min(vals), max(vals)
    for r in rows:
        r[f'{field}_n'] = normalize(r[field], mn, mx, invert)

norm_field_b(bowler_rows, 'death_econ', invert=True)
norm_field_b(bowler_rows, 'death_dot_pct')
norm_field_b(bowler_rows, 'death_bdry_pct', invert=True)
norm_field_b(bowler_rows, 'death_wpi')
norm_field_b(bowler_rows, 'consistency')
norm_field_b(bowler_rows, 'delta_econ', invert=True)  # more negative = better

for r in bowler_rows:
    perf = 0.50 * r['death_econ_n'] + 0.25 * r['death_dot_pct_n'] + 0.25 * r['death_bdry_pct_n']
    r['composite'] = (0.40 * perf + 0.25 * r['death_wpi_n'] +
                      0.20 * r['consistency'] + 0.10 * r['delta_econ_n'] + 0.05 * r['sample_conf'])

bowler_rows.sort(key=lambda x: x['composite'], reverse=True)

# ============================================================
# 6. OUTPUT RESULTS
# ============================================================

print("\n" + "=" * 130)
print("TOP BATTERS - PRESSURE COMPOSITE INDEX (IPL 2022-2026, min 100 death-over balls)")
print("=" * 130)
print(f"{'#':<4} {'Player':<26} {'DthSR':>7} {'DthAvg':>8} {'Bdry%':>7} {'Dot%':>7} {'ChaseSR':>9} {'DeltaSR':>9} {'Consist':>8} {'DthBalls':>9} {'DthInns':>8} {'Index':>7}")
print("-" * 130)
for i, r in enumerate(batter_rows[:30], 1):
    print(f"{i:<4} {r['name']:<26} {r['death_sr']:>7.1f} {r['death_avg']:>8.1f} {r['death_bdry_pct']:>7.1f}% {r['death_dot_pct']:>6.1f}% {r['chase_sr']:>8.1f} {r['delta_sr']:>+8.1f} {r['consistency']:>8.2f} {r['death_balls']:>9} {r['death_innings']:>8} {r['composite']:>7.3f}")

print("\n" + "=" * 130)
print("TOP BOWLERS - PRESSURE COMPOSITE INDEX (IPL 2022-2026, min 60 death-over balls)")
print("=" * 130)
print(f"{'#':<4} {'Player':<26} {'Type':<6} {'DthEco':>8} {'Dot%':>7} {'Bdry%':>7} {'W/Inn':>7} {'DthWkts':>8} {'DthInns':>8} {'CV':>6} {'NrmEco':>8} {'Delta':>8} {'MidEco':>8} {'MidWpi':>7} {'Index':>7}")
print("-" * 130)
for i, r in enumerate(bowler_rows[:30], 1):
    t = 'Spin' if r['pace_or_spin'] == 'Spin' else 'Pace'
    print(f"{i:<4} {r['name']:<26} {t:<6} {r['death_econ']:>8.2f} {r['death_dot_pct']:>7.1f}% {r['death_bdry_pct']:>6.1f}% {r['death_wpi']:>7.2f} {r['death_wkts']:>8} {r['death_innings']:>8} {r['cv_econ']:>6.2f} {r['all_econ']:>8.2f} {r['delta_econ']:>+8.2f} {r['mid_econ']:>8.2f} {r['mid_wpi']:>7.2f} {r['composite']:>7.3f}")

# Middle overs spinner focus
print("\n" + "=" * 100)
print("SPINNERS - MIDDLE OVERS (overs 7-15), min 60 balls bowled in those overs")
print("=" * 100)
spin_mid = [r for r in bowler_rows if r['pace_or_spin'] == 'Spin' and r['mid_balls'] >= 60]
spin_mid.sort(key=lambda x: x['mid_wpi'] * 0.5 - x['mid_econ'] * 0.05, reverse=True)
print(f"{'#':<4} {'Player':<26} {'BowlType':<30} {'MidEco':>8} {'MidDot%':>9} {'MidWpi':>8} {'MidWkts':>9} {'MidInns':>9}")
print("-" * 100)
for i, r in enumerate(spin_mid[:15], 1):
    print(f"{i:<4} {r['name']:<26} {r['bowling_type']:<30} {r['mid_econ']:>8.2f} {r['mid_dot_pct']:>8.1f}% {r['mid_wpi']:>8.2f} {r['mid_wkts']:>9} {r['mid_innings']:>9}")

# Indian death bowlers
print("\n" + "=" * 100)
print("INDIAN DEATH BOWLERS (focusing on death econ + wkts)")
print("=" * 100)
# We need to identify Indian players - use competition_team_player_mapping
indian_teams_check = ['India', 'Indian']
# Load player nationality approximation via team names in int'l comps
player_teams = defaultdict(set)
with open(f"{BASE}/competition_team_player_mapping.csv") as f:
    for row in csv.DictReader(f):
        player_teams[row['player_id']].add(row['team_name'])

indian_pids = set()
for pid, teams in player_teams.items():
    for t in teams:
        if 'India' in t and 'Indian' not in t or t == 'India':
            indian_pids.add(pid)
            break

# Also include players with common Indian names or who've played for India
indian_bowler_names = {
    'Jasprit Bumrah', 'Mohammed Siraj', 'Mohammed Shami', 'Arshdeep Singh',
    'T Natarajan', 'Avesh Khan', 'Harshal Patel', 'Yuzvendra Chahal',
    'Kuldeep Yadav', 'Varun Chakravarthy', 'Ravi Bishnoi', 'Harshit Rana',
    'Mukesh Kumar', 'Khaleel Ahmed', 'Deepak Chahar', 'Shardul Thakur',
    'Bhuvneshwar Kumar', 'Mohit Sharma', 'Umesh Yadav', 'Prasidh Krishna',
    'Tushar Deshpande', 'Akash Deep', 'Washington Sundar', 'Rahul Chahar',
    'Suyash Sharma', 'Nitish Reddy', 'Mayank Markande', 'Shahbaz Ahmed',
    'Vyshak Kumar', 'Yash Dayal', 'Mohsin Khan', 'Akash Madhwal',
    'Naman Dhir', 'Riyan Parag'
}

indian_death = [r for r in bowler_rows 
                if r['name'] in indian_bowler_names or r['pid'] in indian_pids]
indian_death.sort(key=lambda x: x['composite'], reverse=True)
print(f"{'#':<4} {'Player':<26} {'Type':<6} {'DthEco':>8} {'Dot%':>7} {'W/Inn':>7} {'DthWkts':>9} {'DthInns':>8} {'Index':>7}")
print("-" * 85)
for i, r in enumerate(indian_death[:15], 1):
    t = 'Spin' if r['pace_or_spin'] == 'Spin' else 'Pace'
    print(f"{i:<4} {r['name']:<26} {t:<6} {r['death_econ']:>8.2f} {r['death_dot_pct']:>7.1f}% {r['death_wpi']:>7.2f} {r['death_wkts']:>9} {r['death_innings']:>8} {r['composite']:>7.3f}")

# Seed list check
print("\n\nSEED BATTER CHECK:")
seed_b = ['Tim David', 'Liam Livingstone', 'Rovman Powell', 'Rinku Singh',
          'Shashank Singh', 'Ashutosh Sharma', 'Jitesh Sharma', 'Venkatesh Iyer',
          'Nehal Wadhera', 'Sameer Rizvi']
for name in seed_b:
    found = [r for r in batter_rows if name.lower() in r['name'].lower()]
    if found:
        r = found[0]; rank = batter_rows.index(r)+1
        print(f"  {r['name']:<26} Rank:{rank:>3}  DthSR:{r['death_sr']:>7.1f}  DthAvg:{r['death_avg']:>7.1f}  "
              f"ChaseSR:{r['chase_sr']:>7.1f}  Consist:{r['consistency']:>5.2f}  Balls:{r['death_balls']:>5}  Index:{r['composite']:.3f}")
    else:
        # check unfiltered
        all_found = [(pid, bs) for pid, bs in batter_stats.items() if name.lower() in bs.name.lower()]
        if all_found:
            pid, bs = all_found[0]
            print(f"  {bs.name:<26} BELOW THRESHOLD - death_balls={bs.death_balls}")
        else:
            print(f"  {name:<26} NOT FOUND IN DATA")

print("\nSEED BOWLER CHECK:")
seed_bwl = ['T Natarajan', 'Harshit Rana', 'Mukesh Kumar', 'Khaleel Ahmed',
            'Avesh Khan', 'Harshal Patel', 'Varun Chakravarthy', 'Noor Ahmad',
            'Suyash Sharma', 'Matheesha Pathirana']
for name in seed_bwl:
    found = [r for r in bowler_rows if name.lower() in r['name'].lower()]
    if found:
        r = found[0]; rank = bowler_rows.index(r)+1
        print(f"  {r['name']:<26} Rank:{rank:>3}  DthEco:{r['death_econ']:>6.2f}  Dot:{r['death_dot_pct']:>5.1f}%  "
              f"W/Inn:{r['death_wpi']:>5.2f}  MidEco:{r['mid_econ']:>6.2f}  MidWpi:{r['mid_wpi']:>5.2f}  Balls:{r['death_balls']:>5}  Index:{r['composite']:.3f}")
    else:
        all_found = [(pid, bs) for pid, bs in bowler_stats.items() if name.lower() in bs.name.lower()]
        if all_found:
            pid, bs = all_found[0]
            print(f"  {bs.name:<26} BELOW THRESHOLD - death_balls={bs.death_balls}, mid_balls={bs.mid_balls}")
        else:
            print(f"  {name:<26} NOT FOUND IN DATA")

# Save for later use
import json
with open(f"{BASE}/batter_scores_full.json", "w") as f:
    json.dump(batter_rows[:50], f, indent=2)
with open(f"{BASE}/bowler_scores_full.json", "w") as f:
    json.dump(bowler_rows[:50], f, indent=2)

print("\nDone. JSON saved.")

