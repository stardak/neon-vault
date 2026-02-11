"""
RTP Tuner
=========
Adjusts reel strip composition to achieve target RTP.
Strategy: Increase high-value symbol frequency and add more wilds.
"""

import random
import sys
from collections import Counter
from slot_config import (
    SYMBOLS, REEL_STRIPS, NUM_REELS, NUM_ROWS, PAYLINES, PAYTABLE,
    SCATTER_PAYS, TARGET_RTP
)

random.seed(42)

def quick_sim(strips, num_spins=500_000):
    """Fast RTP estimation."""
    total_payout = 0
    num_paylines = len(PAYLINES)

    for _ in range(num_spins):
        # Random stops
        grid = []
        for r in range(NUM_REELS):
            stop = random.randint(0, len(strips[r]) - 1)
            col = [
                strips[r][stop % len(strips[r])],
                strips[r][(stop + 1) % len(strips[r])],
                strips[r][(stop + 2) % len(strips[r])],
            ]
            grid.append(col)

        # Evaluate paylines
        line_total = 0
        for payline in PAYLINES:
            syms = [grid[reel][row] for reel, row in enumerate(payline)]
            pay_sym = None
            for s in syms:
                if s == 'S': pay_sym = None; break
                if s != 'W': pay_sym = s; break
            if pay_sym is None and all(s == 'W' or s == 'S' for s in syms):
                if 'S' not in syms: pay_sym = 'W'
            if pay_sym is None: continue

            count = 0
            for s in syms:
                if s == pay_sym or s == 'W': count += 1
                else: break

            if count >= 3 and pay_sym in PAYTABLE and count in PAYTABLE[pay_sym]:
                line_total += PAYTABLE[pay_sym][count]

        total_payout += line_total / num_paylines

        # Scatters
        sc = sum(1 for col in grid for sym in col if sym == 'S')
        total_payout += SCATTER_PAYS.get(sc, 0)

    return total_payout / num_spins


def tune_strips(target_rtp=TARGET_RTP, iterations=50):
    """Iteratively adjust reel strips to approach target RTP."""
    print(f"Target RTP: {target_rtp*100:.2f}%\n")

    # Start with current strips (mutable copy)
    strips = [list(s) for s in REEL_STRIPS]

    current_rtp = quick_sim(strips)
    print(f"Starting RTP: {current_rtp*100:.2f}%")

    all_symbols = ['W', 'H1', 'H2', 'H3', 'L1', 'L2', 'L3', 'L4', 'S']
    high_value = ['W', 'H1', 'H2', 'H3']
    low_value = ['L3', 'L4']

    best_rtp = current_rtp
    best_strips = [list(s) for s in strips]

    for iteration in range(iterations):
        rtp_diff = target_rtp - current_rtp

        if abs(rtp_diff) < 0.005:
            print(f"\n✅ Target achieved at iteration {iteration}!")
            break

        # Strategy: if RTP too low, swap low-value for high-value
        for reel_idx in range(NUM_REELS):
            strip = strips[reel_idx]

            if rtp_diff > 0:
                # Need higher RTP: replace some low symbols with high ones
                swaps = max(1, int(abs(rtp_diff) * 15))
                for _ in range(min(swaps, 3)):
                    # Find a low-value position
                    low_positions = [i for i, s in enumerate(strip) if s in low_value]
                    if low_positions:
                        pos = random.choice(low_positions)
                        # Replace with weighted high-value
                        new_sym = random.choices(
                            high_value,
                            weights=[3, 4, 5, 6],  # More wilds/diamonds
                            k=1
                        )[0]
                        strip[pos] = new_sym
            else:
                # RTP too high: replace some high symbols with low ones
                swaps = max(1, int(abs(rtp_diff) * 10))
                for _ in range(min(swaps, 2)):
                    high_positions = [i for i, s in enumerate(strip) if s in high_value]
                    if high_positions:
                        pos = random.choice(high_positions)
                        strip[pos] = random.choice(low_value)

        current_rtp = quick_sim(strips)

        if abs(current_rtp - target_rtp) < abs(best_rtp - target_rtp):
            best_rtp = current_rtp
            best_strips = [list(s) for s in strips]

        if (iteration + 1) % 5 == 0:
            print(f"  Iteration {iteration+1:3d}: RTP = {current_rtp*100:.2f}%  (best: {best_rtp*100:.2f}%)")

    print(f"\nFinal RTP: {best_rtp*100:.4f}%")
    print(f"\n{'='*60}")
    print("OPTIMIZED REEL STRIPS:")
    print(f"{'='*60}\n")

    for i, strip in enumerate(best_strips):
        counts = Counter(strip)
        print(f"Reel {i+1} ({len(strip)} stops):")
        print(f"  Strip: {strip}")
        print(f"  Counts: {dict(sorted(counts.items()))}")
        print()

    # Print as Python code for easy copy-paste
    print("# Copy this into slot_config.py:")
    print("REEL_STRIPS = [")
    for strip in best_strips:
        print(f"    {strip},")
    print("]")

    return best_strips, best_rtp


if __name__ == "__main__":
    tune_strips()
