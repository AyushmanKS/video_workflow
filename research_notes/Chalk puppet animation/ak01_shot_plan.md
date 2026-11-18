# AK01 "Rama's Crown Was Ready" — chalk-puppet animation plan (11 shots)

Status: prototype approved by the owner on 2026-11-18. The full episode is rigged in `rigs/ak01.json`, and all 10 illustrations pass `proto.py --rig=ak01 --qa`. Every shot uses the pivot templates in `profiles/rigs.json`.

Some planned actions failed QA and were dropped. Each failed because it moved a piece of the drawing that overlaps scenery or a resting limb:
- the chamara whisk swing;
- the s07 curtain stir;
- the peacock tail fan and the small peacock's head bobs;
- the head turns at the fire in shot 9;
- the torso leans in shots 1, 7 and 11.

PROJECT_CONTEXT §30 explains each one. The rest of the table below is the plan as written.

Rules used in every shot:
- Only the characters and objects that matter to the line move; the rest of the board stays still.
- One main action per line, timed to the word that motivates it; a small string-style overshoot and settle at the end of each action; a slow idle sway and breath while waiting.
- Character parts are rigid chalk cut-outs moved as whole pieces, never redrawn, so grain and strokes stay the drawing's own.
- Continuity: the camera keeps one slow push direction per scene; ambience starts 0.4–0.7 s before its picture (J-cut) and lingers 0.3–1 s after (L-cut); transitions follow the continuity layer (PROJECT_CONTEXT §29). Scenes that share a place (throne 2–3, chamber 7–8) reuse one illustration and continue the action instead of cutting.

| # | Line (en) | Illustration | Moves (action → word) | Stays still | Environment | Sound | Transition in |
|---|---|---|---|---|---|---|---|
| 1 | Rama's crown was ready. His father was afraid. | new: Dasharatha from behind at a palace window, city beyond | head turns a little toward his shoulder on "afraid" (2D tilt + shift); hand tightens on the sill | body, window frame | curtain hangs and sways; flags on distant rooftops; two birds cross | wind, distant bell | chalk-line bloom (series opening) |
| 2 | Old King Dasharatha longed to rest from ruling Ayodhya. | **prototype p1** (throne) | head droops, raised hand sinks (weariness) | legs, throne | chamara whisk swings; banners sway; hanging lamps swing | court murmur, birds | J-cut murmur 0.5 s |
| 3 | So before kings and citizens, he proposed Rama as crown prince. | same as 2 (continuous action) | head lifts, hand rises in proclamation on "proposed" | as 2 | as 2; optional row of seated kings nodding in turn (new wide illustration if wanted) | murmur swells | none (same illustration) |
| 4 | The hall roared, like peacocks greeting a rain cloud. | new: two peacocks on a rooftop under a rain cloud | tails fan open (scale + rotate about the body) on "roared"; heads bob | rooftops | cloud drifts in; chalk rain overlay; one lightning flash | roar → thunder (J-cut 0.7 s) | cut on the roar |
| 5 | Truthful, gentle, dark as a blue lotus, the people said. | new: Rama portrait, three-quarter | slow head tilt and lowered gaze on "gentle"; hand to chest on "said" | body | uttariya end sways; lotus petals fall | soft flute (rama motif) | cut |
| 6 | The king embraced Rama and named the star: Pushya. | **prototype p2** (terrace) | Rama steps in; king leans and reaches to Rama's shoulder on "embraced"; both look up on "Pushya" | legs, balustrade | flags flutter; tree sways; birds | birds, wind | cut on Rama's step |
| 7 | Then he called Rama back. He had seen dreadful dreams. | new: lamp-lit night chamber, king on a couch | king sits up sharply on "called"; hand to chest on "dreadful" | couch, walls | lamp flame flickers; curtain stirs | heartbeat, wind | held dip to indigo (the Turn) |
| 8 | Be crowned tomorrow, he urged, while Bharata is still away. | new: same chamber, king and Rama | king grips Rama's hands and nods twice on "urged"; Rama bows | as 7 | lamp flicker; moon in the window | heartbeat continues | cut (same room) |
| 9 | That night, Rama and Sita kept the sacred fast. Ayodhya rose to decorate. | new: Rama and Sita seated at a small sacred fire | Sita turns her head toward Rama; both join palms on "fast" | seated bodies | fire flickers, smoke curls up | fire crackle; nagada enters softly at the end | 1 s dissolve ("that night") |
| 10 | Banners on rooftops, flowers on the royal road, lamps for the night. | **prototype p3** (city) | — | buildings | flags flutter on "banners"; petals fall from "flowers"; lamps light far→near on "lamps for the night"; clouds drift; birds | nagada, conch, crowd | J-cut nagada 1 s |
| 11 | And from a palace rooftop, Kaikeyi's maid Manthara watched it all. | new: Manthara on a rooftop, back three-quarter, city lamps below | slow head turn toward the camera on "watched"; fingers tighten on the parapet | body | sari end flutters; lamps below flicker | nagada lingers then fades (L-cut); unresolved motif | cut, then chalk drain to the end card |

New illustrations needed for the full episode: 7 (shots 1, 4, 5, 7, 8, 9, 11), generated with the existing chalk style and character prompts, composed for puppetry (limbs clear of the body, side or three-quarter views, open board around moving parts). Rig fitting per illustration: about 10–15 minutes of tracing parts and joints (or SAM 2.1 assisted later).
