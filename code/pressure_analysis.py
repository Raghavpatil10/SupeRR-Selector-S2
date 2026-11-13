#!/usr/bin/env python3
"""
RR IPL 2027 Auction - Pressure Player Analysis
Full pipeline: data loading -> pressure definitions -> metrics -> composite index -> rankings
"""

import csv
import math
import re
from collections import defaultdict

# ============================================================
# 1. LOAD DATA
# ============================================================
print("=" * 70)
print("STEP 1: LOADING DATA")
print("=" * 70)

BASE = "/Users/raghavpatil/Desktop/RR_HACKATHON"

with open(f"{BASE}/matches.csv") as f:
    matches = {r['match_id']: r for r in csv.DictReader(f)}

with open(f"{BASE}/competitions.csv") as f:
    competitions = {r['comp_id']: r for r in csv.DictReader(f)}

with open(f"{BASE}/competition_team_player_mapping.csv") as f:
    ctpm = list(csv.DictReader(f))

with open(f"{BASE}/playing_eleven.csv") as f:
    playing_eleven = list(csv.DictReader(f))

# Get IPL matches
ipl_comp_ids = {cid for cid, c in competitions.items() if 'IPL' in c['comp_name']}
ipl_matches = {mid: m for mid, m in matches.items() if m['comp_id'] in ipl_comp_ids}
ipl_match_ids = set(ipl_matches.keys())

print(f"IPL competitions: {sorted(ipl_comp_ids)}")
print(f"Total IPL matches: {len(ipl_matches)}")

# Load ball by ball - only IPL
print("Loading ball_by_ball.csv (200k rows)...")
bbb_rows = []
with open(f"{BASE}/ball_by_ball.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['match_id'] in ipl_match_ids:
            bbb_rows.append(row)

print(f"IPL ball-by-ball rows: {len(bbb_rows)}")

# ============================================================
# 2. COMPUTE MATCH-LEVEL METADATA
# ============================================================
print("\n" + "=" * 70)
print("STEP 2: COMPUTING MATCH METADATA")
print("=" * 70)

# For each IPL match, compute:
# - innings 1 total runs (to know target for innings 2)
# - wickets fallen at each point in innings 2
# We'll store per-match, per-over data

match_inn1_runs = defaultdict(int)   # match_id -> innings 1 total runs
match_inn1_balls = defaultdict(list) # match_id -> list of balls in inn1
match_inn2_balls = defaultdict(list) # match_id -> list of balls in inn2

for row in bbb_rows:
    mid = row['match_id']
    inn = int(row['innings'])
    runs = int(row['runs']) + int(row['extras1_runs'] or 0) + int(row['extras_2_runs'] or 0)
    if inn == 1:
        match_inn1_runs[mid] += runs
        match_inn1_balls[mid].append(row)
    elif inn == 2:
        match_inn2_balls[mid].append(row)

# ============================================================
# 3. PRESSURE DEFINITIONS
# ============================================================
print("\n" + "=" * 70)
print("STEP 3: DEFINING PRESSURE SCENARIOS")
print("=" * 70)

# PRESSURE DEFINITIONS (explained):
# P1 - DEATH OVER BATTING (overs 16-20): Any batter facing in overs 16-20
# P2 - CHASE PRESSURE: Chasing (innings=2) with RRR > 10 at any point
# P3 - COLLAPSE RECOVERY: Batting when 3+ wickets fell in first 10 overs (early collapse)
# P4 - KNOCKOUT MATCH: knock_out=1 or stage in Qualifier/Eliminator/Final/Semi Final
# P5 - CLOSE MATCH: match won/lost by < 10 runs or last-over finish

# DEATH OVER BOWLING (overs 16-20):
# PB1 - DEATH OVER BOWLING: Bowling in overs 16-20
# PB2 - MIDDLE OVERS BOWLING: Bowling in overs 7-15 
# PB3 - POWERPLAY BOWLING: Bowling in overs 1-6

# Parse match closeness from result string
def is_close_match(result_str):
    """Close = won/lost by <= 9 runs or won/lost by 1 wicket"""
    if not result_str:
        return False
    result_lower = result_str.lower()
    # Check runs
    m = re.search(r'by (\d+) run', result_lower)
    if m and int(m.group(1)) <= 9:
        return True
    # Check wickets (1 wicket = very close)
    m = re.search(r'by (\d+) wk', result_lower)
    if m and int(m.group(1)) <= 2:
        return True
    return False

def is_knockout(match_row):
    """Knockout = knock_out=1 or stage is Qualifier/Eliminator/Final/Semi Final"""
    if match_row['knock_out'] == '1':
        return True
    stage = match_row.get('stage', '')
    return stage in ('Qualifier', 'Eliminator', 'Final', 'Semi Final')

# Pre-compute match metadata
match_meta = {}
for mid, m in ipl_matches.items():
    target = None
    if m.get('revised_target') and m['revised_target'].strip():
        try:
            target = int(float(m['revised_target']))
        except:
            pass
    
    # Compute from ball data
    inn1_total = match_inn1_runs.get(mid, 0)
    if inn1_total > 0:
        target = inn1_total + 1  # target = inn1 total + 1 runs needed
    
    match_meta[mid] = {
        'target': target,
        'inn1_total': inn1_total,
        'is_knockout': is_knockout(m),
        'is_close': is_close_match(m['result']),
        'stage': m['stage'],
        'comp_id': m['comp_id'],
        'comp_name': competitions.get(m['comp_id'], {}).get('comp_name', '')
    }

print(f"Knockout matches: {sum(1 for v in match_meta.values() if v['is_knockout'])}")
print(f"Close matches: {sum(1 for v in match_meta.values() if v['is_close'])}")

# ============================================================
# 4. BUILD PRESSURE BATTER METRICS
# ============================================================
print("\n" + "=" * 70)
print("STEP 4: COMPUTING BATTER PRESSURE METRICS")
print("=" * 70)

# Track per-player metrics
# For each player: normal stats vs pressure stats

class BatterStats:
    def __init__(self):
        self.name = ""
        # Normal stats (all balls)
        self.normal_runs = 0
        self.normal_balls = 0
        self.normal_fours = 0
        self.normal_sixes = 0
        self.normal_dots = 0
        self.normal_dismissals = 0
        
        # Death over stats (overs 16-20)
        self.death_runs = 0
        self.death_balls = 0
        self.death_fours = 0
        self.death_sixes = 0
        self.death_dots = 0
        self.death_dismissals = 0
        self.death_innings = set()  # (match_id, innings)
        
        # Chase pressure (RRR > 10)
        self.chase_pressure_runs = 0
        self.chase_pressure_balls = 0
        self.chase_pressure_dismissals = 0
        self.chase_pressure_innings = set()
        
        # Collapse recovery (3+ wkts in first 10)
        self.collapse_runs = 0
        self.collapse_balls = 0
        self.collapse_dismissals = 0
        
        # Knockout stats
        self.ko_runs = 0
        self.ko_balls = 0
        self.ko_dismissals = 0
        
        # innings-level for consistency (death runs per death innings played)
        self.death_runs_per_innings = []

batter_stats = defaultdict(BatterStats)

# Process innings 2 for RRR computation
# We need cumulative runs and wickets after each ball

for mid in ipl_match_ids:
    target = match_meta.get(mid, {}).get('target')
    is_ko = match_meta.get(mid, {}).get('is_knockout', False)
    
    # Process innings 2 (chasing innings)
    inn2_balls = match_inn2_balls.get(mid, [])
    
    # Sort by ball number
    try:
        inn2_balls_sorted = sorted(inn2_balls, key=lambda x: (int(x['overid']), int(x['over_ball_num'])))
    except:
        inn2_balls_sorted = inn2_balls
    
    # Compute running total of runs and wickets for inn2
    cum_runs = 0
    cum_wickets = 0
    balls_bowled = 0
    
    for ball in inn2_balls_sorted:
        over_num = int(ball['overid'])  # 1-indexed over
        
        # Compute RRR before this ball
        if target and balls_bowled > 0:
            balls_remaining = max(1, 120 - balls_bowled)
            runs_needed = max(0, target - cum_runs)
            overs_remaining = balls_remaining / 6.0
            rrr = runs_needed / overs_remaining if overs_remaining > 0 else 99
        else:
            rrr = 0
        
        pid = ball['striker_id']
        pname = ball['striker_name']
        bs = batter_stats[pid]
        bs.name = pname
        
        # Normal stats
        ball_runs = int(ball['runs'])
        is_four = ball['is_four'] == 'true'
        is_six = ball['is_six'] == 'true'
        is_wkt = ball['is_wicket'] == 'true'
        dismissed_id = ball.get('dismissed_player_id', '')
        is_striker_out = is_wkt and (dismissed_id == pid or dismissed_id == '')
        
        bs.normal_runs += ball_runs
        bs.normal_balls += 1
        bs.normal_fours += 1 if is_four else 0
        bs.normal_sixes += 1 if is_six else 0
        bs.normal_dots += 1 if ball_runs == 0 and ball['extras_type'] == 'None' else 0
        if is_striker_out:
            bs.normal_dismissals += 1
        
        # Death over (overs 16-20, over_num >= 16)
        if over_num >= 16:
            bs.death_runs += ball_runs
            bs.death_balls += 1
            bs.death_fours += 1 if is_four else 0
            bs.death_sixes += 1 if is_six else 0
            bs.death_dots += 1 if ball_runs == 0 and ball['extras_type'] == 'None' else 0
            if is_striker_out:
                bs.death_dismissals += 1
            bs.death_innings.add((mid, 2))
        
        # Chase pressure: RRR > 10
        if rrr > 10:
            bs.chase_pressure_runs += ball_runs
            bs.chase_pressure_balls += 1
            if is_striker_out:
                bs.chase_pressure_dismissals += 1
            bs.chase_pressure_innings.add((mid, 2))
        
        # Knockout
        if is_ko:
            bs.ko_runs += ball_runs
            bs.ko_balls += 1
            if is_striker_out:
                bs.ko_dismissals += 1
        
        # Update cumulative
        ball_total = int(ball['runs']) + int(ball['extras1_runs'] or 0) + int(ball['extras_2_runs'] or 0)
        cum_runs += ball_total
        if is_wkt:
            cum_wickets += 1
        balls_bowled += 1

    # Process innings 1 (setting innings) for collapse recovery
    inn1_balls = match_inn1_balls.get(mid, [])
    try:
        inn1_sorted = sorted(inn1_balls, key=lambda x: (int(x['overid']), int(x['over_ball_num'])))
    except:
        inn1_sorted = inn1_balls
    
    # Compute wickets in first 10 overs
    wkts_first10 = sum(1 for b in inn1_sorted 
                       if int(b['overid']) <= 10 and b['is_wicket'] == 'true')
    
    for ball in inn1_sorted:
        over_num = int(ball['overid'])
        pid = ball['striker_id']
        pname = ball['striker_name']
        bs = batter_stats[pid]
        bs.name = pname
        
        ball_runs = int(ball['runs'])
        is_four = ball['is_four'] == 'true'
        is_six = ball['is_six'] == 'true'
        is_wkt = ball['is_wicket'] == 'true'
        dismissed_id = ball.get('dismissed_player_id', '')
        is_striker_out = is_wkt and (dismissed_id == pid or dismissed_id == '')
        
        bs.normal_runs += ball_runs
        bs.normal_balls += 1
        bs.normal_fours += 1 if is_four else 0
        bs.normal_sixes += 1 if is_six else 0
        bs.normal_dots += 1 if ball_runs == 0 and ball['extras_type'] == 'None' else 0
        if is_striker_out:
            bs.normal_dismissals += 1
        
        # Death overs in inn1
        if over_num >= 16:
            bs.death_runs += ball_runs
            bs.death_balls += 1
            bs.death_fours += 1 if is_four else 0
            bs.death_sixes += 1 if is_six else 0
            bs.death_dots += 1 if ball_runs == 0 and ball['extras_type'] == 'None' else 0
            if is_striker_out:
                bs.death_dismissals += 1
            bs.death_innings.add((mid, 1))
        
        # Knockout
        if is_ko:
            bs.ko_runs += ball_runs
            bs.ko_balls += 1
            if is_striker_out:
                bs.ko_dismissals += 1
        
        # Collapse recovery: batting when 3+ wkts fell in first 10 overs
        if wkts_first10 >= 3 and over_num > 10:
            bs.collapse_runs += ball_runs
            bs.collapse_balls += 1
            if is_striker_out:
                bs.collapse_dismissals += 1


# ============================================================
# 5. BUILD BOWLER PRESSURE METRICS
# ============================================================
print("\n" + "=" * 70)
print("STEP 5: COMPUTING BOWLER PRESSURE METRICS")
print("=" * 70)

class BowlerStats:
    def __init__(self):
        self.name = ""
        self.pace_or_spin = ""
        # Normal
        self.normal_runs_conceded = 0
        self.normal_balls = 0
        self.normal_wickets = 0
        self.normal_fours_conceded = 0
        self.normal_sixes_conceded = 0
        self.normal_dots = 0
        self.normal_innings = set()
        
        # Death over (16-20)
        self.death_runs = 0
        self.death_balls = 0
        self.death_wickets = 0
        self.death_fours = 0
        self.death_sixes = 0
        self.death_dots = 0
        self.death_innings = set()
        
        # Middle overs (7-15)
        self.middle_runs = 0
        self.middle_balls = 0
        self.middle_wickets = 0
        self.middle_dots = 0
        self.middle_innings = set()
        
        # Knockout
        self.ko_runs = 0
        self.ko_balls = 0
        self.ko_wickets = 0
        
        # Innings-level for consistency (death economy per innings)
        self.death_economy_per_innings = []  # will compute later
        self.death_runs_per_inn = defaultdict(int)
        self.death_balls_per_inn = defaultdict(int)
        self.death_wkts_per_inn = defaultdict(int)

bowler_stats = defaultdict(BowlerStats)

for mid in ipl_match_ids:
    is_ko = match_meta.get(mid, {}).get('is_knockout', False)
    all_balls = match_inn1_balls.get(mid, []) + match_inn2_balls.get(mid, [])
    
    for ball in all_balls:
        over_num = int(ball['overid'])
        bid = ball['bowler_id']
        bname = ball['bowler_name']
        bs = bowler_stats[bid]
        bs.name = bname
        bs.pace_or_spin = ball['pace_or_spin']
        
        ball_runs = int(ball['runs']) + int(ball['extras1_runs'] or 0) + int(ball['extras_2_runs'] or 0)
        is_four = ball['is_four'] == 'true'
        is_six = ball['is_six'] == 'true'
        is_wkt = ball['is_wicket'] == 'true'
        # Exclude run-outs from bowler wickets
        dismissal = ball.get('dismissal_type', '')
        bowler_wkt = is_wkt and 'run out' not in dismissal.lower() and dismissal != ''
        # Only legal deliveries count for balls (exclude wides/no-balls from economy calculation)
        extras_type = ball.get('extras_type', 'None')
        is_legal = extras_type in ('None', 'Byes', 'Leg Byes')
        is_dot = ball_runs == 0 and extras_type == 'None'
        
        inn_key = (mid, ball['innings'])
        
        # Normal
        bs.normal_runs_conceded += ball_runs
        if is_legal:
            bs.normal_balls += 1
        bs.normal_wickets += 1 if bowler_wkt else 0
        bs.normal_fours_conceded += 1 if is_four else 0
        bs.normal_sixes_conceded += 1 if is_six else 0
        bs.normal_dots += 1 if is_dot else 0
        bs.normal_innings.add(inn_key)
        
        # Death overs
        if over_num >= 16:
            bs.death_runs += ball_runs
            if is_legal:
                bs.death_balls += 1
            bs.death_wickets += 1 if bowler_wkt else 0
            bs.death_fours += 1 if is_four else 0
            bs.death_sixes += 1 if is_six else 0
            bs.death_dots += 1 if is_dot else 0
            bs.death_innings.add(inn_key)
            bs.death_runs_per_inn[inn_key] += ball_runs
            if is_legal:
                bs.death_balls_per_inn[inn_key] += 1
            if bowler_wkt:
                bs.death_wkts_per_inn[inn_key] += 1
        
        # Middle overs (7-15)
        if 7 <= over_num <= 15:
            bs.middle_runs += ball_runs
            if is_legal:
                bs.middle_balls += 1
            bs.middle_wickets += 1 if bowler_wkt else 0
            if is_dot:
                bs.middle_dots += 1
            bs.middle_innings.add(inn_key)
        
        # Knockout
        if is_ko:
            bs.ko_runs += ball_runs
            bs.ko_balls += 1 if is_legal else 0
            bs.ko_wickets += 1 if bowler_wkt else 0


# ============================================================
# 6. COMPUTE COMPOSITE INDICES
# ============================================================
print("\n" + "=" * 70)
print("STEP 6: COMPUTING COMPOSITE INDICES")
print("=" * 70)

MIN_DEATH_BALLS_BATTER = 100
MIN_DEATH_BALLS_BOWLER = 80
MIN_MIDDLE_BALLS_BOWLER = 100

# Target players for analysis
target_batters = {
    'Tim David', 'Liam Livingstone', 'Rovman Powell', 'Rinku Singh',
    'Shashank Singh', 'Ashutosh Sharma', 'Jitesh Sharma', 'Venkatesh Iyer',
    'Nehal Wadhera', 'Sameer Rizvi', 'Hardik Pandya', 'Suryakumar Yadav',
    'Heinrich Klaasen', 'David Miller', 'Andre Russell', 'Dinesh Karthik',
    'Glenn Maxwell', 'Tristan Stubbs', 'Matthew Wade', 'Shimron Hetmyer',
    'Dasun Shanaka', 'Abdul Samad', 'Tilak Varma', 'Nitish Rana',
    'Deepak Hooda', 'Rahul Tripathi', 'Dhruv Jurel', 'Riyan Parag'
}

target_bowlers = {
    'T Natarajan', 'Thangarasu Natarajan', 'Harshit Rana', 'Mukesh Kumar',
    'Khaleel Ahmed', 'Avesh Khan', 'Harshal Patel', 'Varun Chakravarthy',
    'Noor Ahmad', 'Suyash Sharma', 'Matheesha Pathirana', 'Jofra Archer',
    'Yuzvendra Chahal', 'Rashid Khan', 'Mayank Markande', 'Tushar Deshpande',
    'Mohit Sharma', 'Mohammed Shami', 'T Natarajan', 'Deepak Chahar',
    'Shardul Thakur', 'Arshdeep Singh', 'Bhuvneshwar Kumar', 'Hardik Pandya',
    'Marco Jansen', 'Gerald Coetzee', 'Alzarri Joseph', 'Lockie Ferguson',
    'Adam Zampa', 'Ravi Bishnoi', 'Kuldeep Yadav', 'Washington Sundar',
    'Shahbaz Ahmed', 'Noor Ahmad', 'Mitchell Starc', 'Pat Cummins',
    'Trent Boult', 'Anrich Nortje', 'Spencer Johnson', 'Jasprit Bumrah',
    'Mohammed Siraj', 'Shreyas Iyer', 'Wanindu Hasaranga'
}

# BATTER COMPOSITE INDEX
# Weights: 40% performance, 30% consistency, 20% delta (pressure vs normal), 10% sample
# Performance = death SR + boundary % - dot %
# Consistency = 1 - CV of innings scores (SD/mean), lower CV = more consistent
# Delta = pressure SR - normal SR (normalized)
# Sample = log(balls) / log(max_balls)

def normalize(val, min_val, max_val):
    if max_val == min_val:
        return 0.5
    return max(0, min(1, (val - min_val) / (max_val - min_val)))

batter_scores = []

for pid, bs in batter_stats.items():
    if bs.death_balls < MIN_DEATH_BALLS_BATTER:
        continue
    
    # Death SR
    death_sr = (bs.death_runs / bs.death_balls * 100) if bs.death_balls > 0 else 0
    
    # Death boundary %
    death_boundary = ((bs.death_fours + bs.death_sixes) / bs.death_balls * 100) if bs.death_balls > 0 else 0
    
    # Death dot %
    death_dot = (bs.death_dots / bs.death_balls * 100) if bs.death_balls > 0 else 0
    
    # Death average (runs per dismissal)
    death_avg = bs.death_runs / bs.death_dismissals if bs.death_dismissals > 0 else bs.death_runs + 10
    
    # Normal SR
    normal_sr = (bs.normal_runs / bs.normal_balls * 100) if bs.normal_balls > 0 else 0
    
    # Pressure delta (death SR - normal SR)
    delta_sr = death_sr - normal_sr
    
    # Chase pressure SR
    chase_sr = (bs.chase_pressure_runs / bs.chase_pressure_balls * 100) if bs.chase_pressure_balls > 0 else 0
    
    # Knockout stats
    ko_sr = (bs.ko_runs / bs.ko_balls * 100) if bs.ko_balls > 0 else 0
    
    # Sample confidence (log scale)
    sample_conf = math.log(bs.death_balls + 1) / math.log(300)  # 300 balls as reference max
    
    batter_scores.append({
        'player_id': pid,
        'player_name': bs.name,
        'death_balls': bs.death_balls,
        'death_runs': bs.death_runs,
        'death_sr': death_sr,
        'death_avg': death_avg,
        'death_boundary_pct': death_boundary,
        'death_dot_pct': death_dot,
        'death_dismissals': bs.death_dismissals,
        'death_innings': len(bs.death_innings),
        'chase_pressure_balls': bs.chase_pressure_balls,
        'chase_sr': chase_sr,
        'chase_pressure_runs': bs.chase_pressure_runs,
        'ko_sr': ko_sr,
        'ko_balls': bs.ko_balls,
        'collapse_runs': bs.collapse_runs,
        'collapse_balls': bs.collapse_balls,
        'normal_sr': normal_sr,
        'normal_runs': bs.normal_runs,
        'normal_balls': bs.normal_balls,
        'delta_sr': delta_sr,
        'sample_conf': sample_conf,
    })

# Normalize and score
metrics_to_normalize = ['death_sr', 'death_boundary_pct', 'chase_sr', 'delta_sr']
metrics_neg = ['death_dot_pct']  # lower is better

for metric in metrics_to_normalize + metrics_neg:
    vals = [s[metric] for s in batter_scores]
    mn, mx = min(vals), max(vals)
    for s in batter_scores:
        s[f'{metric}_norm'] = normalize(s[metric], mn, mx)

# Invert negative metrics
for s in batter_scores:
    for metric in metrics_neg:
        s[f'{metric}_norm'] = 1 - s[f'{metric}_norm']

for s in batter_scores:
    # Performance (40%): blend death SR (60%) + boundary % (25%) - dot % (15%)
    perf = 0.60 * s['death_sr_norm'] + 0.25 * s['death_boundary_pct_norm'] + 0.15 * s['death_dot_pct_norm']
    
    # Consistency (30%): hard to compute without match-level splits, use chase SR as proxy for adaptability
    # Using ratio of chase_sr to normal_sr as clutch factor
    clutch = s['chase_sr_norm'] if s['chase_pressure_balls'] > 20 else s['death_sr_norm'] * 0.8
    
    # Delta (20%): how much SR rises under pressure
    delta = s['delta_sr_norm']
    
    # Sample (10%)
    sample = min(1.0, s['sample_conf'])
    
    s['composite'] = 0.40 * perf + 0.30 * clutch + 0.20 * delta + 0.10 * sample

# Sort by composite
batter_scores.sort(key=lambda x: x['composite'], reverse=True)

print("\nTOP 20 BATTERS BY COMPOSITE PRESSURE INDEX (min 100 death balls in IPL):")
print(f"{'Rank':<5} {'Player':<25} {'DeathSR':<10} {'DeathAvg':<10} {'Boundary%':<12} {'Dot%':<8} {'ChaseSR':<10} {'DeltaSR':<10} {'Balls':<8} {'Index':<8}")
print("-" * 110)
for i, s in enumerate(batter_scores[:25], 1):
    print(f"{i:<5} {s['player_name']:<25} {s['death_sr']:>8.1f} {s['death_avg']:>9.1f} {s['death_boundary_pct']:>10.1f}% {s['death_dot_pct']:>6.1f}% {s['chase_sr']:>8.1f} {s['delta_sr']:>+9.1f} {s['death_balls']:>6} {s['composite']:>8.3f}")


# BOWLER COMPOSITE INDEX
bowler_scores = []

for pid, bs in bowler_stats.items():
    if bs.death_balls < MIN_DEATH_BALLS_BOWLER:
        continue
    
    # Death metrics
    death_econ = (bs.death_runs / bs.death_balls * 6) if bs.death_balls > 0 else 99
    death_dot_pct = (bs.death_dots / bs.death_balls * 100) if bs.death_balls > 0 else 0
    death_boundary_pct = ((bs.death_fours + bs.death_sixes) / bs.death_balls * 100) if bs.death_balls > 0 else 0
    death_wkts_per_inn = (bs.death_wickets / len(bs.death_innings)) if bs.death_innings else 0
    
    # Innings-level consistency for death economy
    inn_economies = []
    for inn_key in bs.death_runs_per_inn:
        balls = bs.death_balls_per_inn[inn_key]
        if balls >= 3:  # at least 3 balls bowled in death
            econ = bs.death_runs_per_inn[inn_key] / balls * 6
            inn_economies.append(econ)
    
    if len(inn_economies) >= 3:
        mean_econ = sum(inn_economies) / len(inn_economies)
        variance = sum((e - mean_econ) ** 2 for e in inn_economies) / len(inn_economies)
        std_econ = math.sqrt(variance)
        cv_econ = std_econ / mean_econ if mean_econ > 0 else 1
    else:
        cv_econ = 0.5  # default
    
    # Normal economy
    normal_econ = (bs.normal_runs_conceded / bs.normal_balls * 6) if bs.normal_balls > 0 else 99
    
    # Delta economy (improvement under pressure vs normal, negative = better in death)
    delta_econ = death_econ - normal_econ  # negative = specializes well in death
    
    # Middle over metrics
    middle_econ = (bs.middle_runs / bs.middle_balls * 6) if bs.middle_balls > 0 else 99
    middle_dot_pct = (bs.middle_dots / bs.middle_balls * 100) if bs.middle_balls > 0 else 0
    middle_wkts_per_inn = (bs.middle_wickets / len(bs.middle_innings)) if bs.middle_innings else 0
    
    # Sample confidence
    sample_conf = min(1.0, math.log(bs.death_balls + 1) / math.log(300))
    
    bowler_scores.append({
        'player_id': pid,
        'player_name': bs.name,
        'pace_or_spin': bs.pace_or_spin,
        'death_balls': bs.death_balls,
        'death_econ': death_econ,
        'death_dot_pct': death_dot_pct,
        'death_boundary_pct': death_boundary_pct,
        'death_wkts': bs.death_wickets,
        'death_wkts_per_inn': death_wkts_per_inn,
        'death_innings': len(bs.death_innings),
        'cv_econ': cv_econ,
        'consistency_score': 1 - min(1, cv_econ),  # higher = more consistent
        'normal_econ': normal_econ,
        'delta_econ': delta_econ,
        'middle_balls': bs.middle_balls,
        'middle_econ': middle_econ,
        'middle_dot_pct': middle_dot_pct,
        'middle_wkts_per_inn': middle_wkts_per_inn,
        'middle_wickets': bs.middle_wickets,
        'ko_balls': bs.ko_balls,
        'ko_wickets': bs.ko_wickets,
        'sample_conf': sample_conf,
        'normal_balls': bs.normal_balls,
        'normal_wickets': bs.normal_wickets,
    })

# Normalize bowler metrics (for death economy, lower is better)
def normalize_bowler(val, min_val, max_val, invert=False):
    if max_val == min_val:
        return 0.5
    norm = max(0, min(1, (val - min_val) / (max_val - min_val)))
    return 1 - norm if invert else norm

# Compute normalization bounds
death_econs = [s['death_econ'] for s in bowler_scores]
death_dots = [s['death_dot_pct'] for s in bowler_scores]
death_bdrys = [s['death_boundary_pct'] for s in bowler_scores]
consistencies = [s['consistency_score'] for s in bowler_scores]
delta_econs = [s['delta_econ'] for s in bowler_scores]

mn_econ, mx_econ = min(death_econs), max(death_econs)
mn_dot, mx_dot = min(death_dots), max(death_dots)
mn_bdry, mx_bdry = min(death_bdrys), max(death_bdrys)
mn_cons, mx_cons = min(consistencies), max(consistencies)
mn_delta, mx_delta = min(delta_econs), max(delta_econs)

for s in bowler_scores:
    # Invert economy (lower = better -> higher score)
    s['econ_norm'] = normalize_bowler(s['death_econ'], mn_econ, mx_econ, invert=True)
    s['dot_norm'] = normalize_bowler(s['death_dot_pct'], mn_dot, mx_dot)
    s['bdry_norm'] = normalize_bowler(s['death_boundary_pct'], mn_bdry, mx_bdry, invert=True)
    s['cons_norm'] = normalize_bowler(s['consistency_score'], mn_cons, mx_cons)
    # Delta: more negative = better (bowls more economically in death vs overall)
    s['delta_norm'] = normalize_bowler(s['delta_econ'], mn_delta, mx_delta, invert=True)
    
    # Composite: 40% performance, 30% consistency, 20% delta, 10% sample
    perf = 0.50 * s['econ_norm'] + 0.30 * s['dot_norm'] + 0.20 * s['bdry_norm']
    s['composite'] = 0.40 * perf + 0.30 * s['cons_norm'] + 0.20 * s['delta_norm'] + 0.10 * s['sample_conf']

bowler_scores.sort(key=lambda x: x['composite'], reverse=True)

print("\n\nTOP 20 BOWLERS BY COMPOSITE PRESSURE INDEX (min 80 death balls in IPL):")
print(f"{'Rank':<5} {'Player':<25} {'Type':<8} {'DthEco':<8} {'Dot%':<7} {'Bdry%':<7} {'W/Inn':<7} {'DInns':<7} {'CV':<7} {'Index':<8}")
print("-" * 95)
for i, s in enumerate(bowler_scores[:25], 1):
    print(f"{i:<5} {s['player_name']:<25} {s['pace_or_spin']:<8} {s['death_econ']:>6.2f} {s['death_dot_pct']:>6.1f}% {s['death_boundary_pct']:>6.1f}% {s['death_wkts_per_inn']:>6.2f} {s['death_innings']:>6} {s['cv_econ']:>6.2f} {s['composite']:>8.3f}")


# ============================================================
# 7. MIDDLE OVERS BOWLER RANKINGS (Spinners and Pace)
# ============================================================
print("\n\nTOP MIDDLE OVERS BOWLERS (min 100 middle-over balls):")
middle_bowlers = [s for s in bowler_scores if s['middle_balls'] >= MIN_MIDDLE_BALLS_BOWLER]
middle_bowlers.sort(key=lambda x: x['middle_wkts_per_inn'] * 0.5 + (1/max(x['middle_econ'], 1)) * 20, reverse=True)

print(f"{'Rank':<5} {'Player':<25} {'Type':<8} {'MidEco':<8} {'Dot%':<7} {'W/Inn':<7} {'MidWkts':<8} {'MidInns':<8}")
print("-" * 80)
for i, s in enumerate(middle_bowlers[:20], 1):
    print(f"{i:<5} {s['player_name']:<25} {s['pace_or_spin']:<8} {s['middle_econ']:>6.2f} {s['middle_dot_pct']:>6.1f}% {s['middle_wkts_per_inn']:>6.2f} {s['middle_wickets']:>7} {len([k for k in s]):>7}")


# ============================================================
# 8. SAVE RESULTS TO FILE
# ============================================================
print("\n\nSaving results...")

# Save comprehensive results
with open('/Users/raghavpatil/Desktop/RR_HACKATHON/batter_results.txt', 'w') as f:
    f.write("BATTER PRESSURE ANALYSIS - IPL 2022-2026\n")
    f.write("=" * 120 + "\n")
    f.write(f"{'Rank':<5} {'Player':<25} {'DeathSR':<10} {'DeathAvg':<10} {'Boundary%':<12} {'Dot%':<8} {'ChaseSR':<10} {'DeltaSR':<10} {'DthBalls':<10} {'DthInns':<8} {'Index':<8}\n")
    f.write("-" * 120 + "\n")
    for i, s in enumerate(batter_scores[:50], 1):
        f.write(f"{i:<5} {s['player_name']:<25} {s['death_sr']:>8.1f} {s['death_avg']:>9.1f} {s['death_boundary_pct']:>10.1f}% {s['death_dot_pct']:>6.1f}% {s['chase_sr']:>8.1f} {s['delta_sr']:>+9.1f} {s['death_balls']:>8} {s['death_innings']:>8} {s['composite']:>8.3f}\n")

with open('/Users/raghavpatil/Desktop/RR_HACKATHON/bowler_results.txt', 'w') as f:
    f.write("BOWLER PRESSURE ANALYSIS - IPL 2022-2026\n")
    f.write("=" * 120 + "\n")
    f.write(f"{'Rank':<5} {'Player':<25} {'Type':<8} {'DthEco':<8} {'Dot%':<7} {'Bdry%':<7} {'W/Inn':<7} {'DthWkts':<8} {'DthInns':<8} {'CV':<7} {'NrmEco':<8} {'DeltaEco':<10} {'MidEco':<8} {'MidWkts':<8} {'Index':<8}\n")
    f.write("-" * 120 + "\n")
    for i, s in enumerate(bowler_scores[:50], 1):
        f.write(f"{i:<5} {s['player_name']:<25} {s['pace_or_spin']:<8} {s['death_econ']:>6.2f} {s['death_dot_pct']:>6.1f}% {s['death_boundary_pct']:>6.1f}% {s['death_wkts_per_inn']:>6.2f} {s['death_wkts']:>7} {s['death_innings']:>7} {s['cv_econ']:>6.2f} {s['normal_econ']:>7.2f} {s['delta_econ']:>+9.2f} {s['middle_econ']:>7.2f} {s['middle_wickets']:>7} {s['composite']:>8.3f}\n")

print("Done! Results saved to batter_results.txt and bowler_results.txt")

# Also print top candidates from seed list
print("\n\nSEED LIST PLAYER CHECK - BATTERS:")
seed_batters = ['Tim David', 'Liam Livingstone', 'Rovman Powell', 'Rinku Singh',
                'Shashank Singh', 'Ashutosh Sharma', 'Jitesh Sharma', 'Venkatesh Iyer',
                'Nehal Wadhera', 'Sameer Rizvi']
for player in seed_batters:
    found = [s for s in batter_scores if player.lower() in s['player_name'].lower()]
    if found:
        s = found[0]
        rank = batter_scores.index(s) + 1
        print(f"  {s['player_name']:<25} Rank: {rank:<5} DeathSR: {s['death_sr']:>7.1f} Balls: {s['death_balls']:>5} Index: {s['composite']:.3f}")
    else:
        # Check if they appear in batter_stats but not in filtered list
        found_unfiltered = [bs for pid, bs in batter_stats.items() if player.lower() in bs.name.lower()]
        if found_unfiltered:
            bs = found_unfiltered[0]
            print(f"  {bs.name:<25} Below threshold: death_balls={batter_stats[[pid for pid,b in batter_stats.items() if b.name==bs.name][0]].death_balls}")
        else:
            print(f"  {player:<25} NOT FOUND in data")

print("\nSEED LIST PLAYER CHECK - BOWLERS:")
seed_bowlers = ['T Natarajan', 'Thangarasu Natarajan', 'Harshit Rana', 'Mukesh Kumar',
                'Khaleel Ahmed', 'Avesh Khan', 'Harshal Patel', 'Varun Chakravarthy',
                'Noor Ahmad', 'Suyash Sharma', 'Matheesha Pathirana']
for player in seed_bowlers:
    found = [s for s in bowler_scores if player.lower() in s['player_name'].lower()]
    if found:
        s = found[0]
        rank = bowler_scores.index(s) + 1
        print(f"  {s['player_name']:<25} Rank: {rank:<5} DthEco: {s['death_econ']:>6.2f} Balls: {s['death_balls']:>5} Index: {s['composite']:.3f}")
    else:
        found_unfiltered = [bs for pid, bs in bowler_stats.items() if player.lower() in bs.name.lower()]
        if found_unfiltered:
            bs = found_unfiltered[0]
            pid = [p for p,b in bowler_stats.items() if b.name==bs.name][0]
            print(f"  {bs.name:<25} Below threshold: death_balls={bowler_stats[pid].death_balls}, middle_balls={bowler_stats[pid].middle_balls}")
        else:
            print(f"  {player:<25} NOT FOUND in data")

