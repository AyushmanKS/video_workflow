# AK01 "Rama's Crown Was Ready": why the edit feels like stitched clips

Date: 2026-11-17. Scope: the 11 approved clips in `data/anim_lab/AK01/clips/` and the current finals `AK01-{hi,en}.mp4`, as cut by `AK01/scripts/assemble.py`. Read-only on all media.

Evidence:
- Numbers: `data/anim_lab/AK01/analysis/boundaries.json`, with per-shot and per-boundary data for hi and en.
- Script: `data/anim_lab/AK01/analysis/analyze.py`. It is light CPU work with no model and no `heavy.lock`. The audio stems are rebuilt in memory from the `mix()` logic with seed 11, and nothing in the work dirs is written.
- Contact images: `data/anim_lab/AK01/analysis/contacts/B00.png` … `B11.png`. Each shows the last 3 frames of A and the first 3 of B, from the 540p finals, with hi on the top row and en below. A red ring marks A's attention point and a yellow ring marks B's. I looked at all 12.

Units: camera energy is |pan| + 0.5·|zoom|, in frame fractions per second. L* runs from 0 to 100. b* is warmth (+ = yellow). Palette dE is the matched ΔE between k=4 Lab palettes. Eye-trace distance is the distance between attention points as a fraction of the 9:16 diagonal. Unless marked, numbers are hi; en is within a few percent at every boundary.

---

## 1. Root causes (global)

These apply to almost every cut. They explain the "stitched" feeling better than any single boundary does.

1. **Every change lands on the same instant.** `assemble.py` places each cut exactly 0.12 s before the next narration line, at all 10 cuts in both languages. Within about ±0.25 s of that cut:
   - the picture changes;
   - the voice starts a new sentence;
   - a new caption group appears;
   - a title card fades in at +0.15 s (7 of 11 shots);
   - the ambience bed swaps (beds start or end inside ±0.25 s at 9 of 10 cuts: wind→birds, birds→none, none→crowd, crowd→whoosh, …);
   - a new melodic phrase starts 0.18 s before the cut (leitmotif onsets at B02, B04, B07, B08, B09, B10, plus swells at B03, B05, B09).

   There are **zero J-cuts or L-cuts**. Every shot is a sealed package of one sentence, one picture, one sound bed and one motif, so the viewer hears and sees eleven separate clips.
2. **No handles are used; every clip plays from frame 0 to its last frame.** `clip_frame()` always starts at the keyframe and retimes the whole clip to fill the slot (rate 0.77–1.19). `tail_handle_s` = 0 and `head_handle` = 0 for all 11 shots in both languages. The results:
   - each shot opens on its image-to-video keyframe, which is near-still while the motion ramps up;
   - each shot closes on its settled end anchor;
   - the crossfaded shots (7, 8, 9) run out of frames and **freeze for 0.35–0.4 s** under the transition.

   The non-integer rates are rendered by blending adjacent frames, which ghosts motion. Speed also changes from shot to shot: hi s05 and s11 run at 0.77–0.78×, while en s02 runs at 1.19×.
3. **Motion cadence changes between shots.** s01, s06, s08 and s11 move on twos: the frame difference alternates big/small, which is an effective 12 fps cadence. Their `on_twos_index` is 6.1, 4.7, 7.1 and 5.1. s02, s03, s04, s05, s09 and s10 are smooth 24 fps (1.06–1.42). The motion texture flips at B01, B05, B06, B07, B08 and B10.
4. **Camera moves neither match the plan nor chain across cuts.** The shot list asked for one move per shot. Measured on the clips:

   | Shot | Planned | Measured |
   |---|---|---|
   | 1 | push-in | static, with two on-twos bursts |
   | 2 | tilt down | push-in drifting up, accelerating |
   | 3 | pull-back | pull-back ✓ |
   | 4 | static | slight tilt |
   | 5 | push-in | static |
   | 6 | gentle push | pan wobble, then static |
   | 7 | static, then snap push | snap push mid-clip ✓, then 2 s static |
   | 8 | slow push | pan burst, then static |
   | 9 | very slow push | push ✓ |
   | 10 | crane up | accelerating push-in |
   | 11 | push to her back | static |

   At 9 of 10 cuts at least one side is static, so there is no direction to carry. Only B10 has motion on both sides, and there the speed drops from 0.049/s to 0.007/s.
5. **Light and time of day jump around.** The Kanda doc (§3.2, Phase 2) asks for "golden afternoon to lamp-light". The edit goes: day → day → hall darkening (s03 L* −40 inside the shot) → rainy day → lamp-lit courtyard → sunny terrace → self-fade to murk → **night** → **bright day** → **night** → **golden afternoon** ("lamps for the night" is spoken over it) → bright midday terrace. Three of the four worst cuts are light cuts.
6. **Transitions are all the same kind.** There are eight hard cuts, then 0.35 dip, 0.4 cross and 0.35 cross, all bunched at shots 8–10. The dissolves are too short to read as time passing and too long to read as cuts. Every one blends against a frozen frame (see 2).
7. **The rhythm is metronomic.** Shot lengths are 3.4–6.5 s (hi: mean 4.71, CV 0.17; en: mean 4.27, CV 0.13). This is one shot per sentence, so the picture rhythm is the sentence rhythm.
8. **There is no continuous ambience.** The tanpura is the only layer that runs through. Shots 3, 5 and 6 have no ambience at all: the SFX stem is at −180 dB on both sides of B05. Each bed has a 0.5 s fade-in and a 0.6 s fade-out timed to its own shot.
9. **Screen geography breaks.**
   - Dasharatha jumps from seated to standing in an identical frame (B02).
   - Rama is centre in shot 5, frame-right in shots 6 and 8, then frame-left in shot 9.
   - Shot 5's lamp-lit courtyard contradicts the scripted "soft morning light".

## 2. Boundary by boundary

Severity runs from 1 (fine) to 5 (breaks the sequence).

### B00: chalk bridge → shot 1 (severity 3)
- **What happens.** A static Canny line drawing of frame 0 cross-dissolves into the painting between 0.12 and 0.72 s. L* rises by 48, warmth b* by 24 and palette dE is 40. The impact, bell, wind bed and `dasharatha` motif all start at t=0. The caption is up from frame 0, and the title fades in at 0.35 s, in the middle of the dissolve.
- **Why it feels disconnected.** The chalk never draws, so the bridge reads as a filter crossfade rather than "chalk comes alive". All the sound fires on the chalk frame, not on the moment the colour arrives. The painting under the dissolve is the clip's still keyframe; s01 shows no camera motion in its first 0.5 s.
- **Fix:** light transition. Reveal the chalk strokes over about 0.4 s, then flood the paint and land the impact and bell on the flood. Extend the handle so the meteor or banner motion is already running when the colour lands.

### B01: shot 1 → shot 2 (severity 2)
- **What happens.**
  - Shot 1 ends on a still back view of the king at the window: still for the last 43% of frames in hi and 71% in en, because s01 moves only in two short bursts.
  - Shot 2 opens on a frontal throne WS with a slow push. ΔL* is −3.6, Δb* +8 and palette dE 15, so the light is close.
  - The eye trace is 0.18: from his shoulder (0.43, 0.43) to his chest (0.55, 0.62).
  - The wind bed ends at +0.19 s and the birds start at +0.02 s.
  - In en, the hook line ends 0.71 s before the cut, so dead air sits on a frozen frame.
  - The "Ayodhya Kanda" title is still fading out at the cut.
- **Why.** The cut goes from dead stop to slow start with an ambience swap on the cut. Otherwise this boundary is acceptable.
- **Fix:** J-cut the hall ambience and birds 0.5 s under shot 1, and extend the handle by trimming the still tail of s01 (from clip frame ~82) so the cut lands on the second motion burst.

### B02: shot 2 → shot 3 (severity 4)
- **What happens.**
  - It is a WS → WS with the same king, the same white parasol and the same frontal axis.
  - The king is **seated in A and standing with open arms in B**. Contact B02 shows a near-identical layout in which the king teleports.
  - Camera: A ends on an accelerating push-in (zoom +0.029/s in the final, +0.045/s in the clip tail). B starts with a pull-back (−0.015/s), so the zoom reverses.
  - The halls differ: B has a lapis sky window and seated kings.
  - Light: ΔL* −8, palette dE 10, histogram correlation 0.96. The colour matches, which makes the jump more obvious.
  - Audio: the `ayodhya` motif starts at −0.18 s and the birds end at +0.14 s. Shot 3 has no ambience at all, even though the script calls for a murmur bed.
- **Why.** It is a classic jump cut (it breaks the 30° rule) plus a direction reversal of the camera.
- **Fix:** regenerate s03 from a clearly different angle. The script asks for a low angle from the assembly; use it with seated kings in the foreground. Or cut on action: s03 starts with the king rising from the throne. Or insert a connecting shot of the assembly reacting. If s02 is kept, cut it before its push accelerates.

### B03: shot 3 → shot 4 (severity 3)
- **What happens.**
  - Shot 3 darkens inside its own tail: clip L* goes from 51 to 37, a −40 drift on the gray mean.
  - The cut goes from that darkest interior to the brightest exterior so far: rainy daylight city with peacocks, ΔL* +31, Δb* +12, palette dE 35 (the largest inner palette jump), histogram correlation 0.52.
  - The attention point moves only 0.09, which is fine.
  - The crowd ("army") bed starts at −0.08 s and the swell at +0.12 s. Before the cut, the SFX stem is at −85 dB, effectively silent.
- **Why.** An unmotivated dark → bright location jump into a simile insert. The roar the narration describes starts only with the picture, so nothing in the hall causes the cut.
- **Fix:**
  - J-cut the roar and thunder 0.6–0.8 s under the end of shot 3, so the hall erupts and then we see the peacocks.
  - Trim s03 before its darkening.
  - Optionally use a match cut from the parasol dome to the shikhara dome, which sit at similar screen positions, or a short light-flash transition.

### B04: shot 4 → shot 5 (severity 3)
- **What happens.**
  - A ends with a slight tilt over the rainy exterior. B is a frontal Rama MCU that is **static**: 50% still frames, with clip camera energy of 0.001 in its first and middle 0.5 s.
  - The light changes: ΔL* −19.5, Δb* −6.6, rain daylight → glowing lamp-lit interior.
  - The eye trace is 0.17 (peacock heads → Rama's chest and face).
  - s05 carries the clip's luminance pulses (raw L drops from 125 to 37 at frames 0–8 and 72–90). After `deflicker()`, the final still shows a 160 → 108 → 112 wobble over the first 8 frames and a 105 → 122 wobble at the tail (`lum_flicker_frames` 1–4, 71–74).
  - Audio: the whoosh lands at −0.13 s and the `rama` motif at −0.18 s, while the crowd bed fades out across the cut (+0.34 s).
- **Why.** The scene moves into a frozen poster: Rama's planned head turn and eye-lowering are absent, and residual flicker at the head adds to it. The time of day also contradicts shot 4.
- **Fix:** regenerate s05 with motion from frame 0 (head turn, shawl lifting) and the scripted morning light. Or extend the handle by starting later in the clip, past the flicker frames. The whoosh is already a J-cut, so keep it.

### B05: shot 5 → shot 6 (severity 2)
- **What happens.**
  - Rama's face moves from frame centre (0.46, 0.46) to frame right (0.62, 0.45), and from MCU frontal to a profile two-shot.
  - The setting changes from lamp-lit courtyard to a sunlit terrace with the parasol: ΔL* +10, saturation −0.13.
  - B starts with a jerky on-twos pan (frame differences alternate 0.5/5–12).
  - No ambience on either side (SFX at −180 dB). Only a swell at +0.12 s.
- **Why.** The subject jumps sides with no action to carry it, and the location and light change. The cadence changes from smooth to 12 fps.
- **Fix:** a match cut on Rama, with s06 composed so his face sits where it was in s05. Or cut on the action of the bow or embrace starting. Run one palace ambience bed through B04–B06.

### B06: shot 6 → shot 7, the Turn (severity 4)
- **What happens.**
  - **s06 fades itself to dark.** Final-frame luminance falls linearly from 128 to 32 over about 1.9 s (clip frames 56–96, L* 62 → 21). The embrace, the emotional peak, plays as a murky half-fade under the "Pushya" title, and the 0.5 s pause sits on that murk.
  - Then a hard cut **up** to a lamp-lit indigo night CU at L* about 30–37 (ΔL* +17, palette dE 30, histogram correlation 0.39).
  - At the cut, the music drop starts at −0.33 s, wind starts at −0.18 s and heartbeat at +0.02 s.
  - The eye trace is 0.21, the largest inner jump: from Rama's ear at frame right to the king's chest at centre.
- **Why.** It looks like a broken dissolve: a fade that does not reach black, followed by a hard cut that brightens. The Turn needs the darkness to be a choice. The golden embrace is never seen clearly at the end.
- **Fix:** regenerate s06 without the fade, or use only clip frames up to about 55. Make a deliberate dip to black that holds through the 0.5 s silence, then fade up on the lamp flame. Or use a light transition: the lamp flame blooms and the frame goes dark around it. L-cut the heartbeat 0.5 s earlier, under the embrace.

### B07: shot 7 → shot 8 (severity 5, worst)
- **What happens.**
  - A's snap push happens mid-clip, then about 2 s static. In the edit, the last frame is **frozen for 0.35 s** into the dip: rate 0.84, used 4.0 of 4.0 s, `freeze_hold_s` 0.35.
  - The dip to black lasts 0.35 s.
  - B is a **bright daytime** two-shot by a window: ΔL* +16, **Δb* +23**, histogram correlation 0.34 (the lowest of any inner cut).
  - B opens with the biggest camera-energy jump in the film. Final energy goes from 0.003 to 0.108/s: a push-in plus pan right in an on-twos burst (clip frames 10–55, frame differences up to 31).
  - The verse overlay (+0.3 s), the caption and the `kaikeyi` motif (−0.18 s) all land in the same 0.4 s. The wind bed ends at +0.14 s.
  - Shot 9 then says "That night", so the time order on screen is **night → day → night**.
- **Why.** The time of day contradicts the narration, the dip comes from a freeze, and the incoming shot starts at full energy. The calmest shot (eyes wide, frozen) cuts to the most violent motion.
- **Fix:** regenerate s08 as a lamp-lit night interior that continues shot 7's chamber; the window can show a dark road under a pale moon. Extend the handle so A is still moving into the dip, and start B after its first motion burst, or regenerate it with the scripted slow push. Stagger the verse overlay at least 0.6 s after the cut.

### B08: shot 8 → shot 9 (severity 3)
- **What happens.**
  - A's last 0.5 s is 93% still and **frozen for 0.4 s** under a 0.4 s crossfade (`freeze_hold_s` 0.4).
  - The crossfade goes into the night shrine with a slow push: ΔL* −20, Δb* −11, palette dE 21.
  - **Rama switches from frame right in s08 to frame left in s09.**
  - Audio: heartbeat ends at +0.04 s; fire bed (−0.18 s) and `sages` motif plus bell start together.
- **Why.** A 0.4 s mix from a frozen frame reads as a soft glitch, not "that night". The screen sides flip.
- **Fix:** a proper time dissolve of 0.8–1.2 s on live frames (extend the handle). J-cut the fire crackle under the end of shot 8. Regenerate or mirror s09 so Rama stays frame right.

### B09: shot 9 → shot 10 (severity 3)
- **What happens.**
  - A ends with a steady push; A's last frame freezes 0.35 s under a 0.35 s crossfade.
  - B is a golden-afternoon city, **brighter and warmer** than the night shrine: ΔL* +24, Δb* +29 (the largest warmth jump), saturation +0.24, palette dE 33. Yet the narration says "lamps for the night", and s09 is "that night".
  - Within 0.3 s, five sound events start: the conch at −0.23 s, the nagada at −0.18 s, the `ayodhya` motif at −0.18 s and the swell at +0.12 s; the fire bed also ends at +0.24 s. The title "Who was away that day?" fades in at +0.15 s, during the crossfade.
- **Why.** The time of day goes backwards, and the whole celebration layer switches on like a light.
- **Fix:** regenerate s10 at dusk with lamp-trees being lit, to match the text (2.6.18) and the phase rule. Or use a match cut from the sacred fire to a lamp-tree flame at the same screen position. J-cut the nagada 1 s under the shrine, softly, as if from the city outside.

### B10: shot 10 → shot 11 (severity 4)
- **What happens.**
  - A's push-in **accelerates to its fastest at the cut**: zoom 0.085/s in the clip tail and 0.084/s in the final, energy 0.049. That is the fastest steady move in the film.
  - B is 57% still: a three-quarter back view of Manthara.
  - Grade: Δb* −17, saturation −0.24, palette dE 20. Hazy saturated gold becomes pale and white.
  - Attention moves from right-middle (0.67, 0.55) to her head at upper left. The eye trace is 0.18 measured, and larger visually: her head is at about (0.25, 0.15).
  - The nagada ends at +0.12 s, the wind at −0.08 s and the `unresolved` motif at −0.18 s.
- **Why.** The push-in stops dead, and the grade drops into a different light world. This is the payoff shot, and the momentum dies on it.
- **Fix:** cut on action. Ease s10's push out, or cut it before the acceleration (using the rate), and give s11 its scripted slow push to her back (regenerate, or add a digital push in assembly). Grade s11 warmer so the same city light carries. L-cut the nagada for about 1 s under s11, fading as if heard from below.

### B11: shot 11 → end card (severity 3)
- **What happens.**
  - A bright terrace (still for half of the last 0.5 s) hard-cuts to a near-black static card: ΔL* −45, palette dE 38.
  - Music and ambience go from −43/−39 dB to silence at the cut (the music fade-out ends exactly there), leaving only the snap.
  - "Next: Manthara's Whisper" is on screen for the last 1.2 s of s11 **and** again on the card.
- **Why.** The story sound is cut off, and the screen goes from bright to dark with no transition.
- **Fix:** light transition. Drain the painting back into chalk lines, mirroring B00 and closing the frame. L-cut the wind and `unresolved` tail 0.5–0.8 s into the card. Show the title only once.

## 3. Worst three

1. **B07 (7→8).** Night cuts to daylight and back to night. A 0.35 s freeze dips to black, then the film's largest camera-energy jump follows (0.003 → 0.108/s). Histogram correlation is 0.34. Fix: regenerate s08 at night, extend the handle, and stagger the overlays.
2. **B06 (6→7).** The embrace fades itself to murk (luminance 128 → 32 over about 1.9 s) under the title and through the pause, then hard-cuts *up* to the night CU. Fix: regenerate s06 or trim it before the fade, make a real dip or lamp-flame light transition, and L-cut the heartbeat.
3. **B02 (2→3).** A jump cut: same king, parasol and axis, with seated becoming standing. An accelerating push-in reverses into a pull-back. Fix: regenerate s03 from the scripted low angle, cut on him rising, or insert an assembly cutaway.

Close behind: **B10** (a full-speed push-in into a still shot plus a cold grade) and **B03** (−40 L* darkening into a +31 L* exterior with the roar starting on the cut).

## 4. Assembly-level fixes that need no regeneration

These are in order of expected effect.

- **Decouple the cut points from the narration.**
  - Let picture cuts drift −0.4 to +0.6 s from line starts.
  - Run ambience beds across 2–3 shots and J-cut each new bed 0.3–0.8 s before its picture.
  - Start leitmotifs on musical phrase boundaries, not on cuts.
  - Delay title cards to at least 0.5 s after a cut.
- **Choose in and out points instead of playing whole clips.** Skip still heads and tails and unstable frames (s05 frames 1–4; s06 frames 56+). Prefer rate 1.0 or exact 2:1 rates to avoid blended ghost frames. Never freeze under a dissolve.
- **Add a light digital camera in assembly** (eased scale and translate per shot) so that motion carries across cuts. For example, continue a push-in into the next shot, or let an incoming shot that would start static pick up the outgoing direction.
- **Grade toward the phase rule.** Use one continuous warmth and luminance curve: day gold through shots 1–6, lamp-light and night from shot 7 to shot 9, dusk-gold with lamps at shots 10–11. Even before any regeneration, this softens B03, B04, B09 and B10.
- **Vary the transition grammar.** Use hard cuts within a scene, 0.8–1.2 s dissolves for time jumps (B08), a held dip only at the Turn (B06), and a chalk drain at the end (B11).

Regeneration is still needed for B07 (s08 daylight), B06 (s06 self-fade), B02 (s03 angle) and probably B09 (s10 daylight).
