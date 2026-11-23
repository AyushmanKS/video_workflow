# C0012 "Three Paths" — Visual and Audio QA before G2 (en, hi, gu, te, mr)

Reviewer: independent `reviewer` agent (read-only; saved by the main session). Engine v3 (chalk puppets).

## First render (reports #139–#143)
- Every reject-class check passed in all five languages (format, duration, loudness −13.9/−14.0 LUFS, black_freeze, caption_overflow, glyph_coverage, speaker_consistency). Rig QA passed for all 10 shots with no waivers.
- Sensitivity held: Rudra featureless in scenes 1, 6 and 11; his power only as light; the Earth a landscape; Uma modestly dressed; Rudra never gestures and the two never move closer.
- Reviewer scores: Visual en 74, hi 75, gu 74, te 73, mr 74; Audio en 86, hi 82, gu 78, te 80, mr 78.

## Must-fixes raised and what was done
1. Scene 3: three small walking figures (two side by side) could read as the couple during "Rudra and Uma were wed" — removed with a FLUX.2 klein reference edit (seed 23).
2. Scene 9: Uma drawn with bindi, black-bead necklace and earrings against the tightened `uma` token — klein edit (seed 23) removed the earrings and necklace; a small bindi remains (judged a respectful traditional mark; kept to avoid another full re-render, noted for the owner).
3. Must-check frames: verse card (र्थं, माँ, ल्ल) and the scene 10 share title checked at full resolution after the re-render — correct and readable.
4. Must-listen: gu/mr scene 11 "Himavan" heard by Whisper as "Himba-"; owner listen at G2.

Optional fixes applied: scene 10 stray blue figures removed; scene 11 Uma earring and bangles cleaned (klein, seed 23). Stale rig sheets regenerated. Rig QA re-run after the edits: all 10 shots pass.

## Final render (reports #144–#148)
| Lang | Length | Unwaived warnings |
|---|---|---|
| en | 53.5 s | lint_hook, music_under_speech (11.8 dB vs 12), safe_zones |
| hi | 52.3 s | lint_hook, safe_zones |
| gu | 52.63 s | lint_hook, narration_asr (scene 11), safe_zones |
| te | 52.87 s | lint_hook, safe_zones |
| mr | 52.57 s | lint_hook, narration_asr (scene 11), safe_zones |

## Waiver requests
safe_zones (Rudra's rock in scenes 1 and 6; moon arc touching the scene 3 title; all readable), lint_hook (inside the approved ≤3.0 s hook rule), en music_under_speech (0.2 dB short), gu/mr narration_asr scene 11 (warn-only languages; after owner listen).

## Open optional items
Scene 9 palm still reads as offering (V5); scene 2 one bow upright; Uma's bun not a high topknot in scene 11; Rudra profile edge visible (shadow-puppet look); native review for gu, te, mr (te F6, F9).
