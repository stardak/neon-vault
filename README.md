# Jewel Rush — Stake Engine Slot Game

A complete 5-reel, 3-row, 20-payline slot game built for Stake Engine.

## Architecture

```
stake-slot-game/
├── math-engine/
│   ├── slot_config.py      # Game configuration (symbols, reels, paytable)
│   ├── simulator.py         # Monte Carlo simulator & CSV exporter
│   └── rtp_tuner.py         # Automated RTP optimization tool
├── frontend/
│   └── jewel-rush.html      # Playable PixiJS slot game
└── output/                   # Stake Engine upload files
    ├── base_game.csv(.gz)    # Base game outcomes
    ├── free_spins.csv(.gz)   # Free spins outcomes
    ├── base_game_events.json(.gz)  # Game round event data
    └── game_config.json      # Game metadata
```

## Quick Start

### 1. Tune the Math
```bash
cd math-engine
python3 rtp_tuner.py          # Optimize reel strips → 96% RTP
# Copy the output reel strips into slot_config.py
python3 simulator.py           # Generate all outcome files
```

### 2. Play the Demo
Open `frontend/jewel-rush.html` in a browser. Spacebar or click SPIN.

### 3. Upload to Stake Engine
Upload the compressed CSV files from `output/` to the Stake Engine Admin Control Panel.

## Game Specs

| Feature | Value |
|---------|-------|
| Reels | 5 |
| Rows | 3 |
| Paylines | 20 |
| Target RTP | 96.0% |
| Symbols | 9 (Wild, Scatter, 3 High, 4 Low) |
| Max Win | 1000x (5 Wilds) |
| Free Spins | 3+ Scatters → 10/15/25 spins @ 3x multiplier |

## Stake Engine CSV Format

Each CSV row: `simulation_number, probability, payout_multiplier`

The RGS selects a simulation number at a frequency proportional to its probability weight, then returns the corresponding game events through the `/play` API.

## Customization

- **Paytable**: Edit `PAYTABLE` in `slot_config.py`
- **Reel composition**: Run `rtp_tuner.py` after changes
- **Volatility**: Increase high-symbol payouts for higher volatility, or spread wins more evenly for lower volatility
- **Theme**: Swap symbol textures in the frontend
