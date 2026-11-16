# C0006 hi — Visual + Audio QA (before G2)
QA #55 WARN, no rejects. Story 85 · Visual 72 · Audio 80.
- speaker_consistency passes (window_min 0.557, scene_min 0.618) after regenerating scenes 5 and 9.
- speech_rate: scene 10 (Rama's farewell, 41.55–47.71 s) is 26% slower. The owner should listen; regenerate it if it drags.

**Waivers**
- duration_target: 56.03 s is under the 60 s hard limit and the 57 s lint block; the overrun comes from the slower scene 10 farewell.
- speech_rate: Scene 10 is Rama's farewell after a pause; the slower delivery suits the moment (waive only after the owner listens at 41.55–47.71 s).

## Shared visual findings (same 11 images in every language)
- **Checks passed:** Rama is always shown from behind. Every light figure has two arms, with no crowns or halos. Frame 0 reads muted (the hook image, start_drawn 0.72). Each verse card is in its own script. Captions are legible, and the widest fits within 1020 px.
- **Fix 1 — scene 7 (img 06, take 1):** the hand is malformed (claw-like fingers, gauntlet sleeve) and the light figure's joined palms are missing. Regenerate with chalk line-art wording; reject any photographic take.
- **Fix 2 — scene 11 (img 10):** Vishvamitra drifts (white hair, no topknot, vertical tilak) from scenes 2 and 5 (dark hair, topknot, red tilak). Regenerate to match.
- **Fix 3 — scene 3 (img 02):** the tilt-down pushes the gold discus into the title zone, so the title sits on gold with low contrast. Regenerate with more empty board above the discus.
- **Optional:**
  - scene 3 vajra reads like a trishula;
  - scene 10 figures look blonde, in tunics;
  - scene 9 smoky aura is near a halo;
  - scene 6 has a scribble at lower right;
  - corner board-edge colour on images 00, 01 and 10.
- **Engine behaviour, not a defect:** the hook narration runs about 0.37 s into the scene 1→2 erase.

**Shared waivers**
- chalk_density: Scene 2 (49.9%) is a deliberately dense sunrise forest behind the sage; subjects stay clear and the board stays black elsewhere.
- safe_zones: Scenes 1, 4 and 6 have no title over their top-zone strokes; the scene 2 and 11 titles are legible; the scene 3 overlap is handled by fix 3.
