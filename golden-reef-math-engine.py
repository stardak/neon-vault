"""
Golden Reef - Stake Engine Math Engine
=======================================
Generates all possible game outcomes as static files for Stake Engine.

Game Spec:
- 5 reels, 3 rows (15 visible symbols)
- 20 paylines
- Symbols: WILD, SCATTER, HIGH1-HIGH3, LOW1-LOW4
- Features: Free Spins (3+ scatters), Wild Multiplier
- Target RTP: ~96.5%
"""

import csv
import json
import itertools
import random
import os
import gzip
import shutil
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional

# ============================================================
# SYMBOL DEFINITIONS
# ============================================================

SYMBOLS = {
    "WILD":    {"id": 0, "name": "Treasure Chest",  "type": "wild"},
    "SCATTER": {"id": 1, "name": "Golden Compass",  "type": "scatter"},
    "HIGH1":   {"id": 2, "name": "Gold Coin",        "type": "high"},
    "HIGH2":   {"id": 3, "name": "Pearl",            "type": "high"},
    "HIGH3":   {"id": 4, "name": "Starfish",         "type": "high"},
    "LOW1":    {"id": 5, "name": "Seahorse",         "type": "low"},
    "LOW2":    {"id": 6, "name": "Shell",             "type": "low"},
    "LOW3":    {"id": 7, "name": "Coral",             "type": "low"},
    "LOW4":    {"id": 8, "name": "Anchor",            "type": "low"},
}

# ============================================================
# PAYTABLE (multiplier per bet-line for N matching symbols)
# ============================================================

PAYTABLE = {
    #           3x       4x       5x     (multiplier of LINE BET)
    "WILD":   [108.0,  540.0,  2700.0],
    "HIGH1":  [ 54.0,  200.0,  1080.0],
    "HIGH2":  [ 40.0,  135.0,   675.0],
    "HIGH3":  [ 27.0,  108.0,   405.0],
    "LOW1":   [ 13.5,   54.0,   200.0],
    "LOW2":   [ 10.8,   40.0,   135.0],
    "LOW3":   [  8.0,   27.0,   108.0],
    "LOW4":   [  5.4,   20.0,    80.0],
}

# Scatter pays (total bet multiplier)
SCATTER_PAY = {
    3: 4.0,
    4: 20.0,
    5: 135.0,
}

FREE_SPINS_AWARDED = {
    3: 10,
    4: 15,
    5: 25,
}

# ============================================================
# REEL STRIPS (weighted symbol positions per reel)
# ============================================================

REEL_STRIPS = [
    # Reel 1 (32 stops)
    ["LOW4","LOW2","HIGH3","LOW1","LOW3","HIGH2","LOW4","LOW1",
     "LOW2","HIGH1","LOW3","LOW4","SCATTER","LOW1","HIGH3","LOW2",
     "LOW3","LOW4","HIGH2","LOW1","WILD","LOW2","LOW3","LOW4",
     "HIGH3","LOW1","LOW2","LOW3","HIGH1","LOW4","LOW1","LOW2"],
    # Reel 2 (32 stops)
    ["LOW1","HIGH3","LOW4","LOW2","LOW3","HIGH1","LOW4","SCATTER",
     "LOW2","HIGH2","LOW1","LOW3","LOW4","HIGH3","LOW2","LOW1",
     "LOW3","WILD","LOW4","LOW2","HIGH2","LOW1","LOW3","LOW4",
     "LOW2","HIGH3","LOW1","LOW3","LOW4","LOW2","LOW1","HIGH1"],
    # Reel 3 (32 stops)
    ["LOW3","LOW1","HIGH2","LOW4","LOW2","HIGH3","LOW1","LOW3",
     "SCATTER","LOW2","HIGH1","LOW4","LOW1","LOW3","LOW2","HIGH2",
     "LOW4","LOW1","WILD","LOW3","LOW2","HIGH3","LOW4","LOW1",
     "LOW2","LOW3","HIGH1","LOW4","LOW1","LOW2","LOW3","LOW4"],
    # Reel 4 (32 stops)
    ["LOW2","LOW4","HIGH1","LOW1","LOW3","HIGH3","LOW2","LOW4",
     "LOW1","HIGH2","LOW3","SCATTER","LOW4","LOW2","HIGH3","LOW1",
     "LOW3","LOW4","HIGH2","LOW2","LOW1","WILD","LOW3","LOW4",
     "HIGH1","LOW2","LOW1","LOW3","LOW4","LOW2","HIGH3","LOW1"],
    # Reel 5 (32 stops)
    ["LOW4","LOW1","HIGH3","LOW2","LOW3","HIGH2","LOW4","LOW1",
     "LOW2","HIGH1","LOW3","LOW4","LOW1","SCATTER","HIGH3","LOW2",
     "WILD","LOW3","LOW4","HIGH2","LOW1","LOW2","LOW3","LOW4",
     "HIGH1","LOW1","LOW2","LOW3","LOW4","HIGH3","LOW2","LOW1"],
]

# ============================================================
# PAYLINES (20 lines, each maps row index per reel)
# Row indices: 0=top, 1=middle, 2=bottom
# ============================================================

PAYLINES = [
    [1, 1, 1, 1, 1],  # Line 1:  middle straight
    [0, 0, 0, 0, 0],  # Line 2:  top straight
    [2, 2, 2, 2, 2],  # Line 3:  bottom straight
    [0, 1, 2, 1, 0],  # Line 4:  V shape
    [2, 1, 0, 1, 2],  # Line 5:  inverted V
    [0, 0, 1, 2, 2],  # Line 6:  descending slope
    [2, 2, 1, 0, 0],  # Line 7:  ascending slope
    [1, 0, 0, 0, 1],  # Line 8:  top dip
    [1, 2, 2, 2, 1],  # Line 9:  bottom dip
    [0, 1, 1, 1, 0],  # Line 10: mild V
    [2, 1, 1, 1, 2],  # Line 11: mild inv V
    [1, 0, 1, 0, 1],  # Line 12: zigzag up
    [1, 2, 1, 2, 1],  # Line 13: zigzag down
    [0, 1, 0, 1, 0],  # Line 14: top zigzag
    [2, 1, 2, 1, 2],  # Line 15: bottom zigzag
    [1, 1, 0, 1, 1],  # Line 16: top bump
    [1, 1, 2, 1, 1],  # Line 17: bottom bump
    [0, 0, 1, 0, 0],  # Line 18: slight dip top
    [2, 2, 1, 2, 2],  # Line 19: slight dip bottom
    [0, 2, 0, 2, 0],  # Line 20: extreme zigzag
]

NUM_LINES = len(PAYLINES)

# ============================================================
# GAME LOGIC
# ============================================================

def get_visible_window(reel_strip: List[str], stop: int) -> List[str]:
    """Get 3 visible symbols from a reel strip given a stop position."""
    length = len(reel_strip)
    return [
        reel_strip[stop % length],
        reel_strip[(stop + 1) % length],
        reel_strip[(stop + 2) % length],
    ]


def evaluate_payline(symbols_on_line: List[str]) -> Tuple[Optional[str], int, float]:
    """
    Evaluate a single payline left-to-right.
    Returns (winning_symbol, count, payout_multiplier) or (None, 0, 0.0).
    """
    first = symbols_on_line[0]

    # Determine the paying symbol (first non-wild, or wild if all wilds)
    pay_symbol = None
    for s in symbols_on_line:
        if s == "SCATTER":
            return (None, 0, 0.0)  # Scatters don't pay on lines
        if s != "WILD":
            pay_symbol = s
            break

    if pay_symbol is None:
        pay_symbol = "WILD"  # All wilds

    # Count consecutive matching symbols from left
    count = 0
    for s in symbols_on_line:
        if s == pay_symbol or s == "WILD":
            count += 1
        else:
            break

    if count < 3:
        return (None, 0, 0.0)

    if pay_symbol not in PAYTABLE:
        return (None, 0, 0.0)

    payout = PAYTABLE[pay_symbol][count - 3]
    return (pay_symbol, count, payout)


def count_scatters(grid: List[List[str]]) -> int:
    """Count scatter symbols across the entire grid."""
    count = 0
    for reel in grid:
        for sym in reel:
            if sym == "SCATTER":
                count += 1
    return count


def evaluate_spin(stop_positions: List[int]) -> dict:
    """
    Evaluate a complete spin given stop positions for each reel.
    Returns full result including grid, line wins, scatter wins, total payout.
    """
    # Build the visible grid: grid[reel][row]
    grid = []
    for reel_idx, stop in enumerate(stop_positions):
        grid.append(get_visible_window(REEL_STRIPS[reel_idx], stop))

    # Evaluate each payline
    line_wins = []
    total_line_payout = 0.0

    for line_idx, payline in enumerate(PAYLINES):
        symbols_on_line = [grid[reel][payline[reel]] for reel in range(5)]
        symbol, count, payout = evaluate_payline(symbols_on_line)
        if payout > 0:
            line_wins.append({
                "line": line_idx + 1,
                "symbol": symbol,
                "count": count,
                "payout": payout,
            })
            total_line_payout += payout

    # Evaluate scatters
    scatter_count = count_scatters(grid)
    scatter_payout = SCATTER_PAY.get(scatter_count, 0.0)
    free_spins = FREE_SPINS_AWARDED.get(scatter_count, 0)

    # Total payout relative to TOTAL BET
    # Line wins are per-line-bet, so divide by NUM_LINES for total-bet multiplier
    # Scatter pays are already total-bet multipliers
    total_payout = (total_line_payout / NUM_LINES) + scatter_payout

    # Flatten grid for output: row-major order
    flat_grid = []
    for row in range(3):
        for reel in range(5):
            flat_grid.append(grid[reel][row])

    return {
        "stops": stop_positions,
        "grid": flat_grid,
        "grid_2d": grid,
        "line_wins": line_wins,
        "scatter_count": scatter_count,
        "scatter_payout": scatter_payout,
        "free_spins_awarded": free_spins,
        "total_line_payout": total_line_payout,
        "total_payout": total_payout,
    }


# ============================================================
# SIMULATION ENGINE
# ============================================================

@dataclass
class SimulationResult:
    sim_id: int
    stops: List[int]
    grid: List[str]
    total_payout: float
    line_wins: List[dict]
    scatter_count: int
    scatter_payout: float
    free_spins: int
    mode: str = "base"


def run_simulation(num_sims: int = 100_000, seed: int = 42) -> List[SimulationResult]:
    """Run Monte Carlo simulation to generate game outcomes."""
    rng = random.Random(seed)
    results = []
    reel_lengths = [len(strip) for strip in REEL_STRIPS]

    for sim_id in range(num_sims):
        stops = [rng.randint(0, reel_lengths[r] - 1) for r in range(5)]
        result = evaluate_spin(stops)

        results.append(SimulationResult(
            sim_id=sim_id,
            stops=stops,
            grid=result["grid"],
            total_payout=result["total_payout"],
            line_wins=result["line_wins"],
            scatter_count=result["scatter_count"],
            scatter_payout=result["scatter_payout"],
            free_spins=result["free_spins_awarded"],
            mode="base",
        ))

    return results


def calculate_rtp(results: List[SimulationResult]) -> float:
    """Calculate Return to Player percentage."""
    total_wagered = len(results)  # 1 unit per spin
    total_won = sum(r.total_payout for r in results)
    return (total_won / total_wagered) * 100 if total_wagered > 0 else 0.0


def generate_probability_weights(results: List[SimulationResult]) -> List[Tuple[int, float, float]]:
    """
    Generate (sim_id, probability, payout) tuples.
    Each outcome is equally likely in base simulation.
    For Stake Engine: probability = 1/total_sims per unique outcome.
    """
    total = len(results)
    prob = 1.0 / total
    return [(r.sim_id, prob, r.total_payout) for r in results]


# ============================================================
# OUTPUT GENERATORS (Stake Engine Format)
# ============================================================

def export_csv(results: List[SimulationResult], filepath: str):
    """Export results as Stake Engine compatible CSV."""
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "simulation_number",
            "probability",
            "payout_multiplier",
            "grid",
            "stops",
            "line_wins_count",
            "scatter_count",
            "free_spins",
        ])

        total = len(results)
        prob = 1.0 / total

        for r in results:
            writer.writerow([
                r.sim_id,
                f"{prob:.10f}",
                f"{r.total_payout:.2f}",
                "|".join(r.grid),
                "|".join(str(s) for s in r.stops),
                len(r.line_wins),
                r.scatter_count,
                r.free_spins,
            ])


def export_game_events(results: List[SimulationResult], filepath: str):
    """Export detailed game events as JSON (for /play API responses)."""
    events = {}
    for r in results:
        events[str(r.sim_id)] = {
            "stops": r.stops,
            "grid": r.grid,
            "totalPayout": r.total_payout,
            "lineWins": r.line_wins,
            "scatterCount": r.scatter_count,
            "scatterPayout": r.scatter_payout,
            "freeSpinsAwarded": r.free_spins,
            "mode": r.mode,
        }

    with open(filepath, "w") as f:
        json.dump(events, f, separators=(",", ":"))


def export_game_config(filepath: str):
    """Export game configuration file."""
    config = {
        "game": {
            "name": "Golden Reef",
            "id": "golden-reef",
            "version": "1.0.0",
            "type": "slot",
        },
        "grid": {
            "reels": 5,
            "rows": 3,
            "paylines": NUM_LINES,
        },
        "symbols": {k: {"id": v["id"], "name": v["name"], "type": v["type"]} for k, v in SYMBOLS.items()},
        "paytable": PAYTABLE,
        "scatterPay": {str(k): v for k, v in SCATTER_PAY.items()},
        "freeSpins": {str(k): v for k, v in FREE_SPINS_AWARDED.items()},
        "paylines": PAYLINES,
        "reelStrips": REEL_STRIPS,
    }

    with open(filepath, "w") as f:
        json.dump(config, f, indent=2)


def compress_output(input_path: str, output_path: str):
    """Compress file with gzip for Stake Engine upload."""
    with open(input_path, "rb") as f_in:
        with gzip.open(output_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("  GOLDEN REEF - Stake Engine Math Engine")
    print("=" * 60)

    # --- Run base game simulation ---
    print("\n[1/5] Running base game simulation (100,000 spins)...")
    base_results = run_simulation(num_sims=100_000, seed=42)

    rtp = calculate_rtp(base_results)
    print(f"       Base Game RTP: {rtp:.2f}%")

    # --- Statistics ---
    print("\n[2/5] Calculating statistics...")
    wins = [r for r in base_results if r.total_payout > 0]
    scatter_triggers = [r for r in base_results if r.free_spins > 0]
    max_win = max(r.total_payout for r in base_results)
    avg_win = sum(r.total_payout for r in wins) / len(wins) if wins else 0

    print(f"       Hit Rate: {len(wins)/len(base_results)*100:.1f}%")
    print(f"       Scatter Triggers: {len(scatter_triggers)} ({len(scatter_triggers)/len(base_results)*100:.2f}%)")
    print(f"       Max Win: {max_win:.1f}x")
    print(f"       Avg Win (when winning): {avg_win:.2f}x")

    # --- Payout distribution ---
    print("\n       Payout Distribution:")
    brackets = [(0, 0), (0.01, 2), (2, 5), (5, 10), (10, 50), (50, 100), (100, float("inf"))]
    for lo, hi in brackets:
        count = sum(1 for r in base_results if lo <= r.total_payout < hi)
        if lo == 0 and hi == 0:
            count = sum(1 for r in base_results if r.total_payout == 0)
            label = "  0x (loss)"
        elif hi == float("inf"):
            label = f"  {lo}x+"
        else:
            label = f"  {lo}-{hi}x"
        print(f"       {label}: {count:>6} ({count/len(base_results)*100:.1f}%)")

    # --- Export CSV ---
    print("\n[3/5] Exporting base game CSV...")
    csv_path = os.path.join(output_dir, "base_game.csv")
    export_csv(base_results, csv_path)
    print(f"       Saved: {csv_path}")

    # --- Export game events JSON ---
    print("\n[4/5] Exporting game events JSON...")
    events_path = os.path.join(output_dir, "base_game_events.json")
    export_game_events(base_results, events_path)
    print(f"       Saved: {events_path}")

    # --- Export config ---
    print("\n[5/5] Exporting game configuration...")
    config_path = os.path.join(output_dir, "game_config.json")
    export_game_config(config_path)
    print(f"       Saved: {config_path}")

    # --- Compress for upload ---
    print("\n[+] Compressing files for Stake Engine upload...")
    for fpath in [csv_path, events_path]:
        gz_path = fpath + ".gz"
        compress_output(fpath, gz_path)
        orig_size = os.path.getsize(fpath)
        gz_size = os.path.getsize(gz_path)
        print(f"       {os.path.basename(fpath)}: {orig_size//1024}KB → {gz_size//1024}KB")

    print("\n" + "=" * 60)
    print("  BUILD COMPLETE")
    print(f"  Output directory: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
