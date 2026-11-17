# Kanda visual identities and the Ayodhya Kanda film direction

Status: **proposal for the owner, 2026-11-17.** Nothing here is implemented. Research and writing only: no model was run, nothing was committed, and no approved or published item was touched.

Owner brief (relayed by the main session, 2026-11-17):
- Each Kanda gets its own distinct **animated** look, with real character and environment motion and an animated-film feel, starting with Ayodhya Kanda. Bala Kanda (Ep01–Ep08) stays chalk.
- Rama and Sita may now be shown with faces, respectfully: dignified, inspired by traditional depictions, no caricature. Blue or dark skin only as a deliberate choice (recommendation in §4.2).
- Narration in Hindi and English, 35–55 s per episode (hard limit under 60 s).
- Accuracy to the Valmiki Ramayana with edition-labelled citations (vulgate numbering as on valmikiramayan.net), Critical Edition differences noted where known, no invented quotes, later retellings labelled.

Related files:
- `profiles/characters/ayodhya_kanda.json`: character bible and art-style prefix for the Kanda.
- `content/AK01_draft/script.en.md`, `content/AK01_draft/script.hi.md`: the first episode.
- Rules this builds on: `docs/VIDEO_QUALITY_UPGRADE_PLAN.md` (§2.8 accuracy, §3 visual bible, §4 sound), `docs/TOOLS_AND_SKILLS_RESEARCH.md` (§2.6 video generation, §3.1 music models), `docs/BRAND.md`, `.claude/skills/storytelling/SKILL.md`.

Labels used below, as in the other research docs: **[F]** fact checked against a source named here, **[R]** recommendation, **[U]** unverified or untested, check before relying on it.

---

## 0. Decisions this needs from the owner

1. **Style change.** CLAUDE.md says "Keep the approved chalkboard style", and the creative-director agent needs explicit owner approval, with a side-by-side, for any change to the look. This proposal changes the look for every Kanda after Bala. The step is a 4-keyframe Ayodhya test (§6.4) shown next to a chalk frame, then a one-line update to CLAUDE.md and PROJECT_CONTEXT §9 if the owner approves.
2. **Faces.** The rule "Rama shown from behind" in `profiles/characters/ramayana.json` stays for Bala Kanda. The new bible lifts it for Ayodhya Kanda onward, which follows the owner's brief.
3. **Rama's skin tone.** The recommendation is *indīvara-śyāma*, a deep dark skin with a cool blue-lotus undertone (§4.2). The alternative is deep warm brown with no blue.
4. **Motion technology.** Option A is hybrid: image-to-video for 3–4 hero shots per episode and 2.5D motion for the rest. Option B is image-to-video for every shot. Both need a timing test first (§6).
5. **Chalk SFX.** `chalk.CHALK_SFX_GAIN = 0.035` stays unchanged. Animated episodes have no chalk stroke sounds, but the chalk ident and any chalk transition keep the fixed gain.

---

## 1. Brand constants (never vary between Kandas)

The Kandas change their painting, light, camera and music. The things viewers recognise as *Chalk Tales* stay fixed:

| Constant | Value | Why |
|---|---|---|
| Series name and mark | Chalk Tales; the 45° gold bow at full draw (`docs/BRAND.md`) | Brand recall across the style changes |
| Gold accent | `#E8BE6E` in every frame: a lamp, jewellery, a border, the title | One colour thread that ties all seven looks together |
| Title typography | Chalkduster titles in gold with a dark halo; ChalkboardSE captions (white active, saffron keywords); Indic fonts as in `profiles/brand.json` | The chalk lettering becomes the brand signature once the pictures stop being chalk |
| Kanda bridge | The first shot of each Kanda's first episode starts as a full chalk line drawing on the slate board, which floods with the new paint style in about 0.6 s. Every later episode opens directly in the Kanda's style | Says "same storyteller, new chapter". Frame 0 stays at least 70% drawn (O5) |
| End sting | 0.5 s chalk-board card with the bow mark and "Next: …" in Chalkduster | Chalk is the series' frame; the paint lives inside it |
| Characters | One face, build, accent colour and prop per character for the whole epic. Costume changes only when the text changes it (bark garments 2.37, matted hair at the Ganga 2.52) | Character consistency matters more than style novelty |
| Composition | Title headroom in the top 12%, captions in the lower 25%, subject centred; no borders and no text in images | Unchanged from the visual bible §3.1 |
| Screen direction | Rama's party moves left to right (towards Lanka); threats enter right to left | Unchanged from the visual bible §3.1 |
| Architecture and costume | Ancient Indian: carved sandstone gateways, stepped *shikhara* towers, pillared halls; dhoti, *uttarīya* and tall *mukuṭa* as in the Ajanta murals and Gupta sculpture. No onion domes, minarets, *jama* coats or plumed turbans | Ep03 lesson; the *Adipurush* backlash (VQ §2.8) |
| Sound | Tanpura drone at Sa = 146.83 Hz in every Kanda; the Rama leitmotif returns in every Kanda | Musical identity carries across the looks (VQ §4.4) |
| Disclosure | YouTube `synthetic: true`, Instagram `is_ai_generated: true`; the description says "animated with AI tools", never "hand-drawn" | CLAUDE.md, `docs/PUBLISHING.md` |

A caution on references: Pahari and Mughal-period paintings often dress Rama in a Mughal-era *jama* with a turban, and draw Mughal-style pavilions. **Take colour and light from the painting schools below, but take costume and architecture from the ancient Indian sources** (Ajanta, Gupta and early temple sculpture). This keeps the Ep03 architecture rule.

---

## 2. One look per Kanda

Every reference below is **inspiration for palette, light and mood only**. No designs, characters, compositions or frames are copied from any painting or film, and no reference image is fed to a model.

### 2.1 Overview

| Kanda | Working name | Rendering | Palette (hex guide) | Light | Camera | Motion | Music palette |
|---|---|---|---|---|---|---|---|
| **Bala** (Ep01–08, done) | The Epic in Chalk | Procedural chalk on slate, stroke reveal | chalk `#F2EFE6`, saffron, gold, green on slate `#14191C` | Flat; chalk glow | Zoom, push, parallax | Stroke reveal, dust, breathing | Tanpura and bansuri, Bhairavi colour |
| **Ayodhya** | Pahari Gold | Painterly animated-film still: soft gouache, clean line, Pahari colour | ivory `#F4EBD9`, saffron `#E8973A`, gold `#E8BE6E`, lapis `#2E4A8C`, leaf green `#5E8C4A`, vermilion `#C8432B`; turning to indigo `#1F2547` and ash `#B9B3A6` | Warm top-left sun, then lamp-light, then night interiors, then grey dawn (§3) | Symmetrical, stately; slow push and tilt | Cloth, banners, flames, petals; restrained gestures | Tanpura, reed (shehnai-like), bells, conch, *nagada* in celebration; bansuri alone in grief |
| **Aranya** | Forest Mural | Earth-pigment mural look: flat ochre and green fields, firm dark outline, dappled light | ochre `#C98B2B`, forest green `#2F5D3A`, red earth `#9E3B26`, ivory, black outline | Dappled green day; orange dusk at Panchavati; cold moon for the rakshasa threat | Low angles among trees; trucking moves | Leaves, deer, smoke from ashram fires; the golden deer's shimmer | Bansuri and soft drum, birdsong beds; low drone for danger |
| **Kishkindha** | Monsoon Stone | Rock-and-rain painting: granite ochres, rain-washed blue-greens, heavy clouds | granite `#8C7B65`, monsoon teal `#2F6F6A`, cloud slate `#56606B`, ripe green | Overcast monsoon light; lightning flashes; clear autumn sky at the end | Wide landscapes, high vantage on boulders | Rain, waterfalls, clouds, monkeys leaping in the distance | Rain beds, deep drum, Megh/Malhar colour |
| **Sundara** | Moonlit Lanka | Night painting with backlit translucent jewel tones, like light through coloured leather | night indigo `#151A3A`, lamp gold, jewel crimson `#9B1B30`, emerald `#1E7A5A` in the Ashoka grove | Moon and lamps; gold dawn for the Vedic chanting (5.18.2) | Hanuman's POV, rooftop glides, one big leap | Hanuman's flight, lamp flicker, Ashoka leaves; Sita still and dignified | Hanuman motif (rising run with pulse); Lanka motif low |
| **Yuddha** | Ink and Fire | Bold ink line, high-contrast painted dusk, smoke and dust | crimson `#A3222B`, saffron, smoke grey `#6B6560`, gold | Backlit dusk silhouettes, firelight | Kinetic: whip, shake, low angle; strict screen direction | Arrows, banners, dust storms; armies only as distant masses | Battle ostinato 7 or 8 beats, conch, drums; silence before decisive blows |
| **Uttara** | Back to Chalk | Soft ash-and-ivory wash that dissolves back into the chalk board at Valmiki's ashram | ivory, ash, faded gold, slate | Even, reflective | Still frames, slow pulls | Minimal: wind in the ashram, the river | Tanpura and the first Bala motifs: the series closes where it began |

### 2.2 Visual references (inspiration only)

| Kanda | Reference | Notes |
|---|---|---|
| Ayodhya | **Pahari painting** (Guler and Kangra, 18th–19th c.), including the Guler "Siege of Lanka" series attributed to Manaku (c. 1725) [F, well documented] | Clear lapis skies, warm ivory grounds, saffron and vermilion accents, lyrical figures. Colour only; costume comes from ancient sources (§1) |
| Ayodhya | **Shangri Ramayana** (Pahari, c. 1680–1720) [F] | Flat, bright fields of colour; strong single-colour backgrounds that read well on a phone |
| Ayodhya, Aranya | **Mewar Ramayana** (1649–53, Sahib Din and others; British Library) [F, also VQ §3.3] | Continuous narration in one frame; useful for recap shots |
| Costume, all Kandas | **Ajanta murals** (c. 5th c. CE) and Gupta-era sculpture [F] | Dhoti, *uttarīya*, tall crowns, jewellery, posture. The period-safe costume source |
| Aranya | **Kerala murals**, e.g. the Ramayana panels at Mattancherry Palace, Kochi (16th–17th c.) [F, dating approximate] | Earth pigments, ochre and green, firm outline, dense forest |
| Kishkindha | **Bundi and Kota** painting, known for monsoon and rain imagery [F] | Rain, clouds and lush green; the Kishkindha rainy season (Rama's lament, 4.28 vulgate) [U: sarga to confirm] |
| Sundara | **Tholu Bommalata** (Andhra) and **Togalu Gombeyata** (Karnataka) leather shadow puppetry, whose core repertoire is the Ramayana [F] | Light through translucent coloured leather. Motion stays painterly, not puppet-jointed |
| Yuddha | **Pattachitra** (Odisha) [F] | Bold line, red grounds, ornamental borders inside objects (never as a frame border) |
| Sacred moments | **Tanjore painting** [F] | Gold-leaf glow for the divine, used as light rather than as figures |
| Animated feature | **Ramayana: The Legend of Prince Rama** (1992, Indo-Japanese, Yugo Sako with Ram Mohan) [F] | Proof that a painterly anime-film Ramayana reads with dignity: calm faces, epic landscapes. Its character designs are **not** copied; our designs come from the bible |
| Animated feature | Painterly anime background tradition (hand-painted skies, soft atmospheric depth) | Lighting and depth language only |
| Modern popular iconography | Raja Ravi Varma's oleographs and calendar art | The blue-skinned Rama most viewers know today. A reference for respectful idealisation, not for skin colour (§4.2) |

### 2.3 What local AI video can realistically render

The facts are from `docs/TOOLS_AND_SKILLS_RESEARCH.md` §2.6; nothing has been measured on the M5 Air.

| Option | Licence | Evidence | Practical meaning for one 45 s episode |
|---|---|---|---|
| **LTX-2.3 int8 via ltx-2-mlx `--low-ram`** (image-to-video, first and last frame guides) | LTX-2 Community (free under $10M revenue); ltx-2-mlx MIT | 16 GB M1: about 15 min for about 4 s [F, third-party]; about 26 GB disk [F] | 11 shots × about 15 min ≈ **2.5–3 h per episode** [U on M5]. The clips are shared by every language, so the cost is per episode, not per language. Overnight, alone, holding `data/heavy.lock`, with progress updates |
| Wan 2.2 TI2V 5B (MLX) | Apache-2.0 | "32 GB+ recommended" [F] | Second choice; probably too heavy for 16 GB |
| **2.5D** (Z-Image keyframe + mask parallax + procedural cloth, flame, petal and particle motion) | Own code; BiRefNet MIT, SAM 2.1 Apache-2.0 | Planned in VQ §3.6 | Seconds per shot. Reads as "motion comic", not "anime film" |

**Recommendation [R]: hybrid (Option A).** Use image-to-video for 3–4 hero shots per episode (the hook, the main character moment, the turn, the final mirror shot) and 2.5D for the rest. If the owner likes the test, move up to full image-to-video.

**Shot-design rules for image-to-video, used in every shot list:**
1. **One clear action per shot**: a head turn, a raised palm, a flame bending, banners unfurling. Never two actions in sequence.
2. **At most 2 characters in a close or medium shot.** Crowds only as distant, small, well-separated figures. Ep07 lesson: overlapping figures grow extra arms.
3. **No hand-to-hand contact detail.** An embrace is framed at its start or as hands resting on shoulders, never as interlocked arms.
4. **The environment carries the motion**: cloth, hair, flames, smoke, banners, petals, water, birds. These are what video models render most reliably.
5. **Faces stay calm.** Small expression changes (eyes lift, a soft smile) and no talking mouths, because there is no lip-sync. Narration is voice-over.
6. **Camera moves are slow and simple**: push, pull, tilt, a short truck. No orbits around characters, because identity drifts on the far side.
7. **Clip length is 5 s**, trimmed to the scene's narration in each language. A shot that needs more holds on its last frame with 2.5D drift.
8. **The keyframe is the frame-0 image**, fully readable, so the hook rule (frame 0 at least 70% drawn) is met by construction.

---

## 3. Ayodhya Kanda film direction

Ayodhya Kanda is a domestic tragedy inside a palace: the highest joy turns to exile in a single night. The film language should **start as the most ordered, golden and symmetrical world in the series, and lose that order step by step**: first the light, then the symmetry, then the colour, and finally the music.

Sarga map: vulgate, 119 sargas, titles checked on the valmikiramayan.net contents page (accessed 2026-11-17) [F]. The Critical Edition (Baroda; translated by Sheldon Pollock, Princeton, vol. II) is reported to have fewer sargas in this Kanda (often given as 111) [U]. Cite the vulgate number, and add `[CE x.y.z]` only after checking against the CE or Pollock.

### 3.1 The four phases

| Phase | Vulgate sargas | Story | Episodes (approx.) |
|---|---|---|---|
| **1. Glorious Ayodhya** | 2.1–2.2 | Rama's virtues (2.1.6–33); the aged Dasharatha decides on Rama as Yuvaraja (2.1.34–44); the assembly of kings and citizens (2.1.45–50); his speech (2.2.1–16); joyful approval and the people's praise of Rama (2.2.17–54) | AK01 |
| **2. Coronation preparations** | 2.3–2.6, 2.7.1–11 | Preparations ordered for the Pushya day (2.3); Dasharatha's premonition and "tomorrow" (2.4); Vasishtha and the fast (2.5); the city decorated (2.6); Manthara sees the festive city from the terrace (2.7.1–11) | AK01 ends here; AK02 |
| **3. Turning point** | 2.7.12–2.19 | Manthara's words (2.7–2.8); Kaikeyi persuaded, and the boons recalled (2.9); the anger chamber (2.10); the boons demanded (2.11); Dasharatha's anguish and the night (2.12–2.14); the city still rejoicing, unaware (2.16); Kaikeyi tells Rama (2.18); Rama decides to go (2.19) | AK02–AK05 |
| **4. Exile** | 2.20–2.119 | Kausalya's grief and Lakshmana's anger (2.20–2.25); Sita insists on going (2.26–2.30); bark garments (2.37); departure (2.40); the Tamasa (2.46); Guha and the Ganga (2.50–2.52); Bharadvaja (2.54); Chitrakuta (2.56, 2.94–95); Dasharatha's death (2.65); Bharata's return and refusal (2.69–2.82); Bharata at Chitrakuta (2.93–2.112); the sandals (2.113); Nandigrama (2.115); Atri and Anasuya (2.117–2.119) | AK06 onward |

**An accuracy trap for AK02 [F]:** in Valmiki, Kaikeyi's first reaction to Manthara is joy. She gives Manthara a jewel and says she sees no difference between Rama and Bharata (2.7.31–35). The turn comes only in 2.8–2.9. A script must not show Kaikeyi as hostile from the first moment.

**Respect rule for Manthara:** the text calls her *kubjā*, hunchbacked (e.g. 2.7.12) [F]. Show a slight stoop with dignity. Never make the disability grotesque or comic, and never let the camera mock it. Her menace comes from her words and her stillness, not from her body.

### 3.2 Colour, light and sound progression rules

| Rule | Phase 1 Glorious | Phase 2 Preparations | Phase 3 Turning point | Phase 4 Exile |
|---|---|---|---|---|
| Palette | Ivory, gold, lapis sky, leaf green | Add saffron, marigold and vermilion; lamp gold at night | Indigo and crimson; gold only on Kaikeyi's jewels, then on the floor where she throws them (2.10) | Ash, bark brown, river grey-blue; forest green returns at Chitrakuta; mourning white for Bharata |
| Saturation | High, even | Highest in the series (festival) | One saturated hue per frame (crimson), the rest low | Low; rising slightly with Bharata's devotion (hope as gold) |
| Light | Morning sun from the top-left, soft shadows | Golden afternoon to lamp-light; lamp-trees (2.6.18) | One low lamp, hard shadows, faces half-lit | Grey dawn mist; dusk fires at camp; moon at Chitrakuta |
| Symmetry | Centred, symmetrical halls and gateways | Symmetrical but busy (flags, garlands) | Off-centre framing; the king small in a large dark room | Long horizontals: roads, rivers, the chariot leaving |
| Camera | Slow tilt and pull to reveal scale | Gentle push; crane-up over the decorated city | Static or slow push; one 4–6° Dutch angle at most, only in the anger chamber | Static wides, slow pull-backs (isolation); Bharata's chariot trucks right to left (towards Rama in the forest) |
| Motion | Banners, chamara fans, birds | Petals, flames, flags unfurling, distant crowds | Very little: a flame bending, a curtain stirring, a jewel rolling | Wind, dust behind the chariot, river current, falling leaves |
| Sound | Tanpura, reed phrase, bells; Dasharatha motif; Rama motif | Celebration bed: procedural *nagada* pulse, conch, bells, crowd murmur | Melody out; drone, heartbeat at 60–70 bpm, tension motif; 0.4 s silences | Bansuri alone (grief phrase), no percussion; Rama motif slowed; Bharata's devotion gets a warm major-feeling phrase |
| Rasa (traditional, approximate) | *vīra*, *adbhuta*, *śānta* | *śṛṅgāra* of a city, joy | *bhayānaka*, *raudra* | *karuṇa*, then *śānta* |

### 3.3 Shot vocabulary per phase

| Phase | Signature shots |
|---|---|
| 1 | EWS of Ayodhya beside the Sarayu at morning; WS of the throne hall under the white royal parasol (2.2.7); MCU of Dasharatha with white hair, lit gold; insert of peacocks crying at a rain cloud (the simile, 2.2.17); first MCU of Rama's face in a lotus courtyard |
| 2 | Rooftops with banners unfurling; the royal road strewn with flowers (2.6.17); tall lamp-trees being lit (2.6.18); Rama and Sita at the shrine fire on a kusha mat (2.6.1–4); a daytime meteor streak over the palace (2.4.17); a figure on the moon-white terrace looking down (2.7.1–2) |
| 3 | Kaikeyi's anger chamber: dark floor, scattered jewels, a single lamp; Dasharatha's hand on the floor; Manthara in silhouette in a doorway; the city's lights continuing outside the window (dramatic irony) |
| 4 | Bark garments held in hands; the chariot leaving through the gate with dust (screen direction left to right); the Tamasa at night; the Ganga crossing in Guha's boat; Chitrakuta's mountain and the Mandakini; the empty throne with the sandals (2.113–115) |

---

## 4. Characters for Ayodhya Kanda

The full bible, with keyframe prompts, is in `profiles/characters/ayodhya_kanda.json`. Summary here.

### 4.1 Art-style prefix (one string for the whole Kanda)

> hand-painted animated feature film still, soft gouache and watercolour textures, Pahari miniature colour palette of warm ivory, saffron, lapis blue, leaf green and vermilion, gentle golden rim light, ancient Indian setting with carved sandstone pillars and stepped shikhara towers, graceful expressive Indian faces with calm almond eyes, clean confident linework, vertical composition with open sky at the top and calm space at the bottom

It is positive-only, because Z-Image Turbo ignores negative prompts (WORKFLOW_AUDIT H5). The word "anime" is left out on purpose: in an image model it tends to pull faces and clothing towards Japanese conventions. "Animated feature film" plus explicit Indian detail is the safer wording. Test both versions (§6.4) [U].

### 4.2 Iconography and skin tone

- **[F] What Valmiki says about Rama's appearance:** the people call him *indīvara-śyāma*, dark like the blue lotus (2.2.53); Dasharatha calls him *rājīva-tāmrākṣa*, with lotus-coppery eyes (2.4.2); long-armed, *mahābāhu* (2.2.22). His age at the exile is twenty-five by Sita's account (3.47.10b–11a, vulgate). valmikiramayan.net notes that this line is missing from some older manuscripts, so treat it as an approximate [F, with the caveat].
- **[F] What tradition does:** Pahari painting and Ravi Varma's prints paint Rama blue, and blue is now the popular expectation. The 1992 film also used blue.
- **[R] Recommendation:** a deep dark skin with a cool blue-lotus undertone. It follows the text's *śyāma* (dark), nods to the familiar blue, and avoids a saturated cartoon blue that reads as fantasy. Bharata is described with warm brown skin in the bible, so the brothers stay distinguishable to the model [R; the text does not settle his colour, U].
- **Sita:** shown with a golden-wheat complexion, as tradition paints her. The bible marks this as tradition, because no verse was checked in this pass [U]. Her depiction is never sexualised: full drape, calm, strong presence.
- Deities stay symbolic (radiant light), as in Bala Kanda.

### 4.3 Accent ownership

| Character | Accent | Prop or silhouette key |
|---|---|---|
| Rama | Yellow *pītāmbara* silk with a saffron sash | Simple gold diadem; the bow outdoors |
| Sita | Ivory silk with a broad gold border; lotus-pink *uttarīya* | Long braid, gold forehead ornament |
| Lakshmana | Leaf green | Bow and quiver |
| Bharata | Deep maroon and gold | Kaikeyi's colours, softened; later mourning white |
| Shatrughna | Teal | Sword at the hip |
| Dasharatha | Saffron and white; white beard | Tall gold crown, the white parasol |
| Kaushalya | White and gold | Prayer beads (she is at worship in 2.4.30) |
| Sumitra | Green and gold | Small crown |
| Kaikeyi | Crimson and gold | Ornate jewellery (cast off in 2.10) |
| Manthara | Dusty earth-brown and grey | Slight stoop, one gold ring |
| Vasishtha | White robes, silver beard | Water pot or staff |

---

## 5. Sound direction for Ayodhya Kanda

No copyrighted music. Everything below is procedural (`chalk.music`, `chalk.sound`) or comes from commercially free models (ACE-Step 1.5, MIT; Magenta RealTime 2, Apache-2.0 code with CC-BY-4.0 weights) that are **still untested** (`docs/TOOLS_AND_SKILLS_RESEARCH.md` §3.1). The mix follows the `audio-mix` skill: narration at −16 LUFS, music 18–22 dB under speech, two-pass −14 LUFS.

### 5.1 Instruments

| Role | Instrument | Feasible source |
|---|---|---|
| Drone (series constant) | Tanpura, Sa = 146.83 Hz | `chalk.music` (exists) |
| Royal and auspicious phrases | Reed, shehnai-like | Hard to synthesise (VQ §4.4). Use a nasal additive-synth phrase in `flute_phrase` style with odd harmonics, or an ACE-Step bed. Freesound CC0 has 0 shehnai files (VQ §4.7) |
| Celebration pulse | *Nagada* and *dhol* | Procedural percussion (new one-shot, numpy) or CC0 tabla and drum hits |
| Sacred | Temple bell, conch | `sfx_bell`, `sfx_conch` (exist) |
| Crowd | Joyful distant crowd | `sfx_army` re-tuned as a crowd murmur, or a Sonniss crowd bed logged in `licenses.csv`. A dedicated `crowd` one-shot is a new item |
| Tension | Low drone, heartbeat | `sfx_heartbeat` (exists), `sfx_rumble` (exists) |
| Grief | Solo bansuri, low register | `flute_phrase` with the `grief` phrase (exists) |
| Night | Wind, distant birds stopping | `sfx_wind`, `sfx_birds` (exist) |

### 5.2 Leitmotifs (semitones from Sa, same format as `chalk.LEITMOTIFS`)

| Motif | Proposed notes `(semitone, seconds)` | Character | Status |
|---|---|---|---|
| `rama` | `[(0,.45),(2,.45),(3,.45),(7,1.2),(3,.4),(2,.4),(0,1.4)]` | Rising, resolved | **exists** |
| `dasharatha` | `[(7,1.0),(5,0.6),(4,0.6),(2,0.8),(0,2.0)]` | Slow descent on *shuddha* notes, a tired majesty; with a bell | proposed |
| `ayodhya` (royal, celebration) | `[(0,.4),(4,.4),(7,.4),(9,.6),(7,.4),(4,.4),(5,.4),(7,1.4)]` | Bright, *shuddha* scale (Bilawal colour) | proposed |
| `kaikeyi` (tension) | `[(1,.8),(6,.6),(5,.6),(1,1.8)]` | Komal Re and tivra Ma (Todi colour), unresolved | proposed |
| `manthara` | the `kaikeyi` motif an octave lower, plucked, half speed | Shares the tension family | proposed |
| `unresolved` | exists | Cliffhanger | **exists** |

Raga and rasa links are traditional and approximate, "not an exact science" (VQ §4.4). Keep Sa constant so the motifs stay recognisable across Kandas.

### 5.3 Progression from celebration to sorrow

1. **Phase 1:** tanpura, `dasharatha` motif with a bell, `rama` motif at Rama's first close-up; light reed phrase.
2. **Phase 2:** add the celebration bed (`ayodhya` motif plus nagada pulse plus conch at the decorated-city shots). Duck hard under narration; swell in the gaps.
3. **Phase 3:** a `drop` cue takes out the melody and drums at once. Drone, heartbeat and the `kaikeyi` motif. Planned silences of 0.4–0.8 s.
4. **Phase 4:** bansuri `grief` alone, no percussion. The `rama` motif returns at half speed. A warm phrase for Bharata's devotion at Chitrakuta (sandals).

### 5.4 Model beds (test before use)

- **ACE-Step 1.5** (8–12 GB, run alone): prompts such as "royal Indian court celebration, shehnai-like reed, soft nagada drum, temple bells, bright and festive, no vocals" and "sorrowful solo bansuri over soft tanpura drone, slow, no percussion, no vocals". 30–40 s beds, looped or crossfaded.
- **Magenta RealTime 2 small** (real-time on the Air): the same prompts, as an A/B.
- **Pass criteria (VQ §4.7):** the owner prefers the bed blind over procedural in 2 of 3 moods; it sits on Sa = 146.83 Hz without clashing; there are no vocals or artifacts. Until then, the procedural engine is the default.

---

## 6. Production notes

### 6.1 Pipeline fit
- **Keyframes:** Z-Image Turbo 4-bit at 768×1344 (about 100 s each, measured), with `{character}` tokens from `profiles/characters/ayodhya_kanda.json` and the Kanda prefix. Faces are the new risk: generate 4 seeds per character for an owner-approved reference sheet (VQ §3.4 step 3), then use FLUX.2 klein reference conditioning once tested (A9).
- **Motion:** as in §2.3. Image-to-video clips are shared across languages; each language trims or holds them to its own scene timings.
- **Engine work needed (not in this proposal):** a non-chalk render path in `studio.py` and `styles.py` (an `animated` preset that skips `chalk_from_image` and the stroke reveal), clip import with a trim and hold per scene, and the chalk-to-paint bridge shot.

### 6.2 Memory
Never run two heavy models at once. Z-Image (8.3 GB peak), LTX-2.3 (16 GB claim), ACE-Step (8–12 GB) and Maya 2 each run alone under `data/heavy.lock`, with `pipeline progress --oneline` updates every 3–5 minutes.

### 6.3 Quality risks
- Faces drifting between shots (mitigated by reference sheets and 2-character limits).
- Extra limbs in crowds (crowds distant and separated only).
- Photoreal drift in video models (keep the painterly prefix strong; reject clips that go photographic).
- Indian costume turning Mughal or Japanese (explicit ancient-Indian costume words in every prompt).
- Skin-tone instability for Rama (test 4 seeds; keep the exact wording).

### 6.4 Proposed owner test (about 45 minutes, one model at a time)
1. Z-Image: 4 AK01 keyframes (shots 1, 5, 9, 11) with the prefix, and the same 4 with "anime" added: 8 images, about 14 min.
2. LTX-2.3: 1 hero clip (shot 1) to measure real time and peak RAM on the M5 Air, about 15–20 min.
3. A side-by-side page: chalk Ep08 frame | Pahari Gold still | 2.5D motion | image-to-video clip. The owner chooses.
