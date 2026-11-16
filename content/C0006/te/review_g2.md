# C0006 te — Visual + Audio QA (before G2)
Not native-reviewed (unreviewed-language); the reviewer is not a native Telugu speaker. QA #53 WARN, visual warnings only. Story 77 · Visual 72 · Audio 82.
- speaker_consistency passes (scene_min 0.661). Mix 12.5 dB. narration_asr and speech_rate pass. Length 54.1 s.
- A full listen is still recommended, since there is no native review.

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
