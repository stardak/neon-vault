"""
Slot Game Configuration
=======================
Defines the game's symbols, reels, paylines, and payout table.
This is a 5-reel, 3-row slot game (standard video slot format).
"""

# ─── SYMBOL DEFINITIONS ─────────────────────────────────────────────
# Each symbol has an ID, name, and tier (affects visual treatment)
SYMBOLS = {
    "W":  {"name": "Wild",     "tier": "special", "substitutes": True},
    "S":  {"name": "Scatter",  "tier": "special", "substitutes": False},
    "H1": {"name": "Diamond",  "tier": "high"},
    "H2": {"name": "Ruby",     "tier": "high"},
    "H3": {"name": "Emerald",  "tier": "high"},
    "L1": {"name": "Ace",      "tier": "low"},
    "L2": {"name": "King",     "tier": "low"},
    "L3": {"name": "Queen",    "tier": "low"},
    "L4": {"name": "Jack",     "tier": "low"},
}

# ─── REEL STRIPS ────────────────────────────────────────────────────
# Each reel is a weighted list of symbols. The frequency of each symbol
# on each reel controls the math. More entries = higher probability.
# Standard approach: ~30 stops per reel.

REEL_STRIPS = [
    # Reel 1
    ["L4", "L3", "L2", "H3", "L4", "L1", "L3", "H2", "L4", "L2",
     "L1", "L3", "H1", "L4", "L2", "L3", "L1", "W",  "L4", "L2",
     "L3", "H3", "L1", "L4", "L2", "S",  "L3", "L4", "L1", "L2"],
    # Reel 2
    ["L2", "L4", "L3", "L1", "H3", "L4", "L2", "L3", "H2", "L1",
     "L4", "L3", "L2", "H1", "L1", "L4", "L3", "W",  "L2", "L4",
     "L1", "L3", "H3", "L2", "L4", "L1", "S",  "L3", "L4", "L2"],
    # Reel 3
    ["L3", "L1", "L4", "L2", "H3", "L3", "L1", "L4", "H2", "L2",
     "L3", "L1", "H1", "L4", "L2", "L3", "W",  "L1", "L4", "L2",
     "L3", "H3", "L4", "L1", "L2", "L3", "S",  "L4", "L1", "L2"],
    # Reel 4
    ["L1", "L2", "L3", "L4", "H3", "L1", "L2", "L4", "H2", "L3",
     "L1", "L4", "H1", "L2", "L3", "L1", "L4", "W",  "L2", "L3",
     "L1", "L4", "H3", "L2", "L3", "L4", "S",  "L1", "L2", "L3"],
    # Reel 5
    ["L4", "L1", "L2", "L3", "H3", "L4", "L1", "L3", "H2", "L2",
     "L4", "L1", "H1", "L3", "L2", "L4", "W",  "L1", "L3", "L2",
     "L4", "H3", "L1", "L3", "L2", "S",  "L4", "L1", "L3", "L2"],
]

NUM_REELS = 5
NUM_ROWS = 3
STOPS_PER_REEL = len(REEL_STRIPS[0])  # 30

# ─── PAYLINES ───────────────────────────────────────────────────────
# 20 paylines. Each payline maps reel index -> row index (0-based).
# Row 0=top, 1=middle, 2=bottom
PAYLINES = [
    [1, 1, 1, 1, 1],  #  1: Middle straight
    [0, 0, 0, 0, 0],  #  2: Top straight
    [2, 2, 2, 2, 2],  #  3: Bottom straight
    [0, 1, 2, 1, 0],  #  4: V shape
    [2, 1, 0, 1, 2],  #  5: Inverted V
    [0, 0, 1, 2, 2],  #  6: Diagonal down
    [2, 2, 1, 0, 0],  #  7: Diagonal up
    [1, 0, 0, 0, 1],  #  8: Top hat
    [1, 2, 2, 2, 1],  #  9: Bottom hat
    [0, 1, 1, 1, 0],  # 10: Shallow V
    [2, 1, 1, 1, 2],  # 11: Shallow inverted V
    [1, 0, 1, 0, 1],  # 12: Zigzag up
    [1, 2, 1, 2, 1],  # 13: Zigzag down
    [0, 1, 0, 1, 0],  # 14: Wave top
    [2, 1, 2, 1, 2],  # 15: Wave bottom
    [1, 1, 0, 1, 1],  # 16: Top bump
    [1, 1, 2, 1, 1],  # 17: Bottom bump
    [0, 0, 1, 0, 0],  # 18: Top with dip
    [2, 2, 1, 2, 2],  # 19: Bottom with rise
    [0, 2, 0, 2, 0],  # 20: Big zigzag
]

# ─── PAYTABLE ───────────────────────────────────────────────────────
# Payouts per symbol for 3, 4, or 5 of a kind on a payline.
# Values are multipliers of the LINE BET (total_bet / num_paylines).
PAYTABLE = {
    "W":  {3: 50,  4: 200,  5: 1000},  # Wild pays on its own too
    "H1": {3: 30,  4: 100,  5: 500},   # Diamond
    "H2": {3: 20,  4: 75,   5: 250},   # Ruby
    "H3": {3: 15,  4: 50,   5: 150},   # Emerald
    "L1": {3: 10,  4: 30,   5: 100},   # Ace
    "L2": {3: 8,   4: 25,   5: 75},    # King
    "L3": {3: 5,   4: 20,   5: 50},    # Queen
    "L4": {3: 3,   4: 15,   5: 30},    # Jack
}

# ─── SCATTER RULES ──────────────────────────────────────────────────
# Scatter pays based on total symbols anywhere on the grid (not paylines)
SCATTER_PAYS = {
    3: 5,    # 5x total bet
    4: 20,   # 20x total bet
    5: 100,  # 100x total bet
}

# Scatter also triggers free spins
FREE_SPINS_TRIGGER = {
    3: 10,   # 10 free spins
    4: 15,   # 15 free spins
    5: 25,   # 25 free spins
}

# Free spins multiplier (all wins during free spins multiplied by this)
FREE_SPINS_MULTIPLIER = 3

# ─── TARGET RTP ─────────────────────────────────────────────────────
TARGET_RTP = 0.96  # 96% return to player
