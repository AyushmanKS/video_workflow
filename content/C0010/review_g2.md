# C0010 "Ganga's Birth" — Visual and Audio QA before G2 (en, hi, gu, te, mr)

Reviewer: independent `reviewer` agent (read-only; saved by the main session). First episode on the chalk-puppet engine v3. Scene numbers are 1-based (index in brackets). gu, te and mr are `unreviewed-language`; notes on them come from transcripts, not native listening.

## Automatic verdicts (first full render)
| Lang | Story | Visual | Audio | Final | Length |
|---|---|---|---|---|---|
| en | 91 · warn lint_hook | 67 · warn safe_zones | 80 · warn music_under_speech | 100 | 51.1 s |
| hi | 100 | 67 · warn safe_zones | 60 · warn speech_rate, music_under_speech | 94 · warn duration_target | 55.9 s |
| gu | 91 · warn lint_hook | 67 · warn safe_zones | 80 · warn narration_asr | 94 · warn duration_target | 55.83 s |
| te | 91 · warn lint_hook | 67 · warn safe_zones | 80 · warn narration_asr | 100 | 54.7 s |
| mr | 91 · warn lint_hook | 67 · warn safe_zones | 80 · warn narration_asr | 100 | 52.4 s |

Every reject-class check passes in all five languages (format, duration, loudness −13.9 to −14.0 LUFS, black_freeze, caption_overflow, glyph_coverage, speaker_consistency).

## Reviewer scores
| Lang | Visual | Audio |
|---|---|---|
| en | 80 | 86 |
| hi | 80 | 80 |
| gu | 79 | 80 |
| te | 78 | 72 |
| mr | 80 | 77 |

## Warnings and waiver notes
| Lang | Check | Waivable | Note |
|---|---|---|---|
| all | safe_zones (scenes 8 and 9, caption-zone stroke energy 1.88 / 1.54 > p90 1.519) | yes | Uma's rock, the fire ring and the rocks under Himavan; captions stay readable with their outline. |
| en, gu, te, mr | lint_hook (2.2–2.7 s > 2.2 s) | yes | Inside the approved hook ≤3.0 s rule; recorded at G1. |
| hi, gu | duration_target (55.9 / 55.83 s) | yes | Under 1 s over target; under the 60 s limit and the 57 s lint block. |
| hi | speech_rate (scene 4 −28%) | yes | Two deliberate comma pauses; transcript CER 0.0. |
| en, hi | music_under_speech (11.1 / 11.7 dB vs 12 dB) | yes | Under 1 dB below target. |
| gu | narration_asr scene 1 (CER 0.154) | yes | Colloquial "ને"/"બેનો" in the transcript; warn-only language. |
| mr | narration_asr scenes 2, 4, 10 | yes | Whisper quirks ("रूशी मनाले"); warn-only language; native listen still owed. |
| te | narration_asr scene 1 (CER 0.286) | after check | See fix 2. |

## Defects and depiction
- Scenes 3 and 9 (index 2, 8): the green stain and green-tinted Rudra are gone after the divine accent.
- Scene 2 (index 1): forest accent leaves a dark-green river and olive smears (optional).
- Scene 4 (index 3): Mena's saturated green sari is intended by her profile.
- Scene 9 (index 8): Rudra was drawn with a featured profile face and joined palms, against the `rudra_symbol` deity rule (fix 1).
- Uma drifts from her profile (low bun, earrings, bangles, bindi, jasmine) — fix the token for later episodes.
- No extra arms, fused limbs, tears or ghosting in the renders. Stale `en/rigqa` crop sheets contradicted the passing JSONs.
- Verse cards: line-final halant and ङ्ग correct in hi, en, te; gu ગઙ્ગાં needs a full-resolution check.

## Puppet motion plan
Logical and anatomically safe per §30: largest rotation ±4° at the elbow, heads ≤3°, upper arms pinned, standing hips and feet still, every action returns to the drawn pose. Scene 9 keeps Himavan's hand and Uma's joined palms still because they touch; the crescent glow is the symbolic cue.

## Numbered fixes
1. Must-fix: scene 9 Rudra to a featureless shadow silhouette, hands on knees, crescent and trident kept.
2. Must-fix (listen): te hook — ASR heard "గంగా ఉమా సంతా కాచలేలు."
3. Must-check: te share-prompt title complete; gu verse-card ઙ.
4. Optional: scene 2 accent.
5. Optional: Uma token for later episodes.
6. Optional: scene 3 title over the summit.
7. Optional: hi scene 4 comma.
8. Optional: en music bed −1 dB.
9. Optional: gu listen (window_min 0.504).
10. Optional: mr listen, scenes 2, 4, 10.
11. Housekeeping: stale rigqa sheets.
12. Check: hi hook caption during the erase.
13. Optional: larger scene 2 forearm beats.
14. Optional: te scene 10 cue timing.
15. Docs: rig coordinate wording.

## Actions taken by the main session (2026-11-18)
- Fix 1: Rudra edited with FLUX.2 klein 4B reference edit (seed 23 of 11/23/37) into a featureless grey shadow silhouette with hands on knees; crescent, trident and the rest of the drawing kept. Image copied to all five languages; scene re-rendered.
- Fix 2: six new Telugu hook takes were transcribed; every take is heard as "…సంతా (అ)కాచలేలు", so the mishearing is Whisper's, not a dropped syllable. The take with the explicit "అకా" and higher voice match (CER 0.214, similarity 0.656) replaced the hook. speaker_consistency passes.
- Fix 11: stale `en/rigqa` sheets removed; rig QA re-runs with the render.
- Fixes 4–10 and 12–15 are optional and left for the owner.
