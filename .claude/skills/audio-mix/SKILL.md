---
name: audio-mix
description: Mix rules for shorts-studio narration, SFX and music - hierarchy, narration pre-normalization to -16 LUFS, two-pass linear loudnorm to -14 LUFS, ducking targets, SFX levels, the fixed chalk SFX gain, licensed sound sources with licenses.csv, and the audio QA thresholds. Use when changing step_audio/step_render mixing, adding SFX or music, or reviewing an audio QA result.
---

# Audio mix

Sources: `docs/VIDEO_QUALITY_UPGRADE_PLAN.md` §4, `docs/TOOLS_AND_SKILLS_RESEARCH.md` §3, `docs/WORKFLOW_AUDIT.md` §19.2. Any audible change to the approved sound is an OWNER decision with a listening A/B; level-accuracy fixes with no audible change are SAFE.

## Hierarchy
1. **Narration** is always intelligible and is the loudness anchor.
2. **SFX** are synced to visual events and placed between narration phrases where possible.
3. **Music** is a bed under speech and swells only in gaps.

## Targets
| Element | Target |
|---|---|
| Narration stem | normalized to −16 LUFS before mixing, so the bed behaves the same for Kokoro and Maya 2 Malini and across languages |
| Music under speech | −18 to −22 dB below narration |
| Music in gaps | rises 4–6 dB via the ducker release |
| SFX one-shots | peak 3–6 dB under narration peaks |
| Chalk SFX | `chalk.CHALK_SFX_GAIN = 0.035`, fixed by the owner. Never change it |
| `music_gain` | 0.25 baseline; shape with ducking, not a lower global gain |
| Planned silences | 2–3 per episode, 0.3–0.8 s (before the Turn, before the Payoff, optionally before Next) |
| Final | integrated −14 LUFS, true peak −1.5 dBTP filter target; QA ceiling −1.0 dBTP |

No platform publishes an official Shorts or Reels loudness spec; −14 LUFS / −1 dBTP is a convention, and YouTube only turns loud uploads down.

## Chain (target order)
1. **Narration normalization** to −16 LUFS at the end of the voice concat in `step_audio` (pyloudnorm, MIT, or an ffmpeg `loudnorm` measurement plus a linear gain).
2. **Voice polish, optional, by ear only:** `highpass=f=70`, gentle `deesser` (or `adynamicequalizer` at 6–8 kHz), `acompressor=threshold=-20dB:ratio=3:attack=5:release=80`. TTS is already compressed; over-processing Indic sibilants is the main risk.
3. **Ducking:** keep the numpy envelope ducker, or `[music][voice]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300`. Tune to −18 to −22 dB under speech. The current constant is quoted as 0.45 (VQ) and 0.65 (TL): read `studio.py` step_audio before retuning.
4. **SFX bus** summed as today; chalk gain untouched.
5. **Two-pass linear loudnorm** replacing the single dynamic pass in the encode:
   - Pass 1 on `mix.wav`: `loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json`.
   - Pass 2: feed back `measured_I`, `measured_TP`, `measured_LRA`, `measured_thresh` and `offset` with `linear=true`. One gain, no pumping.
6. **QA** (below).

Baseline before the change (WORKFLOW_AUDIT §1): finals at −15.2 to −14.7 LUFS, TP −1.5 to −1.4, LRA 1.9–2.8.

## SFX sync
- Cue SFX on the visual frame of the event; use `word` + `offset` only when the narration names the sound (C0005's arrow uses −0.35 s).
- An impact always lands on a cut; at most about 4 hits per episode.
- Ambience beds fade in over 0.5 s and change at every erase (change of place).
- Opening: impact plus chalk snap at 0.0 s, tanpura starts with the hit, first word at 0.2–0.3 s.

## Licensed sources only
| Source | Terms | Rule |
|---|---|---|
| Procedural (`chalk.music`, `chalk.sound`) | own code | default; no Content ID risk |
| Sonniss GDC 2026 bundle | royalty-free, commercial, monetized YouTube allowed; no redistribution as SFX; **no AI/ML training** | keep outside git; never feed into any model |
| Freesound | per file | **CC0 only** (`license:"Creative Commons 0"`); CC-BY-NC and Sampling+ are forbidden for a monetized channel; audition every file |
| YouTube Audio Library | copyright-safe on YouTube only | never on Instagram Reels |
| Avoid | Pixabay music, BBC SFX, Incompetech, FMA, Demucs output, MusicGen/AudioGen, AudioLDM2, Tango, MMAudio | — |

**`licenses.csv` is mandatory**, kept with the gitignored sound folder: one row per file used (file, source URL, licence). A file without a row is not used. Shehnai has no CC0 supply. Any Content ID claim blocks a Short over 1 minute globally, which is one more reason to stay under 60 s.

## QA thresholds
| Check | Pass | Effect |
|---|---|---|
| Integrated loudness | −14 ±0.5 LUFS after two-pass (QA band today −16.5 to −13) | fail outside the band |
| True peak | ≤ −1.0 dBTP | fail |
| Music under speech | speech-band level minus bed ≥12 dB | warn below 12 dB |
| Speaker consistency | one voice throughout (`speaker_consistency`) | fail |
| Silence gaps | only the planned 0.3–0.8 s pauses | warn otherwise |

Test a mix change by re-encoding an existing final into a scratch directory and comparing `ebur128` I/TP/LRA against the baseline; never touch a published episode's files.
