# Long-form YouTube: architecture, flow and implementation plan

**Date:** 2026-11-18 · **Status:** plan, with the engine foundation built and tested. Production of Bala Kanda Part 1 starts only when the owner asks.
**Readers:** the owner (approves at the gates) and future Claude Code sessions (implement and produce).
**Decision source:** the owner, 2026-11-18, after the analytics review in `data/reports/insights-2026-11-18.md`. Recorded in PROJECT_CONTEXT §23.0, CLAUDE.md and the memory note `youtube-longform-strategy`.

**Legend**
- **Status:** ✅ built and tested · 🔧 to build · 👤 owner action.
- **Effort:** S = under half a day, M = 1–3 days, L = longer or overnight runs. Every time below is an estimate (`*`) unless it cites a measured figure.

---

## 1. Vision and objectives

YouTube carries the **long-form library** of the Valmiki Ramayana in chalk; Instagram and YouTube Shorts carry the **daily episodes**.

| Item | Decision |
|---|---|
| Videos per Kanda | **2** (Part 1 and Part 2) |
| First Kanda | Bala Kanda. **Part 1:** Valmiki to the divine weapons (the ground of Ep01–06). **Part 2:** the road to Mithila to Rama and Sita's wedding and Parashurama |
| Story | **A new continuous story** per part: one flowing narration, no per-episode hooks, end cards or "Episode N" framing |
| Length | **8–12 minutes** per language |
| Frame | **Horizontal 16:9**, 1920×1080, 30 fps |
| Languages | **English, Hindi, Telugu** |
| Look | Chalk drawn in stroke by stroke, then Kathputli-style puppets (engine v3), verse slides with verse-only time |
| Shorts | **Unchanged**: daily, all languages, 35–55 s, both platforms |
| Gates | The same three: G1 script, G2 final video, G3 publish per platform |

**Why:** YouTube's Shorts feed hardly picked up the new channel. Ep01–03 drew about 175 YouTube views, and only Ep01 Hindi entered the feed (66 feed views). The same Reels drew about 14,000 views on Instagram. YouTube search brought views even to the tiny channel (8 of Ep01 English's 9 views), and long videos are what search and the home feed recommend.

---

## 2. Architecture overview

The long-form flow reuses the Shorts pipeline end to end. Only the frame, the story shape, the script scale and the YouTube packaging differ.

```
                ┌──────────── Claude Code (judgement) ──────────────────────────┐
 part plan ─▶ sources + verse table ─▶ chaptered script (en, hi, te) ─▶ lint ─▶ story review
 (series-planner)   (scriptwriter)          (scriptwriter)                         (reviewer)
                                   ─▶ [G1 script] ─▶ wide visual plan + character bible
                                                        (creative-director)
                └──────────────────────────────────────────────────────────────┘
                                   │ files in content/<ID>/   (manifest format: "long")
                ┌──────────── Python pipeline (deterministic, STUDIO_FORMAT=long) ┐
 voice ─▶ voice QA ─▶ wide images (shared by all languages) ─▶ rig.json (tiered)
 ─▶ rig-qa ─▶ render (draw-in → puppets, chapter cards, verse slides) ─▶ qa
 ─▶ visual/audio review ─▶ [G2 final] ─▶ metadata + chapters + 16:9 thumbnail
 ─▶ [G3 publish] ─▶ /publish (regular YouTube video) ─▶ analytics (long-form cohort)
                └──────────────────────────────────────────────────────────────┘
 state: content/<ID>/manifest.json (format: long, kanda, part) + data/studio.db
```

### 2.1 How the format switch works ✅
- `python -m pipeline new … --format long` writes `"format": "long"` to the manifest.
- `produce` and `rig-qa` run the engine with `STUDIO_FORMAT=long`.
- `frame.py` is the single source of every size:

| | Short (default) | Long |
|---|---|---|
| Frame W×H | 1080×1920 | 1920×1080 |
| Chalk canvas CW×CH (camera headroom) | 1188×2112 | 2112×1188 |
| Generated still | 768×1344 | 1344×768 |
| Image prompt | unchanged | + wide horizontal 16:9 landscape composition |
| Captions | style default (0.75 of height) | 0.88 of height |
| Lint target / warn / fail (estimate) | 35–55 s / outside / > 57 s | 480–720 s / outside / > 780 s |
| QA reject | ≥ 60 s or not 1080×1920 | ≥ 900 s or not 1920×1080 |

- Verse and word-meaning cards re-lay themselves out for the wide canvas.
- Shorts are unchanged; they don't set `STUDIO_FORMAT`.
- **Tested 2026-11-18:** a two-scene 1920×1080 render (story scene plus verse slide) through `studio.step_render` with the puppet engine. The chalk draw-in, stick, verse card, titles and captions were all correct.

### 2.2 Components

| Component | Role in long-form | Status |
|---|---|---|
| `frame.py` | Format switch (sizes, limits, prompt suffix) | ✅ |
| `studio.py` | Voice, images, audio mix, render driver; `effective_style` applies the long-form size, prompt and caption position | ✅ |
| `chalk.py` | Board, reveal order, verse cards (wide layout), music and SFX | ✅ (music: see §6.4) |
| `puppet.py`, `puppetstudio.py` | Puppet rigs, elements, motion QA; engine v3 renderer | ✅ |
| `pipeline/lint.py`, `pipeline/qa.py` | Format-aware duration and resolution checks | ✅ |
| `pipeline/__main__.py` | `new --format long`; format passed to studio and rig-qa | ✅ |
| Chapter cards in the render | Chalk-written chapter title between chapters | 🔧 |
| `pipeline/chapters.py` | Chapter timestamps from `timeline.json` for the description | 🔧 |
| Long-form thumbnail | 1280×720 chalk thumbnail | 🔧 |
| `publish.py` | Upload as a regular video, chapters in the description, thumbnail | 🔧 |
| Analytics | Long-form cohort and metrics | 🔧 |
| Dashboard | Shows the format per project | 🔧 |

---

## 3. Agents and their long-form jobs

The same 5 agents. Each gets a long-form section in its definition (🔧 S each).

| Agent | Long-form job | Main outputs |
|---|---|---|
| series-planner | Splits each Kanda into Part 1 and Part 2 by sarga range; lists the must-tell moments, the verses to show, and the cliff between the parts | `content/series/ramayana-longform.md` |
| scriptwriter | Verse table with edition; **chaptered** continuous script per language (written originally in each language, not translated); chapter titles; word budgets in §5.2; must pass `pipeline lint` | `research/report.md`, `<lang>/script.json` with `chapter` on every scene, `script.md` |
| creative-director | 40–50 wide scenes; reuses the character bible; composes every drawing for puppetry (limbs, hair and props clear of scenery); marks each scene's rig tier (§6.2) | `visual`, `seed` and `tier` fields; bible updates |
| reviewer | Story QA per chapter (pacing, clarity, accuracy, a re-hook every 60–90 s); Visual and Audio QA on the full render | `<lang>/review.md` |
| packager | Long-form title and description with chapter timestamps, tags, playlist, AI disclosure; never a Short | `<lang>/publish.json` |

---

## 4. Execution order and gates

| # | Stage | Who | Command / output | Gate check |
|---|---|---|---|---|
| 0 | Part plan (once per Kanda) | series-planner | `content/series/ramayana-longform.md` | owner OK (lightweight) |
| 1a | Analytics checkup | main | `pipeline analytics`, `pipeline insights` (long-form cohort once it exists) | — |
| 1 | Create | main | `python -m pipeline new --topic "Bala Kanda Part 1: …" --series "RAMAYANA — The Epic in Chalk" --format long --category mythology --style chalk --langs en,hi,te` | — |
| 2 | Sources + chaptered scripts | scriptwriter | verse table, `script.json` and `script.md` per language | — |
| 3 | Visual plan | creative-director | 40–50 wide prompts, rig tiers | — |
| 4 | Lint | main | `pipeline lint <ID>` (long-form limits) | must pass before G1 |
| 5 | Story QA | reviewer | `<lang>/review.md` | — |
| **G1** | **Script approval** | owner | scripts per language with chapter list, length estimate and learnings applied | lint pass |
| 6 | Voice | main | `pipeline produce <ID> --lang X --steps voice` (en, then hi, then te) | per-scene speaker-consistency QA |
| 7 | Images | main | `pipeline produce <ID> --lang en --steps images` (hi and te reuse them) | manual image review |
| 7b | Rig | main | `content/<ID>/rig.json` by tier; `pipeline rig-qa <ID> --lang en` | rig QA must pass |
| 8 | Render | main | `pipeline produce <ID> --lang X --steps render`, one language at a time, overnight if needed | — |
| 9 | Automatic QA | main | `pipeline qa <ID> --lang X` | — |
| 10 | Visual + Audio QA | reviewer | numbered fixes | — |
| **G2** | **Final approval** | owner | videos in Finder | QA pass or recorded waivers |
| 11 | Metadata | packager | title, description with chapters, tags, playlist, 1280×720 thumbnail | — |
| **G3** | **Publish approval (YouTube)** | owner | video, metadata, thumbnail and time per language | — |
| 12 | Publish | `/publish` (manual) | regular YouTube upload; the owner adds end screens and cards in Studio | gates and hashes match |
| 13 | Shorts tie-in | 👤 owner | in Studio, set each related Short's "Related video" to the long video (the API can't set it) | — |
| 14 | Analytics | main | 48 h, 7 d, 14 d and 30 d snapshots; long-form cohort | — |

Heavy models never run in parallel (`data/heavy.lock`). The long-form renders queue behind any running Shorts production, and Shorts keep priority for their daily schedule.

---

## 5. Story design

### 5.1 Shape of a part (8–12 min)

| Block | Time | Purpose |
|---|---|---|
| Cold open | 0:00–0:30 | The most gripping moment of the part, told in 2–3 lines, then "but this story begins long before…". No logo intro |
| Title card | 0:30–0:40 | "Bala Kanda · Part 1" written in chalk with the part title |
| Chapters (4–6) | 1:30–2:30 each | Each is a mini-arc (situation → turn → consequence) and ends with a line that pulls into the next chapter |
| Verse slides | 1–2 per chapter | Sanskrit on screen in chalk; the meaning narrated; 1.2 s of verse-only time |
| Closing | last 0:45 | Lands the part's emotional point, then the cliff into the next part |
| End screen | last 0:20 | A calm chalk board with space for YouTube end-screen elements (the owner adds them in Studio) |

**Retention rules:**
- Re-hook every 60–90 s with a question, a turn or a reveal.
- Never more than 2 consecutive scenes without visible motion.
- A new chapter title is a visual reset.
- The narration style rules apply (memory `narration-style`): flowing, rhythmic storyteller prose, no headline fragments.

### 5.2 Word budgets per language
Measured speech rates (`data/lint_rates.json`, current voices): **en 2.82 words/s (af_heart), hi 2.64 (Malini), te 1.56 (Malini)**. Assuming about 10% of the runtime is pauses, verse-only holds and title cards:

| Language | 8 min | 10 min | 12 min |
|---|---|---|---|
| English | ≈ 1,220 words | ≈ 1,520 | ≈ 1,830 |
| Hindi | ≈ 1,140 | ≈ 1,430 | ≈ 1,710 |
| Telugu | ≈ 670 | ≈ 840 | ≈ 1,010 |

Telugu gets fewer words for the same time because of longer words, not less story. Each language is written natively to its own budget.

### 5.3 Script schema additions 🔧 S
- **Scene fields:** `chapter` (index), `chapter_title` (on a chapter's first scene), `tier` (rig tier, §6.2), plus all existing fields (`narration`, `visual`, `pause`, `kind`, `devanagari`, `source`, `music`, `sfx`, `transition`, `overlay`, `emphasis`).
- **Top level:** `format: "long"`, `kanda`, `part`, `chapters: [{title, first_scene}]`.
- **Lint additions:**
  - 4–6 chapters, each 60–180 s.
  - Every chapter has at least one moving scene (tier A or B).
  - A verse slide's `source` names the edition.
  - The cold open is 20–40 s.

---

## 6. Visual design

### 6.1 Wide drawings
- About 40–50 scenes per part (an average of 12–15 s per scene; verse slides and chapter cards included).
- **Images are shared across languages** (`share_images`), so they're generated once per part.
- **Composition for 16:9:** subject at about a third of the frame width, open board on the far side for camera drift, the lower 18% clear for captions, horizon about a third from the top.
- **Puppetry rules** (creative-director): characters in side or three-quarter view in the line's key pose; limbs, hair, tails, scarves and props clear of the body and of all scenery; flags, lamps and flames on open board.
- **Character continuity:** every character comes from `profiles/characters/ramayana.json` (`{character}` tokens) so Rama looks the same in the long video and the Shorts.

### 6.2 Rig tiers 🔧 S
Rigging is about 10–15 min per scene*, so 45 scenes would be 8–11 h. Tiers keep the motion where the story needs it:

| Tier | Scenes per part | Motion | Rig effort* |
|---|---|---|---|
| **A, hero** | 10–14 | Full character puppet: head, torso and arms timed to words, plus objects | 12–15 min each |
| **B, ambient** | 15–20 | Objects only: flags, lamps, flames, trees, water, birds; characters breathe | 3–5 min each |
| **C, still** | the rest, plus verse slides and cards | Chalk draw-in and camera drift only | 0 |

That is about 3.5–5 h of rigging per part*. The rig is built once and reused by all three languages, because actions are timed by scene and word fraction, not by seconds.

### 6.3 Render features to build
| Feature | Detail | Effort |
|---|---|---|
| Chapter cards 🔧 | A 2.5 s card drawn in chalk ("Chapter 2 · The Weapons"), with the reading-order reveal and the chalk stick | S |
| Part title card 🔧 | "Bala Kanda · Part 1" plus the part title, after the cold open | S |
| End-screen board 🔧 | The last 20 s: calm board, title, space for end-screen elements | S |
| Progress ETA for long renders 🔧 | `pipeline progress` reports frames done, ETA and finish time for 15,000–22,000-frame renders | S |
| Memory guard 🔧 | Render keeps at most 2 puppet stages in memory (already true); add a check that peak memory stays under about 10 GB on the Air | S |

### 6.4 Sound
- **Narration:** per-scene WAVs, unchanged, at −16 LUFS before mixing. With 40–50 scenes, the `speaker_consistency` check matters more: it must hold for the whole 10 minutes.
- **Music 🔧 M:** the generated tanpura and bansuri score was designed for 50 s and loops a short phrase.
  - For 10 minutes it needs **chapter-level variation**: a new phrase per chapter, a swell at each turn, a drop-out under verse slides, and leitmotifs kept (Rama, Sita).
  - The A/B sample goes to the owner before Part 1's G2 (class OWNER).
- **SFX:** unchanged, including the puppet chalk sound at ×0.12.
- **Loudness:** −14 LUFS integrated, true peak ≤ −1 dBFS, the same as Shorts.

---

## 7. Publishing (YouTube long-form)

| Item | Plan | Status |
|---|---|---|
| Upload type | Regular video (16:9, longer than 3 min, so YouTube never treats it as a Short); no `#Shorts` | 🔧 S |
| Title | ≤ 70 chars, searchable: "Bala Kanda Part 1: Valmiki to the Divine Weapons, Ramayana in Chalk" style; Hindi and Telugu written natively | packager |
| Description | Story summary, **chapter timestamps** from `timeline.json` (first at 0:00, at least 3, each at least 10 s), verse sources, AI disclosure line, Instagram link, playlist link | 🔧 S |
| Thumbnail | 1280×720 chalk thumbnail: a character close-up from the part plus 2–4 words in Chalkduster. **Custom thumbnails need a phone-verified YouTube channel** 👤 | 🔧 S |
| Playlists | "Ramayana in Chalk: Full Kandas (English)", one per language | 👤 / API |
| AI disclosure | `synthetic: true` (altered or synthetic content); Made for Kids = No | existing |
| End screen and cards | Studio only (not in the API): the next part, the playlist, subscribe | 👤 at each upload |
| Shorts tie-in | Each Short of the same story links to the long video through "Related video" in Studio | 👤 |
| Schedule | One language per day or all three the same day; the owner decides at G3 | G3 |

---

## 8. Analytics for long-form 🔧 M
- **Separate cohort:** long-form is never compared with Shorts (`features.format`).
- **Metrics per video:** views, average view duration, average percentage viewed, retention curve (`yt-retention` skill), traffic sources (search, browse, suggested, external), impressions and click-through rate, subscribers gained, and chapter-level drop-off from the retention curve.
- **Windows:** 48 h, 7 d, 14 d, 30 d (long videos grow slowly through search).
- **What feeds back:** cold-open retention, chapter drop-off and title/thumbnail CTR go to the next part's G1 "Learnings applied" block. Anecdote until there are at least 6 long videos per language.

---

## 9. Production timeline per part (estimates*)

| Step | Time* | Who |
|---|---|---|
| Part plan + verse table + scripts (3 languages) | 1 working session | scriptwriter, series-planner |
| G1 | owner | 👤 |
| Voice (en ≈ 5 min, hi ≈ 12–15 min, te ≈ 12–15 min of compute) | ≈ 35 min | pipeline |
| Images (≈ 45 wide stills at about 1 min each, measured 58 s at 9:16) | ≈ 45–60 min | pipeline |
| Image review and regenerations | ≈ 30–60 min | creative-director, main |
| Rigging (tiers A and B) | ≈ 3.5–5 h | main |
| Render: a 52 s puppet Short took 282–306 s (≈ 5.5–6× real time), so a 10 min part is ≈ 55–60 min per language | ≈ 3 h for 3 languages | pipeline (overnight-friendly) |
| QA + review + fixes | ≈ 1 h | pipeline, reviewer |
| G2, metadata, G3 | owner | 👤 |

**Total:** roughly **2–3 days per part**, with about 4 h of unattended compute. Shorts production continues in between. Heavy steps take turns through `data/heavy.lock`.

---

## 10. Implementation plan (build order)

| # | Item | Class | Effort | Status |
|---|---|---|---|---|
| L1 | Format switch (`frame.py`), long-form sizes, wide prompt, caption position | SAFE | S | ✅ |
| L2 | Format-aware lint and QA limits; `new --format long`; format passed to studio and rig-qa | SAFE | S | ✅ |
| L3 | Wide verse and word cards; wide test render | SAFE | S | ✅ |
| L4 | Storytelling skill: long-form section (§5); scriptwriter, creative-director, reviewer and packager long-form notes | SAFE | S | ✅ skill + scriptwriter (other agents 🔧) |
| L5 | Script schema `chapter`/`tier` + lint rules (§5.3) | SAFE | S | ✅ chapters 4–6, cold open, chapter lengths, 35–60 scenes |
| L6 | Chapter cards, part title card, end-screen board in `puppetstudio.py` (§6.3) | OWNER (look) | S | ✅ chapter titles in chalk per language; the part title uses `emphasis`; the end board is a script scene |
| L7 | Music with chapter-level variation (§6.4); A/B sample to the owner | OWNER | M | 🔧 |
| L8 | Rig tiers in the rig workflow and rig-qa summary (§6.2) | SAFE | S | 🔧 |
| L9 | Long-render progress ETA and memory guard | SAFE | S | 🔧 |
| L10 | `pipeline/chapters.py`, 1280×720 thumbnail, regular-video upload in `publish.py` (§7) | SAFE | S–M | 🔧 |
| L11 | Long-form analytics cohort and metrics (§8); dashboard format column | SAFE | M | 🔧 |
| L12 | Series plan `content/series/ramayana-longform.md` (Bala Kanda Part 1 and 2 sarga ranges) | G1-adjacent | S | ✅ Part 1 = 1.1–1.30 (proposed; owner confirms at G1) |
| P1 | **Bala Kanda Part 1** (C0011) production through G1 → G2 → G3 | — | ≈ 2–3 days | scripts in progress (2026-11-18) |
| P2 | Bala Kanda Part 2 | — | ≈ 2–3 days | after P1 |

**Suggested order:** L4 → L5 → L12 → **Part 1 scripts to G1** (writing needs no heavy models, so it can start while L6–L9 are built) → L6, L8, L9 → L7 (owner A/B) → Part 1 production → L10 before Part 1's G3 → L11 after the first upload.

---

## 11. Risks and mitigations

| Risk | Mitigation |
|---|---|
| A 10-minute narration drifts in voice (Malini) | Per-scene generation with the speaker-consistency QA; regenerate flagged scenes (existing flow) |
| Telugu is an unreviewed-language cohort (O9) | Native listen recommended before Telugu G2; analysed separately |
| Long render on a 16 GB fanless Air | One language at a time, overnight; at most 2 stages in memory; `caffeinate`; plugged in |
| Rigging effort | Tiers (§6.2); the rig is shared by all languages |
| Verse accuracy over 4–12 verses per part | Verse table with edition and source URL in `research/report.md`; reviewer checks each against the source |
| Custom thumbnails blocked | 👤 Verify the channel by phone in YouTube Studio once |
| Long videos also start slowly on a new channel | Searchable titles and chapters; Shorts and Instagram point to the long video; judge at 14–30 days, not 48 h |
| Contention with daily Shorts | Shorts keep priority for heavy models; long-form scripts and rigging need none |

---

## 12. Owner actions
1. 👤 **Phone-verify the YouTube channel** (Studio → Settings → Channel → Feature eligibility) so custom thumbnails work.
2. 👤 Approve the music A/B for long-form (L7) when it's ready.
3. 👤 At each long-form upload: add end screens and cards in Studio, and link the related Shorts.
4. 👤 Gates G1, G2 and G3 as usual, in chat.
