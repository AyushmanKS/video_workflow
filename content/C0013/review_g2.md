# C0013 "The Newborn Commander" — Visual and Audio QA before G2 (en, hi, gu, te, mr)

Reviewer: independent `reviewer` agent (read-only; saved by the main session). Ep12, Bala Kanda sarga 37, chalk-puppet engine v3. Scene numbers are 1-based (0-based rig index in brackets). gu, te and mr are `unreviewed-language`; notes on them come from transcripts, not native listening. The reviewer listened to no audio.

## Automatic verdicts (render of 2026-11-24)
| Lang | Story | Visual | Audio | Final | Length |
|---|---|---|---|---|---|
| en | 91 · warn lint_hook (2.7 s) | 33 · warn chalk_density, safe_zones | 80 · warn music_under_speech | 100 | 53.03 s |
| hi | 91 · warn lint_hook (2.8 s) | 33 · warn chalk_density, safe_zones | 60 · warn narration_asr, speech_rate | 100 | 54.70 s |
| gu | 91 · warn lint_hook (2.8 s) | 33 · warn chalk_density, safe_zones | 80 · warn narration_asr | 94 · warn duration_target | 55.27 s |
| te | 91 · warn lint_hook (2.4 s) | 33 · warn chalk_density, safe_zones | 80 · warn speech_rate | 94 · warn duration_target | 56.07 s |
| mr | 91 · warn lint_hook (2.5 s) | 33 · warn chalk_density, safe_zones | 60 · warn narration_asr, speech_rate | 100 | 53.83 s |

Every reject-class check passes in all five languages (format, duration, loudness −14.0/−13.9 LUFS, true peak −1.7 to −2.0 dBFS, black_freeze, caption_overflow, glyph_coverage, speaker_consistency). `text_artifacts` and `character_similarity` did not run (tools not installed). Rig QA passes for every shot with two recorded orphan_fragment waivers.

## Reviewer scores
| Lang | Visual | Audio |
|---|---|---|
| en | 82 | 79 |
| hi | 81 | 81 |
| gu | 79 | 72 |
| te | 79 | 82 |
| mr | 81 | 74 |

## Warnings and waiver notes
| Lang | Check | Waivable | Note |
|---|---|---|---|
| all | chalk_density (scenes 8, 11: 47.6 / 47.4%) | yes | Dense golden reeds are the story beat and the closing loop composition. |
| all | safe_zones title zone (scenes 3, 8, 10) | yes | Scenes 3 and 8 have no title; scene 10's engagement title crosses the anointing light column and stays legible. |
| all | safe_zones caption zone (scene 10) | yes | Rock and reeds under the caption; outline keeps it readable. |
| all | lint_hook (2.4–2.8 s) | yes | Inside the approved ≤3.0 s rule. |
| gu, te | duration_target (55.27 / 56.07 s) | yes | Under 60 s and the 57 s lint block. Lint underestimated gu by 3.3 s and te by 2.75 s: recalibrate before Ep13. |
| en | music_under_speech (median 10.2 dB, p10 −0.4 dB) | yes, fix preferred | Lowering the bed about 2 dB would clear it. |
| hi, te, mr | speech_rate scene 7 (−32 / −31 / −34%) | yes | The six-metal list with comma pauses; it answers the engagement question. |
| hi | narration_asr scene 11 (CER 0.192) | after listen | Heard "कार्ति की एका पावंजन" for "कार्तिकेय का पावन जन्म". |
| gu | narration_asr scene 6 (CER 0.269) | after listen | Heard "જાળા" (net) for "જ્વાળા" (flame); would change the meaning if real. |
| gu | narration_asr scene 11 (CER 0.167) | yes | Nasal and ending quirks. |
| mr | narration_asr scene 3 (CER 0.241) | after listen | "सेनापती येईल" may be clipped. |
| mr | narration_asr scene 11 (CER 0.174) | yes | Same Whisper quirk as Ep10 (रुशी मनाले). |
| en (rig) | orphan_fragment [8], 18 px at t 3.8 | recorded | Halo grain during the 2.5° nod; justified. |
| en (rig) | orphan_fragment [9], 33–48 px ×3 | recorded | Halo glow under the grey-matted drifting cloud; justified. |

## Defects and depiction
- **Child:** exactly one child with one head in every scene; featureless face, two arms, dhoti of light; no spear, peacock or rooster; idealised, not a realistic infant. Scene 10 [9]: the head flame is gone.
- **No human or goddess figures:** the Ganga is a river of light, the Krittikas six star-lights, the Earth roots of metal, Brahma the lotus, Agni the flame, the gods orbs. Rudra and Uma are not drawn. Klein edits are clean ([2] riverbanks empty, [5] no figures by the fires).
- **Hatched faces [0, 8, 9, 10]:** warm textured gold at phone size, a clear improvement over hollow dark ovals; at full size the hatching reads as a fine mesh. Owner to judge full-screen.
- **Scene 10 [9]:** the light column reaches the halo (departs from story-review V2) but reads as anointing light.
- **Scene 6 [5]:** before its cue the blaze shows as a grey smoky smudge (reads as smoke).
- **Scene 4 [3]:** metal seams and a green streak on Kailasa before the metals are born (minor).
- **Scene 8 [7]:** the small child has a topknot, earrings and a shoulder robe, close to Buddha iconography and different from the other scenes; dimmed and small, low impact.
- **Titles:** scene 9 "Kartikeya" title has a star over its last letters during the draw in en, hi, te; scene 10 engagement title spans about 90% of the width and an orb touches the first word in hi, te, mr; scene 11 Next card is correct in all five but sits over the snow peak.
- **Verse card:** source text correct in all five; gu ગઙ્ગા and te గఙ્గా not confirmed at contact-sheet resolution.

## Puppet motion plan
Logical and anatomically safe per §30: the seated child only breathes in the torso; one nod (−2.5° / +2.5°) in [8] that returns to the drawn pose; no limbs move. The light carries the motion: orbs and stars flicker (amp 0–0.6 px), fires at 1.2 px, and cues light the radiance star [3], the blaze [5], the metal seams [6], the child's reveal [7] and the anointing column [9]; left reeds sway in [0]. Known engine limit: the cloud drift in [9] runs for the whole scene. Both waivers are justified.

## Numbered fixes
1. Must-check: scene 10 [9] dimmed beam may read as a dark spire before its cue.
2. Must-listen: gu scene 6 ("જ્વાળા", "હિમવાનના").
3. Must-listen: hi scene 11 ("कार्तिकेय का पावन जन्म").
4. Must-listen: mr scene 3 ("सेनापती येईल"); also "हिमवानाच्या" in scene 6.
5. Should-fix: en music bed about −2 dB.
6. Check: scene 10 engagement title over the beam; orb touching the first word in hi, te, mr.
7. Check: scene 11 Next card over the snow peak.
8. Must-check (V7): gu/te verse-card conjuncts at full resolution.
9. Optional: hatched faces (finer or single-direction hatch); scene 9 [8] face a shade lighter.
10. Optional: match the scene 8 [7] child to the others in later episodes.
11. Optional: remove premature metal seams on Kailasa [3].
12. Optional: move the "Kartikeya" title or the top star in [8].
13. Optional: recalibrate gu/te lint rates before Ep13.
14. Optional: listen to mr scene 7 and hi/mr scene 6 pacing.
15. Housekeeping: stale rigqa crop sheet; remove `hi/audio/*.prev.wav` after G2 (never commit media).
16. Docs: rig coordinate wording (`_doc` vs §30).

## Actions taken by the main session (2026-11-24)
- Fix 1: frames at 43.0, 44.5 and 46.5 s (en) show the beam as a light column throughout; no dark spire. No change.
- Fix 8: full-resolution gu and te verse-card frames checked; ગઙ્ગા, the final ્ and గఙ్గా render cleanly. Closed.
- Fix 7: full-resolution en Next-card frame checked; "NEXT: THE CHILDLESS KING" is readable over the peak. Closed.
- Fixes 2–4: left for the owner's listen at G2 (the main session cannot listen).
- Fix 5: offered to the owner; not applied, because it needs a re-render.
- Metadata: packager wrote publish.json in all five languages; `pipeline promo C0013 --apply` added the cross-promotion lines. Titles 57–61 characters; captions ≤1,131 characters with 5 hashtags.
