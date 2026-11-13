#!/usr/bin/env python3
"""
RR Auction 2027 — Tactical Vision Theme
Prepared by: Raghav Patil
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT_DIR / 'reports'
SLIDES_DIR = REPORTS_DIR / 'slides'
SLIDES_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# TACTICAL VISION COLOUR PALETTE
# ============================================================
BG_VOID     = '#05080F'   # Deep space black
BG_DARK     = '#0A0F1E'   # Tactical dark base
BG_MID      = '#0D1628'   # Dark navy panel
BG_PANEL    = '#111E35'   # Card panel
BG_CARD     = '#152338'   # Inner card

CYAN_BRIGHT = '#00E5FF'   # Electric cyan — primary HUD colour
CYAN_DIM    = '#0097A7'   # Muted cyan for borders
CYAN_GLOW   = '#B2EBF2'   # Soft cyan text
GREEN_GO    = '#00FF88'   # Neon green — positive signal
GREEN_DIM   = '#00C853'   # Normal green
AMBER_TAC   = '#FFB300'   # Amber tactical — warnings
RED_TAC     = '#FF1744'   # Red alert
PURPLE_TAC  = '#CE93D8'   # Spinner/wrist-spin tag

RR_PINK     = '#E8175D'   # Rajasthan Royals brand
RR_GOLD     = '#F7CB15'   # RR gold accent
RR_BLUE_DK  = '#1A2F6E'   # RR secondary dark

TEXT_WHITE  = '#E8F4FD'   # Slightly blue-white
TEXT_BRIGHT = '#FFFFFF'
TEXT_DIM    = '#7FB3CC'   # Muted HUD text
TEXT_GOLD   = RR_GOLD

GRID_LINE   = '#1A3050'   # Subtle grid
BORDER_CYAN = '#00BCD4'   # Panel borders


def draw_grid(ax, xlim, ylim, step=5, alpha=0.07):
    """Draw subtle tactical grid lines."""
    for x in np.arange(0, xlim, step):
        ax.axvline(x, color=CYAN_BRIGHT, alpha=alpha, lw=0.4, zorder=0)
    for y in np.arange(0, ylim, step):
        ax.axhline(y, color=CYAN_BRIGHT, alpha=alpha, lw=0.4, zorder=0)


def draw_corner_marks(ax, xlim, ylim, size=2.5, col=CYAN_BRIGHT, alpha=0.5):
    """Corner bracket marks — tactical HUD style."""
    corners = [(0,0), (xlim,0), (0,ylim), (xlim,ylim)]
    for cx, cy in corners:
        dx = size if cx == 0 else -size
        dy = size if cy == 0 else -size
        ax.plot([cx, cx+dx, cx+dx], [cy+dy, cy+dy, cy], color=col, lw=1.2, alpha=alpha, zorder=10)


def header_bar(fig, title, subtitle='Prepared by: Raghav Patil  |  SupeRR Selector Season 2'):
    """Full-width tactical header."""
    ax = fig.add_axes([0, 0.908, 1, 0.092])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')

    # Base stripe
    ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle='square,pad=0', fc=BG_VOID, ec='none'))
    # Left RR-pink accent strip
    ax.add_patch(FancyBboxPatch((0,0), 1.2, 100, boxstyle='square,pad=0', fc=RR_PINK, ec='none'))
    # Cyan bottom border line
    ax.add_patch(FancyBboxPatch((0, 0), 100, 2.5, boxstyle='square,pad=0', fc=CYAN_BRIGHT, ec='none', alpha=0.6))
    # Right dark block
    ax.add_patch(FancyBboxPatch((74, 2.5), 26, 97.5, boxstyle='square,pad=0', fc=BG_MID, ec='none'))
    # Cyan divider
    ax.add_patch(FancyBboxPatch((73.6, 2.5), 0.4, 97.5, boxstyle='square,pad=0', fc=CYAN_BRIGHT, ec='none', alpha=0.8))

    ax.text(2.0, 56, title, color=TEXT_BRIGHT, fontsize=14, fontweight='bold', va='center',
            path_effects=[pe.withStroke(linewidth=2, foreground=BG_VOID)])
    ax.text(2.0, 20, subtitle, color=TEXT_DIM, fontsize=8, va='center', style='italic')

    # Right block content
    ax.text(86.5, 72, 'RAGHAV PATIL', color=CYAN_BRIGHT, fontsize=8.5, ha='center', va='center',
            fontweight='bold')
    ax.text(86.5, 30, 'NOV 2026', color=TEXT_DIM, fontsize=7.5, ha='center', va='center')

    return ax


def footer_bar(fig, text='IPL 2022–2026  |  87,687 Deliveries  |  371 Matches  |  Prepared by: Raghav Patil'):
    ax = fig.add_axes([0, 0, 1, 0.028])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
    ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle='square,pad=0', fc=BG_VOID, ec='none'))
    ax.add_patch(FancyBboxPatch((0, 97), 100, 3, boxstyle='square,pad=0', fc=CYAN_BRIGHT, ec='none', alpha=0.4))
    ax.text(50, 42, text, color=TEXT_DIM, fontsize=6.8, ha='center', va='center')


def tac_fig(title, subtitle='Prepared by: Raghav Patil  |  SupeRR Selector Season 2'):
    fig = plt.figure(figsize=(19.2, 10.8), facecolor=BG_DARK)
    header_bar(fig, title, subtitle)
    footer_bar(fig)
    return fig


def panel(ax, x, y, w, h, fc=BG_PANEL, border_col=BORDER_CYAN, lw=0.8, alpha=1.0, radius=0.3):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f'round,pad={radius}',
                                fc=fc, ec=border_col, lw=lw, alpha=alpha, zorder=2))


def label(ax, x, y, text, color=TEXT_WHITE, fs=10, bold=False, ha='left', va='center', glow=False):
    kwargs = dict(color=color, fontsize=fs, ha=ha, va=va,
                  fontweight='bold' if bold else 'normal')
    if glow:
        kwargs['path_effects'] = [pe.withStroke(linewidth=3, foreground=BG_DARK)]
    ax.text(x, y, text, **kwargs)


def tag_badge(ax, x, y, w, h, text, fc, tc=TEXT_BRIGHT, fs=8.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.15', fc=fc, ec='none', zorder=5))
    ax.text(x+w/2, y+h/2, text, color=tc, fontsize=fs, ha='center', va='center',
            fontweight='bold', zorder=6)


def index_bar(ax, x, y, w, h, val, max_val=1.0):
    """Horizontal progress bar."""
    pct = min(1.0, val / max_val)
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='square,pad=0', fc=GRID_LINE, ec='none', zorder=3))
    if pct > 0:
        col = GREEN_GO if pct > 0.72 else (AMBER_TAC if pct > 0.55 else RED_TAC)
        ax.add_patch(FancyBboxPatch((x, y), w*pct, h, boxstyle='square,pad=0', fc=col, ec='none', zorder=4))
    ax.text(x+w/2, y+h/2, f'{val:.3f}', color=TEXT_BRIGHT, fontsize=8.5, ha='center', va='center',
            fontweight='bold', zorder=5)


# ============================================================
# DATA
# ============================================================

REVISED_BATTERS = [
    # name, team26, nat, role, dsr, davg, csr, dot, balls, idx, note
    ("Liam Livingstone",  "SRH",      "OS",  "Death/Mid Bat",    223.7, 28.3, 174.5, 25.0, 152, 0.844,
     "Highest death SR in dataset. SRH likely releases; bowls off-spin too. Direct Hetmyer replacement."),
    ("Tim David",         "RCB",      "OS",  "Death Finisher",   197.0, 31.1, 190.2, 26.0, 427, 0.738,
     "World #1 death finisher by volume (427 balls). RCB likely releases. Chase SR 190 is elite."),
    ("Shashank Singh",    "PBKS",     "IND", "Middle Ord 4-6",   195.4, 39.4, 172.8, 19.1, 262, 0.728,
     "PBKS rebuilding; Shashank available. Best Indian middle-order finisher. Avg 39.4 = no gift wickets."),
    ("Ashutosh Sharma",   "DC",       "IND", "Finisher 5-7",     191.6, 29.3, 181.4, 23.8, 214, 0.716,
     "DC frequently rebuilds. Chase SR 181 under RRR pressure. Calm and reliable under the pump."),
    ("Jitesh Sharma",     "RCB",      "IND", "WK-Finisher",      182.4, 21.7, 167.0, 29.4, 262, 0.649,
     "RCB rebuilding post-Kohli era. Gives RR Indian WK cover AND death hitting in one slot."),
    ("Rovman Powell",     "KKR",      "OS",  "Death Hitter 6-7", 188.9, 23.5, 147.9, 32.1, 162, 0.672,
     "KKR OS crowded (Starc, Narine, Russell). Powell likely released. 29% boundary rate in death."),
    ("Tristan Stubbs",    "DC",       "OS",  "Anchor-Finisher",  197.1, 60.0, 157.2, 16.4, 274, 0.730,
     "Best death AVERAGE (60.0) in top-50. Doesn't throw his wicket. DC rebuilding squad."),
    ("Venkatesh Iyer",    "RCB",      "IND", "All-Rounder",      160.7, 16.7, 150.3, 23.5, 135, 0.568,
     "Modest numbers but rare: Indian all-rounder with medium pace + batting. Covers Shanaka role."),
    ("Marcus Stoinis",    "PBKS",     "OS",  "All-Rounder 4-6",  203.1, 29.1, 162.5, 26.0, 258, 0.729,
     "PBKS rebuild; 203 death SR + medium pace. Doubles as 5th bowler to ease bowling burden."),
    ("Glenn Maxwell",     "PBKS'25",  "OS",  "Mid Ord + Spin",   195.0, 25.0, 165.0, 22.0, 90,  0.0,
     "Below data threshold. Included on PROFILE: elite T20 batter + off-spin = genuine 2-in-1 overseas slot."),
]

REVISED_BOWLERS = [
    # name, team26, nat, type, deco, dot, wpi, midecon, mwpi, balls, idx, note
    ("Varun Chakravarthy", "KKR",  "IND", "Wrist-Spin",   8.87, 37.2, 0.43, 7.67, 0.81, 226, 0.485,
     "KKR has Narine+Kuldeep; Varun surplus. India #1 mystery spinner. 37.2% death dot + 0.81 mid wpi."),
    ("Harshal Patel",      "SRH",  "IND", "Pace-Death",   9.38, 30.4, 1.04, 7.91, 0.45, 504, 0.599,
     "SRH crowded (Siraj, Cummins, Natarajan). 53 IPL death wkts = most of any available Indian pacer."),
    ("Noor Ahmad",         "CSK",  "OS",  "Wrist-Spin L", 7.63, 40.4, 0.59, 7.79, 0.88, 151, 0.605,
     "CSK rebuilding post-Dhoni. Best economy (7.63) + dot rate (40.4%) of any spinner. Left-arm unique."),
    ("Matheesha Pathirana","KKR",  "OS",  "Pace-Slinga",  8.32, 31.3, 1.16, 7.02, 0.44, 403, 0.665,
     "KKR OS-crowded. 1.16 wkts/inn in death = best available pace. Slinga action complements Archer."),
    ("T Natarajan",        "DC",   "IND", "Pace-Yorker",  10.02, 26.0, 0.84, 8.85, 0.23, 442, 0.521,
     "DC frequently changes bowlers. 38 death wkts. Indian death pace cover. Specialist yorker."),
    ("Avesh Khan",         "LSG",  "IND", "Pace",         9.68, 26.7, 0.70, 8.39, 0.48, 460, 0.531,
     "LSG may release on rebuild. Largest Indian death-pace sample (460 balls). Experienced."),
    ("Harshit Rana",       "KKR",  "IND", "Pace",         9.32, 33.8, 0.74, 9.05, 0.46, 157, 0.544,
     "KKR has Starc + Mustafizur; Harshit may be released. 33.8% dot rate — 3rd best Indian pacer."),
    ("Yuzvendra Chahal",   "PBKS", "IND", "Leg-Spin",     9.41, 29.8, 0.81, 8.29, 0.81, 336, 0.538,
     "PBKS rebuilding. 57 mid-over wkts in dataset. Plan B if Varun Chakravarthy price runs away."),
    ("Mustafizur Rahman",  "KKR",  "OS",  "Pace-Cutter",  9.27, 29.9, 0.77, 7.62, 0.33, 224, 0.539,
     "KKR crowded on OS pace. Left-arm cutter variety specialist. 9.27 eco, 0.77 wpi. Low-cost value."),
    ("Mohit Sharma",       "DC",   "IND", "Pace-Death",   10.18, 24.8, 1.07, 8.39, 0.68, 290, 0.562,
     "DC's experienced death bowler. 1.07 wkts/inn = highest death wicket-rate of available Indian pacers."),
]

PRIORITY = [
    (1, "MUST BID",  RR_PINK,    "Varun Chakravarthy",  "Indian",   13, "37.2% dot, 0.81 mid wpi",   "Open Rs.2Cr. Walk to ceiling. No other Indian wrist-spin option."),
    (2, "MUST BID",  RR_PINK,    "Harshal Patel",       "Indian",   10, "53 death wkts, 1.04 wpi",   "Walk to Rs.10Cr. 53 death wkts — most of any available Indian pacer."),
    (3, "MUST BID",  RR_PINK,    "Noor Ahmad",          "Overseas",  9, "7.63 eco, 40.4% dots",      "Walk to Rs.9Cr. Best spinner economy + Jadeja = world-class spin pair."),
    (4, "HIGH",      CYAN_DIM,   "Tim David",           "Overseas", 14, "Chase SR 190, 427 balls",    "Open low. Max Rs.14Cr. Pivot to Livingstone if overbid."),
    (5, "HIGH",      CYAN_DIM,   "Liam Livingstone",    "Overseas", 11, "Death SR 223.7",             "Plan B if Tim David lost. Highest death SR in dataset. Walk to Rs.11Cr."),
    (6, "HIGH",      CYAN_DIM,   "Shashank Singh",      "Indian",    9, "195 SR, avg 39.4, 262 balls","Best Indian finisher with large sample. Fills middle-order 4-6 gap."),
    (7, "HIGH",      CYAN_DIM,   "Matheesha Pathirana", "Overseas", 10, "1.16 wpi, 8.32 eco",         "Slinga complements Archer. 1.16 wkts/inn best of available pacers."),
    (8, "TACTICAL",  '#4A148C',  "Ashutosh Sharma",     "Indian",    7, "Chase SR 181, 214 balls",    "Only if Shashank overbid. Calm under pressure. Ceiling Rs.7Cr."),
    (9, "TACTICAL",  '#4A148C',  "Tristan Stubbs",      "Overseas",  8, "Death avg 60.0 (best!)",     "Best death average in pool. If OS slots remain. Rs.8Cr ceiling."),
    (10,"TACTICAL",  '#4A148C',  "T Natarajan",         "Indian",    7, "38 death wkts, 0.84 wpi",    "Death yorker backup if Harshal/Harshit overbid. Rs.7Cr ceiling."),
]

NOT_AVAILABLE = [
    ("Rinku Singh",      "KKR",  "KKR franchise finisher 3 yrs. Will NEVER sell."),
    ("Rishabh Pant",     "LSG",  "LSG captain Rs.27Cr. Franchise face. Zero chance."),
    ("Suryakumar Yadav", "MI",   "MI captain 2026. India T20 captain."),
    ("Nitish Reddy",     "SRH",  "SRH breakout star 2025-26. Mandatory retention."),
    ("Rashid Khan",      "GT",   "GT captain & premier spinner. IPL icon."),
    ("Jasprit Bumrah",   "MI",   "MI franchise bowler since 2013. Never auctioned since."),
    ("Virat Kohli",      "RCB",  "RCB's brand IS Kohli. Will retire at RCB."),
    ("Tilak Varma",      "MI",   "MI's young star. Core for next 5 years."),
    ("Shreyas Iyer",     "PBKS", "PBKS captain. Rs.26.75Cr buy. Will retain."),
    ("Arshdeep Singh",   "PBKS", "PBKS captain 2026. India #1 left-arm pace."),
    ("Shubman Gill",     "GT",   "GT captain. India opener. GT's poster boy."),
    ("Ravi Bishnoi",     "RR",   "ALREADY IN RR SQUAD — retained 2026."),
]


# ============================================================
# SLIDE 1: TITLE
# ============================================================
fig1 = plt.figure(figsize=(19.2, 10.8), facecolor=BG_DARK)

# Full background
ax = fig1.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle='square,pad=0', fc=BG_VOID, ec='none'))
draw_grid(ax, 100, 100, step=5, alpha=0.06)
draw_corner_marks(ax, 100, 100, size=4, col=CYAN_BRIGHT, alpha=0.5)

# Diagonal accent stripe
from matplotlib.patches import Polygon
verts = [(0, 65), (40, 100), (100, 100), (100, 92), (40, 56), (0, 56)]
ax.add_patch(Polygon(verts, closed=True, fc=RR_PINK, ec='none', alpha=0.12, zorder=1))

# Central content panel
panel(ax, 8, 20, 84, 72, fc=BG_MID, border_col=CYAN_BRIGHT, lw=1.5, radius=0.5)
draw_grid(ax, 100, 100, step=10, alpha=0.04)

# Pink top accent inside panel
ax.add_patch(FancyBboxPatch((8, 83), 84, 9, boxstyle='square,pad=0', fc=RR_PINK, ec='none', zorder=3))

# Title
ax.text(50, 88, 'SupeRR Selector Season 2', color=TEXT_BRIGHT, fontsize=28,
        ha='center', va='center', fontweight='bold', zorder=10,
        path_effects=[pe.withStroke(linewidth=3, foreground=BG_VOID)])
ax.text(50, 79, 'IPL 2027 Mini-Auction  |  Pressure Player Intelligence Report',
        color=CYAN_BRIGHT, fontsize=14, ha='center', va='center', fontweight='bold', zorder=10)

ax.text(50, 70, 'RAJASTHAN ROYALS — AUCTION ANALYTICS',
        color=TEXT_BRIGHT, fontsize=18, ha='center', va='center', fontweight='bold', zorder=10)

# Cyan divider
ax.add_patch(FancyBboxPatch((15, 65.5), 70, 0.4, boxstyle='square,pad=0', fc=CYAN_BRIGHT, ec='none', alpha=0.6, zorder=4))

ax.text(50, 61, '5 IPL Seasons  ·  371 Matches  ·  87,687 Deliveries Analysed',
        color=TEXT_DIM, fontsize=11, ha='center', va='center', zorder=10)

# Stat badges
stats_data = [('371', 'IPL Matches'), ('87,687', 'Deliveries'), ('20', 'Knockout\nMatches'), ('35', 'Close\nFinishes'), ('5', 'Pressure\nScenarios')]
for i, (val, lbl) in enumerate(stats_data):
    bx = 10 + i * 17
    panel(ax, bx, 25, 14, 28, fc=BG_PANEL, border_col=CYAN_DIM, lw=1.0, radius=0.3)
    ax.text(bx+7, 46, val, color=CYAN_BRIGHT, fontsize=16, ha='center', va='center',
            fontweight='bold', zorder=6, path_effects=[pe.withStroke(linewidth=2, foreground=BG_PANEL)])
    ax.text(bx+7, 35, lbl, color=TEXT_DIM, fontsize=8, ha='center', va='center', zorder=6)

# Bottom attribution
panel(ax, 8, 10, 84, 9, fc=BG_PANEL, border_col=RR_PINK, lw=1.2, radius=0.3)
ax.text(50, 14.5, 'Prepared by:  Raghav Patil', color=RR_GOLD, fontsize=13,
        ha='center', va='center', fontweight='bold', zorder=6)
ax.text(50, 11, 'Auction: 16 Dec 2026, Goa  |  Retention Deadline: 15 Nov 2026  |  CONFIDENTIAL',
        color=TEXT_DIM, fontsize=9, ha='center', va='center', zorder=6)

# Scanline effect strips
for y_scan in np.arange(0, 100, 2.5):
    ax.add_patch(FancyBboxPatch((0, y_scan), 100, 0.5, boxstyle='square,pad=0',
                                fc=BG_VOID, ec='none', alpha=0.04, zorder=0))

plt.savefig(str(SLIDES_DIR / 'tac_slide01_title.png'),
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 1 done")


# ============================================================
# SLIDE 2: AVAILABILITY FILTERS
# ============================================================
fig2 = tac_fig("AVAILABILITY FILTERS  |  Who Is NOT In The Auction Pool")
ax = fig2.add_axes([0.01, 0.038, 0.98, 0.862])
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle='square,pad=0', fc=BG_VOID, ec='none'))
draw_grid(ax, 100, 100, step=5, alpha=0.05)

ax.text(50, 97, 'REAL-WORLD AVAILABILITY FILTERS — WHO IS DEFINITELY NOT IN THE AUCTION POOL',
        color=CYAN_BRIGHT, fontsize=11, ha='center', va='center', fontweight='bold',
        path_effects=[pe.withStroke(linewidth=2, foreground=BG_VOID)])

# Left: Not available
panel(ax, 0.5, 2, 56, 93, fc=BG_MID, border_col=RED_TAC, lw=1.5)
ax.text(29, 93.5, 'RETAINED / NOT AVAILABLE', color=RED_TAC, fontsize=11,
        ha='center', va='center', fontweight='bold')

for i, (player, team, reason) in enumerate(NOT_AVAILABLE):
    y = 90 - i*7.0
    row_fc = '#1A0510' if i % 2 == 0 else '#220810'
    ax.add_patch(FancyBboxPatch((1.3, y-4.8), 54.5, 6.0, boxstyle='square,pad=0', fc=row_fc, ec='none', zorder=3))
    # Red dot
    ax.add_patch(plt.Circle((3.5, y-1.8), 1.0, color=RED_TAC, zorder=5))
    ax.text(5.5, y-0.8, player, color=TEXT_BRIGHT, fontsize=10, fontweight='bold', va='center', zorder=5)
    tag_badge(ax, 23, y-3.5, 8, 2.8, team, fc='#5D0000', tc='#FF8A80', fs=7.5)
    # Reason (1 line)
    ax.text(5.5, y-3.2, reason, color=TEXT_DIM, fontsize=7.8, va='center', zorder=5)

# Right: Available / Uncertain
panel(ax, 57.5, 2, 42, 93, fc=BG_MID, border_col=AMBER_TAC, lw=1.5)
ax.text(78.5, 93.5, 'STATUS & AVAILABILITY', color=AMBER_TAC, fontsize=11,
        ha='center', va='center', fontweight='bold')

uncertain = [
    ("Varun Chakravarthy", "KKR",  "MAYBE",  "KKR has Narine + Kuldeep. Varun could be surplus."),
    ("Harshal Patel",      "SRH",  "MAYBE",  "SRH: Siraj, Cummins, Natarajan. Could release."),
    ("Avesh Khan",         "LSG",  "MAYBE",  "LSG rebuilding around Pant. Could be released."),
    ("Harshit Rana",       "KKR",  "MAYBE",  "KKR OS-crowded. Harshit might enter pool."),
    ("Matheesha Pathirana","KKR",  "MAYBE",  "KKR pace crowded (Starc, Mustafizur). Could go."),
    ("Tim David",          "RCB",  "LIKELY", "RCB's 3rd-4th OS pick. Likely released."),
    ("Liam Livingstone",   "SRH",  "LIKELY", "SRH: Klaasen retained. Livingstone spare OS slot."),
    ("Rovman Powell",      "KKR",  "LIKELY", "KKR OS heavy. Powell likely out."),
    ("Tristan Stubbs",     "DC",   "LIKELY", "DC frequently releases. Stubbs enters pool."),
    ("Shashank Singh",     "PBKS", "LIKELY", "PBKS rebuild. Mid-order up for grabs."),
    ("T Natarajan",        "DC",   "LIKELY", "DC doesn't retain many veterans."),
    ("Mohit Sharma",       "DC",   "LIKELY", "Not in DC 2026 mapping. Available."),
]

avcol = {"MAYBE": AMBER_TAC, "LIKELY": GREEN_GO}
for i, (player, team, status, reason) in enumerate(uncertain):
    y = 90 - i * 7.5
    row_fc = '#0D1A08' if i % 2 == 0 else '#112208'
    ax.add_patch(FancyBboxPatch((58.3, y-4.8), 40.8, 6.2, boxstyle='square,pad=0', fc=row_fc, ec='none', zorder=3))
    sc = avcol.get(status, TEXT_WHITE)
    ax.add_patch(plt.Circle((60.5, y-1.8), 1.0, color=sc, zorder=5))
    ax.text(62.5, y-0.8, player, color=RR_GOLD, fontsize=9.5, fontweight='bold', va='center', zorder=5)
    tag_badge(ax, 78, y-3.5, 10, 2.5, status, fc=sc, tc=BG_VOID, fs=7.5)
    ax.text(62.5, y-3.2, reason, color=TEXT_DIM, fontsize=7.5, va='center', zorder=5)
    ax.text(90, y-0.8, f'[{team}]', color=TEXT_DIM, fontsize=8, ha='center', va='center')

plt.savefig(str(SLIDES_DIR / 'tac_slide02_availability.png'),
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 2 done")


# ============================================================
# SLIDE 3: TOP 10 BATTERS
# ============================================================
fig3 = tac_fig("TOP 10 BATTERS  |  Pressure-Tested, Real-World Available Targets")
ax = fig3.add_axes([0.005, 0.035, 0.99, 0.865])
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle='square,pad=0', fc=BG_VOID, ec='none'))
draw_grid(ax, 100, 100, step=5, alpha=0.04)

# Column header row
col_defs = [
    ('#',       0.3,  2.0),
    ('PLAYER',  2.5,  12.0),
    ('TEAM 26', 15.0, 6.0),
    ('NAT',     21.3, 4.0),
    ('ROLE',    25.6, 9.0),
    ('DTH SR',  35.0, 5.5),
    ('DTH AVG', 40.8, 5.5),
    ('CHASE SR',46.6, 5.5),
    ('DOT %',   52.4, 4.5),
    ('BALLS',   57.2, 4.5),
    ('INDEX',   61.8, 8.5),
    ('NOTE',    70.8, 29.2),
]

for name, cx, cw in col_defs:
    ax.add_patch(FancyBboxPatch((cx, 94.5), cw-0.3, 5.0, boxstyle='square,pad=0',
                                fc=RR_PINK if name in ('#','INDEX') else BG_MID,
                                ec=CYAN_DIM, lw=0.5, zorder=3))
    ax.text(cx+cw/2, 97.0, name, color=TEXT_BRIGHT, fontsize=7.5,
            ha='center', va='center', fontweight='bold', zorder=4)

for i, (name, team, nat, role, dsr, davg, csr, dot, balls, idx, note) in enumerate(REVISED_BATTERS):
    y = 91.0 - i * 9.0
    row_fc = BG_MID if i % 2 == 0 else BG_PANEL
    ax.add_patch(FancyBboxPatch((0.3, y-5.8), 99.5, 7.5, boxstyle='square,pad=0', fc=row_fc, ec=GRID_LINE, lw=0.4, zorder=2))

    # Rank badge
    rcol = RR_PINK if i < 5 else CYAN_DIM
    ax.add_patch(plt.Circle((1.4, y-2.0), 2.3, color=rcol, zorder=5))
    ax.text(1.4, y-2.0, str(i+1), color=TEXT_BRIGHT, fontsize=12, ha='center', va='center', fontweight='bold', zorder=6)

    # Name
    ax.text(2.8, y-0.8, name, color=RR_GOLD if i < 5 else CYAN_BRIGHT, fontsize=10,
            fontweight='bold', va='center', zorder=5)

    # Team
    ax.text(18.0, y-2.0, team, color=AMBER_TAC, fontsize=8.5, ha='center', va='center', zorder=5)

    # Nat badge
    nc = CYAN_BRIGHT if nat == 'OS' else RED_TAC
    tag_badge(ax, 21.5, y-4.0, 3.5, 3.5, nat, fc=nc, tc=BG_VOID, fs=8)

    # Role
    ax.text(25.8, y-2.0, role, color=TEXT_DIM, fontsize=8, va='center', style='italic', zorder=5)

    # Stats
    dsr_col = GREEN_GO if dsr >= 200 else (AMBER_TAC if dsr >= 185 else RED_TAC)
    dsr_txt = f'{dsr:.1f}' if balls >= 100 else f'{dsr:.0f}*'
    ax.text(37.8, y-2.0, dsr_txt, color=dsr_col, fontsize=10, ha='center', va='center', fontweight='bold', zorder=5)
    ax.text(43.6, y-2.0, f'{davg:.1f}', color=TEXT_WHITE, fontsize=9.5, ha='center', va='center', zorder=5)
    ax.text(49.4, y-2.0, f'{csr:.0f}', color=TEXT_WHITE, fontsize=9.5, ha='center', va='center', zorder=5)
    ax.text(54.7, y-2.0, f'{dot:.0f}%', color=TEXT_WHITE, fontsize=9, ha='center', va='center', zorder=5)
    ax.text(59.5, y-2.0, f'{balls}', color=TEXT_DIM, fontsize=8.5, ha='center', va='center', zorder=5)

    # Index bar
    if idx > 0:
        index_bar(ax, 62.0, y-4.0, 7.5, 3.5, idx)
    else:
        tag_badge(ax, 62.5, y-4.0, 7.0, 3.5, 'PROFILE', fc='#4A148C', tc=PURPLE_TAC, fs=7.5)

    # Note
    words = note.split()
    line, lines = '', []
    for w in words:
        if len(line+' '+w) > 48: lines.append(line); line = w
        else: line = (line+' '+w).strip()
    if line: lines.append(line)
    for j, l in enumerate(lines[:2]):
        ax.text(71.2, y-0.6-j*2.6, l, color=TEXT_DIM, fontsize=7.8, va='center', zorder=5)

ax.text(0.5, 0.8, '* = below 100-ball minimum; on PROFILE only  |  DTH SR ≥200 green  ≥185 amber  <185 red  |  INDEX = composite 0-1',
        color=GRID_LINE, fontsize=6.8)

plt.savefig(str(SLIDES_DIR / 'tac_slide03_batters.png'),
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 3 done")


# ============================================================
# SLIDE 4: TOP 10 BOWLERS
# ============================================================
fig4 = tac_fig("TOP 10 BOWLERS  |  Pressure-Tested, Real-World Available Targets")
ax = fig4.add_axes([0.005, 0.035, 0.99, 0.865])
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle='square,pad=0', fc=BG_VOID, ec='none'))
draw_grid(ax, 100, 100, step=5, alpha=0.04)

bcol_defs = [
    ('#',       0.3,  2.0),
    ('PLAYER',  2.5,  12.0),
    ('TEAM',    15.0, 6.0),
    ('NAT',     21.3, 4.0),
    ('TYPE',    25.6, 7.5),
    ('DTH ECO', 33.4, 5.5),
    ('DOT %',   39.2, 4.5),
    ('W/INN',   44.0, 4.5),
    ('MID ECO', 48.8, 5.5),
    ('MID WPI', 54.6, 5.0),
    ('BALLS',   59.9, 4.5),
    ('INDEX',   64.6, 7.5),
    ('NOTE',    72.4, 27.6),
]

for name, cx, cw in bcol_defs:
    ax.add_patch(FancyBboxPatch((cx, 94.5), cw-0.3, 5.0, boxstyle='square,pad=0',
                                fc=RR_PINK if name in ('#', 'INDEX') else BG_MID,
                                ec=CYAN_DIM, lw=0.5, zorder=3))
    ax.text(cx+cw/2, 97.0, name, color=TEXT_BRIGHT, fontsize=7.5,
            ha='center', va='center', fontweight='bold', zorder=4)

for i, (name, team, nat, btype, deco, dot, wpi, midecon, mwpi, balls, idx, note) in enumerate(REVISED_BOWLERS):
    y = 91.0 - i * 9.0
    row_fc = BG_MID if i % 2 == 0 else BG_PANEL
    ax.add_patch(FancyBboxPatch((0.3, y-5.8), 99.5, 7.5, boxstyle='square,pad=0', fc=row_fc, ec=GRID_LINE, lw=0.4, zorder=2))

    rcol = RR_PINK if i < 5 else CYAN_DIM
    ax.add_patch(plt.Circle((1.4, y-2.0), 2.3, color=rcol, zorder=5))
    ax.text(1.4, y-2.0, str(i+1), color=TEXT_BRIGHT, fontsize=12, ha='center', va='center', fontweight='bold', zorder=6)

    ax.text(2.8, y-0.8, name, color=RR_GOLD if i < 5 else CYAN_BRIGHT, fontsize=10,
            fontweight='bold', va='center', zorder=5)

    ax.text(18.0, y-2.0, team, color=AMBER_TAC, fontsize=8.5, ha='center', va='center', zorder=5)

    nc = CYAN_BRIGHT if nat == 'OS' else RED_TAC
    tag_badge(ax, 21.5, y-4.0, 3.5, 3.5, nat, fc=nc, tc=BG_VOID, fs=8)

    type_fc = PURPLE_TAC if 'Spin' in btype else CYAN_DIM
    type_tc = BG_VOID if 'Spin' in btype else TEXT_BRIGHT
    tag_badge(ax, 25.8, y-4.0, 7.0, 3.5, btype, fc=type_fc, tc=type_tc, fs=7.5)

    eco_col = GREEN_GO if deco < 9.0 else (AMBER_TAC if deco < 10.0 else RED_TAC)
    ax.text(36.2, y-2.0, f'{deco:.2f}', color=eco_col, fontsize=10, ha='center', va='center', fontweight='bold', zorder=5)
    ax.text(41.5, y-2.0, f'{dot:.0f}%', color=TEXT_WHITE, fontsize=9.5, ha='center', va='center', zorder=5)
    ax.text(46.3, y-2.0, f'{wpi:.2f}', color=TEXT_WHITE, fontsize=9.5, ha='center', va='center', zorder=5)
    ax.text(51.6, y-2.0, f'{midecon:.2f}', color=TEXT_WHITE, fontsize=9.5, ha='center', va='center', zorder=5)
    ax.text(57.1, y-2.0, f'{mwpi:.2f}', color=TEXT_WHITE, fontsize=9.5, ha='center', va='center', zorder=5)
    ax.text(62.2, y-2.0, f'{balls}', color=TEXT_DIM, fontsize=8.5, ha='center', va='center', zorder=5)

    index_bar(ax, 64.8, y-4.0, 7.0, 3.5, idx)

    words = note.split()
    line, lines = '', []
    for w in words:
        if len(line+' '+w) > 48: lines.append(line); line = w
        else: line = (line+' '+w).strip()
    if line: lines.append(line)
    for j, l in enumerate(lines[:2]):
        ax.text(72.8, y-0.6-j*2.6, l, color=TEXT_DIM, fontsize=7.8, va='center', zorder=5)

ax.text(0.5, 0.8, 'INDEX = composite 0-1  |  DTH ECO: <9.0 green  <10.0 amber  ≥10.0 red  |  Spinner TYPE shown in purple',
        color=GRID_LINE, fontsize=6.8)

plt.savefig(str(SLIDES_DIR / 'tac_slide04_bowlers.png'),
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 4 done")


# ============================================================
# SLIDE 5: AUCTION PRIORITY
# ============================================================
fig5 = tac_fig("AUCTION PRIORITY ORDER  |  Price Ceilings & Bidding Sequence")
ax = fig5.add_axes([0.01, 0.038, 0.98, 0.862])
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle='square,pad=0', fc=BG_VOID, ec='none'))
draw_grid(ax, 100, 100, step=5, alpha=0.04)

ax.text(50, 97.5, 'BIDDING SEQUENCE — WHAT RR DOES AT THE AUCTION TABLE',
        color=CYAN_BRIGHT, fontsize=12, ha='center', va='center', fontweight='bold',
        path_effects=[pe.withStroke(linewidth=2, foreground=BG_VOID)])

# Legend
for lx, lbl, lc in [(2,'MUST BID',RR_PINK),(20,'HIGH',CYAN_DIM),(36,'TACTICAL','#4A148C')]:
    tag_badge(ax, lx, 92.5, 15, 4.5, lbl, fc=lc, tc=TEXT_BRIGHT, fs=9)
ax.text(53, 94.8, 'Walk to ceiling on MUST BID. Stop 15% above on HIGH. Hard-cap TACTICAL.',
        color=TEXT_DIM, fontsize=8.5, va='center')

# Header row
h_defs = [('SEQ',0.5,4), ('PRIORITY',5,11), ('PLAYER',16.5,27), ('NATIONALITY',44,9),
           ('CEILING',53.5,10), ('STAT PROOF',64,15), ('BIDDING INSTRUCTION',79.5,20.3)]
for ht, hx, hw in h_defs:
    fc = RR_PINK if ht in ('SEQ','CEILING') else BG_MID
    ax.add_patch(FancyBboxPatch((hx, 87), hw-0.4, 4.5, boxstyle='square,pad=0', fc=fc, ec=CYAN_DIM, lw=0.5, zorder=3))
    ax.text(hx+hw/2, 89.3, ht, color=TEXT_BRIGHT, fontsize=8.5, ha='center', va='center', fontweight='bold', zorder=4)

for i, (seq, pri, pcol, player, nat, ceil, stat, strategy) in enumerate(PRIORITY):
    y = 84.5 - i * 8.1
    row_fc = BG_MID if i % 2 == 0 else BG_PANEL
    ax.add_patch(FancyBboxPatch((0.5, y-5.0), 99.3, 7.0, boxstyle='square,pad=0', fc=row_fc, ec=GRID_LINE, lw=0.4, zorder=2))

    # Seq number
    ax.add_patch(plt.Circle((2.7, y-1.5), 2.5, color=pcol, zorder=5, alpha=0.9))
    ax.text(2.7, y-1.5, str(seq), color=TEXT_BRIGHT, fontsize=13, ha='center', va='center', fontweight='bold', zorder=6)

    # Priority badge
    tag_badge(ax, 5.3, y-4.2, 10.2, 5.5, pri, fc=pcol, tc=TEXT_BRIGHT, fs=8.5)

    # Player name
    ax.text(17.0, y-0.8, player, color=RR_GOLD if seq <= 3 else CYAN_BRIGHT,
            fontsize=11, fontweight='bold', va='center', zorder=5)

    # Nationality
    nc = CYAN_BRIGHT if nat == 'Overseas' else RED_TAC
    tag_badge(ax, 44.5, y-3.5, 8.0, 4.0, nat, fc=nc, tc=BG_VOID, fs=8.5)

    # Ceiling
    ceil_col = GREEN_GO if ceil <= 9 else (AMBER_TAC if ceil <= 11 else RED_TAC)
    ax.text(58.5, y-1.5, f'Rs.{ceil} Cr', color=ceil_col, fontsize=12,
            ha='center', va='center', fontweight='bold', zorder=5)

    # Stat proof
    ax.text(64.5, y-1.5, stat, color=TEXT_WHITE, fontsize=8.5, va='center', zorder=5)

    # Strategy (up to 2 lines)
    words = strategy.split()
    line, lines = '', []
    for w in words:
        if len(line+' '+w) > 32: lines.append(line); line = w
        else: line = (line+' '+w).strip()
    if line: lines.append(line)
    for j, l in enumerate(lines[:2]):
        ax.text(80.0, y+0.0-j*2.8, l, color=TEXT_DIM, fontsize=8.5, va='center', zorder=5)

# OS slot bar at bottom
panel(ax, 0.5, 2.0, 99.3, 5.5, fc=BG_MID, border_col=CYAN_BRIGHT, lw=1.5)
ax.text(2, 5.4, 'OVERSEAS SLOTS:', color=CYAN_BRIGHT, fontsize=9.5, fontweight='bold', va='center')
ax.text(2, 3.0, 'Retained (4/8): Archer  |  Burger  |  Maphaka  |  Ferreira       '
               'New Targets (4): Noor Ahmad  +  Pathirana  +  Tim David  +  Stubbs / Livingstone / Powell',
        color=TEXT_WHITE, fontsize=9, va='center')

plt.savefig(str(SLIDES_DIR / 'tac_slide05_priority.png'),
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 5 done")


# ============================================================
# SLIDE 6: METHODOLOGY
# ============================================================
fig6 = tac_fig("METHODOLOGY  |  Pressure Definitions, Metrics & Composite Index")
ax = fig6.add_axes([0.01, 0.038, 0.98, 0.862])
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle='square,pad=0', fc=BG_VOID, ec='none'))
draw_grid(ax, 100, 100, step=5, alpha=0.04)

# Left column: Pressure Defs
panel(ax, 0.5, 2, 48, 95, fc=BG_MID, border_col=CYAN_DIM, lw=1.2)
ax.text(24.5, 95, 'PRESSURE DEFINITIONS', color=CYAN_BRIGHT, fontsize=11, ha='center', va='center', fontweight='bold')

pdefs = [
    ('P1','DEATH OVERS',    RR_PINK,  'overid ≥ 16, both innings. Highest-leverage batting phase.'),
    ('P2','CHASE PRESSURE', CYAN_DIM, 'Inn 2, computed RRR > 10 at delivery time.'),
    ('P3','COLLAPSE REC.',  AMBER_TAC,'Inn 1, 3+ wkts in first 10 overs, entering after over 10.'),
    ('P4','KNOCKOUT',       GREEN_DIM,'knock_out=1 or Stage: Qualifier/Eliminator/Final/Semi-Final.'),
    ('P5','CLOSE FINISH',   PURPLE_TAC,'Result margin ≤ 9 runs or ≤ 2 wickets.'),
]
for i, (code, lbl, col, desc) in enumerate(pdefs):
    y = 88 - i * 15
    panel(ax, 1.5, y-9, 46.5, 11, fc=BG_PANEL, border_col=col, lw=1.0, radius=0.3)
    tag_badge(ax, 2.5, y-7.5, 7, 7.5, code, fc=col, tc=BG_VOID, fs=10)
    ax.text(11, y-2.5, lbl, color=col, fontsize=10, fontweight='bold', va='center')
    words = desc.split()
    line, lines = '', []
    for w in words:
        if len(line+' '+w) > 42: lines.append(line); line = w
        else: line = (line+' '+w).strip()
    if line: lines.append(line)
    for j, l in enumerate(lines[:2]):
        ax.text(11, y-5.5-j*2.5, l, color=TEXT_DIM, fontsize=8.5, va='center')

# Right column: Metrics + Index
panel(ax, 49.5, 2, 50, 95, fc=BG_MID, border_col=RR_PINK, lw=1.2)
ax.text(74.5, 95, 'METRICS & COMPOSITE INDEX', color=RR_PINK, fontsize=11, ha='center', va='center', fontweight='bold')

ax.text(51, 91, 'BATTER METRICS', color=CYAN_BRIGHT, fontsize=10, fontweight='bold')
bmet = ['Death-over Strike Rate (overs 16-20)',
        'Death Average (runs per dismissal)',
        'Boundary % (4s+6s / balls in death)',
        'Dot Ball % (legal balls with 0 runs)',
        'Chase SR under RRR > 10']
for i, m in enumerate(bmet):
    ax.text(51.5, 88 - i*4, f'  {m}', color=TEXT_WHITE, fontsize=9, va='center')
    ax.add_patch(plt.Circle((51.0, 88 - i*4), 0.5, color=CYAN_BRIGHT, zorder=5))

ax.text(51, 65, 'BOWLER METRICS', color=CYAN_BRIGHT, fontsize=10, fontweight='bold')
bomet = ['Death Economy (runs/over in overs 16-20)',
         'Death Dot % (legal zero-run deliveries)',
         'Wickets per Innings (death + middle)',
         'Middle Economy (overs 7-15)',
         'CV of Economy (consistency measure)']
for i, m in enumerate(bomet):
    ax.text(51.5, 62 - i*4, f'  {m}', color=TEXT_WHITE, fontsize=9, va='center')
    ax.add_patch(plt.Circle((51.0, 62 - i*4), 0.5, color=RR_PINK, zorder=5))

# Weights panel
panel(ax, 50.5, 2.5, 48.5, 28, fc=BG_PANEL, border_col=RR_GOLD, lw=1.5, radius=0.3)
ax.text(74.5, 28, 'COMPOSITE INDEX WEIGHTS', color=RR_GOLD, fontsize=10, ha='center', va='center', fontweight='bold')
weights = [('40%','PERFORMANCE','Death SR / Eco + Boundary% + Dot%'),
           ('25%','CHASE CLUTCH','SR when RRR > 10'),
           ('20%','CONSISTENCY','1 - CV of innings-level metric'),
           ('10%','DELTA','Improvement vs overall performance'),
           ('5%', 'SAMPLE','log(balls)/log(400) confidence')]
for i, (pct, lbl, desc) in enumerate(weights):
    y = 24 - i*4.5
    ax.text(52, y, pct, color=RR_GOLD, fontsize=11, fontweight='bold', va='center')
    ax.text(57, y, f'{lbl}:', color=CYAN_BRIGHT, fontsize=8.5, fontweight='bold', va='center')
    ax.text(57, y-2.2, desc, color=TEXT_DIM, fontsize=7.8, va='center')

ax.text(51, 2, 'Min 100 death balls (bat) / 60 death balls (bowl) to qualify',
        color=AMBER_TAC, fontsize=8, va='center', style='italic')

plt.savefig(str(SLIDES_DIR / 'tac_slide06_method.png'),
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 6 done")


# ============================================================
# SLIDE 7: RISKS & DATA LIMITATIONS
# ============================================================
fig7 = tac_fig("RISKS, ASSUMPTIONS & DATA LIMITATIONS")
ax = fig7.add_axes([0.01, 0.038, 0.98, 0.862])
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0), 100, 100, boxstyle='square,pad=0', fc=BG_VOID, ec='none'))
draw_grid(ax, 100, 100, step=5, alpha=0.04)

panel(ax, 0.5, 2, 49, 95, fc=BG_MID, border_col=RED_TAC, lw=1.5)
ax.text(25, 95.5, 'RISKS', color=RED_TAC, fontsize=13, ha='center', va='center', fontweight='bold')

risks = [
    ('Injury',         'Harshal Patel (shoulder surgery 2025). Confirm clearance before bidding.'),
    ('Overseas Slots', 'If RR retains >4 OS already, Tim David + Stubbs compete for 2 slots vs Noor + Pathirana.'),
    ('Overbidding',    'Varun Chakravarthy + Rinku-class players will see 10-team bidding wars. Have walk-away price.'),
    ('Form Recency',   '5 IPL seasons equally weighted. Manually adjust if player had breakout or slump in 2026.'),
    ('Small Sample',   'Noor Ahmad (151 death balls), Suyash Sharma (95 balls). Treat as directional only.'),
    ('Maxwell',        'Glenn Maxwell below data threshold. Included on profile; risk of past form not repeating.'),
    ('Availability',   'KKR/SRH retention decisions not confirmed. Varun/Harshal availability is uncertain.'),
    ('Data Bug',       'extras1_runs is delivery-type code (not runs). Fixed in analysis. Run totals verified.'),
]
for i, (title, body) in enumerate(risks):
    y = 90 - i*10.8
    panel(ax, 1.5, y-7.5, 47, 9.5, fc='#1A0505', border_col=RED_TAC, lw=0.6, radius=0.2)
    ax.add_patch(plt.Circle((3.5, y-2.5), 0.9, color=RED_TAC, zorder=5))
    ax.text(5.5, y-1.0, title, color=RED_TAC, fontsize=9.5, fontweight='bold', va='center')
    words = body.split()
    line, lines = '', []
    for w in words:
        if len(line+' '+w) > 55: lines.append(line); line = w
        else: line = (line+' '+w).strip()
    if line: lines.append(line)
    for j, l in enumerate(lines[:2]):
        ax.text(5.5, y-4.0-j*2.5, l, color=TEXT_DIM, fontsize=8, va='center')

panel(ax, 50.5, 2, 49.3, 95, fc=BG_MID, border_col=AMBER_TAC, lw=1.5)
ax.text(75, 95.5, 'ASSUMPTIONS & LIMITATIONS', color=AMBER_TAC, fontsize=12, ha='center', va='center', fontweight='bold')

assumptions = [
    ('Data Scope',     'Ball-by-ball covers IPL 2022-2026 (5 seasons). T20I data exists in DB but excluded.'),
    ('Nationality',    'Indian vs Overseas inferred from team names in competition_team_player_mapping.'),
    ('Dot Ball Def.',  'Dot = legal delivery + 0 runs off bat. Byes on 0 not counted as dot for batter.'),
    ('Extras Fix',     'extras1_runs = delivery type code (6=regular, 2=wide). NOT extra runs. Fixed.'),
    ('Dismissed ID',   'Some run-out rows have dismissed_player_id empty. Excluded from bowler wkt count.'),
    ('Season Weight',  'All 5 IPL seasons equally weighted. Adjust manually for 2026 breakout stars.'),
    ('Chase RRR',      'RRR computed from ball-by-ball reconstruction, not live scorecard.'),
    ('Availability',   'No real-time retention data. All availability is based on franchise logic Nov 2026.'),
]
for i, (title, body) in enumerate(assumptions):
    y = 90 - i*10.8
    panel(ax, 51.5, y-7.5, 47.5, 9.5, fc='#121A05', border_col=AMBER_TAC, lw=0.6, radius=0.2)
    ax.add_patch(plt.Circle((53.5, y-2.5), 0.9, color=AMBER_TAC, zorder=5))
    ax.text(55.5, y-1.0, title, color=AMBER_TAC, fontsize=9.5, fontweight='bold', va='center')
    words = body.split()
    line, lines = '', []
    for w in words:
        if len(line+' '+w) > 55: lines.append(line); line = w
        else: line = (line+' '+w).strip()
    if line: lines.append(line)
    for j, l in enumerate(lines[:2]):
        ax.text(55.5, y-4.0-j*2.5, l, color=TEXT_DIM, fontsize=8, va='center')

plt.savefig(str(SLIDES_DIR / 'tac_slide07_risks.png'),
            dpi=150, bbox_inches='tight', facecolor=BG_DARK)
plt.close()
print("Slide 7 done")


# ============================================================
# COMBINE ALL INTO PDF
# ============================================================
print("\nBuilding Tactical Vision PDF...")
from matplotlib.backends.backend_pdf import PdfPages

slides_final = [
    str(SLIDES_DIR / 'tac_slide01_title.png'),
    str(SLIDES_DIR / 'tac_slide06_method.png'),
    str(SLIDES_DIR / 'tac_slide02_availability.png'),
    str(SLIDES_DIR / 'tac_slide03_batters.png'),
    str(SLIDES_DIR / 'tac_slide04_bowlers.png'),
    str(SLIDES_DIR / 'tac_slide05_priority.png'),
    str(SLIDES_DIR / 'tac_slide07_risks.png'),
]

out = str(REPORTS_DIR / 'RR_Auction_2027_Raghav_Patil.pdf')
with PdfPages(out) as pdf:
    for sp in slides_final:
        img = plt.imread(sp)
        fig = plt.figure(figsize=(19.2, 10.8))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.imshow(img); ax.axis('off')
        pdf.savefig(fig, bbox_inches='tight', facecolor='black')
        plt.close()
    d = pdf.infodict()
    d['Title'] = 'RR IPL 2027 Auction Intelligence — SupeRR Selector Season 2'
    d['Author'] = 'Raghav Patil'
    d['Subject'] = 'Pressure Player Analysis — Tactical Vision Edition'

print(f"PDF saved: {out}")
print("Done!")
