"""
Slot Game Simulator & Outcome Generator
========================================
Generates all possible game outcomes for Stake Engine.
Each outcome includes: simulation_number, probability, payout_multiplier

For a 5-reel, 30-stop slot, total combinations = 30^5 = 24,300,000.
We use Monte Carlo sampling to generate a representative set of outcomes,
then bucket them by payout to create the compressed outcome files.
"""

import csv
import gzip
import json
import os
import random
import time
from collections import defaultdict
from itertools import product as cartesian_product

from slot_config import (
    SYMBOLS, REEL_STRIPS, NUM_REELS, NUM_ROWS, STOPS_PER_REEL,
    PAYLINES, PAYTABLE, SCATTER_PAYS, FREE_SPINS_TRIGGER,
    FREE_SPINS_MULTIPLIER, TARGET_RTP
)

random.seed(42)  # Reproducible results

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─── CORE EVALUATION FUNCTIONS ──────────────────────────────────────

def get_visible_grid(stop_positions):
    """
    Given a list of stop positions (one per reel), return the 5x3 visible grid.
    Each reel wraps around, so we take stop, stop+1, stop+2 (mod reel length).
    Returns: list of 5 columns, each column is 3 symbols (top to bottom).
    """
    grid = []
    for reel_idx, stop in enumerate(stop_positions):
        strip = REEL_STRIPS[reel_idx]
        reel_len = len(strip)
        column = [
            strip[stop % reel_len],
            strip[(stop + 1) % reel_len],
            strip[(stop + 2) % reel_len],
        ]
        grid.append(column)
    return grid


def evaluate_payline(grid, payline):
    """
    Evaluate a single payline on the grid.
    Returns (winning_symbol, count, payout_multiplier) or None if no win.
    Wilds substitute for all symbols except Scatter.
    """
    # Get the symbols on this payline
    symbols_on_line = [grid[reel][row] for reel, row in enumerate(payline)]

    # Determine the paying symbol (first non-wild from left)
    pay_symbol = None
    for sym in symbols_on_line:
        if sym == "S":
            return None  # Scatter doesn't pay on paylines
        if sym != "W":
            pay_symbol = sym
            break

    # If all wilds, pay as wild
    if pay_symbol is None:
        pay_symbol = "W"

    # Count consecutive matches from left (wilds count)
    count = 0
    for sym in symbols_on_line:
        if sym == pay_symbol or sym == "W":
            count += 1
        else:
            break

    # Check if we have a winning combination
    if count >= 3 and pay_symbol in PAYTABLE and count in PAYTABLE[pay_symbol]:
        return (pay_symbol, count, PAYTABLE[pay_symbol][count])

    return None


def evaluate_scatters(grid):
    """
    Count scatter symbols anywhere on the grid.
    Returns (scatter_count, scatter_payout, free_spins_awarded).
    """
    scatter_count = 0
    for reel in grid:
        for sym in reel:
            if sym == "S":
                scatter_count += 1

    scatter_payout = SCATTER_PAYS.get(scatter_count, 0)
    free_spins = FREE_SPINS_TRIGGER.get(scatter_count, 0)

    return scatter_count, scatter_payout, free_spins


def evaluate_spin(stop_positions):
    """
    Evaluate a complete spin. Returns:
    - total_payout: total multiplier (relative to total bet)
    - details: dict with breakdown of wins
    """
    grid = get_visible_grid(stop_positions)

    total_line_payout = 0
    winning_lines = []

    # Evaluate each payline
    for line_idx, payline in enumerate(PAYLINES):
        result = evaluate_payline(grid, payline)
        if result:
            symbol, count, payout = result
            total_line_payout += payout
            winning_lines.append({
                "line": line_idx + 1,
                "symbol": symbol,
                "count": count,
                "payout": payout,
            })

    # Line payouts are per-line, convert to total bet multiplier
    # If 20 paylines, each line bet = total_bet / 20
    num_paylines = len(PAYLINES)
    total_payout_multiplier = total_line_payout / num_paylines

    # Evaluate scatters (pays on total bet)
    scatter_count, scatter_payout, free_spins = evaluate_scatters(grid)
    total_payout_multiplier += scatter_payout

    details = {
        "grid": grid,
        "winning_lines": winning_lines,
        "scatter_count": scatter_count,
        "scatter_payout": scatter_payout,
        "free_spins": free_spins,
        "total_payout": round(total_payout_multiplier, 4),
    }

    return total_payout_multiplier, details


# ─── SIMULATION ─────────────────────────────────────────────────────

def run_simulation(num_samples=2_000_000):
    """
    Run Monte Carlo simulation to generate outcome distribution.
    Returns a dict mapping payout_multiplier -> (count, example_details).
    """
    print(f"Running simulation with {num_samples:,} spins...")
    start = time.time()

    # Track outcomes bucketed by payout (rounded to 2 decimal places)
    outcome_buckets = defaultdict(lambda: {"count": 0, "examples": []})
    total_payout = 0

    for i in range(num_samples):
        # Random stop positions for each reel
        stops = [random.randint(0, STOPS_PER_REEL - 1) for _ in range(NUM_REELS)]
        payout, details = evaluate_spin(stops)

        # Round payout for bucketing
        payout_key = round(payout, 2)
        outcome_buckets[payout_key]["count"] += 1

        # Store a few example grids per bucket (for frontend testing)
        if len(outcome_buckets[payout_key]["examples"]) < 3:
            outcome_buckets[payout_key]["examples"].append({
                "stops": stops,
                "grid": details["grid"],
                "winning_lines": details["winning_lines"],
                "scatter_count": details["scatter_count"],
            })

        total_payout += payout

        if (i + 1) % 500_000 == 0:
            elapsed = time.time() - start
            print(f"  {i+1:>10,} spins | RTP so far: {total_payout/(i+1)*100:.2f}% | {elapsed:.1f}s")

    elapsed = time.time() - start
    actual_rtp = total_payout / num_samples

    print(f"\n{'='*60}")
    print(f"Simulation Complete")
    print(f"{'='*60}")
    print(f"  Total spins:    {num_samples:,}")
    print(f"  Time:           {elapsed:.1f}s")
    print(f"  Actual RTP:     {actual_rtp*100:.4f}%")
    print(f"  Target RTP:     {TARGET_RTP*100:.2f}%")
    print(f"  Unique payouts: {len(outcome_buckets)}")
    print(f"  Hit rate:       {(1 - outcome_buckets[0.0]['count']/num_samples)*100:.2f}%")
    print(f"{'='*60}\n")

    return outcome_buckets, actual_rtp


# ─── FREE SPINS SIMULATION ─────────────────────────────────────────

def simulate_free_spins_mode(num_sessions=500_000):
    """
    Simulate free spins sessions to get average payout distribution.
    Free spins use the same reels but with a multiplier on all wins.
    """
    print(f"Simulating free spins mode ({num_sessions:,} sessions)...")
    start = time.time()

    fs_outcomes = defaultdict(lambda: {"count": 0, "examples": []})

    for session in range(num_sessions):
        # Determine number of free spins (weighted by trigger frequency)
        # For simplicity, use 10 spins as the most common trigger
        num_fs = random.choices(
            [10, 15, 25],
            weights=[0.85, 0.12, 0.03],
            k=1
        )[0]

        session_payout = 0
        session_grids = []

        for spin in range(num_fs):
            stops = [random.randint(0, STOPS_PER_REEL - 1) for _ in range(NUM_REELS)]
            payout, details = evaluate_spin(stops)
            # Apply free spins multiplier (but not to scatter wins within FS)
            line_payout = sum(w["payout"] for w in details["winning_lines"]) / len(PAYLINES)
            boosted = line_payout * FREE_SPINS_MULTIPLIER
            session_payout += boosted
            session_grids.append(details["grid"])

        payout_key = round(session_payout, 2)
        fs_outcomes[payout_key]["count"] += 1
        if len(fs_outcomes[payout_key]["examples"]) < 2:
            fs_outcomes[payout_key]["examples"].append({
                "num_spins": num_fs,
                "grids": session_grids[:3],  # Store first 3 grids as preview
            })

    elapsed = time.time() - start
    avg_payout = sum(p * d["count"] for p, d in fs_outcomes.items()) / num_sessions

    print(f"  Free spins avg payout: {avg_payout:.2f}x")
    print(f"  Time: {elapsed:.1f}s\n")

    return fs_outcomes


# ─── EXPORT TO STAKE ENGINE FORMAT ─────────────────────────────────

def export_base_game_csv(outcome_buckets, total_samples):
    """
    Export base game outcomes to CSV in Stake Engine format.
    Format: simulation_number, probability, payout_multiplier
    """
    filepath = os.path.join(OUTPUT_DIR, "base_game.csv")

    # Sort by payout
    sorted_outcomes = sorted(outcome_buckets.items(), key=lambda x: x[0])

    sim_number = 0
    rows = []

    for payout, data in sorted_outcomes:
        probability = data["count"] / total_samples
        rows.append({
            "simulation_number": sim_number,
            "probability": round(probability, 10),
            "payout_multiplier": payout,
        })
        sim_number += 1

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["simulation_number", "probability", "payout_multiplier"])
        writer.writeheader()
        writer.writerows(rows)

    # Also create compressed version
    with open(filepath, "rb") as f_in:
        with gzip.open(filepath + ".gz", "wb") as f_out:
            f_out.write(f_in.read())

    print(f"Exported {len(rows)} base game outcomes to {filepath}")
    return filepath


def export_free_spins_csv(fs_outcomes, total_sessions):
    """
    Export free spins outcomes to CSV.
    """
    filepath = os.path.join(OUTPUT_DIR, "free_spins.csv")

    sorted_outcomes = sorted(fs_outcomes.items(), key=lambda x: x[0])

    sim_number = 0
    rows = []

    for payout, data in sorted_outcomes:
        probability = data["count"] / total_sessions
        rows.append({
            "simulation_number": sim_number,
            "probability": round(probability, 10),
            "payout_multiplier": payout,
        })
        sim_number += 1

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["simulation_number", "probability", "payout_multiplier"])
        writer.writeheader()
        writer.writerows(rows)

    with open(filepath, "rb") as f_in:
        with gzip.open(filepath + ".gz", "wb") as f_out:
            f_out.write(f_in.read())

    print(f"Exported {len(rows)} free spins outcomes to {filepath}")
    return filepath


def export_game_events(outcome_buckets, mode="base"):
    """
    Export detailed game events (grids, winning lines) as JSON.
    These are the actual game-round data returned by the /play API.
    """
    filepath = os.path.join(OUTPUT_DIR, f"{mode}_game_events.json")

    events = {}
    sim_number = 0

    for payout, data in sorted(outcome_buckets.items(), key=lambda x: x[0]):
        # Use the first example for this payout bucket
        if data["examples"]:
            example = data["examples"][0]
            events[str(sim_number)] = {
                "payout_multiplier": payout,
                "grid": example.get("grid", []),
                "winning_lines": example.get("winning_lines", []),
                "scatter_count": example.get("scatter_count", 0),
            }
        sim_number += 1

    with open(filepath, "w") as f:
        json.dump(events, f, indent=2)

    # Compressed version
    with open(filepath, "rb") as f_in:
        with gzip.open(filepath + ".gz", "wb") as f_out:
            f_out.write(f_in.read())

    print(f"Exported {len(events)} game events to {filepath}")
    return filepath


def export_game_config():
    """
    Export game configuration for the frontend.
    """
    filepath = os.path.join(OUTPUT_DIR, "game_config.json")

    config = {
        "game_name": "Jewel Rush",
        "num_reels": NUM_REELS,
        "num_rows": NUM_ROWS,
        "num_paylines": len(PAYLINES),
        "symbols": {k: {"name": v["name"], "tier": v["tier"]} for k, v in SYMBOLS.items()},
        "paylines": PAYLINES,
        "paytable": PAYTABLE,
        "scatter_pays": {str(k): v for k, v in SCATTER_PAYS.items()},
        "free_spins_trigger": {str(k): v for k, v in FREE_SPINS_TRIGGER.items()},
        "free_spins_multiplier": FREE_SPINS_MULTIPLIER,
        "target_rtp": TARGET_RTP,
    }

    with open(filepath, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Exported game config to {filepath}")
    return filepath


# ─── MAIN ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════╗")
    print("║        JEWEL RUSH - Slot Game Generator         ║")
    print("║        Stake Engine Outcome Builder              ║")
    print("╚══════════════════════════════════════════════════╝\n")

    # Phase 1: Simulate base game
    NUM_BASE_SAMPLES = 2_000_000
    base_outcomes, base_rtp = run_simulation(NUM_BASE_SAMPLES)

    # Phase 2: Simulate free spins
    NUM_FS_SESSIONS = 500_000
    fs_outcomes = simulate_free_spins_mode(NUM_FS_SESSIONS)

    # Phase 3: Export everything
    print("Exporting files for Stake Engine...\n")
    export_base_game_csv(base_outcomes, NUM_BASE_SAMPLES)
    export_free_spins_csv(fs_outcomes, NUM_FS_SESSIONS)
    export_game_events(base_outcomes, "base")
    export_game_config()

    # Summary
    print(f"\n{'='*60}")
    print("All files exported to: ./output/")
    print("Files:")
    for f in os.listdir(OUTPUT_DIR):
        size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
        print(f"  {f:40s} {size:>10,} bytes")
    print(f"{'='*60}")
