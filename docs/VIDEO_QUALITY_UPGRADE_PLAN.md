# Video quality upgrade plan: RAMAYANA, The Epic in Chalk

**Date:** 2026-11-16 · **Status:** proposal. Nothing here is approved yet.
**Readers:** the owner (a creator, not a film specialist) and future Claude Code sessions that implement it.
**Built from:** `research_notes/Studio upgrade research/creative_direction_storytelling.md` (CDS), `visual_tools.md` (VT), `audio_and_claude_skills.md` (AUD), `audit_summary.md`, `docs/WORKFLOW_AUDIT.md` (AUDIT), and a read of `chalk.py`, `studio.py`, `styles.py`, `profiles/characters/ramayana.json` and `.claude/skills/storytelling/SKILL.md` at commit `ef038fe`.
**Re-verified this session:** the Hugging Face API lists `black-forest-labs/FLUX.2-klein-4B` as `apache-2.0` and ungated, and `depth-anything/Depth-Anything-V2-Small-hf` as `apache-2.0`. No other new web research was done.

**Tags used throughout**
- **[F]** sourced fact. The source note is named, and its links are there.
- **[M]** measured in this repo. The file, function or line is given.
- **[R]** recommendation. This is judgement, not evidence.
- **[U]** unverified or unmeasured. Check before relying on it.
- **Approval classes** (used in §6):
  - **OWNER**: changes the approved look or sound. Needs a side-by-side sample and the owner's yes before it reaches any episode.
  - **SAFE**: engineering with no visible or audible style change.
  - **G1**: script content. Goes through the normal script gate.

**Constraints that apply everywhere**
- Zero cost, and commercial-use licences only.
- MacBook Air M5 16 GB: one heavy model loaded at a time, with progress updates during long runs.
- Keep the chalkboard identity and `chalk.CHALK_SFX_GAIN = 0.035`.
- **Never regenerate or replace published episodes.** A/B tests render into a scratch output from an episode's existing assets, and nothing is re-uploaded.
- No code comments in the code changes this plan proposes.

---

## 1. Diagnosis: what limits quality today

| # | Limitation | Evidence | Why it matters |
|---|---|---|---|
| D1 | **Every video is too long.** | **[M]** 20 of 20 renders run 74.8–111.2 s, and none is under 60 s. By language: en 74.8–89.5, hi 83.2–101.6, gu 93.3–108.5, te 99.5–111.2 s (AUDIT §1, ffprobe). Scripts carry 155–257 words, about twice the 45 s budget (CDS §1.4). The target is written as 60–90 s in `storytelling/SKILL.md` (description and checklist, "scene count 9–14"). `qa.py:11` enforces only `max_seconds: 180`. | **[F]** Engaged views exclude loops and count viewers who "stayed to watch past the initial seconds". Instagram ranks on watching all the way through (CDS §1.1). **[R]** A shorter runtime raises completion almost mechanically, and this is the largest lever. |
| D2 | **Frame 0 is a blank board.** | **[M]** `chalk.plan()` sets `draw = 1.6` for scene 0, starting at progress 0 (`chalk.py:241`). Frame 0 extracted from C0005-en is empty board (AUDIT F12). Audio also has a 0.35 s silent lead (`studio.py:631-632`), so the first word can never land before 0.35 s. | **[F]** "You have one second to hook someone" (Hoyos, CDS §1.1). **[M/F]** Custom thumbnails may not show in the Shorts feed (AUDIT §2.13), so frame 0 effectively is the thumbnail. |
| D3 | **Every shot uses the same grammar.** | **[M]** Each scene follows the same sequence: stroke-draw for 2.0–3.6 s (`draw = min(max(0.5*avail, 2.0), 3.6)`), then a slow zoom alternating 1.00–1.03 and 1.04–1.10, ±2.5 px jitter, a 0.55 s streak-erase (`ERASE`), and an 11% ghost of the previous image (`chalk.render`). With about 6.3 s per scene (82 s / 13 scenes), roughly half of each scene is drawing or erasing (estimate from the `plan()` formula). | **[R]** It becomes monotonous after the third scene. At 45 s with 12 shots, the full draw would leave each image fully visible for about 1 s (CDS §0). |
| D4 | **Character consistency is text-only.** | **[M]** `ramayana.json` has 15 character prompts and the rule "reuse verbatim", but nothing in `studio.py`, `chalk.py` or `pipeline/` reads it (AUDIT F06). `step_images` only appends `script["character"]` (`studio.py:305-306`). There are no reference images and no similarity metric; the only check is the video-qa contact sheet. Narada needed a prompt patch to stop drifting to a bearded or child figure (`ramayana.json` notes). | Recurring figures drift in age, beard and costume between scenes and episodes. |
| D5 | **Negative prompts do nothing, so prompts bloat.** | **[M]** mflux forces guidance to 0 for Z-Image Turbo (`mflux/.../z_image_turbo_generate.py:23`), so `styles.py` `negative` and `--negative-prompt` (`studio.py:313`) have no effect. C0005 scene 1's `visual` runs about 110 words, about a third of them negations ("no wings, no horns…"), which may prime the very concepts they forbid. Borders still appear despite "full-bleed, no border"; a manual crop `(24,42,744,1302)` is in the handoff gotchas (AUDIT §2.6). | Wasted prompt capacity, unwanted elements, and manual fixes. |
| D6 | **The palette is global, so every world looks the same.** | **[M]** `restrict_palette()` snaps every saturated hue to the nearest of `PALETTE_HUES = [27, 42, 95]` (saffron, gold, green). | Lanka cannot be crimson, and Ayodhya, the forest and the battle share one colour language. |
| D7 | **Sound design is flat.** | **[M]** One numpy envelope ducker (`duck = 1 - 0.45·clip(env/0.05)` for chalk, `studio.py:663,672`). Single-pass dynamic `loudnorm=I=-14:TP=-1.5:LRA=11` inside the video encode (`studio.py:705`) ends at −15.2 to −14.7 LUFS with LRA 1.9–2.8 (AUDIT §1). Eight SFX in total: chalk, erase, birds, river, wind, arrow, cry, bell (`chalk.sound`). There is no impact hit, no planned silence and no measurement of music against voice. | No sonic punctuation at the hook, turn or payoff. Dynamic loudnorm can pump the bed. |
| D8 | **QA does not check what matters for quality.** | **[M]** Only `format`, `loudness`, `black_freeze` and `speaker_consistency` can fail (`qa.py:201`). There is no check for target duration, frame 0, image content (border, text, duplicates, character) or safe zones. Caption overflow only warns, and C0005-te shipped 976/984 px lines against a 960 px budget. 28 of 40 QA reports are warn or fail, and G2 never reads the verdict (AUDIT F03, §19.1). | Defects reach G2 and publication, and no improvement can be measured. |

**Doc inconsistency to resolve separately [M]:** `CLAUDE.md` names Veena kavya as the Hindi voice, but `voices.json` and PROJECT_CONTEXT §22 say `maya2:Malini` (audit_summary). This plan does not touch voices.

---

## 2. Storytelling framework for 35–55 s (hard limit under 60 s)

### 2.1 Platform facts that shape it [F] (CDS §1.1)
- Since 2025-03-31, a Shorts view counts every start and replay. Engaged views (used for YPP earnings) exclude loops.
- A Short over 1 minute with any active Content ID claim is blocked globally.
- Instagram's top predictions are reshare, watch to the end and like.
- **[U]** The blog benchmarks ("70% viewed vs swiped", "50% drop before 4 s", "sends weigh 3–5× likes") are unofficial. Never use them as targets. Use the channel's own analytics once they work (AUDIT F08: the Analytics API currently returns 403).

### 2.2 Beats [R] (CDS §1.3, built on Hoyos's startle → curiosity → payoff and Loewenstein's information gap [F])

| Beat | Job | Rule |
|---|---|---|
| **H1** Hook-visual | Stop the scroll | Frame 0 shows the episode's most striking image, already readable, with an impact sound at 0.0 s |
| **H2** Hook-line | Open the main loop | A contradiction, a specific number or a stake, ≤12 EN words, with the first word at ≤0.3 s |
| **C** Context | Ground the viewer | Who, where and why in ≤2 shots, using only names the story needs |
| **E** Escalation | Raise the stakes | Answer one small question and open another. Pattern interrupt here |
| **T** Turn | Reversal or reveal | 0.3–0.6 s silence first. The verse card goes here if one is used |
| **P** Payoff | Close the main loop | Fastest cutting and the loudest moment, by 85–90% of runtime |
| **N** Next / loop | Cliffhanger and loop | One line opening the next question, with a final composition that matches frame 0 |

**Pattern interrupt:** change at least one of shot size, angle, accent, sound bed or rhythm every 6–8 s. Change all of them together only at the Turn.
**Open-loop cadence:** a question opened or answered every 8–12 s. This replaces the current "every 2 scenes" rule.

### 2.3 Beat timings per length [R] (CDS §1.3)

| Beat | 35 s ("anecdote") | 45 s (default) | 55 s (two-beat; dense episodes) |
|---|---|---|---|
| H1+H2 | 0.0–2.0 · 1 shot · 8–10 w | 0.0–2.0 · 1 · 8–10 w, then H2b 2.0–4.5 · 1 · 6–8 w | 0.0–2.0 · 1 · 8–10 w, then H2b 2.0–5.0 · 1 · 7–8 w |
| C | 2.0–8.0 · 2 · 14–16 w | 4.5–12.0 · 2 · 18–20 w | 5.0–13.0 · 2 · 20 w |
| E | 8.0–18.0 · 3 · 25 w | 12.0–22.0 · 3 · 25–28 w | E1 13.0–24.0 · 3 · 28 w |
| T | 18.0–25.0 · 1–2 · 15 w | 22.0–30.0 · 2 · 16–18 w | T1 24.0–33.0 · 2 · 20 w, then E2 33.0–43.0 · 3 · 25 w |
| P | 25.0–31.0 · 2 · 14 w | 30.0–40.0 · 3 · 20–22 w | 43.0–50.0 · 2–3 · 18 w |
| N | 31.0–35.0 · 1 · 8–10 w | 40.0–45.0 · 1 · 10–12 w | 50.0–55.0 · 1 · 10–12 w |
| **Shots / stills** | 10–11 / 6–8 | 12–13 / 8–10 | 15–16 / 10–12 |

Words (w) are EN/HI. Shots exceed stills because one still serves several shots through crops (§3.4).

### 2.4 Word budgets per language

**Measured rates [M]**

| Lang (voice) | Effective rate, pauses and transitions included (CDS §1.4, C0002–C0005) | Speech-only rate, C0005 scene WAVs (AUDIT §1) |
|---|---|---|
| en (Kokoro af_heart) | 2.55–2.67 w/s | 2.81 |
| hi (Malini) | 2.51–2.63 | 2.80 |
| gu (Malini) | 1.89–2.14 | about 2.3 |
| te (Malini) | 1.43–1.56 | 1.66 |

**Budget formula [R]:** `words ≤ rate_eff × (target − 1.0 s tail − verse_card_s)`, with planning rates of en 2.6, hi 2.6, gu 2.0 and te 1.5. Use the effective rate for writing budgets. Use the speech-only rate plus explicit pauses and 1.15 s of lead and tail inside the lint.

| Target | en | hi | gu | te | With a 3 s silent verse card, subtract |
|---|---|---|---|---|---|
| 35 s | 88 | 88 | 68 | 51 | 8 / 8 / 6 / 4 |
| 45 s | 114 | 114 | 88 | 66 | 8 / 8 / 6 / 4 |
| 55 s | 140 | 140 | 108 | 81 | 8 / 8 / 6 / 4 |

**Rules [R]**
- Never speed the voice up to fit. English already sits at the brisk end of audiobook pace (150–160 wpm [F]); cut words instead.
- Telugu is the longest language every time [M], so write it natively to its own budget. Keep the visual scene parity rule, and shorten te narration per scene rather than dropping scenes.
- Hard limits:
  - the lint rejects an estimated duration above 57 s per language;
  - final QA rejects anything ≥60.0 s;
  - final QA warns outside 35–55 s.
- **Verse recitation:** a full anuṣṭubh costs about 6–9 s in Hindi. Default to showing the verse on screen while the narration gives the meaning. Optionally recite one pāda (2–3 s) as the hook or payoff. Keep full recitation for a separate "Shloka" Short.

### 2.5 Scene and shot counts [R]
- About 9–10 narrated scenes (AUDIT §2.8). That saves about 4–6 min of image time per episode [M-derived: 85–108 s per image].
- 12–13 *shots* at 45 s via crops.
- Each shot lasts 0.8–5 s, set by emotion (§3.6).
- Lint thresholds: 8–11 scenes, each scene 2.5–7 s of narration (AUDIT §19.2).

### 2.6 Hook rules [R]
1. **Frame 0 is readable on its own, without sound.** Many viewers start muted, so the image and the first caption must carry the hook.
2. **First word at ≤0.3 s.** This needs the audio lead cut from 0.35 s to about 0.15 s (`studio.py:631-632`).
3. **Impact hit at 0.0 s**, together with the chalk snap. The tanpura starts with the hit, with no fade-in.
4. **Hook spoken length:** lint rejects above 3.0 s and warns above 2.2 s (AUDIT §19.2).
5. The existing 6-criterion rubric (`storytelling/SKILL.md`) still applies, with two added checks:
   - the visual hook check (does frame 0 alone make sense?);
   - hook-to-payoff distance (the main loop closes by 85–90% of runtime; "next episode" never counts as the payoff).
6. Build gaps on names the audience already knows. "Rama hesitated" is stronger than "Suketu's daughter" (Loewenstein [F]).

**Hook types that fit the series, using only verified lines (CDS §1.5)**
- *Contradiction:* "Rama's first enemy had the strength of a thousand elephants. And he did not want to kill her." (1.24.26, 1.26.12)
- *Request with a twist:* "A king promised a sage anything. The sage asked for his son." (C0004)
- *Text versus belief:* "Every TV Ramayana shows the Lakshman Rekha. Valmiki never wrote it." Use at most once every 4–5 episodes, with a respectful frame.
- *Sensory in medias res:* open on the bowstring twang (1.26.6–8), with image and sound only for 0.8 s.

### 2.7 Loops and cliffhangers [R] (CDS §1.6)
- **Order:** close this episode's loop first, then open the next one with exactly one line. The "Next:" card stays at ≤3 words.
- **Use one loop type per episode:**
  - *Composition loop:* the last shot reuses frame 0's framing (same `image`, or the same shot and angle).
  - *Sentence loop:* the last line flows grammatically into the first. Never cut mid-word; that reads as an error in hi, gu and te.
  - *Sound loop:* the music ends on the note the intro starts on.
- **Engagement prompt:** at most one, ≤6 words, with a real answer in the text ("Which sage cursed her?"). Otherwise move it to the pinned comment.
- **Series glue:** a fixed 0.5 s end sting (the same chalk snap and bell every episode) and a small "Ep N" badge in the top 12%.

### 2.8 Accuracy rules

**Citations [F/R]** (CDS §2.1)
- **[F]** The project verifies against the vulgate (southern recension; sa.wikisource and valmikiramayan.net).
- **[F]** The Baroda Critical Edition (CE) and Goldman's Princeton translation number some verses differently. *Mā niṣāda* is CE 1.2.14 but vulgate 1.2.15.
- **[R]** Cite as `VR <kāṇḍa>.<sarga>.<verse> (vulgate)`, adding `[CE x.y.z]` only when checked against the CE or Goldman.
- **[R]** Put the edition in `script.json` `sources`, e.g. `"edition": "vulgate (sa.wikisource)"`.
- **[R]** For a line absent from the CE, say "found in the southern manuscripts", not "Valmiki says".

**No invented quotes [R]** (CDS §2.3)
- Reported speech is fine. Every `"` in narration needs a `quote_src` locator, and the lint rejects it otherwise.
- Never present TV dialogue or Ramcharitmanas chaupais as Valmiki.
- Add no motives the text lacks. Valmiki gives Dasharatha's fear and the "not yet sixteen" line (1.20.2), not a modern "father's heartbreak".

**Popular retelling versus Valmiki, summarised [F]** (verified in CDS §2.2; sources there)

| Popular version | In Valmiki | Origin |
|---|---|---|
| Lakshman Rekha | Absent | Ramcharitmanas mentions it only in Laṅkā Kāṇḍa 35.1 (Mandodari); TV made it central |
| Ahalya turned to stone | Unseen by all, living on air, lying on ash (1.48) | Adhyātma Rāmāyaṇa and later |
| Shabari's tasted berries | Roots and fruits as hospitality; no tasting | Later regional retellings |
| Swayamvara with assembled kings | Sita *vīryaśulkā*: kings had failed individually earlier, and Rama breaks the bow on Vishvamitra's visit | Ramcharitmanas staging, TV |
| Ravana lifts Sita with the earth | He seizes her physically | Kamba Ramayanam |
| Maya Sita | Absent | Bhakti retellings |

- **[U] Check in the text before using:** the squirrel at the setu, Hanuman's gada, the name "Kodanda", and the verses for Lanka as a golden city.
- **Framing [R]:**
  - say "In Valmiki's telling…", never "myth busted";
  - name later traditions with respect ("Tulsidas, centuries later…");
  - each difference must be accurate in both directions;
  - in gu and te, nod to Giridhar or Molla only where they agree with Valmiki.

**Ravana with depth [F/R]** (CDS §2.5)
- **[F] Text anchors:**
  - 5.49.17–18: Hanuman marvels at Ravana's form, courage and radiance; "if [he] were not so strong in adharma, he could be the protector even of the gods' world";
  - 5.18.2–3: Vedic chanting at dawn in Ravana's realm;
  - 3.35.9 and 6.71.27 (*Daśagrīva*): the ten heads.
- **[R]** Show splendour, learning, power and *choice*: greatness undone by adharma. Do not adopt Ravana-as-hero readings.
- **[R] Visual:** keep the existing symbolic rule. A proposed evolution, subject to owner approval: ten crowned heads as a layered silhouette row, two visible arms, no third eye, ancient Indian royal ornaments, and nothing Mughal-coded (the *Adipurush* backlash [F]).

**Sensitivity checklist [R]** (CDS §2.6)
- Rama calm, never snarky.
- Sita never sexualised.
- Mutilation and gore off-screen (shadow or cut-away).
- Hanuman never comic.
- Deities as symbols.
- No political tie-ins.
- Pilgrimage sites named neutrally.

**Pronunciation [R]:** use the per-scene `tts` override (`studio.py` `sc.get("tts", sc["narration"])`) for English respellings such as "Raama", "Seetaa", "Raavana" and "Maareecha" (full table in CDS §2.4). Recite Sanskrit verses with the schwa kept.

### 2.9 Illustration only: Ep05 (Tataka) at about 45 s [R]
This is not a replacement script. Ep05 is already produced, and any new version would need G1. It shows how the framework and the shot fields fit together (full table in CDS §3.7).

| # | t (s) | Shot / move | Reveal / transition | Narration (EN) | Sound |
|---|---|---|---|---|---|
| 1 | 0–2.0 | ECU silhouette of Tataka's eyes, low, push 1.0→1.15 | instant / — | Rama's first enemy had the strength of a thousand elephants. | impact at 0.0, wind |
| 2 | 2.0–4.5 | OTS Rama from behind, slow push | fast / cut | And he did not want to kill her. | drone; melody out |
| 3 | 4.5–8.5 | EWS tangled forest, tilt down | draw / erase | Vishvamitra led the princes to a forest no one dared enter. | wind bed |
| 4 | 8.5–12 | WS ruined fields, shadow, truck right→left | fast / cut | Once rich land, laid waste by the yakshi Tataka. | rumble |
| 5 | 12–17 | MS Vishvamitra; lotus-of-light insert | fast / match | Her strength was a boon from Brahma. Her hunger for men, a curse from Agastya. | bell |
| 6 | 17–21 | verse card 1.25.18 | draw / erase | To protect the people, said the sage, a protector must act. | sparse tanpura |
| 7 | 21–23 | ECU bowstring, low | instant / cut | Rama twanged his bowstring. | twang, shake |
| 8 | 23–25.5 | low-angle WS, Tataka from dust | instant / dust | The forest shook, and she charged. | drums in |
| 9 | 25.5–29.5 | CU Rama's hand easing the draw | fast / cut | Still he told Lakshmana, I will only stop her. | drums out |
| 10 | 29.5–33.5 | WS dust and rock storm, Dutch 5° | fast / whip | She raised a storm of dust and rocks, then vanished into illusion. | wind, rocks |
| 11 | 33.5–37 | near-black dusk, slow push | instant / black | Dusk was falling. Rama aimed by sound alone. | 0.5 s silence, heartbeat |
| 12 | 37–39 | POV arrow streak | instant / whip | One arrow. | arrow, impact, silence |
| 13 | 39–45 | EWS with the framing of #1, forest blooming, petals, pull-out | draw / cut | The cursed forest bloomed again. And next morning, the sage gave Rama divine weapons. | birds, unresolved bansuri |

- **Totals:** about 120 words ≈ 46 s, 13 shots from about 10 stills, 3 erases and 3 draws.
- **Accuracy flags for G1:**
  - "hunger for men" rests on 1.25.10–13;
  - Valmiki's "stopping" (1.26.12–18) involves maiming, so any added detail must cite 1.26.17–18.

---

## 3. Visual direction

### 3.1 Series visual bible: constants (never vary) [M/R]
- Procedural black board (`make_board`), chalk texture and stroke reveal (`chalk_from_image`, `reveal_order`).
- **Palette:** chalk white plus at most 2 accents per frame, chosen from the house set plus one approved world hue (§3.2).
- **Fonts:** Chalkduster titles, gold (226,190,112), with a dark halo (`title_layer`). ChalkboardSE captions (`styles.py` chalk: size 76, y 0.75, 4 words per group, white active, (200,198,190) idle, saffron (246,168,82) keywords).
- **Composition:** title headroom in the top 12%, captions in the lower 25%, subject centred, no frames or borders, no text in images.
- **Depiction:** ancient Indian architecture (no onion domes or minarets), deities symbolic, Rama from behind (`ramayana.json` `rules`).
- **Sound constant:** `CHALK_SFX_GAIN = 0.035`.
- **Screen direction [R]:** Rama's party moves left → right (towards Lanka), and threats enter right → left, consistently across episodes.

### 3.2 Per-world accents (the board stays black) [R] (CDS §4.2)

| World | Mood | Accent hues (HSV degrees; `PALETTE_HUES` today: 27 saffron, 42 gold, 95 green) | Prompt add-ons (positive only) | Overlays | Light |
|---|---|---|---|---|---|
| Ayodhya | golden, serene, ordered | 42 + 27 | carved stone gateways, stepped shikhara towers, pillared halls, Sarayu river, banners, symmetrical | soft motes, banner flutter | morning, from the top-left |
| Ashram / forest | living, sacred; dangerous at dusk | 95 + 42 (yajña fire) | thatched huts, fire altar, banyan and sal trees, deer | leaves, smoke, fireflies | dappled, orange at dusk |
| Mithila | festive, cultured | 27 + 95, with Madhubani-style pattern fills *inside* objects (fish, lotus, double lines), never as a border | palace courtyard, painted walls with fish and lotus motifs | petals | warm, even |
| Lanka | monumental, splendid, smoky, ominous; **not cartoon-evil** | **crimson ≈ 0–8 (new)** + 42; 95 only in the Ashoka grove | towering golden fortress on a sea cliff, vast pillared halls, lamps, smoke | embers, smoke, sea spray | low, from lamps and fire; warm gold for the dawn-chant scenes (5.18.2) |
| Battle | kinetic, dusty, dusk | 27 + crimson, dust grey | dust clouds, banners, arrows in flight, chariots | dust storm, embers, arrow streaks | backlit dusk silhouettes |
| Divine | radiant, abstract | 42 + white glow | radiant lotus of light, rays | god rays, flash-white | central bloom |

**Engineering [M→R]:**
- `restrict_palette(rgb)` reads the global `PALETTE_HUES`.
- Change it to `restrict_palette(rgb, hues=PALETTE_HUES)`, thread `hues` through `chalk_from_image(img, seed, hues)`, and resolve them in `render()` from the scene's `accent`. A world map in `profiles/characters/ramayana.json` (e.g. `"worlds": {"lanka": [4, 42]}`) is one option.
- Allow ≤3 hues per frame. The default is unchanged when `accent` is absent.

### 3.3 Complementary treatments [R] (CDS §4.3)
All of these stay on the black board with chalk texture and the house fonts; only the line language changes. **Rule: at most one non-default treatment per episode, covering ≤25% of runtime, and the payoff always returns to detailed chalk.**

| Treatment | Narrative purpose (the only time it is used) | Pipeline method |
|---|---|---|
| Detailed chalk (default) | Main narrative present | current `styles.py` prefix |
| Kalamkari-line chalk | Tale within the tale: a sage narrating backstory (Tataka's origin 1.25, Ahalya 1.48), Puranic flashback | positive add-on "flat ornamental figures, flowing outlines, patterned garments, profile faces, Kalamkari temple-cloth style, drawn in chalk"; `reveal: ghost`. **[F]** precedent: Srikalahasti Kalamkari Ramayana cloths |
| Mewar continuous narration | Journeys and multi-event recaps | one tall still with 3–4 events stacked top to bottom; a slow tilt passes through them; one still covers 8–10 s. **[F]** precedent: Mewar Ramayana 1649–53 |
| Motion-comic panels | Confrontation or simultaneous action | 2–3 chalk-ruled panels drawn in sequence, reusing crops |
| Cinematic chalk impact frame | The 1–2 biggest action beats | heavy contrast, chalk speed lines, ECU, shake. Never prompt "anime" |

**[U]** Base-model quality on these styles is untested. A 4-style × 4-image Z-Image test costs about 30 min (VT §5).

### 3.4 Character design system and consistency method

**Design rules [R]** (CDS §4.4)
- **Silhouette-first:** every recurring figure must read as a solid silhouette:
  - Vishvamitra: staff, matted hair, deerskin;
  - Valmiki: white beard, topknot;
  - Dasharatha: crown, short beard;
  - Rama: bow on shoulder, from behind;
  - Lakshmana: bow and quiver;
  - Tataka: two arms, wild hair;
  - Ravana: row of crowns (§2.8).
- **Accent ownership:** Rama saffron sash, Lakshmana green, Sita gold, sages white or ochre, Kaikeyi crimson-gold, Ravana crimson and gold.
- **Prop in every shot of a character**, inserts included: bow, staff, beads, veena, kamandalu.
- **Age tracks:** `rama_teen` until the marriage arc, then `rama_adult` with the same accent and props.

**Consistency method, in order [R]**

| Step | What | Component | Evidence / status |
|---|---|---|---|
| 1 | **Character tokens.** `visual` contains `{vishvamitra}`, and `step_images` expands it verbatim from `ramayana.json` `characters.<id>.prompt`. This ends copy drift. | `studio.py step_images` (prompt build at :304-306) | **[M]** no link exists today. Deterministic and free |
| 2 | **Positive-only prompts.** Rewrite negations as positive descriptions ("a silhouette of a rakshasi with two arms and flowing hair"). Drop `--negative-prompt` for Z-Image Turbo, or keep it knowing it is inert. | `styles.py` chalk `prefix`/`negative`; scriptwriter and creative-director guidance | **[M]** negatives are ignored (D5) |
| 3 | **Reference sheets.** For each recurring figure, three owner-approved stills (from behind, three-quarter, silhouette), stored with the canonical prompt, 2–3 good seeds and notes. | `profiles/characters/refs/<id>/` (new). The files are media, so keep them out of git and record their hashes in `ramayana.json` | **[R]** |
| 4 | **FLUX.2 [klein] 4B reference conditioning.** Pass up to 4 reference images plus the scene prompt, and use edit passes to remove stray borders and figures. | new `scene_with_refs` path in `step_images`, via mflux (installed; MIT) | **[F]** Apache-2.0, ungated (re-verified 2026-11-16). M1 Max: 1024² t2i 21–32 s, edit with reference about 52–53 s; hair colour drifted in that test (VT §1). **[U]** M5 Air time and peak RAM unmeasured. Measure with `/usr/bin/time -l` at 768×1344 before adopting. Never run it alongside Z-Image or a voice model |
| 5 | **Drift flag.** DINOv2 cosine similarity of each character-bearing raw image (`img/NN_raw.png`, before chalk conversion) against the sheet, below a calibrated threshold, flags the scene for a human. | new visual-QA check in `pipeline/qa.py` | **[R]** (AUDIT §2.7). Flag only, never an auto-reject |
| 6 | **Optional LoRAs.** A chalk-style LoRA (fixes "shaded pastel, not line art") and per-character LoRAs on Z-Image base or klein base 4B via `mflux-train`. | overnight solo run | **[U]** no Apple Silicon time or RAM figures; a CUDA reference shows about 10 GB. Pilot 500–1000 steps at 512 px |

**Excluded [F]** (VT §1): IP-Adapter, InstantID, PuLID and InfiniteYou. They are either non-commercial (insightface or NC weights) or built for photoreal faces.

### 3.5 Shot grammar: per-scene fields and validator [R] (CDS §3.6)
These fields are optional additions to each scene in `script.json`. Every default reproduces today's behaviour, so old scripts render unchanged.

| Field | Values | Default (today's behaviour) | Consumed by |
|---|---|---|---|
| `shot` | `EWS WS MS CU ECU insert silhouette map text` | none | lint, prompt hint |
| `angle` | `eye low high ots pov dutch` | `eye` | prompt hint; `dutch` rotates in `cam_matrix` |
| `move` | `{"type": static\|push\|pull\|tilt\|truck\|parallax\|dollyzoom\|shake\|whip, "z": [a,b], "ease": "inout"}` | alternating zoom 1.00–1.10 | `chalk.render` camera block, `cam_matrix` |
| `reveal` | `draw fast instant ghost` | `draw` (scene 0 at 1.6 s) | `chalk.plan()` draw duration |
| `transition` | `cut erase match dust flash black whip wipe` | `erase` | `chalk.plan()` vs/ds windows; `render()` transition branch; `sound()` erase SFX |
| `image` + `crop` | still id + `[cx, cy, width_frac]` | own still | `render()` before `chalk_from_image`; `step_images` skips scenes that reuse a still |
| `dur_hint` | seconds | from narration | lint |
| `hit` | `{"name": "impact", "at": 0.0}` | none | `chalk.sound` |
| `overlay` | `dust embers smoke petals rain godrays` | ambient motes | new overlay layer in `render()` |
| `accent` | world key or hue list | global hues | `restrict_palette` |
| `music` | `{"cue": "drop\|swell\|unresolved", "leitmotif": "rama"}` | `melody`/`swell` fields | `chalk.music` |
| `quote_src` | verse locator | none | lint |

**Validator rules (pre-render lint, then G1) [R]**
1. Estimated duration ≤57 s per language, and words ≤ that language's budget (§2.4).
2. Scene 1: `reveal` is `instant` or starts ≥70% drawn; a `hit` at 0.0; first word ≤0.3 s; hook spoken length ≤3.0 s.
3. At least 3 distinct `shot` sizes, and no more than 2 consecutive shots with the same `shot` and `move`.
4. `erase` used 1–3 times; `draw` reveal used ≤3 times.
5. A pattern interrupt (shot size, accent, bed or rhythm) at least every 8 s.
6. Final shot: `music.cue = unresolved`, and composition matches scene 1 (same `image`, or the same `shot` and `angle`).
7. Every quoted line has a `quote_src`, and every verse card has a `source` with its edition.
8. At most one non-default treatment, covering ≤25% of runtime (§3.3).
9. `crop` `width_frac` ≥0.5 unless the scene has its own insert still. Source width is 768 px [M], so ECU crops beyond 2× need a dedicated insert.

### 3.6 Faking cinematography with stills [R] (CDS §3.2–3.5, VT §3–5)

**Moves (all inside `chalk.render`)**

| Move | How | Use |
|---|---|---|
| Push / pull | interpolate `z` (e.g. 1.00→1.20) in `cam_matrix` | push builds emotion; pull reveals scale or isolation |
| Tilt | interpolate focus y along the 2112 px canvas | towering subjects; reveal a fortress top to bottom; Mewar stills |
| Truck | interpolate focus x; strongest with parallax | travel, chase |
| Shake | 4–10 px decaying noise on `jx, jy` for 0.3–0.5 s | impacts (bowstring, arrow, rocks) |
| Dutch | add a rotation argument to `cam_matrix` (4–8°) | illusion, curse; ≤2 s, rare |
| Whip | 6–10 frames of horizontal motion blur across the cut | action transitions |
| Snap push | 0.2 s push after a silence | reveal or turn |
| Dolly-zoom | foreground plane fixed, background plane scales (needs planes) | once per arc, for shock |
| Rack focus | blur one plane, sharpen the other (needs planes) | shift of attention |

**Multiplane parallax ("Kid Stays in the Picture" [F]) [R]**
1. After `chalk_from_image`, get a figure mask from BiRefNet (MIT, automatic) or SAM 2.1 small (Apache-2.0, box-prompted). Optionally add a Depth Anything V2 *Small* depth map (Apache-2.0, re-verified). Load each model in turn and unload it.
2. Quantise into 2–3 planes: figure, mid and far. The board moves with the far plane, so the chalk never detaches from the board.
3. Warp each plane with its own matrix (e.g. far 1.00→1.03, figure 1.00→1.08 plus 10–20 px drift). Fill thin disocclusions with `cv2.inpaint` or a dilated far plane. The board is procedural, so no background inpainting is needed (VT §3).
4. Parallax starts once a plane has been drawn.
5. QA: SSIM between consecutive frames to catch tearing.
- **[U]** Monocular depth on chalk stills is unvalidated. If depth is noisy, fall back to mask-only two-plane parallax.
- **Licence traps [F]:** Depth Pro and ml-sharp weights are research-only, Depth Anything V2 Base/Large/Giant are CC-BY-NC, and DepthFlow is AGPL. Write our own renderer, estimated at about 150–250 lines.

**Procedural "alive" motion and overlays [R]** (own numpy code, zero licence risk)
- Figure-mask breathing: 0.5–1% vertical scale at about 0.25 Hz.
- Sway via `cv2.remap` inside a soft mask, and hair or cloth flutter at the top of the mask.
- Embers, smoke wisps, petals (1.26.27), dust or rock storm (1.26.15–20), god-ray sweep and rain, all extending the existing `Particles` class.
- Skip blinking; chalk eyes are too small.
- The owner judges whether this reads as charming or uncanny.

**Reveal modes [R]** (a chalk-specific axis, set in `plan()`)

| Mode | Draw time | Use |
|---|---|---|
| `draw` | 2.0–3.6 s (today's formula) | ≤3 per episode: first appearance of a character, the verse card, the final image |
| `fast` | 0.5–0.8 s | default for story shots |
| `instant` | 0, with a dust puff covering the cut | frame 0, action, inserts |
| `ghost` | previous ghost morphs into the new image over 0.4 s | "meanwhile", memory, tale within the tale |

**Pacing per emotion [R]** (CDS §3.5)

| Emotion | Average shot | Move | Reveal | Sound |
|---|---|---|---|---|
| Awe | 3.5–5 s | slow tilt or pull | draw or fast | swell, drone |
| Context | 2.5–3.5 s | gentle push | fast | calm bed |
| Suspense | 2–3 s, then one held 4 s shot | slow push, no jitter | fast | drone only |
| Action | 0.8–1.5 s | shake, whip, POV | instant | percussion, hits on cuts |
| Turn | 0.4 s silence, then 2–3 s | snap push | instant | hit, then silence |
| Grief | 4–6 s | static or slow pull | ghost | thin bansuri, no drums |
| Divine | 3–4 s | slow push with god rays | draw | glissando and bell |
| Cliffhanger | 2.5–4 s | slow push, then hard cut | fast | unresolved note |

**Not worth it now [F/R]** (VT §2, §4)
- Video diffusion: LTX-2.3 int8 via ltx-2-mlx takes 10–15+ min per 4 s clip on 16 GB and risks style drift. At most one owner-judged hero-shot test, much later.
- Wan 14B, LTX-2.5, FramePack and Hunyuan: too heavy or licence-restricted.
- Upscalers, frame interpolation, LUT packs, anime models, Remotion/Node stacks: low value or against the rules.

---

## 4. Sound direction

### 4.1 Facts [F/M]
- **[M]** Today's chain:
  - narration scenes are concatenated with a 0.35 s lead, per-scene `pause` (default 0.18) and a 0.8 s tail;
  - music comes from `chalk.music` (tanpura at Sa = 146.83 Hz plus Bhairavi-coloured bansuri phrases `intro calm love grief rise` and `swell`);
  - ducking is `1 - 0.45·clip(env/0.05)` with a 0.25 s window, and `music_gain` is 0.25;
  - SFX come from `chalk.sound`;
  - the mix is peak-limited to 0.98, followed by single-pass `loudnorm` in the encode (`studio.py:630-705`).
- **[M]** Results: −15.2 to −14.7 LUFS, TP −1.5 to −1.4 dBFS, LRA 1.9–2.8 (AUDIT §1). QA band −16.5 to −13 LUFS, TP ≤−1.0 (`qa.py:11`).
- **[F]** Neither YouTube nor Meta publishes a Shorts/Reels loudness spec. −14 LUFS is a convention, and YouTube only turns loud uploads down (AUD §A4).
- **[F]** Any Content ID claim blocks a Short over 1 min globally. Procedural music carries no claim risk (CDS §5.1).
- **[F]** Local ffmpeg 9.0.1 has `loudnorm`, `sidechaincompress`, `acompressor`, `deesser`, `adynamicequalizer`, `alimiter` and `ebur128` (AUD).

### 4.2 Hierarchy and targets [R] (CDS §5.2)
1. **Narration** is always intelligible and is the loudness anchor.
2. **SFX** are synced to visual events and placed between narration phrases where possible.
3. **Music** is a bed under speech, swelling only in gaps.

| Element | Target |
|---|---|
| Music under speech | −18 to −22 dB below narration; QA warns below 12 dB of separation (AUDIT §19.2) |
| Music in gaps | rises 4–6 dB (via the ducker release) |
| SFX one-shots | peak 3–6 dB under narration peaks |
| Chalk SFX | `CHALK_SFX_GAIN = 0.035`, unchanged |
| `music_gain` | stays 0.25 as the baseline; shape with ducking rather than a lower global gain |
| Planned silences | 2–3 per episode, 0.3–0.8 s: before the Turn, before the Payoff, optionally before Next |

### 4.3 Per-moment recipes [R] (CDS §5.4)

| Moment | Recipe |
|---|---|
| Opening (0.0 s) | Low drum and sub `impact` plus chalk snap at frame 0. Tanpura starts with the hit. First word at 0.2–0.3 s. The bansuri intro enters *after* the hook line |
| Divine reveal | 0.4 s with all beds out, then an upward glissando, a bell, a phrase resolving to Sa, a flash-white transition and god rays |
| Suspense | Melody out. Drone plus a heartbeat pulse at 60–70 bpm plus wind. Short phrases, then silence before the reveal |
| Battle | Percussion ostinato at 120–140 bpm, whooshes and impacts on cuts, hard ducking under lines, then everything out for 0.3 s before the decisive blow and a single hit |
| Grief | No percussion, low slow bansuri, `pause` 0.5–0.8, dip to black, bed slightly lower |
| Royal / auspicious | Reed-like phrase and a bell, brighter scale |
| Illusion | Detuned shimmer, reversed swells |
| Cliffhanger | Phrase ends on Re or Ma (not Sa), then a hard cut to the 0.5 s series sting |

### 4.4 Leitmotifs on the existing raga engine [R] (CDS §5.5)
Add named motifs to the `phrases` dictionary in `chalk.music()`, driven by `music.leitmotif`. Keep Sa = 146.83 Hz constant across the series so motifs stay recognisable.

| Motif | Shape | Timbre | Rasa |
|---|---|---|---|
| Rama | Rising 4-note phrase, resolved (Sa Re Ga Pa / Pa Ga Re Sa) | bansuri (exists) | vīra, śānta |
| Sita | Ornamented, higher register | bansuri or santoor-like pluck | śṛṅgāra, karuṇa |
| Lakshmana | Rama's motif one beat behind (canon) | plucked | vīra |
| Sages | Drone and a single bell | tanpura and bell | śānta, adbhuta |
| Ravana / Lanka | Low descending phrase with komal degrees (Malkauns or Darbari colour) | low bowed drone, never a "villain synth" | raudra, bhayānaka, grandeur |
| Hanuman | Energetic rising run with pulse | percussion and bansuri | vīra, adbhuta |
| Battle | 7- or 8-beat ostinato | drums | vīra, raudra |

- **[F]** Raga–rasa links are traditional, "not an exact science" (CDS §5.1).
- **[R]** Shehnai, sarangi and nagada are hard to synthesise. Options are procedural percussion only, CC0 one-shots, or model beds (§4.7).

### 4.5 SFX sync rules [R] (CDS §5.3)
- Cue SFX on the **visual frame** of the event. Use the existing `word` + `offset` mechanism only when the narration names the sound (the C0005 arrow cue uses −0.35 s).
- An impact always lands on a cut. Implement the `hit` field in `chalk.sound` relative to the scene's `vs`.
- Ambience beds fade in over 0.5 s (exists) and must change at every erase, to mark a change of place.
- **New procedural one-shots** (numpy, like `sfx_arrow`/`sfx_bell`): `impact`, `bowstring`, `whoosh`, `rumble`, `rocks`, `conch`, `swarm` (glissando), `heartbeat`, plus beds `fire`, `army`, `sea`. Register them in the dispatch dicts inside `chalk.sound`.

### 4.6 Mix chain (target order) [R] (AUD §A4)

| Step | What | Where |
|---|---|---|
| 1 | Normalise the narration stem to −16 LUFS before mixing, so music gain behaves the same for Kokoro and Malini | end of the voice concat in `step_audio`. pyloudnorm (MIT) or ffmpeg `loudnorm` measurement plus a linear gain |
| 2 | Optional voice polish, A/B by ear: `highpass=f=70`, gentle `deesser` (or `adynamicequalizer` at 6–8 kHz), `acompressor=threshold=-20dB:ratio=3:attack=5:release=80` | on the voice stem. **Risk:** TTS is already compressed, and over-processing Indic sibilants is the main danger |
| 3 | Sidechain ducking: keep the numpy ducker, or replace it with `[music][voice]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300`. Tune for −18 to −22 dB under speech and a 4–6 dB swell in gaps | `step_audio` (`duck` lines :660-673) |
| 4 | SFX bus summed as today; chalk gain untouched | `chalk.sound` |
| 5 | **Two-pass loudnorm, linear.** Pass 1: `loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json` on `mix.wav`. Pass 2: feed `measured_I/TP/LRA/thresh/offset` back with `linear=true`. This replaces the dynamic single pass at `studio.py:705` | measure in `step_audio`, apply in `step_render` |
| 6 | QA: integrated loudness within −14 ±0.5; TP ≤−1.0; new music-under-speech metric | `pipeline/qa.py` |

### 4.7 Sources and model tests

**Licensed libraries [F]** (AUD §A2)

| Source | Terms | Use |
|---|---|---|
| **Sonniss GDC 2026 bundle** (347+ files, 7.47 GB) | royalty-free, commercial, "no attribution required", monetised YouTube explicitly allowed; no redistribution as SFX; **no AI/ML training** | download once; keep outside git; log in a `licenses.csv` (file, URL, licence) |
| **Freesound, CC0 filter only** (`f=license:"Creative Commons 0"`) | per-sound licence; CC-BY-NC and Sampling+ forbidden for a monetised channel | CC0 counts on the research date: tanpura 179, tabla 150, temple bell 91, harmonium 59, sitar 36, bansuri 21, conch 14, veena 9, shehnai 0. Audition every file |
| YouTube Audio Library ("attribution not required") | copyright-safe on YouTube; no Google guidance for other platforms | YouTube uploads only, never Reels |
| Avoid | Pixabay music (Content ID exposure), BBC SFX (non-commercial), Incompetech/FMA (attribution, overuse), Demucs output (unclear weights licence) | — |

**Music model tests [F/R]**

| Model | Licence [F] | Fit [F] | Test [R] |
|---|---|---|---|
| **ACE-Step 1.5** (2B turbo + 0.6B LM, MLX) | MIT code and weights; outputs commercial per the card | 8–12 GB with the 0.6B LM; no published Mac timings | Generate 3 beds × 2 moods (devotional calm, suspense), 30–40 s each, then loop or crossfade. Record peak RSS. Run alone, with progress updates |
| **Magenta RealTime 2** small (230M) | Apache-2.0 code, CC-BY-4.0 weights; "Google claims no rights in outputs" | real-time on any Apple Silicon including the Air; `mrt mlx generate` | same prompts; A/B against ACE-Step and the procedural raga |

- **Pass criteria [R]:**
  - the owner prefers it blind over procedural in at least 2 of 3 moods;
  - it sits under the numpy tanpura without clashing with Sa = 146.83 Hz;
  - no vocals or artifacts.
- **[U]** No model documents raga or Indian-instrument quality.
- **Excluded [F]:** MusicGen and AudioGen, AudioLDM2, Tango and TangoFlux, and MMAudio (all non-commercial weights). Stable Audio 3 is "maybe" only (revocable licence, <$1M revenue cap).

---

## 5. Editing, captions and transitions

### 5.1 Editing rhythm [R]
- Cut first for emotion, then story (Murch's Rule of Six [F]: emotion 51%, story 23%, rhythm 10%, eye-trace 7%).
- On 9:16, keep the subject of consecutive shots in roughly the same screen zone so the eye does not hunt.
- Default inside a beat: **hard cut**. The chalk texture keeps the identity, and the ghost carry-over is dropped on cuts.

### 5.2 Transitions with meaning [R] (CDS §3.4)

| Transition | Meaning | Budget |
|---|---|---|
| Cut | continuity inside a beat | default |
| **Erase** (signature, `ERASE = 0.55`) | time or place jump, chapter break | 1–3 per episode: after the hook, at the Turn, before Next |
| Match cut | thematic link (bow arc → crescent moon; arrow → falling rock) | as the story offers |
| Dust blow-out | action continuity; the impact dust covers the cut | action beats |
| Flash white (6 frames) | divine or supernatural | divine moments |
| Dip to black (0.4–0.8 s) | death, grief, curse | rare |
| Whip | speed, chase | battle |
| Chalk-stroke wipe or sponge | turn the page; journeys | rare |

**Implementation [M→R]:**
- `plan()` hardcodes `vs = start − ERASE` for every scene after the first.
- Make `vs`/`ds` depend on `transition` (cut: `vs = ds = start`).
- Branch the `if i > 0 and t < p["ds"]` block in `render()` per transition type.
- Emit `sfx_erase` in `sound()` only for erase transitions.
- Keep `black_freeze` QA in mind: a dip to black must stay under its threshold.

### 5.3 Captions [M/R]
- **[M] Keep:**
  - word-synced groups (`caption_groups`, `studio.py:360`; timing from `align_words` Whisper word timestamps plus difflib, `:580-622`);
  - Indic postposition rule (`POSTPOSITIONS`);
  - `caption_max_chars` en/hi 24, gu 22, te 20 (`profiles/languages/*.json`);
  - y = 0.75, 4 words per group, saffron keywords.
- **[R] Changes:**
  1. **Overflow becomes a failure, not a warning.** Fail above W−60 px (today it warns at `qa.py:132`) and auto-split in `caption_groups`. Rationale: te shipped 976/984 px lines.
  2. **Glyph-coverage check.** Every narration and verse character must be in the chosen font's cmap. This prevents tofu (missing-glyph boxes).
  3. **Hook captions.** The first group shows by 0.3 s. Use 2–3 words per group for the hook only, so the opening line reads at a glance when the video starts muted.
  4. **One share line per episode,** visually emphasised: keyword colour plus the gold title (`emphasis`). For example "In Valmiki, there is no Lakshman Rekha."
  5. **Safe zones.** Render the Shorts/Reels UI mask onto the contact sheet. Keep captions inside it and titles inside the top 12%.
  6. **Later:** forced alignment against the known script for Indic languages, for more exact timing. **Trap [F]:** MMS aligner checkpoints are CC-BY-NC (AUDIT §2.11).
- Do not switch caption engines. pycaps and captacity would regress Indic shaping (VT §4).

### 5.4 Titles and series furniture [R]
- `emphasis` titles at ≤3 words.
- "Ep N" badge in the headroom.
- 0.5 s end sting (same chalk snap and bell each episode).
- The "Next:" card stays at ≤3 words and is drawn with a `fast` reveal.

---

## 6. Prioritised change list

**How to test every OWNER item:**
1. Render variant A (current) and variant B (change) from the *same existing assets* of one already-produced episode (C0005 en is the default) into a scratch directory.
2. Make no re-upload and no change to published files.
3. Show the owner a side-by-side clip and contact sheet, plus the objective metric listed.
4. After adoption, compare engaged-view and completion metrics only once analytics work (AUDIT F08) and the sample allows. Do not claim an effect before then.

### P0: no engine change (do first)

| # | Change | Why (evidence) | Component | Free? | Requirements | Expected benefit | Risk | Test / metric | Class |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Encode the 35–55 s target, beats (§2.2–2.3), word budgets (§2.4), loop rules, citation and edition labels, and `quote_src` | D1 [M] | `.claude/skills/storytelling/SKILL.md` (60–90 s → 35–55 s; "9–14 scenes" → 8–11), `.claude/agents/scriptwriter.md`, `creative-director.md` | yes | none | completion; about 40% less voice, image, render and QA time | scripts feel rushed if words are cut badly | next script: estimated vs rendered seconds per language, all ≤57 s | SAFE (owner's stated target) + G1 per script |
| 2 | `pipeline lint <ID>`: duration per language, hook length, scene count, words, quote sources, edition labels, visual parity, digits in gu/te, shot-grammar rules 3–9 (§3.5) | D1, D8 [M] | new `pipeline/lint.py`; `__main__.py` `approve script` requires a pass | yes | measured w/s per voice (§2.4) | defects caught before G1 | rate drift per voice; recalibrate from each new render | lint estimate within ±3 s of the rendered duration on C0004 and C0005 (all 4 languages) | SAFE |
| 3 | Final QA: duration ≥60.0 s rejects, outside 35–55 warns; caption overflow > W−60 fails; glyph coverage fails; first-frame non-board share warns | D2, D8 [M] | `pipeline/qa.py` (`STANDARD`, `check_captions` :111) | yes | none | stops shipping known defects | false positives on the first-frame metric | run on all 20 existing renders: all 20 must fail duration; te C0005 must fail overflow | SAFE |
| 4 | Positive-only prompt rewrite + deterministic border auto-crop (edge-band luminance > interior + 0.25) | D5 [M] | `styles.py` chalk `prefix`; `studio.py step_images` (after generation) | yes | none | shorter prompts, fewer manual crops | crop could clip a real edge element | re-crop the existing C0001–C0005 raws offline: border detections versus the manual crop list | SAFE |
| 5 | `{character}` token expansion from `ramayana.json` | D4 [M] | `studio.py step_images` :304-306; scriptwriter and creative-director docs | yes | none | ends prompt copy drift | none | unit test: expanded prompt equals the bible text verbatim | SAFE |
| 6 | Planned silences, end sting text and engagement-line rules in scripts (pause values only) | D7 | `script.json` `pause` | yes | none | pattern interrupts at no word cost | none | lint counts 2–3 silences of ≥0.3 s | G1 |

### P1: small engine changes (each needs an OWNER sample)

| # | Change | Why | Component | Free? | Requirements | Expected benefit | Risk | Test / metric | Class |
|---|---|---|---|---|---|---|---|---|---|
| 7 | Frame-0 rule: scene 0 `instant` (or starting ≥70% drawn), `impact` hit at 0.0, audio lead 0.35 → 0.15 s | D2 [M]; AUDIT F12 | `chalk.plan()` i==0 branch; `studio.py step_audio` lead :631-632; `chalk.sound` | yes | none | a readable hook and thumbnail at frame 0 | loses the "drawing appears" opening the owner approved; the hybrid (hold the finished image 0.3 s, then a trace flourish) is an option | non-board pixel share at t=0 ≥ about 5% (today about 0); first word at ≤0.3 s from word timestamps; owner A/B | OWNER |
| 8 | Per-scene `reveal` (draw/fast/instant/ghost) | D3 [M] | `chalk.plan()` draw duration; `render()` vis mask | yes | none | images readable for most of each shot | too many instant reveals dilute the chalk identity; lint caps draw at ≤3 | fully-drawn time share per shot (A vs B); owner A/B | OWNER |
| 9 | Per-scene `transition` (cut/erase/black/flash/dust) | D3 [M] | `plan()` vs/ds; `render()` transition branch; `sound()` erase emission | yes | #8 | rhythm, and the erase regains meaning as a chapter mark | `black_freeze` false positives on dips | `black_freeze` QA passes; erase count 1–3 | OWNER |
| 10 | Move vocabulary: push/pull with z up to 1.20, tilt, truck, shake, Dutch rotation, whip blur | D3 [M] | `cam_matrix` (add a rotation argument); camera interpolation block in `render()` | yes | none | shot variety from the same stills | overscan limit: canvas 1188×2112 vs 1080×1920 output allows about 10% before edges show; clamp with `clamp_focus` | SSIM tear check; no board edge visible (corner-pixel test); owner A/B | OWNER |
| 11 | `image` + `crop` shot reuse | D3; saves about 100 s of image time per reused still [M] | `render()` before `chalk_from_image`; `step_images` skips reused scenes | yes | #10 | 12–13 shots from 8–10 stills | soft crops beyond 2× (768 px source) | lint rule 9; visual check of crops at G2 | OWNER (via G2 sample) |
| 12 | Two-pass linear loudnorm + narration pre-normalisation to −16 LUFS | D7 [M] | `studio.py step_audio`, `step_render` :705 | yes | ffmpeg 9.0.1 (installed) or pyloudnorm (MIT) | consistent bed level, no pumping, −14 hit precisely | none audible beyond the level change | integrated −14 ±0.5 on C0005 ×4 (today −15.2 to −14.7); LRA not reduced further | SAFE |
| 13 | New procedural SFX + `hit` field | D7 [M] | `chalk.sound` dispatch dicts; new `sfx_*` functions | yes | none | punctuation at the hook, turn and payoff | cheesy or over-busy; cap at about 4 hits per episode | owner listening A/B; SFX peaks 3–6 dB under narration peaks | OWNER |
| 14 | Ducking retune (−18 to −22 dB under speech, +4–6 dB in gaps) + music-under-speech QA metric | D7 | `step_audio` duck lines :660-673; `pipeline/qa.py` | yes | #12 | clearer narration, music that breathes | over-ducking sounds pumped | speech-band minus bed ≥12 dB; owner A/B | OWNER (sound) / SAFE (metric) |

### P2: medium

| # | Change | Why | Component | Free? | Requirements | Expected benefit | Risk | Test / metric | Class |
|---|---|---|---|---|---|---|---|---|---|
| 15 | Per-scene `accent` hues (Lanka crimson etc.) | D6 [M] | `restrict_palette(rgb, hues)`, `chalk_from_image`, `render()`; world map in `ramayana.json` | yes | none | worlds become distinguishable | crimson can read as gore or "evil"; cap ≤3 hues | owner A/B on one scene recoloured; hue histogram per frame | OWNER |
| 16 | Mask-based two-plane parallax, then 3-plane with DA-V2 Small | D3 | new plane compositor in `chalk.py` (about 200 lines); BiRefNet (MIT) or SAM 2.1 (Apache) | yes | about 1 GB of models, loaded and unloaded in turn | real depth instead of a flat zoom, look unchanged | tearing; noisy depth on chalk [U] | SSIM between frames; test DA-V2 on 5 existing stills first; owner A/B | OWNER |
| 17 | Procedural overlays + "alive" figure motion | D3 | `Particles` extension; `cv2.remap` sway in `render()` | yes | #16 masks for figure motion | scenes stop feeling static | uncanny motion; render time | render time per frame (today 2,460 frames in 49 s [M]); owner A/B | OWNER |
| 18 | Character reference sheets + FLUX.2 klein 4B reference A/B + DINOv2 drift flag | D4 [M] | `profiles/characters/refs/`; `step_images` `scene_with_refs`; `pipeline/qa.py` | yes (Apache-2.0, re-verified) | about 4–8 GB disk; measure M5 time and peak RSS first; never concurrent with Z-Image or voice | stable faces, beards, ages and props | slower images (M1 Max about 52 s per edit [F]; Air slower [U]); style shift away from Z-Image chalk | same 4 character scenes from C0004/C0005 with both models: DINOv2 cosine to the sheet, time per image, owner preference | OWNER |
| 19 | Visual QA automation: OCR text artifacts (Tesseract), perceptual-hash duplicates, chalk density 3–45%, safe-zone stroke energy | D8 | `pipeline/qa.py` on `img/NN_raw.png` | yes | Tesseract (Apache-2.0) | defects caught before render | false positives, so these warn only | precision on C0001–C0005 raws against the known fixes | SAFE |
| 20 | SFX library: Sonniss GDC + Freesound CC0, with `licenses.csv` | D7 | a data directory outside git; `chalk.sound` file loader | yes | 7.47 GB disk | real conch, bells, tabla | licence slip; keep the CSV mandatory | every file used has a CSV row (lint) | SAFE (library) / OWNER (sounds used) |

### P3: later

| # | Change | Why | Component | Free? | Requirements | Expected benefit | Risk | Test / metric | Class |
|---|---|---|---|---|---|---|---|---|---|
| 21 | Leitmotif library | series identity | `chalk.music` `phrases` + `music.leitmotif` | yes | none | recognisable characters by ear | motifs clash with narration | owner listening | OWNER |
| 22 | Kalamkari-line and Mewar-continuous treatments (≤1 per episode) | tale-within-tale clarity | prompt add-ons; `reveal: ghost`; long-tilt move | yes | #8, #10; 4-style prompt test (about 30 min) | narrative layers become legible | dilutes the brand if overused | owner judges test stills | OWNER + G1 |
| 23 | Motion-comic panels | confrontations | panel compositor in `render()` | yes | #11 | simultaneous action | busy frames on a phone | owner A/B | OWNER |
| 24 | ACE-Step 1.5 / Magenta RT 2 bed tests (§4.7) | richer timbres | separate run; `--music` path exists in `step_audio` | yes | run alone; progress updates | shehnai or sarangi-like colour | quality unknown; Indian timbres unproven | blind owner A/B in 3 moods; peak RSS | OWNER |
| 25 | Chalk-style LoRA, then per-character LoRAs (`mflux-train`) | "shaded pastel, not line art" | overnight solo run | yes | RAM-tight [U]; public-domain or owned training images only | closer to sparse line-art chalk | memory pressure; overfitting | 500–1000-step pilot at 512 px; owner A/B | OWNER |
| 26 | Forced alignment for Indic captions | caption timing | `align_words` | yes | a non-NC aligner (not MMS checkpoints) | tighter word sync | licence trap | onset error against hand-marked words on 2 scenes | SAFE |
| 27 | LTX-2.3 single hero-shot test | possible "wow" shot | separate venv | yes (LTX-2 Community, free under $10M; read in full first) | about 26 GB disk, 10–15+ min per clip | unknown | style drift into photoreal | one first/last-frame test on a chalk still; owner decides | OWNER |

### Suggested run order [R]
1. **P0, items 1–6.** Lint and QA first, so every later change is measurable.
2. **One owner review session** covering items 7–11 and 13 as a single bundled A/B on C0005-en.
3. **Item 12** (SAFE) at any time.
4. **P2**, in the order 15 → 16 → 17 → 18. Item 18 needs its own measurement run first.
5. **P3** only after analytics confidence reaches medium (PROJECT_CONTEXT §15).

**Rules for every run:** one heavy model loaded at a time, and an update every 3–5 minutes on long runs via `python -m pipeline progress <ID> --oneline`.
