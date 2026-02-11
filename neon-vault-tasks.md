# NEON VAULT — Game Build Task List

---

## PHASE 1: Symbol Design (Priority 🔴)

- [ ] **Set up workspace** — Create a 256×256px artboard in Figma/Photoshop, import the template from the asset guide
- [ ] **Design Wild symbol** (wild.png) — Most important. Needs to be instantly recognizable, brightest glow, cyan/magenta colours
- [ ] **Design Scatter symbol** (scatter.png) — Must look distinct from everything else. Yellow/green colours. This triggers the bonus
- [ ] **Design Diamond symbol** (diamond.png) — Premium high-pay. Cyan tones
- [ ] **Design Ruby symbol** (ruby.png) — Premium high-pay. Magenta/red tones
- [ ] **Design Emerald symbol** (emerald.png) — Premium high-pay. Green tones
- [ ] **Design Ace symbol** (ace.png) — Low-pay card. Muted blue-grey, less detail than high-pay
- [ ] **Design King symbol** (king.png) — Low-pay card. Same family as Ace
- [ ] **Design Queen symbol** (queen.png) — Low-pay card
- [ ] **Design Jack symbol** (jack.png) — Low-pay card. Least prominent of all symbols
- [ ] **QA pass** — View all 9 side by side at 140×130px. Check: Wild pops most → High-pay stands out → Low-pay is clearly lower tier
- [ ] **Export all** — 256×256px PNG, transparent backgrounds, into `/assets/` folder

---

## PHASE 2: Background & Branding (Priority 🟡)

- [ ] **Design background** (bg.png) — 1800×1000px. Dark cyberpunk scene. Must not compete with symbols — keep it moody and atmospheric
- [ ] **Design logo** (logo.png) — 800×120px. "NEON VAULT" or your custom game name. PNG with transparency
- [ ] **Export both** to `/assets/` folder

---

## PHASE 3: Bonus Round Assets (Priority 🟢)

- [ ] **Design locked cell** (cell-locked.png) — 240×180px. The encrypted/locked look before a player picks it
- [ ] **Design low-win cell** (cell-low.png) — Cyan tint, subtle
- [ ] **Design mid-win cell** (cell-mid.png) — Green tint, bit more glow
- [ ] **Design high-win cell** (cell-high.png) — Yellow tint, strong glow
- [ ] **Design mega-win cell** (cell-mega.png) — Magenta tint, maximum glow and impact
- [ ] **Export all** to `/assets/` folder

---

## PHASE 4: Integration (I'll handle this)

- [ ] **Wire symbol assets** into the PixiJS game — replace procedural textures with your PNGs
- [ ] **Wire background** — replace programmatic gradient/grid with your bg.png
- [ ] **Wire logo** — replace CSS text title with your logo.png
- [ ] **Wire bonus cells** — replace CSS-styled cells with your custom assets
- [ ] **Test at 1x and 2x resolution** — check sharpness on retina screens
- [ ] **Adjust particle colours** to match your final symbol palette if needed
- [ ] **Tune glow/highlight colours** on payline wins to complement your art

---

## PHASE 5: Polish & Ship

- [ ] **Add sound effects** — spin start, reel stop, win jingle, bonus trigger, bonus pick, mega win fanfare
- [ ] **Add win animations** — symbol-specific animations on winning paylines (bounce, glow pulse, scale)
- [ ] **Playtest 100+ spins** — check visual clarity, bonus frequency feels right, no layout bugs
- [ ] **Re-run math engine** with final config — generate fresh CSV outcome files
- [ ] **Package for Stake Engine** — compress CSVs, bundle static files, prepare for ACP upload
- [ ] **Submit to Stake Engine Admin Control Panel**

---

## File Checklist

| # | File | Size | Status |
|---|------|------|--------|
| 1 | wild.png | 256×256 | ⬜ |
| 2 | scatter.png | 256×256 | ⬜ |
| 3 | diamond.png | 256×256 | ⬜ |
| 4 | ruby.png | 256×256 | ⬜ |
| 5 | emerald.png | 256×256 | ⬜ |
| 6 | ace.png | 256×256 | ⬜ |
| 7 | king.png | 256×256 | ⬜ |
| 8 | queen.png | 256×256 | ⬜ |
| 9 | jack.png | 256×256 | ⬜ |
| 10 | bg.png | 1800×1000 | ⬜ |
| 11 | logo.png | 800×120 | ⬜ |
| 12 | cell-locked.png | 240×180 | ⬜ |
| 13 | cell-low.png | 240×180 | ⬜ |
| 14 | cell-mid.png | 240×180 | ⬜ |
| 15 | cell-high.png | 240×180 | ⬜ |
| 16 | cell-mega.png | 240×180 | ⬜ |
