# Editing craft for continuity: a rulebook for automated AI-animated Shorts

Research date: **2026-11-17**. Research and writing only; no project file was changed and no model was run.

Scope: making a 45–55 s, 9:16, narrated, AI-animated story Short (11 LTX-2.3 image-to-video shots of 4–5 s each, as in AK01) feel like one directed and edited sequence rather than stitched clips. Written so the rules can be turned into code in an automated assembler (today `data/anim_lab/AK01/scripts/assemble.py`).

Inputs read: `docs/KANDA_VISUAL_IDENTITIES.md` (Ayodhya "Pahari Gold", the four phases, §3.2 progression rules), `docs/ANIMATION_RESEARCH.md` §7 (AK01 sample), `content/AK01_draft/script.en.md` (shot list), `.claude/skills/audio-mix/SKILL.md`, and the AK01 assembler and timeline JSON.

Evidence labels, as in the other research docs:
- **[S]** stated in a cited source (book, manual or reputable craft publication).
- **[P]** practitioner convention reported by several secondary sources; a starting value, tuned by eye and ear.
- **[H]** our own heuristic for this pipeline, derived from the above; untested here. Every [H] number is a default to calibrate on AK01, not a fact.

---

## 0. Summary in ten rules

1. **Emotion first, then story, then rhythm, then eye-trace, then screen geometry** (Murch's Rule of Six, in priority order). When rules conflict, drop the lower ones first. [S]
2. **Default to the hard cut.** Every other transition must state a reason: time passing, place changing, a mood shift, or a motivated optical event. Dmytryk: never cut without a positive reason. [S]
3. **Cut on motion, not on stillness**: at the motion peak of a gesture or camera move, and never inside a morph or a model "settling" tail. [S] for live action, [H] for the AI-specific part.
4. **Keep the viewer's eye where it already is.** Measure the salient point at the out-frame of A and the in-frame of B; keep them close, or move them on purpose. [S]
5. **Carry sound across every cut.** Narration is continuous, but the music bed, ambience and SFX should lead (J) or trail (L) the picture by 4–24 frames at most boundaries. [S]/[P]
6. **Keep camera energy continuous**: a push-in should not hard-cut into a pull-back at full speed; enter B already moving. [P]/[H]
7. **Transitions soften as grief deepens and sharpen as tension builds**: hard cuts for tension and shock, short dissolves for tenderness and time, dip to black for chapter ends. [P]
8. **Grade the sequence, not the shot**: match neighbouring shots, then let the look drift on purpose across the four phases. [S]/[H]
9. **AI clips: use the middle.** Trim unstable heads and settling tails, and choose in and out points from measured motion coherence. Regenerate when no clean window of the needed length exists. [P]/[H]
10. **Vertical short form: no soft transition in the first 3 s, keep captions and faces in the safe area, and end on a frame that loops into frame 0.** [P]

---

## 1. Foundations (what the classic texts actually say)

### 1.1 Walter Murch, *In the Blink of an Eye* (2nd ed. 2001): the Rule of Six
An ideal cut satisfies, in priority order: **emotion 51%, story 23%, rhythm 10%, eye-trace 7%, two-dimensional plane of the screen 5%, three-dimensional space of action 4%**. If not all can be met, sacrifice from the bottom up. [S: UT Austin RTF wiki; No Film School; Artlist]
- Pipeline meaning: the boundary scorer is **weighted**, not a checklist. A geometry violation (screen side flips) is acceptable if it serves emotion; a mood mismatch never is.
- **Blink as a thought boundary.** Murch cuts "a frame or two before" the actor's blink, because the blink marks a completed thought; a cut placed where the thought completes feels inevitable. His door example: cut when the door's closing becomes inevitable, not before. [S: ProVideo Coalition interview; No Film School; Web of Stories]
- Pipeline meaning: the narration phrase end (a completed thought) and the *inevitability point* of a gesture (about 60–70% of the way through it [H]) are the preferred cut anchors.

### 1.2 Karel Reisz and Gavin Millar, *The Technique of Film Editing* (1953; 2nd ed. 1968)
- A **smooth cut** joins two shots "in such a way that the transition does not create a noticeable jerk", and the most elementary requirement is that the actions of consecutive shots match. Duplicating part of an action looks unnatural; skipping part of one makes a visible jump. [S: Lantern scan of the 1958 printing]
- But "mechanical smoothness is only a secondary factor"; the primary requirement is "a smooth flow of ideas from shot to shot", and a cut that is dramatically useful "will often appear smooth even if the mechanical matching is imperfect". [S]
- Pipeline meaning: our clips are separate generations, so there is no true action across a cut. Continuity comes mostly from **idea flow** (the narration), **eye-trace**, **sound** and **colour**, with action matching as a bonus when two shots share a character.

### 1.3 Edward Dmytryk, *On Film Editing* (1984)
Commonly summarised rules (numbering differs between summaries):
- Never make a cut without a positive reason. [S, secondary]
- When undecided about the exact frame, cut long rather than short. [S, secondary]
- Whenever possible, cut "in movement". [S, secondary]
- The fresh is preferable to the stale. Substance first, then form. [S, secondary]
- A cut should not be made only because the shot feels long; dramatic requirements take precedence over the aesthetics of matching. [S, secondary]
- Pipeline meaning: **do not cut on a fixed grid.** Shot length follows narration phrases and emotion; a long-held shot is fine if the motion inside it is alive. "Cut long" means: on ambiguous scores, prefer the later out-point.

### 1.4 Intensified continuity (David Bordwell, *Film Quarterly* 55:3, 2002)
Contemporary mainstream style is classical continuity "raised to a higher pitch": faster cutting (average shot length falling from 8–11 s in the studio era to 2–4 s, some films 2.7 s), closer framings, more camera movement. [S]
- Pipeline meaning: AK01's 3.5–5.2 s shots are slower than mainstream features but normal for narrated, contemplative short-form story content. Pace comes from **motion inside the shot** and **sound**, not only from cut count. Do not chase 2 s shots: each shot costs 6–10 min of LTX time.

### 1.5 Animation editing practice
- Animation is "edit first, shoot later": the editor builds the **animatic / story reel** (boards plus scratch voice, SFX and music) and locks timing *before* animation is produced; the editor also shapes "the flow of action in between" in and out points. [S: Frame.io blog on animation editing; No Film School / Slate on Pixar editors; Toon Boom Storyboard Pro animatic docs]
- Pipeline meaning: our equivalent is the **timed narration plus keyframes** before any LTX render. The cut, including handles, transition type and where each motion peak should land, should be decided on a keyframe animatic (keyframe stills with simple Ken Burns, voice and music) **before** LTX. Then shots can be generated with the right length, motion direction and end pose, instead of being repaired in the edit.

---

## 2. Technique catalogue

Each entry: **what**, **use when**, **avoid when**, **signals** (what a program can measure), **implementation** (automatic rule with default numbers). Frame counts are at the 30 fps delivery rate unless stated; LTX clips are 24 fps.

### 2.1 Match cuts

**Graphic match** (shape, colour, composition). *What:* the dominant shape, colour mass or layout of A's last frame repeats in B's first frame. *Use:* to link two ideas (AK01: the king's open palm spreading into the peacock's fan; s10's city below into s11's same city below); for a loop ending. *Avoid:* when the shared shape would read as a gimmick in a grave moment, or when no real thematic link exists (graphic matches draw attention to themselves). [S: Boris FX; StudioBinder; Videomaker; Spotlight FX]
- Signals: IoU of the main salient masks (A out-frame vs B in-frame); edge-orientation histogram similarity; dominant-colour ΔE in CIELAB; centroid distance.
- Implement: score = 0.4·mask IoU + 0.3·(1 − centroid distance) + 0.3·colour similarity. If the score is ≥ 0.6 [H], prefer a **hard cut exactly on the matched frames** (no dissolve; a dissolve muddies a graphic match). If 0.4–0.6, a 4–6 frame dissolve can help the shapes "melt".

**Movement match / match on action.** *What:* a motion begun in A completes in B (a hand rises in A, the palm opens in B), or the camera's motion continues across the cut. *Use:* whenever the same character continues an action, or the direction of motion can carry over. *Avoid:* when B's motion runs in the opposite direction at a similar speed (reads as a bounce). [S: Backstage; Videomaker; StudioBinder continuity editing]
- Signals: mean optical-flow vector of the salient region over the last 6 frames of A and the first 6 of B: angle difference and speed ratio.
- Implement: angle difference ≤ 45° and speed ratio 0.6–1.6 [H] → a movement match is available; cut at A's motion peak (§2.2).

**Idea / sound match.** *What:* the link is conceptual or aural: a word in the narration lands on the image it names; a sound in A becomes a different sound in B (the crowd's roar becomes thunder). *Use:* similes and metaphors (AK01 shot 4 is a simile insert by design). *Avoid:* when the matched sound is louder than the narration (audio hierarchy). [S: Boris FX; Webiano; CapCut on carrying one element across the cut]
- Signals: script tags (`simile`, `insert`); SFX cue list; word timestamps from Whisper alignment.
- Implement: the picture cut lands on the onset of the named noun's first syllable minus 2–4 frames [H], so the image arrives with the word.

### 2.2 Action continuity and cut on action
*What:* cut during a movement, so the motion carries the eye through the cut and hides it. [S: Dmytryk; Reisz & Millar; Videomaker "Cutting on Action"]
*Use:* every boundary where A or B contains a gesture or camera move. *Avoid:* cutting at the start of an action (unmotivated) or after it has fully settled (dead frames); cutting during a morph.
- Signals: per-frame motion energy E(t) = mean optical-flow magnitude of the salient region; the gesture's onset, peak and settle times; Murch's "inevitability point".
- Implement:
  - Out-point of A: inside the last third of A's gesture, at or just after the peak of E(t) (peak to peak + 4 frames [H]), and never inside the AI settling tail (§3).
  - In-point of B: skip the "rest" frames before B's motion starts, so B opens already moving (2–6 frames into the motion [H]). Reisz and Millar's rule against duplicated or skipped action applies only when both shots show the same continuous action; then overlap 0–2 frames [P].

### 2.3 Eye-trace and screen-position continuity
*What:* the viewer's attention sits at a point in A's last frame; if B's point of interest is at the same place, the cut is nearly invisible; if it is far away, the eye must hunt (a mini-jolt). [S: Murch (eye-trace 7%); StudioBinder continuity; Vashi Nedomansky on the centre framing of *Mad Max: Fury Road*: viewers need no "hunting" of each new shot]
*Use:* always. A deliberate jump (eye pulled from the bottom-left to the top-right) is a tool for shocks and the Turn. *Avoid:* large unmotivated jumps between calm, connected shots.
- Signals: saliency centroid (spectral-residual saliency or a face/character detector) over the last 3 frames of A and the first 3 of B, normalised to frame width and height; Euclidean distance d.
- Implement [H]:
  - d ≤ 0.15: invisible cut; hard cut.
  - 0.15–0.35: acceptable; prefer a hard cut on motion that points towards B's point of interest (movement leads the eye).
  - d > 0.35 on a calm boundary: (a) reframe B with a small crop or pan in the upscale (1080×1920 from 576×1024 leaves headroom for a 0–8% zoom), or (b) choose another in-point, or (c) use a 4–8 frame dissolve, so the eye can travel. On a tense boundary, keep the jump; it adds impact.
  - Vertical framing: most attention sits in the central column; keep subject centroids in x ∈ [0.3, 0.7] and y ∈ [0.25, 0.65] (above the caption band, below the title band; see §2.19).

### 2.4 Screen direction: the 180° and 30° rules
*What:* 180°: keep the camera on one side of the line of action, so screen direction and eyelines stay consistent. 30°: two consecutive shots of the same subject should differ by at least about 30° of camera angle (and usually by shot size), or the cut reads as a jump cut. [S: StudioBinder continuity editing; Wikipedia "30-degree rule"; Restream]
*Use:* every pair of shots of the same character or space. The project rule already fixes direction: Rama's party moves left to right; threats enter right to left (KANDA_VISUAL_IDENTITIES §1).
*Avoid:* breaking them unless the break is the meaning (disorientation in the anger chamber, for example).
- Signals: facing direction (head yaw from a face landmark model, or a "faces left/right" tag in the shot list); dominant motion direction along x; shot scale (subject bounding-box height / frame height); same-character flag.
- Implement:
  - Facing flip for the same character on consecutive shots without a cutaway between them → warn; fix by horizontal flip **only** if the frame has no text, asymmetric costume detail or lettering (check the crown and the sacred-thread side), else regenerate B's keyframe.
  - Same character, scale ratio between 0.8 and 1.25, and similar angle → jump-cut warning; change B's crop by ≥ 20% [P] or insert a cutaway.

### 2.5 J-cuts and L-cuts (split edits)
*What:* J-cut: B's audio starts before B's picture. L-cut: A's audio continues under B's picture. [S: StudioBinder; Vimeo; No Film School]
*Use:* at nearly every boundary in narrated work; they are the main reason edited sequences feel continuous. *Avoid:* leads so long that the source is unclear; J-leading a sound whose image is a surprise (it spoils it).
- Typical leads [P]: about 3–12 frames for tight dialogue; 6–25 frames as natural anticipation; 25–75 frames for a scene or location change. Add a 2–4 frame audio fade on each edge to avoid clicks.
- Our narration is one continuous voice-over, so the split edit applies to **the picture against the narration phrase**, and to music, ambience and SFX:
  - **Picture cut vs. narration [H]:** cut the picture 4–10 frames **after** the start of the narration phrase that belongs to B when the line *names* B's subject (the voice introduces it, the image confirms it: a J relationship), or 3–8 frames **before** the phrase when B is a reveal the line comments on.
  - **Ambience:** B's ambience J-leads by 8–20 frames at a change of place; A's ambience L-trails 10–30 frames with a fade-out.
  - **Music phrase changes:** land the new cue's downbeat on the picture cut, or 1 beat before as a J.

### 2.6 Sound bridges
*What:* a sound that carries across the cut to bind two shots or scenes. [S: How To Film School; CapCut]
*Use:* transitions in time or place (AK01: the crowd roar in s03 carrying into the peacocks in s04; the nagada pulse leading from s09 into s10). *Avoid:* masking a planned silence.
- Implement: a sound bridge is mandatory [H] whenever the picture changes location or time **and** the transition is a hard cut. The bridge can be a music sustain, a leading SFX, or a continuous ambience.

### 2.7 Ambience beds and room-tone continuity
*What:* a constant background bed under every shot, so the sound floor never drops out at a cut. A cut to true digital silence sounds wrong; what breaks the illusion is the **tone changing** at a cut, not its level. [S: StudioBinder "What is room tone"; postaudiotips]
*Use:* every shot gets a location bed (hall reverb murmur, courtyard birds, chamber hush, fire crackle, city festival). *Avoid:* switching beds on every cut within one location.
- Signals: location ID per shot (shot-list field or the locked location plate in `ayodhya_kanda.json`).
- Implement: one bed per location, crossfaded over 0.3–0.5 s at location changes (the audio-mix skill already says beds fade in over 0.5 s at each change of place), positioned as a J (lead 8–20 frames). Same location on both sides → no crossfade, continuous bed. Planned silences keep the bed at about −40 to −45 dBFS [H] rather than true zero, unless the silence is meant as a "drop out" effect (the Turn).

### 2.8 Motivated transitions
*What:* a transition whose cause is inside the picture or the story: a door closing, a lamp flaring, a character turning away, smoke filling the frame, a time phrase in the narration ("That night", "Then"). [S: Dmytryk; Vimeo "natural transitions"]
- Signals: script time markers (regex on "that night|then|next morning|later|meanwhile" and their Hindi equivalents); visual events detected in the clip (luminance spike = flare; large low-texture region growing = occluder or smoke).
- Implement: a non-cut transition is allowed only when one of these motivations is present; otherwise force a hard cut [H].

### 2.9 Camera-movement continuity
*What:* consecutive moving shots should agree in direction, speed and energy, or change on purpose. A push-in that ends while the next shot starts static feels like a stop; a push-in cut straight into a pull-back at the same speed feels like a bounce. [P: whip-pan practice (match speed and direction), No Film School; Insta360; Splice]
*Use:* AK01 is mostly slow pushes, so the main risks are **reversals** (s02 push → s03 pull-back) and **dead heads/tails** (LTX eases in and out).
- Signals: global camera motion from optical flow: fit an affine/similarity model to background flow per frame → zoom rate (push/pull), pan and tilt rate; classify as push, pull, pan L/R, tilt U/D, crane or static; mean speed over the last 6 frames of A and the first 6 of B.
- Implement [H]:
  - Same type and direction: cut while both are moving; speed ratio 0.5–2.0 is fine.
  - Opposite zoom direction (push → pull): cut when A's push has *decelerated* to under 50% of its peak but before it stops, and enter B at its motion start; or put a hard cut on a strong narration beat so the reversal reads as a new idea; or retime B's first 8 frames to ease in. Never dissolve between opposite zooms (the overlap creates a "breathing" warp).
  - Moving → static: let A finish moving 0–4 frames before the cut (Dmytryk "cut long"), or accept the stop only on a dramatic beat (the Turn).
  - Static → moving: start B with motion already under way.
  - Synthetic continuity: when B is too static, add a slow 2.5D push of 1–3% scale over the shot during upscale to keep energy constant; never add a push opposite to the clip's own motion.

### 2.10 Shot–reverse-shot and reaction shots
*What:* alternating views of two characters, keeping eyelines consistent; the reaction shot shows how a line lands. [S: StudioBinder continuity; Adobe eyeline-match guide]
*Use:* conversation beats (Dasharatha urging Rama in s08). *Avoid with current I2V:* two-character close shots drift (ANIMATION_RESEARCH §7.6: about 1 in 2 character clips needed a retake). A reaction single (one face, one small expression change) is safer to generate than a two-shot.
- Implement: when the script has reported speech plus a listener, prefer **speaker two-shot → listener single (reaction)**, with eyelines: speaker looks screen-right, listener looks screen-left (or the reverse, kept for the scene). Signal: head yaw sign; flag mismatches.

### 2.11 Establishing, cutaway, insert and connecting shots
- **Establishing (wide) shot**: orients place and scale at a location change. Use at the first appearance of a location. Avoid repeating it for a return to the same place within 20 s [H].
- **Insert**: a close detail (a lamp flame, a jewel, a hand). Cheapest and most reliable I2V content (environment motion). Good for covering a gap or a jump cut and for emphasis.
- **Cutaway**: a related image away from the main action (peacocks, the city); covers time or a continuity break.
- **Connecting / bridge shot**: a short 1–2 s shot whose only job is to join two incompatible shots (a lamp-lit corridor, smoke, a curtain, the sky).
- Implement: insert a bridge shot when the boundary score (§5) is below threshold **and** no motivated transition is available **and** the narration has ≥ 1.2 s of non-critical words or a pause at that point [H]. Generate it as a 2.5D environment move (seconds of compute) rather than an LTX shot.

### 2.12 Rhythm and pacing: narration phrasing, music beats, breath
*What:* Murch's third priority. In narrated short-form work the voice-over sets the tempo; "visual cut tempo should mirror the pace of the voiceover" [P: Syllaby]. Keep the breath before an important clause and the small hang before a reveal [P: podfeet; Hindenburg].
- Signals: word timestamps (Whisper alignment, already used for captions); phrase boundaries (pauses ≥ 120 ms from VAD or alignment gaps); music tempo grid (the procedural nagada is 104 bpm in `assemble.py`; the tanpura bed has no beat); planned silences from `script.json`.
- Implement [H]:
  1. Candidate cut times = phrase boundaries ± 6 frames.
  2. Snap to the nearest music beat if one is within 3 frames (only in sections with a pulse, e.g. the celebration cue).
  3. Snap to the motion peak of A (§2.2) if within 6 frames; motion beats rhythm when they conflict, rhythm beats geometry (Murch's order).
  4. Never cut inside a word; never cut within 2 frames of a hard consonant onset (it reads as a glitch).
  5. Planned silences (0.3–0.8 s): the cut lands **at the start** of the silence for a shock, or **at its end** (with B's first sound) for a reveal.

### 2.13 Emotional progression: shot length and transition softness
*What:* shot length and transition hardness are emotional controls. Short shots and hard cuts raise tension; longer holds and soft transitions express tenderness, grief and time. [P: Backstage; Riverside; FilmDaft on dissolves; Bordwell]
- Map to the Ayodhya phases (KANDA_VISUAL_IDENTITIES §3.2) [H]:

| Phase / mood | Median shot length | Default transition | Dissolve length if motivated | Notes |
|---|---|---|---|---|
| 1 Glorious (vīra, adbhuta) | 4–5 s | hard cut on motion | 8–12 frames | Stately, symmetrical; cut on the camera's push |
| 2 Preparations (festive joy) | 3–4.5 s | hard cut on beat | 6–10 frames | Cuts on nagada beats; sound bridges |
| 3 Turning point (bhayānaka, raudra) | 3–5 s, with one long hold | hard cut; one dip to black | none (dissolves soften tension) | Silences 0.4 s; eye-trace jumps allowed |
| 4 Exile (karuṇa → śānta) | 4.5–6 s | dissolve 12–24 frames, L-cuts | 15–30 frames | Long L-cuts of bansuri; dip to black between days |

### 2.14 Dissolves vs hard cuts
*What:* the hard cut is the default and does not announce itself; a dissolve implies time or space change, or a mood shift, and is softer because both images overlap. Longer dissolves read as more time passing. Overuse looks dated, and a dissolve should not be used to hide a weak cut. [S/P: Backstage; Riverside; FilmDaft; Videomaker]
- Software defaults for reference: Premiere Pro's default video transition is a 30-frame cross dissolve; the default audio crossfade is 1 s Constant Power. [S: Adobe Learn; Adobe help on audio transitions]. These defaults are long for short form.
- Implement [H]:
  - Allowed only with a motivation (§2.8). Lengths at 30 fps: 4–8 frames "soft cut" (smoothing a small eye-trace jump), 10–15 frames time skip within a scene, 18–30 frames a new day or a reflective beat.
  - **Both** shots must be in motion-coherent frames for the whole overlap (the overlap uses A's tail and B's head, the AI's worst frames; see §3). The current assembler freezes A on its last frame during a dissolve; use real handle frames instead.
  - Use a gamma-correct (linear-light) blend, so mid-dissolve frames do not dip in brightness.
  - Never dissolve opposite camera moves, or two faces of different characters at the same screen position (a ghost "morph face").

### 2.15 Dip to black or to a colour
*What:* fade out to a colour and back in; marks the end of a chapter, a strong time cut, or a death. Dip to white reads as a flash, revelation or memory. [P: Backstage transitions guide; ffmpeg `xfade` has `fadeblack`, `fadewhite`]
- Implement [H]: at most one per Short (plus the end sting). 8–12 frames out, 0–6 frames held, 8–12 frames in. Audio: music decays naturally into the dip; never dip the narration. In Phase 3 it pairs with a planned silence. Dip to the Kanda's shadow colour (indigo `#1F2547` in Phase 3) instead of pure black, so the dip stays inside the palette.

### 2.16 Foreground wipes and natural wipes
*What:* an object passing close to the lens (a pillar, a curtain, a banner, a lamp flame, smoke) fills the frame and the cut is hidden at the moment of full occlusion; B ideally starts with a similar occluder clearing. Works best when the movement direction matches. [P: Vimeo "natural transitions"; Insta360; Fstoppers]
- AK01 note: shot 7 already has a foreground lamp flame sweeping past with a rack focus; it is a natural wipe point.
- Signals: fraction of the frame covered by a blurred, low-texture region (Laplacian variance per tile below a threshold) with coherent lateral motion; occlusion peak time.
- Implement: cut at the occlusion peak (± 1 frame); B's first frames should be occluded and clearing in the same direction, or masked with a 4–6 frame blurred crossfade. Prompt future clips for "foreground silk banner sweeps across the lens at the end" when a wipe is planned in the animatic.

### 2.17 Light, flash and flare transitions
*What:* a burst of light (lamp flare, sun glint, lightning, fire flare) whites out part of the frame and the cut is placed inside the burst. Motivated in Ayodhya by lamps, the sacred fire and the daytime meteor; in Kishkindha by lightning. [P]
- Signals: frame mean luma derivative; local highlight blooming (fraction of pixels above 0.9 luma).
- Implement: only when a light source exists in A or B. Additive flare peaks over 3–4 frames, cut at the peak, decays over 6–10 frames. Keep peak frame luma below 0.85 average to avoid a hard flash (also a photosensitivity concern: never more than 3 flashes per second).

### 2.18 Whip pans, speed ramps, freeze and hold frames
- **Whip pan:** fast motion-blur pan used as a wipe. Match the speed and direction of the two pans; cut at the most blurred frame. [P: No Film School; PremiumBeat; CineD] **Avoid in Ayodhya Phases 1–4** (stately camera, KANDA §3.2); reserve for Yuddha ("kinetic: whip"). I2V models rarely make clean whips; synthesise them in post with directional blur over 4–6 frames.
- **Speed ramp:** speed change within a shot. Use sparingly. [P: Splice; Nikon] For AI clips the useful variant is **micro-ramping**: 0.9–1.1× to fit narration, or easing an LTX deceleration tail (1.0 → 1.2× over the last 8 frames) so the motion doesn't die before the cut (HackerNoon AI chaining guide recommends a short ramp instead of a hard cut if a catch remains).
  - Current assembler retimes each clip by 0.75–1.25× with **frame blending**, which ghosts on fast motion. Prefer optical-flow interpolation for slowdowns below 0.9× (RIFE-class interpolator or ffmpeg `minterpolate`), or pick a different in/out window instead of slowing.
- **Freeze / hold frame:** stop on a frame for emphasis (a reveal, the last frame before the end card). The project rule "a shot that needs more holds on its last frame with 2.5D drift" (KANDA §2.3 rule 7) is right: never a dead freeze; add a 1–2% drift and keep environment particles moving. Never hold a frame inside the settling tail if its face is soft.

### 2.19 Colour, light and atmosphere continuity
*What:* neighbouring shots in one scene should match in exposure, white balance, contrast and saturation; across scenes the look should evolve on purpose. Resolve's Shot Match exists to "match a scene's worth of clips together so you have a starting point". [S: Resolve manual via Larry Jordan; Tuts+]
- Signals per shot (computed on the frames actually used): mean L*, a*, b* (CIELAB), luma percentiles p5/p50/p95, saturation (mean chroma), colour temperature proxy (b* mean), plus per boundary ΔE76 of the means and ΔL.
- Implement [H]:
  - Same location and time on both sides: target ΔE ≤ 4 and |ΔL| ≤ 5 at the boundary; correct B towards A with a per-shot 3×3 colour matrix plus a luma curve fitted on p5/p50/p95 (a "shot match"), clamped to ±15% gain so a weak image isn't stretched.
  - Location or time change: a large ΔE is expected; check only that it moves in the **phase direction** (KANDA §3.2: Phase 1 warm even light; Phase 3 one saturated crimson, the rest low; Phase 4 low saturation, ash). Express each phase as a target (L*, chroma, b*) and grade each shot partway towards it.
  - Within-shot flicker (AK01 s05 had two brightness dips): measure per-frame mean luma; any dip > 4% over < 10 frames → per-frame gain correction (already done for s05) or exclude that window.
  - Atmosphere continuity: haze, smoke, dust and particles should not appear or vanish at a cut inside one location; add a constant particle or haze layer per location in post if the clips disagree.

### 2.20 Music-driven editing
*What:* aligning cuts and transitions with musical structure (downbeats, phrase ends, swells, drops). [P]
- Our music is procedural (`chalk.music` leitmotifs, nagada pulse at 104 bpm, tanpura drone), so beat times are **known exactly**. No beat tracking needed.
- Implement [H]: emit the music cue times as data; picture cuts within ±3 frames of a cue boundary snap to it; a leitmotif should start on the cut where its character first appears (the Rama motif on s05's first frame), or J-lead it by one beat. A "drop" (melody out) lands on a hard cut, never in the middle of a dissolve.

### 2.21 SFX for transitions; whooshes only when motivated
*What:* transition SFX (whooshes, risers, hits) emphasise a cut. In story work, unmotivated whooshes feel like a template; every SFX should belong to something in the frame. [P: audio-mix skill: "An impact always lands on a cut; at most about 4 hits per episode"]
- Implement: a whoosh only with a visible fast motion across the cut (a whip pan, a banner sweeping, a bird crossing), peak aligned to the cut ± 2 frames, 3–6 dB under narration peaks. A riser only into the Turn or Payoff. Otherwise use diegetic sounds (bell, conch, fire crackle) as transition marks.

### 2.22 Silence
*What:* removing music (and sometimes ambience) creates emphasis; a cut into silence is one of the strongest transitions available. [P; KANDA §3.2 Phase 3 uses 0.4 s silences; audio-mix skill: 2–3 planned silences of 0.3–0.8 s]
- Implement: silences sit at the planned script points only. During a silence, the picture should hold a slow motion (flame bending) rather than cut; the cut comes at the end of the silence with the next sound (reveal), or at the start (shock).

---

## 3. AI-generated clips: special rules

### 3.1 Known failure modes of image-to-video clips (from AK01 and practice)
- **Head instability:** the first frames re-establish motion from a still keyframe, causing a small hitch; one vendor guide says reliable motion begins around frame 3 of an extended clip [P: InVideo FAQ]. With a frame-0 keyframe (our case), frame 0 is the sharpest frame but also the most static.
- **Settling tail:** generators ease camera and subject to stillness in roughly the last 10–15% of the clip; the literal last frame is the most settled [P: HackerNoon AI clip-chaining guide]. With an end anchor (`--image end.png last 0.7`), the tail also snaps towards the anchor and can morph.
- **Mid-clip morphs and identity drift:** s05r's crown shrank mid-clip then recovered; s08 has about 0.7 s of crown softening during the lean; two-character shots drift most (ANIMATION_RESEARCH §7.0, §7.6).
- **Brightness dips / flicker:** s05 had two brightness dips.
- **Intrusions:** an extra giant hand (s03 take 1), a modern highway (s08 take 1). These are rejections, not edit problems.
- Mismatched start and end frames (lighting, angle, position) are the main cause of morphing artefacts in first/last-frame generation [P: Dreamina/CapCut, Artlist guides].

### 3.2 Handles
*What:* extra frames beyond the in and out points, needed for dissolves, J/L cuts on picture, trims and ramps. Professional practice always edits with handles.
- AK01 clips are 97 or 121 frames at 24 fps (4.04 or 5.04 s), and the edit uses 3.5–5.2 s per shot. There are almost **no handles**: the assembler stretches each clip by 0.75–1.25× and starts at frame 0.
- Rule [H]: generate `needed + 0.6 s` minimum (≈ 15 frames at 24 fps: about 4 head + 11 tail), i.e. 97 frames for a ≤ 3.4 s shot, 121 for ≤ 4.4 s; a 5 s shot needs about 145 frames (or plan a 2.5D hold). LTX frame counts must be 8k+1, so 97, 121, 145. The time cost is roughly linear in frames (6 min for 97, 7.5–10 min for 121).

### 3.3 Choosing in and out points inside a clip
Compute per frame t (on a 540p proxy, CPU only, no heavy lock needed) [H]:
- `m(t)`: mean optical-flow magnitude (OpenCV Farneback or DIS).
- `w(t)`: **warp error**: warp frame t to t+1 with the flow and take the mean absolute residual in the salient region, or LPIPS between the warped and the real frame. Real motion has low warp error; morphs, wobbles and melting have high warp error at modest flow. This is the core "morph detector".
- `id(t)`: identity similarity of each character crop to its locked front anchor (DINOv2 or CLIP image embedding cosine; a face embedding where a frontal face exists).
- `s(t)`: sharpness (variance of the Laplacian) in the face or salient box.
- `L(t)`: mean luma, for flicker.
- Frame is **clean** when: w(t) ≤ median(w) + 2·MAD; id(t) ≥ 0.9·id(0) (or ≥ the shot's approved level); s(t) ≥ 0.7·max(s) for faces; |ΔL| ≤ 4% versus a 10-frame moving average.
- **Usable window** = the longest run of clean frames. Choose in/out inside it to (a) meet the narration duration at 0.9–1.1× speed, (b) put A's out-point near its motion peak, (c) skip the first 3 frames unless frame 0 is needed for the hook (shot 1, where frame 0 *is* the hook frame), and (d) avoid the last 10–15% unless the end pose is needed for a loop or match.
- **Never cut during a morph:** a cut within ±4 frames of a warp-error spike makes the morph read as a cut glitch. Move the cut to before the spike, or out of the spike's tail.

### 3.4 Regenerate, bridge, or mask? (criteria)

| Situation | Action |
|---|---|
| Usable window ≥ needed duration at 0.9–1.1× speed | Edit; no action |
| Usable window ≥ 70% of needed, rest is narration that can sit on another image | Shorten the shot; extend a neighbour or add a 1–1.5 s 2.5D insert (bridge) under the remaining words |
| Artefact ≤ 6 frames at the head or tail | Trim, or cover with the transition (a 4–6 frame dissolve or a natural wipe), or a 1–2 frame hold. **Masking is allowed only at heads and tails, never mid-shot** |
| Artefact 2–8 frames mid-shot, small area (e.g. crown softening), not on the face | Split the shot into two halves with an insert between them (a cutaway hides the bad frames); or localised frame substitution in the region if nothing moves there |
| Mid-shot identity loss on a face, or id(t) < 0.85·id(0) for > 6 frames | **Regenerate** (new seed, shorter clip, stronger end anchor, or static camera) |
| Intrusion (extra limb, modern object, wrong period), wrong action vs narration, or character leaves frame | **Regenerate**; never edit around it |
| Boundary score below threshold (§5) and no motivated transition, no space for a bridge | Regenerate one side with a changed keyframe (move the subject's screen position, adjust light) planned on the animatic |
| Boundary between two shots needing a time or space jump and no image fits | Bridge shot: 2.5D environment shot (sky, lamp, smoke, banner) of 1–2 s |

Cost guard: a regeneration costs 6–10 min of LTX on the M5 Air under `data/heavy.lock`, and about 1 in 2 two-character shots needed one in AK01. A bridge shot costs seconds. Prefer bridge and re-cut when the defect is **structural** (screen position, colour); prefer regeneration when it is **on a face or in the story action**.

---

## 4. Vertical short-form specifics

- **Hook timing.** The first 1.5–3 s decide the swipe; open on motion, with no slow intro or logo. [P: Opus Clip; JoinBrands; multiple creator guides; no official YouTube figure]. Rule [H]: **no transition other than a hard cut in the first 3 s**; frame 0 is a complete, readable image (project rule: ≥ 70% drawn); first narration word at 0.15–0.3 s (audio-mix skill); the first cut at or after the end of the hook sentence (AK01: 3.0–3.6 s).
- **Duration.** Shorts can be up to 3 minutes since 15 October 2024 [S: TechCrunch, 9to5Google, Tubefilter, PetaPixel reporting the YouTube announcement], but the project rule stays 35–55 s, hard limit under 60 s (Content ID claims block >1-min Shorts; audio-mix skill).
- **Safe areas.** No official YouTube Shorts spec; third-party measurements of the overlays at 1080×1920 put a top band of 120–180 px, a right-hand action column of ~120 px, and a bottom band of 300–400 px [P: several safe-zone checkers]. Meta publishes margins for **Reels ads** only: 14% top, 35% bottom, 6% sides [P: reported by several ad-spec guides; organic Reels have no published spec]. The project's composition rule (title headroom top 12%, captions in the lower 25%, subject centred) fits YouTube; for Instagram, keep captions above ~65% height, i.e. y ≤ 1250 px [H: compromise].
  - Editing consequence: when reframing for eye-trace (§2.3) never push the subject's face into the bottom 25% or the right 11%.
- **Caption continuity.** Captions are a continuity channel too: keep the caption block position fixed for the whole video, and avoid a caption line change in the same frame as a picture cut where possible (offset ≥ 4 frames [H]) so two things don't jump at once.
- **Loop endings.** Shorts loop automatically; a final frame that flows into frame 0 earns replays [P: creator guides; the replay effect on ranking is not documented by YouTube]. AK01's design is a **composition loop** (s11 Manthara on a high terrace mirrors s01 Dasharatha at a high window). Rules [H]: match the last picture frame before the end sting to frame 0 on saliency position (d ≤ 0.15), dominant colour ΔE ≤ 10, and camera direction (both pushing in); keep the end sting at 0.5–1.0 s so the loop seam is short; end the music on an unresolved note (already the `unresolved` cue) so the restart resolves it.
- **No slow dissolves at the start, no long fades at the end**: a fade-out to black before the end card signals "finished" and invites a swipe; prefer a hard cut to the sting.

---

## 5. The decision table

Boundary features (computed per §6) → recommended technique, timing, audio treatment and escalation. Rows are evaluated top to bottom; the first match wins. Timings at 30 fps.

| # | Boundary features (condition) | Technique | Picture timing | Audio treatment | Escalate to regeneration / bridge when |
|---|---|---|---|---|---|
| 1 | Boundary inside the first 3 s, or into the hook shot | Hard cut | Cut at the hook sentence end + 0–4 frames | Impact on frame 0 only; music continues | Frame 0 not readable, or the first 3 s contain no motion |
| 2 | Planned **Turn** silence at the boundary (script `pause` ≥ 0.4 s before the Turn) | Hard cut **into** the silence, or a dip to the phase shadow colour if the narration states a time change ("Then", "That night") | Dip: 8–10 out + 0–4 hold + 8–10 in; or a hard cut at the silence start | Music "drop": melody out on the cut; ambience falls to −40 dBFS bed; heartbeat or drone enters on B's first frame | B's opening frames have warp-error spikes (the silence exposes them) |
| 3 | Graphic-match score ≥ 0.6 | Hard cut on the matched frames | Exact frame match; no dissolve | Sound bridge or match (e.g. roar → thunder), J-lead 4–8 frames | — |
| 4 | Same character on both sides, movement match available (angle Δ ≤ 45°, speed ratio 0.6–1.6) | Cut on action | Out at A's motion peak to +4 frames; in 2–6 frames into B's motion | Narration continuous; bed continuous if same location | Facing flip without motivation; scale ratio 0.8–1.25 at a similar angle (jump cut) → crop B ≥ 20% or regenerate |
| 5 | Location change, same time, hard cut desirable (phases 1–3) | Hard cut + sound bridge | On the narration phrase start for B + 4–10 frames (J) | B's ambience J-leads 8–20 frames; A's L-trails 10–30 frames with a fade | No bridge sound exists and ΔE > 25 between A and B → add a 1–1.5 s 2.5D establishing insert |
| 6 | Time change stated in the narration (regex time marker) within one location or a calm mood | Dissolve | 10–15 frames (same night/day), 18–30 frames (next day, reflective); both sides in clean frames | Music crossfade over the same span; constant-power audio crossfade | Either side lacks clean handles ≥ dissolve length → shorten the dissolve to ≥ 6 frames, or switch to a dip, or regenerate with 145 frames |
| 7 | A has a natural occluder (foreground object, smoke, flame) passing at its end | Natural wipe | Cut at the occlusion peak ± 1 frame; B opens occluded or with a 4–6 frame blurred cross | Whoosh only if the occluder moves fast; otherwise diegetic (cloth rustle, fire) | — |
| 8 | A or B has a light source flaring (lamp, fire, sun, meteor, lightning) | Light / flare transition | Flare rises 3–4 frames, cut at peak, decays 6–10 frames; peak mean luma ≤ 0.85 | Bell, conch or fire swell on the peak, under narration | — |
| 9 | Opposite camera moves (push → pull, tilt up → tilt down) at speed | Hard cut on a narration beat; never a dissolve | Out when A's speed ≤ 50% of its peak; in at B's motion start | Music phrase change on the cut | Speed of both > 60% of their peaks at every candidate point → retime B's first 8 frames (ease-in), or regenerate B with a static camera |
| 10 | Eye-trace distance d > 0.35, calm boundary | Reframe B (crop/pan up to 8%), else soft cut 4–8 frames | Dissolve only if both sides clean | Continuous bed | Reframe would push the face out of the safe area and no other in-point gives d ≤ 0.35 → regenerate B's keyframe with the subject moved |
| 11 | Same location, ΔE > 4 or |ΔL| > 5 | Grade match B towards A, then decide by the other rows | — | — | Correction needs > ±15% gain or changes skin tone visibly → regenerate B's keyframe with the location plate's lighting |
| 12 | Celebration / pulse section (music with beats) | Hard cut on beat | Snap to the beat within ±3 frames | Cut on downbeats; J-lead the next motif by one beat | — |
| 13 | Phase 4 grief, reflective, or end of a day | Dissolve 15–30 frames or dip to black | As row 6 | Long L-cut of bansuri, 1–2 s | As row 6 |
| 14 | Last shot → end sting | Hard cut | Out on the loop-matching frame (§4) | Music ends on the unresolved note; bell under the sting | Loop match fails (d > 0.25, ΔE > 15) → re-choose s11's out-point, or regenerate its end anchor to mirror frame 0 |
| 15 | Anything else | Hard cut on motion at a phrase boundary | Phrase boundary ± 6 frames, snapped to motion peak | Narration continuous; bed continuous or crossfaded 0.3 s | Boundary score < 0.35 (§6.3) after reframing and grading → bridge shot or regeneration |

Global caps [H]: at most 3 non-cut transitions per 45 s Short (excluding the end sting); at most 1 dip; no whip pans in Ayodhya; at most about 4 SFX hits (audio-mix skill).

---

## 6. Measurable features

All computable on the 540p proxies or the 576×1024 LTX outputs with CPU tools (OpenCV, NumPy, librosa or the known music grid, the existing Whisper alignment). None needs a heavy model except optional identity embeddings (a small DINOv2-S or CLIP-B is light, but should still respect `data/heavy.lock` if run alongside LTX). Candidate tools: PySceneDetect (content/adaptive detectors; default content threshold 27) to verify no unintended cuts inside generated clips [S: scenedetect.com docs]; OpenCV optical flow; ffmpeg `xfade` for dissolves and dips (`offset` must be ≤ first clip duration − transition duration) [S: FFmpeg wiki Xfade]. Check each library's licence before adding it to the pipeline.

### 6.1 Per shot (time series and summaries)
| Feature | How | Used by |
|---|---|---|
| Motion energy m(t) and its peak, onset, settle times | Mean flow magnitude in the salient mask | Cut on action, in/out points |
| Camera motion class and speed (push, pull, pan, tilt, crane, static) | Affine/similarity fit to background flow; zoom = scale rate | Camera continuity |
| Subject motion direction (x, y) | Mean flow inside the subject mask | Movement match, screen direction |
| Warp error w(t) | Flow-warped residual or LPIPS(warp(t), t+1) in the salient region | Morph detection, clean window |
| Identity similarity id(t) per character | Embedding cosine of character crop vs locked anchor | Drift detection, regeneration trigger |
| Sharpness s(t) in the face box | Variance of the Laplacian | Clean window |
| Luma L(t), flicker events | Mean luma and its 10-frame deviation | Flicker fix, clean window |
| Usable window [t_in, t_out] and length | §3.3 | Handles, regeneration |
| Saliency centroid trajectory | Spectral-residual saliency or detector box centre | Eye-trace |
| Shot scale | Main subject box height / frame height | 30° / jump-cut check |
| Facing / head yaw sign | Landmarks or shot-list tag | 180° rule, eyelines |
| Colour stats: mean L*a*b*, chroma, p5/p50/p95 luma | On used frames | Grade match, phase progression |
| Occlusion events | Fraction of low-texture moving area | Natural wipe |
| Light events | Luma derivative and highlight fraction | Flare transition |
| Script fields: phase, beat (H/C/E/T/P/N), location ID, time marker, characters, planned pause, music cue | `script.json` / shot list | Every row of the table |

### 6.2 Per boundary
| Feature | Definition |
|---|---|
| Eye-trace distance d | Normalised distance of saliency centroids (A last 3 frames vs B first 3) |
| Graphic-match score | §2.1 |
| Camera-motion agreement | Cosine of camera vectors and speed ratio (A last 6 frames vs B first 6) |
| Subject-motion agreement | Same, for subject flow |
| ΔE, ΔL, Δchroma | CIELAB means of A's out-frames vs B's in-frames |
| Scale ratio and angle similarity | Same-character jump-cut test |
| Facing flip | Same character, yaw sign changes |
| Location change, time change | From the script |
| Phase and mood delta | From the shot list beats and the phase table |
| Narration timing | Phrase start/end times for A and B; gap length; planned pause |
| Music | Distance to the nearest cue boundary or beat |
| Handle availability | Clean frames before B's in-point and after A's out-point |
| Clean-at-cut | No warp-error spike within ±4 frames of the cut on either side |

### 6.3 Boundary score (for QA and escalation) [H]
`score = 0.51·emotion_fit + 0.23·story_fit + 0.10·rhythm_fit + 0.07·eye_trace_fit + 0.05·screen_2d_fit + 0.04·space_3d_fit`, Murch's weights, each term in [0, 1]:
- emotion_fit: transition type and length agree with the phase table (§2.13) and the beat; 1 if yes, 0.5 if neutral, 0 if contradicting (e.g. a dissolve at the Turn).
- story_fit: the image on screen matches the narration words it sits under (shot-list mapping; word-to-cut offset within the J/L rules).
- rhythm_fit: cut within ±6 frames of a phrase boundary and, where applicable, ±3 frames of a beat.
- eye_trace_fit: 1 − min(1, d/0.5).
- screen_2d_fit: camera and subject motion agreement, facing consistency.
- space_3d_fit: 180°/30° rules, scale change.
- Hard gates (fail regardless of score): cut within ±4 frames of a warp-error spike; identity below threshold in used frames; a dissolve or dip in the first 3 s; captions or faces outside the safe area.
- Report per boundary in the timeline JSON next to `transition_in`, and show the lowest three at G2.

---

## 7. Applying it to AK01 (recommendations for the next assembly pass)

Observed in the current assembler (`assemble.py`, `AK01-en.timeline.json`):
- Every clip starts at frame 0 and is time-stretched by 0.75–1.25× with frame blending to fill its narration span; there are no in/out selections, no handles and no head/tail trims.
- During a dissolve the outgoing clip is clamped on its last frame (a frozen tail under the blend), i.e. the transition is built from A's most settled frame.
- Transitions are: dip into s08, cross into s09 and s10 (`XFADE` keys 7, 8, 9 are 0-based scene indices), all others hard cuts. The script's planned silences are after shot 6 (before the Turn), after shot 8 and after shot 10.

Per-boundary proposal (to verify with the measured features; all [H]):

| Boundary | Reading | Proposal |
|---|---|---|
| 1 → 2 | Hook; the king's gaze lifts to the sky → s02 starts on the parasol at the top of frame and tilts down | Hard cut at the hook sentence end; the upward gaze leads the eye to the parasol (eye-trace match). Tanpura continuous; `ayodhya` reed phrase J-leads 6–8 frames |
| 2 → 3 | s02 push-in → s03 pull-back (opposite zoom); the king lowers his head, then rises with an open palm | Cut when s02's push has eased (row 9) and enter s03 with the palm already moving (cut on action). Hall murmur bed J-leads 10–15 frames |
| 3 → 4 | Open palm → peacock fans spreading; "the hall roared, like peacocks" | Graphic and idea match (row 3): hard cut on the fan-shape match, crowd roar as a sound bridge that turns into the thunder rumble |
| 4 → 5 | Rain-cloud dark → Rama in morning light | Hard cut on the `rama` leitmotif downbeat; grade s04's tail slightly warmer or s05's head slightly cooler to reduce ΔL. Exclude s05's brightness-dip frames from the window if gain correction leaves residue |
| 5 → 6 | Rama single → king and Rama two-shot | Check that Rama's screen side is the same in both (eye-trace and 180°). Hard cut; `dasharatha` motif J-leads one beat |
| 6 → 7 | **The Turn**, 0.5 s silence, "Then he called Rama back" (time change) | Move the dip here (from 7 → 8): dip to indigo `#1F2547`, 8–10 out + 0–4 hold + 8–10 in, aligned with the silence; music drop on the dip; s07's lamp flame is the first thing seen |
| 7 → 8 | Eyes open wide (action peak) → lean-in and grip; same night, tension rising | **Hard cut** on the eyes reaching full open (cut on action); remove the current dip. Choose s08's in/out window to exclude its 0.7 s of crown softening, or cover it with the verse overlay only if the face isn't in that region |
| 8 → 9 | "Tomorrow" → "That night … the sacred fast"; 0.4 s pause; time change | Dissolve 15–18 frames using real handles (not a frozen s08 tail), or a fire-flare transition from s09's sacred fire; bansuri and bell L/J across it |
| 9 → 10 | Stillness (eyes closed) → festival city crane-up | **Hard cut on the nagada downbeat** with the pulse J-leading 12–18 frames under s09's tail (sound bridge), replacing the current cross dissolve; joy should arrive with energy |
| 10 → 11 | City from above → Manthara looking down on the same city; 0.3 s pause | Hard cut; the city stays in the lower half of frame across the cut (eye-trace). Celebration bed L-trails 20–30 frames and thins to distance, so the city sounds far below her |
| 11 → sting | Loop to s01 | Out-point on the frame that best mirrors s01 frame 0 (§4), hard cut to the 0.5–1.0 s chalk sting, `unresolved` cue under it |

Generation changes for the next episode (cheaper than repair):
1. Make a **keyframe animatic** first (keyframes, voice, music, simple pushes), lock cut points, transitions and motion directions on it, then render LTX.
2. Render with **handles**: 121 frames for shots ≤ 4.4 s, 145 for longer; plan the out-point before the settling tail.
3. Write motion direction and end pose into each shot's prompt from the boundary plan (e.g. "the banner sweeps across the lens to the right at the end" for a planned natural wipe; "the camera keeps pushing in" for continuity into the next push).
4. Keep the analysis features in the timeline JSON so the reviewer sees boundary scores at G2.

---

## 8. Sources (accessed 2026-11-17)

Books and long-form references
- Walter Murch, *In the Blink of an Eye*, 2nd ed., Silman-James Press, 2001. Rule of Six summarised at: https://cloud.wikis.utexas.edu/wiki/spaces/rtf318/pages/80022510/Murch+s+Rule+of+Six ; https://nofilmschool.com/2016/11/6-rules-good-cutting-according-oscar-winning-editor-walter-murch ; https://new-blog.artlist.io/blog/eye-trace-and-rule-of-six-editing/
- Murch on the blink and cut point: https://www.provideocoalition.com/aotc-murch-bcpc/ ; https://www.nofilmschool.com/2016/05/not-sure-where-cut-editor-walter-murch-says-answer-may-be-eyes ; https://www.webofstories.com/play/56382
- Karel Reisz and Gavin Millar, *The Technique of Film Editing* (1953; 2nd ed. 1968), scanned 1958 printing: https://lantern.mediahist.org/catalog/techniquefilmedit00reis_0220 (and pages _0221, _0223, _0231); publisher listing: https://oreilly.com/library/view/technique-of-film/9780240521855
- Edward Dmytryk, *On Film Editing*, Focal Press, 1984. Rule summaries: https://www.provideocoalition.com/seven_rules_for_film_and_video_editors/ ; https://www.nyfa.edu/student-resources/what-you-can-learn-from-edward-dmytryks-7-rules-of-cutting/ ; https://www.routledge.com/products/9780429506086
- David Bordwell, "Intensified Continuity: Visual Style in Contemporary American Film", *Film Quarterly* 55:3 (2002); follow-up: https://davidbordwell.net/blog/2007/05/27/intensified-continuity-revisited/

Craft publications
- StudioBinder: continuity editing https://www.studiobinder.com/blog/what-is-continuity-editing/ ; J-cut https://www.studiobinder.com/blog/what-is-a-j-cut/ ; L-cut https://www.studiobinder.com/blog/what-is-an-l-cut/ ; match cuts https://www.studiobinder.com/blog/match-cuts/ ; room tone https://www.studiobinder.com/blog/what-is-room-tone/
- No Film School: J and L cuts https://nofilmschool.com/2017/10/editing-101-what-are-j-and-l-cuts-and-why-should-you-be-using-them ; whip pans https://nofilmschool.com/how-to-do-a-whip-pan ; animation editing https://nofilmschool.com/2017/01/what-does-an-animation-editor-do ; Mad Max framing https://nofilmschool.com/2015/05/how-framing-mad-max-fury-road-keep-viewer-oriented-world-gone-mad
- Frame.io, "Edit First, Shoot Later: A Real-World Look at Editing Animation": https://blog.frame.io/2019/07/15/animation-editing/
- Toon Boom Storyboard Pro, animatic docs: https://docs.toonboom.com/help/storyboard-pro-7/storyboard/getting-started/animatic.html
- Vimeo: J and L cuts https://vimeo.com/blog/post/j-cuts-l-cuts ; cuts guide https://vimeo.com/blog/post/guide-to-film-cuts
- Boris FX, match cut types: https://borisfx.com/blog/what-is-a-match-cut/ ; Videomaker match cuts: https://www.videomaker.com/how-to/editing/editing-technique/what-are-match-cuts-and-how-are-they-used/ ; cutting on action: https://www.videomaker.com/article/c10/13536-cutting-on-action/
- Backstage, transitions guide: https://www.backstage.com/magazine/article/video-transitions-75727/ ; continuity editing: https://www.backstage.com/magazine/article/continuity-editing-guide-75720/
- Wikipedia, 30-degree rule: https://en.wikipedia.org/wiki/30-degree_rule ; J cut: https://en.wikipedia.org/wiki/J_cut
- Vashi Nedomansky, centre framing / eye trace (via PetaPixel): https://petapixel.com/2015/05/31/the-center-framed-style-of-mad-max-fury-road ; Bordwell's response: https://www.davidbordwell.net/blog/2016/02/10/off-center-mad-maxs-headroom/
- PremiumBeat, whip pan: https://www.premiumbeat.com/blog/create-seamless-transitons-whip-pan/ ; CineD: https://www.cined.com/whip-pans-when-and-why-filmmakers-use-them/
- Dissolves: https://riverside.fm/video-editor/video-editing-glossary/dissolve ; https://filmdaft.com/what-is-a-crossfade-in-film-definition-examples-how-to-use-it/
- Room tone continuity: https://postaudiotips.beehiiv.com/p/production-fill-library-room-tone-here-s-why
- Narration pacing: https://www.podfeet.com/blog/?p=36177 ; https://syllaby.io/blog/voiceover-pacing-silence-trimming-retention-editing/

Software documentation
- Adobe Premiere Pro, audio transitions: https://helpx.adobe.com/premiere-pro/using/audio-transitions.html ; timeline preferences (default transition durations): https://helpx.adobe.com/premiere/desktop/get-started/preferences-and-settings/timeline-preferences.html ; Adobe Learn (30-frame default dissolve): https://www.adobe.com/th_en/learn/premiere-pro/web/premiere-pro-add-transitions-cc
- DaVinci Resolve Shot Match (manual quoted): https://larryjordan.com/articles/how-to-color-match-clips-in-davinci-resolve-20/
- FFmpeg `xfade`: https://trac.ffmpeg.org/wiki/Xfade
- PySceneDetect: https://www.scenedetect.com/docs/cli.html

AI video clip practice (vendor and community; treat as heuristics)
- Chaining AI clips, deceleration tail, seed frame choice: https://hackernoon.com/how-to-chain-ai-video-clips-into-one-shot-without-the-hidden-stutter-at-every-cut
- First frames of extended clips: https://invideo.io/faq/why-do-the-first-frames-of-an-ai-extended-video-clip/
- Start/end frame mismatch and morphing: https://dreamina.capcut.com/ai-video/how-to-use-start-and-end-frame-generators ; https://www.artlist.io/blog/ai-video-transitions

Short-form vertical
- Shorts up to 3 minutes from 15 Oct 2024: https://techcrunch.com/2024/10/03/youtube-takes-on-tiktok-with-longer-shorts-templates-trends-and-more ; https://www.tubefilter.com/2024/10/03/youtube-shorts-three-minutes-max-length-redesign-trends-templates/
- Safe zones (third-party measurements, no official spec): https://reap.video/blog/short-form-video-safe-zones ; https://www.clipspeed.ai/blog/youtube-shorts-size.html ; Meta Reels ad margins as reported: https://billo.app/blog/meta-ads-safe-zones
- Hooks and loops (creator guides; no official YouTube data): https://www.opus.pro/blog/youtube-shorts-hook-formulas ; https://joinbrands.com/blog/youtube-shorts-best-practices/ ; https://stingray-alligator-3g85.squarespace.com/blog/seamlessloop

Caveats: the Murch percentages and Dmytryk rules are cited through secondary summaries (the books were not read directly). J-cut frame ranges, safe-zone pixels and AI clip head/tail behaviour come from practitioner and vendor sources with no formal standard. Every [H] number in this document is a starting value to calibrate on AK01, not a measured result.
