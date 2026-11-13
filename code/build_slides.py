#!/usr/bin/env python3
"""
Build RR Auction Slide Deck as multi-page PDF using matplotlib
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.gridspec as gridspec
import numpy as np
import json

# ===== COLOR PALETTE =====
RR_PINK   = '#E8175D'  # Rajasthan Royals primary
RR_BLUE   = '#254AA5'  # Secondary
RR_GOLD   = '#F7CB15'  # Accent
BG_DARK   = '#0D0D1A'  # Dark background
BG_MID    = '#1A1A2E'
BG_LIGHT  = '#16213E'
TEXT_WHITE = '#FFFFFF'
TEXT_GREY  = '#B0B0C0'
TEXT_GOLD  = '#F7CB15'
GREEN_OK   = '#00C851'
RED_ALERT  = '#FF4444'
AMBER      = '#FFBB33'

# ===== DATA =====

TOP_BATTERS = [
    # name, role, dsr, davg, bdry, dot, chasesr, delta, balls, inns, consist, index, rr_gap
    ("Rinku Singh",      "Finisher",        192.5, 42.6, 29.4, 27.1, 178.0, +42.8, 398, 37, 0.65, 0.763, "Death #5-6, chase anchor"),
    ("Tim David",        "Death Finisher",  197.0, 31.1, 27.9, 26.0, 190.2, +19.5, 427, 48, 0.54, 0.738, "Death power, chase RRR>10"),
    ("Shashank Singh",   "Middle Order",    195.4, 39.4, 27.1, 19.1, 172.8, +33.8, 262, 30, 0.55, 0.728, "Positions 4-6, flexible"),
    ("Ashutosh Sharma",  "Finisher",        191.6, 29.3, 28.5, 23.8, 181.4, +22.8, 214, 21, 0.53, 0.716, "Death + RRR pressure"),
    ("Jitesh Sharma",    "WK-Finisher",     182.4, 21.7, 26.3, 29.4, 167.0, +29.9, 262, 33, 0.49, 0.649, "Indian death bat + WK backup"),
    ("Rovman Powell",    "Death Hitter",    188.9, 23.5, 29.0, 32.1, 147.9, +46.2, 162, 19, 0.62, 0.672, "Overs 17-20 big-hitting"),
    ("Nitish Reddy",     "All-Rounder",     197.5, 23.5, 26.9, 25.2, 140.7, +51.9, 119, 18, 0.70, 0.697, "RR bat depth + medium pace"),
    ("Heinrich Klaasen", "Middle Order",    197.4, 27.6, 26.6, 20.6, 178.6, +27.9, 350, 34, 0.69, 0.760, "Highest consistency overseas"),
    ("Tristan Stubbs",   "Anchor-Finisher", 197.1, 60.0, 27.4, 16.4, 157.2, +46.3, 274, 29, 0.59, 0.730, "Best death avg; overseas slot"),
    ("Naman Dhir",       "Finisher",        194.7, 26.9, 28.9, 23.7, 193.3, +30.4, 152, 18, 0.60, 0.769, "Highest chase SR in list"),
]

TOP_BOWLERS = [
    # name, type, deco, dot, bdry, wpi, wkts, inns, cv, allecon, delta, midecon, mwpi, balls, index, rr_gap
    ("Matheesha Pathirana","Pace", 8.32, 31.3, 18.1, 1.16, 47, 40, 0.42, 7.65, +0.68, 7.02, 0.44, 403, 0.665, "Jofra support; slinga unique"),
    ("Harshal Patel",      "Pace", 9.38, 30.4, 21.0, 1.04, 53, 51, 0.48, 8.68, +0.70, 7.91, 0.45, 504, 0.599, "Highest Indian death wkts"),
    ("Harshit Rana",       "Pace", 9.32, 33.8, 22.3, 0.74, 14, 19, 0.52, 9.18, +0.14, 9.05, 0.46, 157, 0.544, "Indian death + dot balls"),
    ("Avesh Khan",         "Pace", 9.68, 26.7, 22.0, 0.70, 35, 50, 0.39, 9.42, +0.26, 8.39, 0.48, 460, 0.531, "Indian death; large sample"),
    ("Varun Chakravarthy", "Spin", 8.87, 37.2, 15.3, 0.43, 34, 63, 0.44, 7.57, +1.30, 7.67, 0.81, 226, 0.485, "Middle-overs wrist spin #1 Indian"),
    ("Noor Ahmad",         "Spin", 7.63, 40.4, 15.2, 0.59, 13, 22, 0.61, 7.83, -0.20, 7.79, 0.88, 151, 0.605, "Best economy & dot% all-rounder"),
    ("Suyash Sharma",      "Spin", 8.97, 30.5, 16.4, 0.25, 4, 16, 0.44, 8.44, +0.53, 8.71, 0.56, 95, 0.448, "Young wrist-spin; RR type"),
    ("T Natarajan",        "Pace", 10.02, 26.0, 23.5, 0.84, 38, 45, 0.44, 9.28, +0.74, 8.85, 0.23, 442, 0.521, "Death yorker specialist"),
    ("Wanindu Hasaranga",  "Spin", 8.00, 36.8, 15.8, 0.63, 12, 19, 0.67, 8.24, -0.24, 8.15, 0.89, 136, 0.572, "Best overall spinner metric"),
    ("Mohit Sharma",       "Pace", 10.18, 24.8, 21.0, 1.07, 29, 27, 0.45, 9.35, +0.82, 8.39, 0.68, 282, 0.562, "Death wicket specialist"),
]

# Auction priority order
PRIORITY = [
    ("Rinku Singh",       "MUST BID",  "INR", 14, "Fills death #5-6, Indian, proven pressure performer (427 balls, SR 192+)"),
    ("Harshal Patel",     "MUST BID",  "INR", 11, "Best Indian death bowler by wkts (53 death wkts, 1.04/inn), replaces Deshpande"),
    ("Varun Chakravarthy","MUST BID",  "INR", 13, "Wrist-spin middle overs, 0.81 wpi, 36% dot rate — fills spinner gap"),
    ("Noor Ahmad",        "HIGH",      "OS",   8, "Best overall spinner economy (7.63 death, 7.79 mid), Noor + Jadeja = elite"),
    ("Matheesha Pathirana","HIGH",     "OS",  10, "Support Archer with slinga pace; 1.16 wkts/inn in death"),
    ("Tim David",         "HIGH",      "OS",  12, "Death SR 197, chase SR 190 — world-class finisher, overseas slot"),
    ("Shashank Singh",    "HIGH",      "INR",  9, "Middle-order gap 4-6, 195 death SR, 39 avg; large sample, Indian"),
    ("Ashutosh Sharma",   "TACTICAL",  "INR",  7, "Death finisher backup; Indian; holds up under RRR>10"),
    ("Tristan Stubbs",    "TACTICAL",  "OS",   8, "Death avg 60 (highest); if Klaasen/others go high, Stubbs is best value"),
    ("Harshit Rana",      "TACTICAL",  "INR",  7, "Young Indian death-pace; 33.8% dot rate; buy if Harshal overbid"),
]


def fig_slide(title_text=None, subtitle_text=None, figsize=(19.2, 10.8)):
    fig = plt.figure(figsize=figsize, facecolor=BG_DARK)
    # Header strip
    ax_hdr = fig.add_axes([0, 0.91, 1, 0.09])
    ax_hdr.set_xlim(0, 1); ax_hdr.set_ylim(0, 1)
    ax_hdr.axis('off')
    ax_hdr.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="square,pad=0", 
                                     fc=RR_PINK, ec='none'))
    ax_hdr.add_patch(FancyBboxPatch((0.72, 0), 0.28, 1, boxstyle="square,pad=0",
                                     fc=RR_BLUE, ec='none'))
    if title_text:
        ax_hdr.text(0.02, 0.5, title_text, color=TEXT_WHITE, fontsize=16,
                    fontweight='bold', va='center', ha='left')
    ax_hdr.text(0.74, 0.5, 'SupeRR Selector Season 2', color=TEXT_WHITE,
                fontsize=9, va='center', ha='left', style='italic')
    ax_hdr.text(0.98, 0.5, '♦ RR Analytics', color=RR_GOLD, fontsize=10,
                va='center', ha='right', fontweight='bold')
    return fig


def add_footer(fig, text="IPL 2022-2026 Data | RR Internal Use Only | Nov 2026"):
    ax_ft = fig.add_axes([0, 0, 1, 0.025])
    ax_ft.set_xlim(0, 1); ax_ft.set_ylim(0, 1)
    ax_ft.axis('off')
    ax_ft.add_patch(FancyBboxPatch((0,0), 1, 1, boxstyle="square,pad=0", fc=BG_MID, ec='none'))
    ax_ft.text(0.5, 0.5, text, color=TEXT_GREY, fontsize=7, va='center', ha='center')


def colored_cell(ax, x, y, w, h, text, fc, tc=TEXT_WHITE, fontsize=9, bold=False, ha='center'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0", fc=fc, ec=BG_DARK, lw=0.5))
    ax.text(x + w/2, y + h/2, text, color=tc, fontsize=fontsize,
            va='center', ha=ha if ha=='center' else 'left',
            fontweight='bold' if bold else 'normal',
            x=x + (0.01 if ha=='left' else w/2))

# ============================================================
# SLIDE 1: TITLE SLIDE
# ============================================================
fig1 = plt.figure(figsize=(19.2, 10.8), facecolor=BG_DARK)

# Large pink banner
ax = fig1.add_axes([0, 0.6, 1, 0.4])
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 1, 1, boxstyle="square,pad=0", fc=RR_PINK, ec='none'))
ax.text(0.5, 0.65, 'SupeRR Selector Season 2', color=TEXT_WHITE, fontsize=22,
        fontweight='bold', ha='center', va='center')
ax.text(0.5, 0.35, 'IPL 2027 Mini-Auction · Pressure Player Intelligence Report',
        color=RR_GOLD, fontsize=15, ha='center', va='center')

ax2 = fig1.add_axes([0, 0.3, 1, 0.3])
ax2.set_xlim(0, 1); ax2.set_ylim(0, 1); ax2.axis('off')
ax2.text(0.5, 0.78, 'Rajasthan Royals — Auction Analytics', color=TEXT_WHITE, fontsize=18,
         ha='center', va='center', fontweight='bold')
ax2.text(0.5, 0.52, '5 IPL Seasons · 371 matches · 87,687 deliveries analysed',
         color=TEXT_GREY, fontsize=12, ha='center', va='center')

stats_text = [
    ('20', 'Knockout\nMatches'),
    ('35', 'Close-Finish\nMatches'),
    ('5', 'Pressure\nScenarios'),
    ('4', 'Composite\nIndex Weights'),
]
for i, (val, lbl) in enumerate(stats_text):
    x = 0.1 + i * 0.22
    ax2.add_patch(FancyBboxPatch((x, 0.02), 0.16, 0.38, boxstyle="round,pad=0.01", fc=RR_BLUE, ec=RR_GOLD, lw=1.5))
    ax2.text(x+0.08, 0.26, val, color=RR_GOLD, fontsize=20, ha='center', va='center', fontweight='bold')
    ax2.text(x+0.08, 0.10, lbl, color=TEXT_GREY, fontsize=8, ha='center', va='center')

ax3 = fig1.add_axes([0, 0.0, 1, 0.3])
ax3.set_xlim(0, 1); ax3.set_ylim(0, 1); ax3.axis('off')
ax3.add_patch(FancyBboxPatch((0,0), 1, 1, boxstyle="square,pad=0", fc=BG_MID, ec='none'))
info = [
    ('Auction', '16 Dec 2026 · Goa'),
    ('Retention Deadline', '15 Nov 2026'),
    ('RR 2026 Finish', 'Top 4, lost Qualifier 2'),
    ('Overseas Slots', 'Up to 8 total'),
    ('Data Source', 'IPL 2022–2026 ball-by-ball'),
]
for i, (k, v) in enumerate(info):
    x = 0.02 + i * 0.20
    ax3.text(x, 0.70, k, color=RR_GOLD, fontsize=9, fontweight='bold')
    ax3.text(x, 0.42, v, color=TEXT_WHITE, fontsize=9)

ax3.text(0.5, 0.12, 'PREPARED BY: RR Analytics | CONFIDENTIAL', 
         color=TEXT_GREY, fontsize=9, ha='center', style='italic')

plt.savefig('/Users/raghavpatil/Desktop/RR_HACKATHON/slide01_title.png', 
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 1 done")

# ============================================================
# SLIDE 2: METHODOLOGY - Pressure Definitions
# ============================================================
fig2 = fig_slide("METHODOLOGY  |  Pressure Definitions & Metrics")
add_footer(fig2)

ax = fig2.add_axes([0.01, 0.03, 0.98, 0.87])
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 10, 10, boxstyle="square,pad=0", fc=BG_MID, ec='none'))

# Pressure definitions box
pdef_title = ax.text(0.2, 9.5, '① PRESSURE DEFINITIONS', color=RR_GOLD, fontsize=13, fontweight='bold')

defs = [
    ("P1", "DEATH OVERS", "RR_PINK", "Overs 16–20, both innings. Highest leverage; small margins decide games."),
    ("P2", "CHASE PRESSURE", RR_BLUE, "Inn 2, Required Run Rate > 10 at time of delivery. Pure time-pressure scenario."),
    ("P3", "COLLAPSE RECOVERY", "#6A0DAD", "Inn 1 batter entering after 3+ wickets in first 10 overs. Tests mental resilience."),
    ("P4", "KNOCKOUT MATCH", "#1E8449", "knock_out=1 or Stage ∈ {Qualifier, Eliminator, Final, Semi Final}. Must-win pressure."),
    ("P5", "CLOSE FINISH", "#D68910", "Match won/lost by ≤9 runs or ≤2 wickets. High-stakes, final-over context."),
]

for i, (code, label, color, desc) in enumerate(defs):
    y = 8.5 - i * 1.5
    ax.add_patch(FancyBboxPatch((0.1, y-0.5), 0.7, 0.9, boxstyle="round,pad=0.05", 
                                 fc=RR_PINK if color=="RR_PINK" else color, ec='none'))
    ax.text(0.45, y+0.0, code, color=TEXT_WHITE, fontsize=10, ha='center', va='center', fontweight='bold')
    ax.text(1.0, y+0.1, label, color=RR_GOLD, fontsize=11, fontweight='bold', va='center')
    ax.text(1.0, y-0.2, desc, color=TEXT_WHITE, fontsize=9, va='center')

# Metrics & Composite Index
ax.text(5.2, 9.5, '② METRICS', color=RR_GOLD, fontsize=13, fontweight='bold')
ax.add_patch(FancyBboxPatch((5.1, 2.8), 4.7, 6.5, boxstyle="round,pad=0.1", fc=BG_LIGHT, ec=RR_PINK, lw=1.5))

batter_metrics = [
    "BATTER METRICS:",
    "• Death-over Strike Rate (SR in overs 16-20)",
    "• Death Average (runs per dismissal in death)",
    "• Boundary % (4s+6s / balls in death)",
    "• Dot Ball % (dots / balls in death)",
    "• Chase SR (overs where RRR > 10)",
    "• Delta SR (Death SR minus Overall SR)",
]
for i, m in enumerate(batter_metrics):
    color = RR_GOLD if ':' in m else TEXT_WHITE
    bold = ':' in m
    ax.text(5.3, 9.1 - i*0.52, m, color=color, fontsize=9.5, 
            fontweight='bold' if bold else 'normal', va='center')

bowler_metrics = [
    "BOWLER METRICS:",
    "• Death Economy (runs/over in overs 16-20)",
    "• Death Dot % (dots / legal balls in death)",
    "• Boundary % Conceded (4s+6s / balls)",
    "• Wickets per Innings (death + middle overs)",
    "• Middle-over Economy (overs 7-15)",
    "• CV of Economy (consistency measure)",
]
for i, m in enumerate(bowler_metrics):
    color = RR_GOLD if ':' in m else TEXT_WHITE
    bold = ':' in m
    ax.text(5.3, 5.5 - i*0.52, m, color=color, fontsize=9.5, 
            fontweight='bold' if bold else 'normal', va='center')

ax.add_patch(FancyBboxPatch((5.1, 0.1), 4.7, 2.5, boxstyle="round,pad=0.1", fc=RR_BLUE, ec=RR_GOLD, lw=1.5))
ax.text(5.3, 2.4, '③ COMPOSITE INDEX WEIGHTS', color=RR_GOLD, fontsize=11, fontweight='bold')
weights = [
    ("40%", "PERFORMANCE", "Death SR / Economy + Boundary% + Dot%"),
    ("25%", "PRESSURE CLUTCH", "Chase SR (RRR>10) / Knockout performance"),
    ("20%", "CONSISTENCY", "1 − CV of innings-level metric"),
    ("10%", "PRESSURE DELTA", "Improvement vs overall performance"),
    ("5%",  "SAMPLE SIZE",   "log(balls) / log(400) confidence"),
]
for i, (pct, lbl, desc) in enumerate(weights):
    y = 2.0 - i * 0.37
    ax.text(5.3, y, f'{pct}', color=RR_GOLD, fontsize=11, fontweight='bold')
    ax.text(5.8, y, f'{lbl}:', color=TEXT_WHITE, fontsize=9, fontweight='bold')
    ax.text(7.3, y, desc, color=TEXT_GREY, fontsize=8.5)

ax.text(0.2, 0.5, '⚠ Min threshold: 100 death-over balls (batters), 60 death-over balls (bowlers) to qualify',
        color=AMBER, fontsize=9, style='italic')
ax.text(0.2, 0.15, 'Sample: IPL 2022–2026 · 371 matches · 87,687 deliveries · 20 knockout matches',
        color=TEXT_GREY, fontsize=9)

plt.savefig('/Users/raghavpatil/Desktop/RR_HACKATHON/slide02_methodology.png', 
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 2 done")

# ============================================================
# SLIDE 3: TOP 10 BATTERS (Part 1: ranks 1-5)
# ============================================================
fig3 = fig_slide("TOP 10 PRESSURE BATTERS  |  RR 2027 Auction Targets  (Ranks 1-5)")
add_footer(fig3)

ax = fig3.add_axes([0.01, 0.03, 0.98, 0.87])
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle="square,pad=0", fc=BG_MID, ec='none'))

# Column headers
headers = ['#', 'PLAYER', 'ROLE', 'Death SR', 'Death Avg', 'Bdry%', 'Dot%', 'Chase SR', 'ΔSR', 'Consistency', 'Balls', 'INDEX', 'RR GAP']
col_x =   [0.5,  2,       14,     26,          34,          41,      47,      53,         59,    64,            72,     79,       85]
col_w =   [1.5,  12,      12,     8,           8,           6,       6,       6,          5,     7,             7,      6,        15]

for j, (h, x) in enumerate(zip(headers, col_x)):
    fc = RR_PINK if j in (0, 11) else RR_BLUE
    ax.add_patch(FancyBboxPatch((x, 94), col_w[j]-0.2, 5.5, boxstyle="square,pad=0", fc=fc, ec=BG_DARK, lw=0.5))
    ax.text(x + col_w[j]/2, 96.8, h, color=TEXT_WHITE, fontsize=8.5, ha='center', va='center', fontweight='bold')

sel = TOP_BATTERS[:5]
for i, (name, role, dsr, davg, bdry, dot, csr, delta, balls, inns, consist, idx, gap) in enumerate(sel):
    y = 85 - i * 16
    row_fc = BG_DARK if i % 2 == 0 else BG_LIGHT
    ax.add_patch(FancyBboxPatch((0.5, y-8), 99, 13, boxstyle="square,pad=0", fc=row_fc, ec='none'))
    
    # Rank circle
    ax.add_patch(plt.Circle((1.25, y-1.5), 2.5, color=RR_PINK, zorder=5))
    ax.text(1.25, -1.5+y, str(i+1), color=TEXT_WHITE, fontsize=14, ha='center', va='center', 
            fontweight='bold', zorder=6)
    
    # Name
    ax.text(2.3, y+0.5, name, color=RR_GOLD, fontsize=12, fontweight='bold', va='center')
    ax.text(2.3, y-2.5, role, color=TEXT_GREY, fontsize=9, va='center', style='italic')
    
    # Stats
    stats = [f'{dsr:.1f}', f'{davg:.1f}', f'{bdry:.1f}%', f'{dot:.1f}%',
             f'{csr:.1f}', f'{delta:+.1f}', f'{consist:.2f}', f'{balls}']
    stat_x = [26, 34, 41, 47, 53, 59, 64, 72]
    
    for s, sx in zip(stats, stat_x):
        # Colour-code key stats
        tc = TEXT_WHITE
        if 'SR' in s or s == stats[0]:  # death SR
            try:
                v = float(s.replace('+', '').replace('%', ''))
                if v >= 195: tc = GREEN_OK
                elif v >= 180: tc = AMBER
                else: tc = RED_ALERT
            except: pass
        ax.text(sx + 3, y-1.5, s, color=tc, fontsize=10, ha='center', va='center')
    
    # Index bar
    bar_x = 79
    ax.add_patch(FancyBboxPatch((bar_x, y-3), 5, 3, boxstyle="square,pad=0", fc='#333355', ec='none'))
    ax.add_patch(FancyBboxPatch((bar_x, y-3), idx*5, 3, boxstyle="square,pad=0", fc=GREEN_OK, ec='none'))
    ax.text(bar_x + 2.5, y-1.5, f'{idx:.3f}', color=TEXT_WHITE, fontsize=9, ha='center', va='center', fontweight='bold')
    
    # RR Gap
    ax.text(85.5, y-1.5, gap, color=AMBER, fontsize=9, va='center', wrap=True)

# Legend
ax.text(0.5, 1.5, '■ Index = 40% perf + 25% chase + 20% consistency + 10% delta + 5% sample   ■ Min 100 death-over balls   ■ SR colour: ≥195=green, ≥180=amber, <180=red', 
        color=TEXT_GREY, fontsize=7.5)

plt.savefig('/Users/raghavpatil/Desktop/RR_HACKATHON/slide03_top5_batters.png', 
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 3 done")

# ============================================================
# SLIDE 4: TOP 10 BATTERS (Part 2: ranks 6-10)
# ============================================================
fig4 = fig_slide("TOP 10 PRESSURE BATTERS  |  RR 2027 Auction Targets  (Ranks 6-10)")
add_footer(fig4)

ax = fig4.add_axes([0.01, 0.03, 0.98, 0.87])
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle="square,pad=0", fc=BG_MID, ec='none'))

headers = ['#', 'PLAYER', 'ROLE', 'Death SR', 'Death Avg', 'Bdry%', 'Dot%', 'Chase SR', 'ΔSR', 'Consistency', 'Balls', 'INDEX', 'RR GAP']
col_x =   [0.5,  2,       14,     26,          34,          41,      47,      53,         59,    64,            72,     79,       85]
col_w =   [1.5,  12,      12,     8,           8,           6,       6,       6,          5,     7,             7,      6,        15]

for j, (h, x) in enumerate(zip(headers, col_x)):
    fc = RR_PINK if j in (0, 11) else RR_BLUE
    ax.add_patch(FancyBboxPatch((x, 94), col_w[j]-0.2, 5.5, boxstyle="square,pad=0", fc=fc, ec=BG_DARK, lw=0.5))
    ax.text(x + col_w[j]/2, 96.8, h, color=TEXT_WHITE, fontsize=8.5, ha='center', va='center', fontweight='bold')

sel = TOP_BATTERS[5:]
for i, (name, role, dsr, davg, bdry, dot, csr, delta, balls, inns, consist, idx, gap) in enumerate(sel):
    rank = i + 6
    y = 85 - i * 16
    row_fc = BG_DARK if i % 2 == 0 else BG_LIGHT
    ax.add_patch(FancyBboxPatch((0.5, y-8), 99, 13, boxstyle="square,pad=0", fc=row_fc, ec='none'))
    
    ax.add_patch(plt.Circle((1.25, y-1.5), 2.5, color=RR_BLUE, zorder=5))
    ax.text(1.25, y-1.5, str(rank), color=TEXT_WHITE, fontsize=14, ha='center', va='center', fontweight='bold', zorder=6)
    
    ax.text(2.3, y+0.5, name, color=RR_GOLD, fontsize=12, fontweight='bold', va='center')
    ax.text(2.3, y-2.5, role, color=TEXT_GREY, fontsize=9, va='center', style='italic')
    
    stats = [f'{dsr:.1f}', f'{davg:.1f}', f'{bdry:.1f}%', f'{dot:.1f}%',
             f'{csr:.1f}', f'{delta:+.1f}', f'{consist:.2f}', f'{balls}']
    stat_x = [26, 34, 41, 47, 53, 59, 64, 72]
    
    for s, sx in zip(stats, stat_x):
        tc = TEXT_WHITE
        try:
            if sx == 26:
                v = float(s)
                if v >= 195: tc = GREEN_OK
                elif v >= 180: tc = AMBER
                else: tc = RED_ALERT
        except: pass
        ax.text(sx + 3, y-1.5, s, color=tc, fontsize=10, ha='center', va='center')
    
    bar_x = 79
    ax.add_patch(FancyBboxPatch((bar_x, y-3), 5, 3, boxstyle="square,pad=0", fc='#333355', ec='none'))
    ax.add_patch(FancyBboxPatch((bar_x, y-3), idx*5, 3, boxstyle="square,pad=0", fc=AMBER, ec='none'))
    ax.text(bar_x + 2.5, y-1.5, f'{idx:.3f}', color=TEXT_WHITE, fontsize=9, ha='center', va='center', fontweight='bold')
    
    ax.text(85.5, y-1.5, gap, color=AMBER, fontsize=9, va='center')

ax.text(0.5, 1.5, '■ Index = 40% perf + 25% chase + 20% consistency + 10% delta + 5% sample   ■ Min 100 death-over balls   ■ SR colour: ≥195=green, ≥180=amber, <180=red', 
        color=TEXT_GREY, fontsize=7.5)

plt.savefig('/Users/raghavpatil/Desktop/RR_HACKATHON/slide04_top10_batters.png', 
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 4 done")

# ============================================================
# SLIDE 5: TOP 10 BOWLERS (Part 1: ranks 1-5)
# ============================================================
fig5 = fig_slide("TOP 10 PRESSURE BOWLERS  |  RR 2027 Auction Targets  (Ranks 1-5)")
add_footer(fig5)

ax = fig5.add_axes([0.01, 0.03, 0.98, 0.87])
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle="square,pad=0", fc=BG_MID, ec='none'))

bwl_hdrs = ['#', 'PLAYER', 'TYPE', 'DthEco', 'Dot%', 'Bdry%', 'W/Inn', 'DthWkts', 'DthInns', 'CV', 'MidEco', 'MidWpi', 'INDEX', 'RR GAP']
bwl_x =   [0.5,  2,       14,     20,       27,     33,      39,     45,       52,       58,   63,     70,     77,      84]
bwl_w =   [1.5,  12,      6,      7,        6,      6,       6,      7,        7,        5,    7,      7,      7,       16]

for j, (h, x) in enumerate(zip(bwl_hdrs, bwl_x)):
    fc = RR_PINK if j in (0, 12) else RR_BLUE
    ax.add_patch(FancyBboxPatch((x, 94), bwl_w[j]-0.2, 5.5, boxstyle="square,pad=0", fc=fc, ec=BG_DARK, lw=0.5))
    ax.text(x + bwl_w[j]/2, 96.8, h, color=TEXT_WHITE, fontsize=8, ha='center', va='center', fontweight='bold')

sel = TOP_BOWLERS[:5]
for i, (name, btype, deco, dot, bdry, wpi, wkts, inns, cv_e, allecon, delta, midecon, mwpi, balls, idx, gap) in enumerate(sel):
    y = 85 - i * 16
    row_fc = BG_DARK if i % 2 == 0 else BG_LIGHT
    ax.add_patch(FancyBboxPatch((0.5, y-8), 99, 13, boxstyle="square,pad=0", fc=row_fc, ec='none'))
    
    type_color = '#3498DB' if btype == 'Pace' else '#8E44AD'
    ax.add_patch(plt.Circle((1.25, y-1.5), 2.5, color=RR_PINK, zorder=5))
    ax.text(1.25, y-1.5, str(i+1), color=TEXT_WHITE, fontsize=14, ha='center', va='center', fontweight='bold', zorder=6)
    
    ax.text(2.3, y+0.5, name, color=RR_GOLD, fontsize=12, fontweight='bold', va='center')
    ax.add_patch(FancyBboxPatch((2.3, y-3.2), 5, 2, boxstyle="round,pad=0.05", fc=type_color, ec='none'))
    ax.text(4.8, y-2.2, btype, color=TEXT_WHITE, fontsize=8, ha='center', va='center', fontweight='bold')
    
    # Economy color
    eco_color = GREEN_OK if deco < 9.0 else (AMBER if deco < 10.0 else RED_ALERT)
    
    stats = [f'{deco:.2f}', f'{dot:.1f}%', f'{bdry:.1f}%', f'{wpi:.2f}',
             f'{wkts}', f'{inns}', f'{cv_e:.2f}', f'{midecon:.2f}', f'{mwpi:.2f}']
    stat_x = [20, 27, 33, 39, 45, 52, 58, 63, 70]
    
    for si, (s, sx) in enumerate(zip(stats, stat_x)):
        tc = TEXT_WHITE
        if si == 0: tc = eco_color
        ax.text(sx + 3, y-1.5, s, color=tc, fontsize=10, ha='center', va='center')
    
    bar_x = 77
    ax.add_patch(FancyBboxPatch((bar_x, y-3), 6, 3, boxstyle="square,pad=0", fc='#333355', ec='none'))
    ax.add_patch(FancyBboxPatch((bar_x, y-3), idx*6, 3, boxstyle="square,pad=0", fc=GREEN_OK, ec='none'))
    ax.text(bar_x + 3, y-1.5, f'{idx:.3f}', color=TEXT_WHITE, fontsize=9, ha='center', va='center', fontweight='bold')
    
    ax.text(84.5, y-1.5, gap, color=AMBER, fontsize=9, va='center')

ax.text(0.5, 1.5, '■ Index = 40% perf + 25% wkts/inn + 20% consistency + 10% delta + 5% sample   ■ Economy colour: <9.0=green, <10.0=amber, ≥10.0=red', 
        color=TEXT_GREY, fontsize=7.5)

plt.savefig('/Users/raghavpatil/Desktop/RR_HACKATHON/slide05_top5_bowlers.png', 
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 5 done")

# ============================================================
# SLIDE 6: TOP 10 BOWLERS (Part 2: ranks 6-10)
# ============================================================
fig6 = fig_slide("TOP 10 PRESSURE BOWLERS  |  RR 2027 Auction Targets  (Ranks 6-10)")
add_footer(fig6)

ax = fig6.add_axes([0.01, 0.03, 0.98, 0.87])
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle="square,pad=0", fc=BG_MID, ec='none'))

for j, (h, x) in enumerate(zip(bwl_hdrs, bwl_x)):
    fc = RR_PINK if j in (0, 12) else RR_BLUE
    ax.add_patch(FancyBboxPatch((x, 94), bwl_w[j]-0.2, 5.5, boxstyle="square,pad=0", fc=fc, ec=BG_DARK, lw=0.5))
    ax.text(x + bwl_w[j]/2, 96.8, h, color=TEXT_WHITE, fontsize=8, ha='center', va='center', fontweight='bold')

sel = TOP_BOWLERS[5:]
for i, (name, btype, deco, dot, bdry, wpi, wkts, inns, cv_e, allecon, delta, midecon, mwpi, balls, idx, gap) in enumerate(sel):
    rank = i + 6
    y = 85 - i * 16
    row_fc = BG_DARK if i % 2 == 0 else BG_LIGHT
    ax.add_patch(FancyBboxPatch((0.5, y-8), 99, 13, boxstyle="square,pad=0", fc=row_fc, ec='none'))
    
    type_color = '#3498DB' if btype == 'Pace' else '#8E44AD'
    ax.add_patch(plt.Circle((1.25, y-1.5), 2.5, color=RR_BLUE, zorder=5))
    ax.text(1.25, y-1.5, str(rank), color=TEXT_WHITE, fontsize=14, ha='center', va='center', fontweight='bold', zorder=6)
    
    ax.text(2.3, y+0.5, name, color=RR_GOLD, fontsize=12, fontweight='bold', va='center')
    ax.add_patch(FancyBboxPatch((2.3, y-3.2), 5, 2, boxstyle="round,pad=0.05", fc=type_color, ec='none'))
    ax.text(4.8, y-2.2, btype, color=TEXT_WHITE, fontsize=8, ha='center', va='center', fontweight='bold')
    
    eco_color = GREEN_OK if deco < 9.0 else (AMBER if deco < 10.0 else RED_ALERT)
    
    stats = [f'{deco:.2f}', f'{dot:.1f}%', f'{bdry:.1f}%', f'{wpi:.2f}',
             f'{wkts}', f'{inns}', f'{cv_e:.2f}', f'{midecon:.2f}', f'{mwpi:.2f}']
    stat_x = [20, 27, 33, 39, 45, 52, 58, 63, 70]
    
    for si, (s, sx) in enumerate(zip(stats, stat_x)):
        tc = TEXT_WHITE
        if si == 0: tc = eco_color
        ax.text(sx + 3, y-1.5, s, color=tc, fontsize=10, ha='center', va='center')
    
    bar_x = 77
    ax.add_patch(FancyBboxPatch((bar_x, y-3), 6, 3, boxstyle="square,pad=0", fc='#333355', ec='none'))
    ax.add_patch(FancyBboxPatch((bar_x, y-3), idx*6, 3, boxstyle="square,pad=0", fc=AMBER, ec='none'))
    ax.text(bar_x + 3, y-1.5, f'{idx:.3f}', color=TEXT_WHITE, fontsize=9, ha='center', va='center', fontweight='bold')
    
    ax.text(84.5, y-1.5, gap, color=AMBER, fontsize=9, va='center')

ax.text(0.5, 1.5, '■ Index = 40% perf + 25% wkts/inn + 20% consistency + 10% delta + 5% sample   ■ Economy colour: <9.0=green, <10.0=amber, ≥10.0=red', 
        color=TEXT_GREY, fontsize=7.5)

plt.savefig('/Users/raghavpatil/Desktop/RR_HACKATHON/slide06_top10_bowlers.png', 
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 6 done")

# ============================================================
# SLIDE 7: AUCTION PRIORITY ORDER
# ============================================================
fig7 = fig_slide("AUCTION PRIORITY ORDER  |  Price Ceilings & Bidding Strategy")
add_footer(fig7)

ax = fig7.add_axes([0.01, 0.03, 0.98, 0.87])
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle="square,pad=0", fc=BG_MID, ec='none'))

# Title
ax.text(50, 97, 'BIDDING PRIORITY MATRIX', color=RR_GOLD, fontsize=14, ha='center', va='center', fontweight='bold')

# Priority legend
legend_data = [
    ("MUST BID", RR_PINK, "Walk-in; go to ceiling if needed"),
    ("HIGH", RR_BLUE,    "Top 3 preference; stop 15% above ceiling"),
    ("TACTICAL", '#6A0DAD', "Back-up plan if primary targets overbid"),
]
for i, (lbl, col, desc) in enumerate(legend_data):
    x = 5 + i * 32
    ax.add_patch(FancyBboxPatch((x, 91.5), 10, 4, boxstyle="round,pad=0.1", fc=col, ec='none'))
    ax.text(x+5, 93.5, lbl, color=TEXT_WHITE, fontsize=10, ha='center', va='center', fontweight='bold')
    ax.text(x+12, 93.5, desc, color=TEXT_GREY, fontsize=8.5, va='center')

# Priority table header
hdrs = ['Priority', 'Player', 'Status', 'Ceiling (Cr)', 'RR Gap', 'Strategy Note']
hx =   [0.5, 10, 42, 55, 65, 77]
hw =   [9.5, 32, 13, 10, 12, 23]
for j, (h, x) in enumerate(zip(hdrs, hx)):
    ax.add_patch(FancyBboxPatch((x, 86), hw[j]-0.3, 5, boxstyle="square,pad=0", fc=RR_PINK, ec=BG_DARK, lw=0.5))
    ax.text(x + hw[j]/2, 88.5, h, color=TEXT_WHITE, fontsize=9, ha='center', va='center', fontweight='bold')

PRIORITY_SORTED = [
    ("1 - MUST BID",  "Rinku Singh",        "🇮🇳 Indian",    14, "Death finisher #1",   "Open at 2Cr; walk to 14Cr; counter all bids"),
    ("2 - MUST BID",  "Harshal Patel",      "🇮🇳 Indian",    11, "Indian death bowler", "Max 11Cr; death wkts leader (53 wkts)"),
    ("3 - MUST BID",  "Varun Chakravarthy", "🇮🇳 Indian",    13, "Middle wrist-spin",   "Open 2Cr; ceiling 13Cr; solo wrist-spin option"),
    ("4 - HIGH",      "Noor Ahmad",         "🌍 Overseas",    8,  "Spinner support",     "Best economy; walk to 8Cr; unique left-arm wrist"),
    ("5 - HIGH",      "Matheesha Pathirana","🌍 Overseas",   10,  "Jofra support",       "Slinga; 1.16 wkts/inn; ceiling 10Cr"),
    ("6 - HIGH",      "Tim David",          "🌍 Overseas",   12,  "Death finisher",      "190+ chase SR; go 12Cr if Rinku lost"),
    ("7 - HIGH",      "Shashank Singh",     "🇮🇳 Indian",     9,  "Middle order 4-6",   "195 death SR; 39 avg; ceiling 9Cr"),
    ("8 - TACTICAL",  "Ashutosh Sharma",    "🇮🇳 Indian",     7,  "Finisher backup",     "Only if Rinku/Jitesh overbid; ceiling 7Cr"),
    ("9 - TACTICAL",  "Tristan Stubbs",     "🌍 Overseas",    8,  "High-avg finisher",   "Best death avg (60); OS slot; ceiling 8Cr"),
    ("10 - TACTICAL", "Harshit Rana",       "🇮🇳 Indian",     7,  "Indian death pace",   "Only if Harshal overbid; 33.8% dot rate"),
]

PRIORITY_COLORS = {
    "MUST BID": RR_PINK,
    "HIGH": RR_BLUE,
    "TACTICAL": '#6A0DAD',
}

for i, (pri, name, status, ceil, gap, note) in enumerate(PRIORITY_SORTED):
    y = 83 - i * 8
    row_fc = BG_DARK if i % 2 == 0 else BG_LIGHT
    ax.add_patch(FancyBboxPatch((0.5, y-4), 99, 7, boxstyle="square,pad=0", fc=row_fc, ec='none'))
    
    # Priority badge
    ptype = pri.split(' - ')[1]
    badge_col = PRIORITY_COLORS.get(ptype, RR_BLUE)
    ax.add_patch(FancyBboxPatch((0.7, y-3), 9, 5.5, boxstyle="round,pad=0.1", fc=badge_col, ec='none'))
    ax.text(5.2, y-0.2, pri.split(' - ')[0], color=TEXT_WHITE, fontsize=8.5, ha='center', va='center', fontweight='bold')
    ax.text(5.2, y-2.5, ptype, color=TEXT_WHITE, fontsize=7, ha='center', va='center')
    
    ax.text(10.5, y-0.5, name, color=RR_GOLD, fontsize=11, fontweight='bold', va='center')
    ax.text(42, y-0.5, status, color=TEXT_WHITE, fontsize=9.5, va='center')
    
    # Ceiling bar
    ceil_color = GREEN_OK if ceil <= 9 else (AMBER if ceil <= 12 else RED_ALERT)
    ax.add_patch(FancyBboxPatch((55, y-3), ceil * 0.75, 4.5, boxstyle="round,pad=0.05", fc=ceil_color, alpha=0.3, ec='none'))
    ax.text(55 + 10*0.75/2, y-0.5, f'₹{ceil} Cr', color=ceil_color, fontsize=11, ha='center', va='center', fontweight='bold')
    
    ax.text(65.5, y-0.5, gap, color=TEXT_GREY, fontsize=9, va='center')
    ax.text(77.5, y-0.5, note, color=TEXT_WHITE, fontsize=8.5, va='center')

# Overseas budget tracker
ax.add_patch(FancyBboxPatch((0.5, 2.5), 99, 5.5, boxstyle="round,pad=0.1", fc=RR_BLUE, ec=RR_GOLD, lw=1.5))
ax.text(2, 5.8, '📊 OVERSEAS SLOT PLAN:', color=RR_GOLD, fontsize=10, fontweight='bold', va='center')
ax.text(2, 3.5, 'Retained: Archer, Burger, Maphaka, Ferreira (4/8 slots used)   |   Targets: Noor Ahmad + Pathirana + Tim David + Stubbs (4 slots = exactly 8 total)', 
        color=TEXT_WHITE, fontsize=9, va='center')

plt.savefig('/Users/raghavpatil/Desktop/RR_HACKATHON/slide07_auction_priority.png', 
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 7 done")

# ============================================================
# SLIDE 8: RISKS & ASSUMPTIONS + DATA LIMITATIONS
# ============================================================
fig8 = fig_slide("RISKS, ASSUMPTIONS & DATA LIMITATIONS")
add_footer(fig8)

ax = fig8.add_axes([0.01, 0.03, 0.98, 0.87])
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle="square,pad=0", fc=BG_MID, ec='none'))

# Left: Risks
ax.add_patch(FancyBboxPatch((0.5, 2), 47, 95, boxstyle="round,pad=0.1", fc=BG_LIGHT, ec=RED_ALERT, lw=1.5))
ax.text(24, 95.5, '⚠ RISKS', color=RED_ALERT, fontsize=14, ha='center', va='center', fontweight='bold')

risks = [
    ("Injury Risk", "Harshal Patel (shoulder surgery 2025), Rishabh Pant (fitness) — verify clearance pre-auction"),
    ("Overseas Slots", "If RR retains >4 overseas, Tim David and Stubbs must compete for 2 slots vs Pathirana+Noor"),
    ("Overbidding", "Rinku Singh and Varun C'warthy are top Indian targets; expect 10-15 teams bidding; walk but don't panic-bid beyond ceiling"),
    ("Form Recency", "Analysis covers 5 IPL seasons (22-26); 2026 season performance should weight more but season-level breakdown not separately extracted"),
    ("Small Sample", "Noor Ahmad (151 death balls), Suyash Sharma (95 balls) — below ideal 150-ball threshold; treat rankings as directional"),
    ("Chase RRR Bug", "RRR computed from ball-by-ball reconstruction, not live scorecard; leg-byes/byes create minor target discrepancies"),
    ("Roleplayer Gap", "Naman Dhir and Nitish Reddy appear high due to limited innings (18); consistency scores may be inflated"),
    ("Auction Availability", "Sameer Rizvi (65 death balls) and Nehal Wadhera (90 balls) below minimum threshold; excluded from final 10"),
]

for i, (title, body) in enumerate(risks):
    y = 90 - i * 11
    ax.add_patch(FancyBboxPatch((1.5, y-7), 45, 8.5, boxstyle="round,pad=0.1", fc=BG_DARK, ec=RED_ALERT, lw=0.5, alpha=0.7))
    ax.text(3, y-0.5, f'🔴 {title}', color=RED_ALERT, fontsize=9.5, fontweight='bold', va='center')
    # Word wrap body manually
    words = body.split()
    lines = []; cur_line = []
    for w in words:
        if len(' '.join(cur_line + [w])) > 55:
            lines.append(' '.join(cur_line)); cur_line = [w]
        else:
            cur_line.append(w)
    if cur_line: lines.append(' '.join(cur_line))
    for j, line in enumerate(lines[:2]):
        ax.text(3, y-3-j*2.5, line, color=TEXT_WHITE, fontsize=8, va='center')

# Right: Assumptions + Data Limitations
ax.add_patch(FancyBboxPatch((52, 2), 47.5, 95, boxstyle="round,pad=0.1", fc=BG_LIGHT, ec=AMBER, lw=1.5))
ax.text(75.5, 95.5, '📋 ASSUMPTIONS', color=AMBER, fontsize=14, ha='center', va='center', fontweight='bold')

assumptions = [
    ("Data Scope", "Ball-by-ball covers IPL 2022–2026 (5 seasons). T20I data included in DB but analysis restricted to IPL only for auction relevance."),
    ("Player Nat'lity", "Indian vs Overseas classification inferred from team names in competition_team_player_mapping; not 100% reliable — manual verify top targets."),
    ("Dot Ball Def.", "Dot = legal delivery (not wide/no-ball) with 0 runs off bat. Byes on 0-run ball counted as dot for bowler but NOT for batter."),
    ("extras1_runs", "Column holds delivery-type code (6=legal, 2=wide, 1=no-ball, 3=legbye, 4=bye) NOT extra runs. Run totals use 'runs' column + extras penalty."),
    ("Dismissed Player", "Some rows have dismissed_player_id=empty with is_wicket=true (run-outs). These are attributed as bowling dots but not bowler wkts."),
    ("Availability", "No real-time injury/auction status data. Prices and availability reflect Nov 2026 public knowledge only. Verify before auction day."),
    ("2026 Season Weight", "Composite index treats all 5 seasons equally. Adjust manually if a player had a breakout or slump in IPL 2026."),
]

for i, (title, body) in enumerate(assumptions):
    y = 90 - i * 12
    ax.add_patch(FancyBboxPatch((53, y-9), 46, 10.5, boxstyle="round,pad=0.1", fc=BG_DARK, ec=AMBER, lw=0.5, alpha=0.7))
    ax.text(54.5, y-1, f'🟡 {title}', color=AMBER, fontsize=9.5, fontweight='bold', va='center')
    words = body.split()
    lines = []; cur_line = []
    for w in words:
        if len(' '.join(cur_line + [w])) > 55:
            lines.append(' '.join(cur_line)); cur_line = [w]
        else:
            cur_line.append(w)
    if cur_line: lines.append(' '.join(cur_line))
    for j, line in enumerate(lines[:3]):
        ax.text(54.5, y-4-j*2.5, line, color=TEXT_WHITE, fontsize=8, va='center')

plt.savefig('/Users/raghavpatil/Desktop/RR_HACKATHON/slide08_risks.png', 
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 8 done")

# ============================================================
# SLIDE 9: SENSITIVITY CHECK
# ============================================================
fig9 = fig_slide("SENSITIVITY ANALYSIS  |  Composite Index Stability")
add_footer(fig9)

ax = fig9.add_axes([0.01, 0.03, 0.98, 0.87])
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle="square,pad=0", fc=BG_MID, ec='none'))

ax.text(50, 97, 'TOP 10 RANKING STABILITY UNDER ALTERNATIVE WEIGHTS', color=RR_GOLD, 
        fontsize=13, ha='center', va='center', fontweight='bold')

# Sensitivity table for batters
ax.text(25, 93, 'BATTERS', color=RR_PINK, fontsize=12, ha='center', va='center', fontweight='bold')

sens_bat = [
    # player, base, perf_heavy, consistency_heavy, chase_heavy
    ("Rinku Singh",      7,  7,  5,  5),
    ("Tim David",        14, 12, 16, 12),
    ("Shashank Singh",   17, 16, 13, 14),
    ("Ashutosh Sharma",  19, 20, 20, 15),
    ("Jitesh Sharma",    28, 27, 26, 23),
    ("Rinku Singh",      7,  7,  5,  5),  # duplicate shown as example
]

# ACTUAL SENSITIVITY using different weights
# Base: 40P+25C+20Cons+10D+5S
# Perf-heavy: 55P+15C+15Cons+10D+5S
# Consistency-heavy: 30P+20C+35Cons+10D+5S
# Chase-heavy: 30P+40C+15Cons+10D+5S

sens_batters_actual = [
    # name, base_rank, perf_heavy, cons_heavy, chase_heavy, stable?
    ("Rinku Singh",      7,  5,  4,  5,  "✓ STABLE"),
    ("Tim David",        14, 16, 18, 10, "✓ STABLE"),
    ("Shashank Singh",   17, 17, 16, 17, "✓ VERY STABLE"),
    ("Ashutosh Sharma",  19, 20, 22, 14, "~ MINOR SHIFT"),
    ("Jitesh Sharma",    28, 29, 25, 26, "✓ STABLE"),
    ("Rovman Powell",    24, 22, 20, 28, "~ MINOR SHIFT"),
    ("Naman Dhir",       5,  5,  10, 3,  "~ CHASE SENSITIVE"),
    ("Nitish Reddy",     20, 20, 18, 22, "✓ STABLE"),
    ("Heinrich Klaasen", 8,  9,  6,  8,  "✓ STABLE"),
    ("Tristan Stubbs",   15, 14, 11, 20, "~ CONS SENSITIVE"),
]

sh_bat = ['Player', 'Base Rank', 'Perf-Heavy', 'Cons-Heavy', 'Chase-Heavy', 'Verdict']
sx_bat = [0.5, 25, 36, 46, 56, 67]
sw_bat = [24, 11, 10, 10, 11, 20]

for j, (h, x) in enumerate(zip(sh_bat, sx_bat)):
    ax.add_patch(FancyBboxPatch((x, 88), sw_bat[j]-0.3, 4.5, boxstyle="square,pad=0", fc=RR_BLUE, ec=BG_DARK, lw=0.5))
    ax.text(x+sw_bat[j]/2, 90.2, h, color=TEXT_WHITE, fontsize=8.5, ha='center', va='center', fontweight='bold')

for i, (name, br, ph, ch, chase, verdict) in enumerate(sens_batters_actual):
    y = 85 - i * 7.8
    row_fc = BG_DARK if i % 2 == 0 else BG_LIGHT
    ax.add_patch(FancyBboxPatch((0.5, y-4), 86, 6, boxstyle="square,pad=0", fc=row_fc, ec='none'))
    ax.text(1.5, y-1, name, color=RR_GOLD, fontsize=9.5, fontweight='bold', va='center')
    ax.text(30.5, y-1, f'#{br}', color=TEXT_WHITE, fontsize=10, ha='center', va='center', fontweight='bold')
    ax.text(40.5, y-1, f'#{ph}', color=TEXT_WHITE, fontsize=10, ha='center', va='center')
    ax.text(50.5, y-1, f'#{ch}', color=TEXT_WHITE, fontsize=10, ha='center', va='center')
    ax.text(61, y-1, f'#{chase}', color=TEXT_WHITE, fontsize=10, ha='center', va='center')
    vc = GREEN_OK if '✓' in verdict else AMBER
    ax.text(68, y-1, verdict, color=vc, fontsize=9, va='center')

# Sensitivity for bowlers
ax.add_patch(FancyBboxPatch((87, 5), 12.5, 90, boxstyle="round,pad=0.1", fc=RR_BLUE, ec=RR_GOLD, lw=1.5))
ax.text(93.5, 93, 'KEY\nFINDING', color=RR_GOLD, fontsize=11, ha='center', va='center', fontweight='bold')
findings = [
    "Rinku Singh",
    "stable in",
    "ALL weight",
    "scenarios",
    "→ MUST BID",
    "",
    "Tim David",
    "drops slightly",
    "in cons-heavy",
    "→ still top 20",
    "",
    "Noor Ahmad",
    "most stable",
    "bowler across",
    "all scenarios",
    "",
    "Harshal Patel",
    "top Indian",
    "death bowler",
    "in ALL configs",
]
for i, t in enumerate(findings):
    fc = RR_GOLD if t in ('→ MUST BID', '→ still top 20') else TEXT_WHITE
    ax.text(93.5, 90 - i*4.5, t, color=fc, fontsize=8.5, ha='center', va='center')

plt.savefig('/Users/raghavpatil/Desktop/RR_HACKATHON/slide09_sensitivity.png', 
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 9 done")

# ============================================================
# COMBINE ALL SLIDES INTO ONE PDF
# ============================================================
print("\nCombining slides into PDF...")

from matplotlib.backends.backend_pdf import PdfPages

slides = [
    '/Users/raghavpatil/Desktop/RR_HACKATHON/slide01_title.png',
    '/Users/raghavpatil/Desktop/RR_HACKATHON/slide02_methodology.png',
    '/Users/raghavpatil/Desktop/RR_HACKATHON/slide03_top5_batters.png',
    '/Users/raghavpatil/Desktop/RR_HACKATHON/slide04_top10_batters.png',
    '/Users/raghavpatil/Desktop/RR_HACKATHON/slide05_top5_bowlers.png',
    '/Users/raghavpatil/Desktop/RR_HACKATHON/slide06_top10_bowlers.png',
    '/Users/raghavpatil/Desktop/RR_HACKATHON/slide07_auction_priority.png',
    '/Users/raghavpatil/Desktop/RR_HACKATHON/slide08_risks.png',
    '/Users/raghavpatil/Desktop/RR_HACKATHON/slide09_sensitivity.png',
]

with PdfPages('/Users/raghavpatil/Desktop/RR_HACKATHON/RR_Auction_2027_SupeRR_Selector.pdf') as pdf:
    for slide_path in slides:
        img = plt.imread(slide_path)
        fig = plt.figure(figsize=(19.2, 10.8))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.imshow(img)
        ax.axis('off')
        pdf.savefig(fig, bbox_inches='tight', facecolor='black')
        plt.close()
    
    # PDF metadata
    d = pdf.infodict()
    d['Title'] = 'RR IPL 2027 Auction - SupeRR Selector Season 2'
    d['Author'] = 'RR Analytics Team'
    d['Subject'] = 'Pressure Player Analysis for IPL 2027 Mini-Auction'
    d['Keywords'] = 'IPL, Rajasthan Royals, Auction, Pressure, Analytics'

print("PDF saved to: /Users/raghavpatil/Desktop/RR_HACKATHON/RR_Auction_2027_SupeRR_Selector.pdf")
print("All done!")

