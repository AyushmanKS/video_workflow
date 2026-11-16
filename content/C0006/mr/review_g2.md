# C0006 mr — Visual + Audio QA (before G2)
Not native-reviewed (unreviewed-language, new to the pipeline); the reviewer is not a native Marathi speaker. QA #54 WARN, no rejects. Story 79 · Visual 72 · Audio 62.
- speaker_consistency passes (scene_min 0.666). The mix median is 13.0 dB, but p10 is 1.6 dB, so listen to the swell scenes 1, 6 and 9.
- narration_asr: the same differences repeat across scenes, so they are likely real:
  - म्हणाले/म्हणाली is heard as भणाले/भनाली/मनाले/मणाले in scenes 2, 6, 8, 10 and 11;
  - झ is heard as ज (scenes 1, 2, 4, 6);
  - ळ is heard as ल (सकाळी, scene 2);
  - scene 11 "येणाऱ्या राक्षसांचा" is heard as "येडार्यार आक्षसांचा".
- **Fix:** the owner (or a native speaker) listens at 2.25–7.77, 21.13–26.57, 31.33–37.17, 44.27–48.59 and 48.99–55.31 s. If these are mispronounced, add `tts` respellings, test them in a voicepack, and re-voice those scenes.
- **Profile:** lint estimated 44.5 s against 56.3 s rendered; calibrate the mr duration basis before the next mr script.

**Waivers**
- narration_asr: only after the listen. Note: "Recurring म्हणाले/झ/ळ ASR differences checked by ear at the listed timestamps; CER warn-only for unreviewed mr."
- duration_target: 56.27 s is under the 60 s hard limit and the 57 s lint block; re-check after any re-voice.

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
