# Creative direction and storytelling research: RAMAYANA, The Epic in Chalk

**Research date:** 2026-11-16, about 45 web searches and fetches plus a repo audit.
**Scope:** under-60 s storytelling, Valmiki accuracy, cinematography for animated stills, visual identity bible and sound direction. Each part maps to fields the pipeline can encode.
**Inputs read:** `PROJECT_CONTEXT.md`, `.claude/skills/storytelling/SKILL.md`, `.claude/agents/creative-director.md`, `.claude/agents/scriptwriter.md`, `styles.py`, `chalk.py`, `profiles/characters/ramayana.json`, and the scripts and QA files for C0003, C0004 and C0005.
**Related notes (not repeated here):** `research_notes/Shorts studio voices and tools/visual_animation_tools.md` (depth and parallax tools, licences) and `.../audio_automation_skills.md` (music models, licences).

**Evidence tags used throughout**
- **[F]** sourced fact, with a link in the bullet or in §8.
- **[M]** measured in this repo, with the file named.
- **[R]** creative recommendation (judgement, not evidence).
- **[U]** unverified or from prior knowledge. Check before relying on it.

---

## 0. Executive summary

1. **[M]** The current engine wastes the first second. In `chalk.plan()`, scene 1 always starts as an empty board and takes 1.6 s to draw. Every later scene spends 2.0–3.6 s on its stroke reveal and 0.55 s on an erase. In a 45 s short with about 12 shots, most images are fully visible for only about 1 s. **[R]** Frame 0 must show a readable, high-contrast image. Keep the full stroke-draw for 2–3 hero reveals per episode, and use fast (0.5–0.8 s) or instant reveals elsewhere.
2. **[F]** Both platforms reward completion and replays. Since 2025-03-31, a Shorts view counts each start or replay. Monetisation and "engaged views" exclude loops. Instagram's most important Reels predictions are reshare, watch to the end and like. **[R]** The 35–55 s target is right. Design every episode to loop: the last image and line should hand back to the first.
3. **[M]** Measured effective narration rates are EN 2.55–2.67 words/s and HI 2.51–2.63 words/s (pauses and transitions included). Gujarati runs about 1.9–2.1 and Telugu about 1.4–1.6. At 45 s the word budget is about 115 EN / 115 HI / 92 GU / 68 TE words, which is roughly half of today's 191–257.
4. **[F]** The project's verse numbers follow the vulgate (southern recension, valmikiramayan.net and sa.wikisource). The Baroda Critical Edition (CE) and Goldman's Princeton translation number some verses differently; for example, *mā niṣāda* is 1.2.14 in the CE and 1.2.15 in the vulgate. **[R]** Label the edition on every citation.
5. **[R]** Add a per-scene shot grammar (`shot`, `angle`, `move`, `reveal`, `transition`, `hit`) and let one still serve several shots through crops. That gives more shots per image without more model time. See §3.6 for the schema and §3.7 for a worked 45 s version of Ep05.
6. **[R]** Keep the chalkboard identity constant: black board, chalk texture, the house palette and caption font. Vary only the *accent hue* per world (gold for Ayodhya, green for forest, crimson for Lanka) and the *line treatment* per narrative layer (Kalamkari or Pattachitra-style line for tales-within-the-tale, Mewar-style continuous narration for journeys).
7. **[R]** Keep the audio hierarchy as narration > SFX > music. Add an impact hit at frame 0, a silence before every payoff, and character leitmotifs on the existing procedural raga engine. Avoid third-party music, because any Content ID claim blocks a Short longer than 1 minute globally **[F]**.

---

## 1. Short-form storytelling under 60 seconds

### 1.1 Platform facts [F]

| Fact | Source |
|---|---|
| From 2025-03-31, Shorts views count every start and replay with no minimum watch time. The older metric was renamed "engaged views" (moved to Advanced Mode), and it still drives YPP earnings. | [TechCrunch 2025-03-26](https://techcrunch.com/2025/03/26/youtube-is-changing-how-youtube-shorts-views-are-counted) |
| YouTube Help defines engaged views as "How many times viewers stayed to watch past the initial seconds, not including any loops." The Shorts "How viewers engaged" report gives "the percentage of times viewers stayed to watch past the initial seconds of a Short." | [YouTube Help 12220281](https://support.google.com/youtube/answer/12220281) |
| Shorts can be up to 3 minutes (from Oct 2024). A Short over 1 minute with an active Content ID claim is **blocked globally** (not playable, not recommended). Audio Library tracks are capped at 90 s, and some at 60 or 30 s. | [YouTube Help 15424877](https://support.google.com/youtube/answer/15424877?hl=en) |
| YouTube's Shorts lead Todd Sherman: there is no ideal length, so prioritise the story. "The audience is the algorithm." A view should "encode for your intent of watching that thing." | [Search Engine Journal (2023 interview)](https://www.searchenginejournal.com/youtube-explains-how-shorts-algorithm-works/494953/) |
| Jenny Hoyos (YouTube blog): "you have one second to hook someone, especially on Shorts." Her opening runs startle, then curiosity, then payoff. She says 99.9% of Shorts views come from the feed, so thumbnails barely matter for discovery. Sherman notes creators also make 15-second "moments." | [YouTube Blog, Shorts deep dive](https://blog.youtube/creator-and-artist-stories/youtube-shorts-deep-dive/) |
| Instagram: "The most important predictions we make are how likely you are to reshare a reel, watch a reel all the way through, like it," plus whether you visit the audio page. Watermarked, low-resolution and reposted reels are made less visible. | [Instagram Ranking Explained](https://about.instagram.com/blog/announcements/instagram-ranking-explained) |
| Mosseri (Jan 2025, reported secondhand) named watch time, likes per reach and sends per reach as the top three signals. He said sends matter more for reaching non-followers. Reels went to 3 minutes in Jan 2025. | [Social Media Today](https://www.socialmediatoday.com/news/instagram-officially-expands-reels-length-3-minutes/737766/); [secondary summary](https://buffer.com/resources//instagram-algorithms/) |
| Curiosity is an information-gap effect. People need enough knowledge to notice the gap, and the gap has to feel closable (Loewenstein 1994, *Psychological Bulletin* 116(1):75–98). | [summary](https://stafforini.com/works/loewenstein-1994-psychology-curiosity-review/); [Golman & Loewenstein PDF](https://www.cmu.edu/dietrich/sds/docs/golman/Information%20Gaps--Golman%20and%20Loewenstein.pdf) |

**Not official [U]:** the "70%+ viewed vs swiped" benchmarks, the "50% drop before 4 s" figure and the "sends weigh 3–5× likes" multiplier come only from marketing blogs. Do not use them as targets. Use the channel's own `pipeline analytics` data once it exists.

### 1.2 What this means for the series [R]
- **Completion rate is the lever.** A 45 s video watched to the end, and sometimes replayed, beats a 90 s video abandoned at 40 s. Shorter runtime raises completion almost mechanically.
- **Shares (sends) carry mythology to new audiences.** Give each episode one sentence people would forward: a surprising textual fact ("In Valmiki there is no Lakshman Rekha"), a moral line, or the verse. Make it legible on screen.
- **The first second is visual first.** Captions and the opening word land within 0.3 s, but the image is what stops the scroll.

### 1.3 The beat framework

Core beats [R], based on Hoyos's startle → curiosity → payoff (sourced) and Loewenstein's gap theory:

| Beat | Job | Rule |
|---|---|---|
| **H1 Hook-visual** | Stop the scroll | Frame 0 shows the most striking image of the episode, already readable. Impact sound at 0.0 s. |
| **H2 Hook-line** | Open the main loop | A contradiction, a specific number or a stake, ≤12 EN words. First word at ≤0.3 s. |
| **C Context** | Ground the viewer | Who, where and why in ≤2 shots. Each name used is earned by the story. |
| **E Escalation** | Raise stakes, open loop 2 | Answer one small question and open another. Pattern interrupt here. |
| **T Turn** | Reversal or reveal | Hold or silence the sound for 0.3–0.6 s first. The verse card belongs here if used. |
| **P Payoff** | Close the main loop | Fastest cutting and the loudest moment, then a hard stop. |
| **N Next / loop** | Cliffhanger plus loop | One line that opens the next episode's question. The final image composition matches frame 0. |

**Pattern interrupts [R]:** change at least one of shot size, angle, colour accent, sound bed or rhythm every 6–8 s. Never change all of them at once except at the Turn.

**Open-loop cadence [R]:** this tightens the existing "every 2 scenes" rule to "a new or answered question every 8–12 s". In a 45 s video that is about 4 loops: the main loop (H2 to P) plus 2–3 small ones.

#### 35 s (single beat, an "anecdote" episode)
| t (s) | Beat | Shots | Words EN/HI | Notes |
|---|---|---|---|---|
| 0.0–2.0 | H1 + H2 | 1 (hero, instant reveal) | 8–10 | impact hit at 0.0 |
| 2.0–8.0 | C | 2 | 14–16 | one establishing wide |
| 8.0–18.0 | E | 3 | 25 | interrupt at about 12 s |
| 18.0–25.0 | T | 1–2 | 15 | 0.4 s silence before |
| 25.0–31.0 | P | 2 | 14 | fastest cuts |
| 31.0–35.0 | N/loop | 1 | 8–10 | composition matches frame 0 |
| **Total** | | **10–11 shots (6–8 stills)** | **≈85–90 EN/HI · 70 GU · 50 TE** | |

#### 45 s (default)
| t (s) | Beat | Shots | Words EN/HI |
|---|---|---|---|
| 0.0–2.0 | H1 + H2a | 1 | 8–10 |
| 2.0–4.5 | H2b (the stake or twist) | 1 | 6–8 |
| 4.5–12.0 | C | 2 | 18–20 |
| 12.0–22.0 | E (interrupt at about 13 s; loop 2 opens) | 3 | 25–28 |
| 22.0–30.0 | T (silence, optional verse card) | 2 | 16–18 |
| 30.0–40.0 | P | 3 (short) | 20–22 |
| 40.0–45.0 | N/loop | 1 | 10–12 |
| **Total** | | **12–13 shots (8–10 stills)** | **≈110–118 EN/HI · 90 GU · 65–70 TE** |

#### 55 s (two-beat, for dense episodes; keep 3 s of margin below 60 s)
| t (s) | Beat | Shots | Words EN/HI |
|---|---|---|---|
| 0.0–2.0 | H1 + H2a | 1 | 8–10 |
| 2.0–5.0 | H2b | 1 | 7–8 |
| 5.0–13.0 | C | 2 | 20 |
| 13.0–24.0 | E1 (loop 2 opens and closes) | 3 | 28 |
| 24.0–33.0 | T1 (verse card optional) | 2 | 20 |
| 33.0–43.0 | E2 (escalation, loop 3) | 3 | 25 |
| 43.0–50.0 | P | 2–3 | 18 |
| 50.0–55.0 | N/loop | 1 | 10–12 |
| **Total** | | **15–16 shots (10–12 stills)** | **≈135–140 EN/HI · 110 GU · 80 TE** |

### 1.4 Word budgets and narration rate

**[M] Measured effective rates.** These divide total narration words by rendered duration (from each language's `script.json` and `qa.md`), so they include pauses, erase transitions and verse cards:

| Lang | Episodes (words / s) | Effective rate |
|---|---|---|
| en (Kokoro af_heart, speed 1.04–1.08) | C0002 207/77.5 · C0003 235/89.5 · C0004 191/74.8 · C0005 214/82.0 | **2.55–2.67 w/s (153–160 wpm)** |
| hi (Malini or Veena) | C0002 255/101.6 · C0003 251/99.3 · C0004 217/83.2 · C0005 257/97.8 | **2.51–2.63 w/s** |
| gu (Malini) | 217/104 · 205/108.5 · 193/93.3 · 230/107.5 | **1.89–2.14 w/s** |
| te (Malini) | 156/105.3 · 156/109.1 · 155/99.5 · 174/111.2 | **1.43–1.56 w/s** (agglutinative, so fewer and longer words) |

**[F]** For comparison, audiobook convention is about 150–160 wpm, with 130–150 for dense educational content ([BookFoundry calculator](https://bookfoundry.ai/audiobook-length-calculator/), secondary). English narration already sits at the brisk end. Do not speed the voice up to fit the target; cut words instead.

**[R] Budget formula:** `words ≤ rate × (target − 1.0 s tail − verse_card_seconds)`. Planning rates are 2.6 for en and hi, 2.0 for gu and 1.5 for te. For a 45 s episode with a 3 s silent verse card that gives 107 EN words. Add a hard validator: estimated duration ≤ 57 s.

**[R] Verse recitation in short format.** A full anuṣṭubh shloka recited in Hindi costs about 6–9 s, which is 15–20% of a 45 s episode. Options:
- (a) put the verse on screen only, while the narration gives the meaning;
- (b) recite just one pāda (about 2–3 s) as the hook or the payoff;
- (c) save full recitation for a separate "Shloka of the day" Short.

### 1.5 Hooks for 35–55 s [R]
The existing 6-criterion rubric (curiosity, emotion, specificity, speed, resonance, accuracy) still applies. Add two checks:
- **Visual hook check.** Can frame 0 alone make sense of the hook without audio? (Many viewers start muted; captions and image must carry it.)
- **Hook-to-payoff distance.** The main loop must close by 85–90% of runtime. A hook paid off only by "Next episode" breaks trust.

Hook types that suit this series, with examples drawn only from verified lines in C0003–C0005:
- *Contradiction:* "Rama's first enemy had the strength of a thousand elephants. And he did not want to kill her." (C0005, 1.24.26, 1.26.12)
- *Request with a twist:* "A king promised a sage anything. The sage asked for his son." (C0004)
- *Text-vs-belief:* "Every TV Ramayana shows the Lakshman Rekha. Valmiki never wrote it." (see §2.2). This one is high-share but needs a respectful frame.
- *Sensory in medias res:* open on the twang of a bowstring (1.26.6–8), with sound and image only for the first 0.8 s.

### 1.6 Endings, cliffhangers and loops [R]
- **Payoff then button.** Close the episode's loop first, then open the next with exactly one line. The existing "Next:" title card is good; keep it to ≤3 words.
- **Loop construction.** Pick one of three:
  - (1) *Composition loop:* the final shot reuses frame 0's composition. For example, end on Tataka's silhouette fading into the bloomed forest at the same framing.
  - (2) *Sentence loop:* the last line flows into the first, e.g. last "…and that was only his first enemy." with first "Rama's first enemy had the strength of a thousand elephants." Never cut a sentence mid-word just to fake a loop; it reads as an error in Hindi and regional languages.
  - (3) *Sound loop:* music that ends on the note the intro starts on.
- **Engagement prompt.** One per episode at most, ≤6 words, or move it to the pinned comment. Ask questions with a real answer in the text ("Which sage cursed her? Comment."), not generic "like and subscribe".
- **Series glue.** A fixed 0.5 s series sting (the same chalk-snap and bell) at the very end, plus a small "Ep 5" badge in the top 12% headroom, builds recognition without spending narration time.

### 1.7 Craft sources informing the framework
- Murch's *Rule of Six* (emotion 51%, story 23%, rhythm 10%, eye-trace 7%, 2-D plane 5%, 3-D space 4%) **[F]** ([UT Austin RTF wiki](https://wikis.utexas.edu/display/rtf318/Murch%27s+Rule+of+Six)). **[R]** Choose each cut first for emotion, then for story. Eye-trace matters more than usual on a 9:16 phone: keep the subject of consecutive shots in roughly the same screen zone so the eye does not hunt.
- Loewenstein's information gap **[F]** (above). **[R]** A hook works only if the viewer already knows enough. "Rama" and "Ravana" are known to the Indian audience, so gaps built on known names ("Rama hesitated") outperform gaps built on unknown names ("Suketu's daughter").

---

## 2. Making Valmiki engaging while staying accurate

### 2.1 Editions, recensions and citing [F]
- **Critical Edition (CE).** Oriental Institute, Baroda, 1951–1975, seven volumes. General editor G. H. Bhatt; Bālakāṇḍa 1958 (Bhatt), Ayodhyākāṇḍa 1961–62 (P. L. Vaidya), Uttarakāṇḍa 1973–75 (U. P. Shah). It was reconstructed from over 2,000 manuscripts and is widely called the most reliable text. ([Cambridge JRAS review](https://www.cambridge.org/core/journals/journal-of-the-royal-asiatic-society/article/valmikiramayana-critical-edition-general-editor-g-h-bhatt-volume-ii-ayodhyakanda-edited-by-drp-l-vaidya-pp-iv-706-lxvi-oriental-institute-baroda-19611962/019DF2CE532AC9EF190497A43A065D26); [Free Press Journal](https://www.freepressjournal.in/book-reviews/the-ramayana-of-valmiki))
- **Recensions.** The text survives in Northern and Southern recensions, with sub-versions by script. The CE editors systematically preferred the Southern recension, which keeps more grammatical and metrical irregularities. ([Clay Sanskrit Library intro](https://claysanskritlibrary.org/book-extras/ramayana-book-i-boyhood-ancilliaries-introduction/); [INDOLOGY list, 2016](https://list.indology.info/pipermail/indology/2016-November/044710.html))
- **Goldman translation.** *The Rāmāyaṇa of Vālmīki: An Epic of Ancient India*, Princeton University Press, 7 volumes, 1984–2017. Led by Robert P. Goldman with Sally J. Sutherland Goldman and others, it translates the CE. "Most Indologists" regard much of the Uttarakāṇḍa as by a later hand. ([Princeton UP vol. VII](https://press.princeton.edu/books/hardcover/9780691168845/the-ramayana-of-valmiki-an-epic-of-ancient-india-volume-vii); [vLex review](https://law-journals-books.vlex.com/vid/the-ramayana-of-valmiki-730754705))
- **Numbering differs.** The CE numbers *mā niṣāda* as **1.2.14** ([INDOLOGY](https://list.indology.info/pipermail/indology/2016-November/044710.html)). The project's storytelling skill example and vulgate sites use **1.2.15**. Interpolated verses (present in the vulgate, relegated to the CE apparatus) have no CE number at all.
- **valmikiramayan.net** gives verse-by-verse Sanskrit with word meanings. Translators are Desiraju Hanumanta Rao (Bāla, Araṇya, Kiṣkindhā) and K. M. K. Murthy (Ayodhyā, Sundara, Yuddha), and the site follows vulgate numbering. Its home page does not name the Sanskrit edition. ([valmikiramayan.net](https://www.valmikiramayan.net/))
- **IIT Kanpur** (now heritage.iitk.ac.in/valmiki) organises all 7 kāṇḍas by sarga with summaries. The landing page does not name its source edition either. ([heritage.iitk.ac.in/valmiki](https://heritage.iitk.ac.in/valmiki/))
- **[U]** IIT Kanpur's text is widely reported to follow the Gita Press (Gorakhpur) edition. Not confirmed this session.

**[R] Citation policy**
1. Cite as `VR <kāṇḍa>.<sarga>.<verse> (vulgate)`, which is what the team already verifies against sa.wikisource and valmikiramayan.net. Add `[CE x.y.z]` when checked against Goldman or the CE.
2. Put the edition in `script.json` `sources`, e.g. `"edition": "vulgate (sa.wikisource रामायणम्)"`.
3. If a famous line is *not in the CE*, say "found in the southern manuscripts" rather than "Valmiki says".
4. For on-screen verses, always show the locator, which `text_scene` already does.
5. Prefer narrating actions over quoting. Quote only lines that are translations of a located verse.

### 2.2 Popular beliefs vs Valmiki's text (verified this session)
| Popular version | Valmiki | Where it comes from | Source |
|---|---|---|---|
| Lakshmana draws the **Lakshman Rekha** | **Absent.** Lakshmana leaves after Sita's harsh words, with no line drawn. | Ramcharitmanas does *not* have it in Araṇya Kāṇḍa; Mandodari mocks Ravana in **Laṅkā Kāṇḍa 35.1** for being unable to cross "a small line drawn by Lakshmana". Later the Radheshyam Ramayan and TV made it central. | [Wikipedia: Lakshmana rekha](https://en.wikipedia.org/wiki/Lakshmana_rekha); [Scroll](https://scroll.in/article/981115/what-can-notions-of-dharma-and-contemporary-law-tell-us-about-the-ramayana-two-books-investigate) |
| **Ahalya turned to stone** | Cursed to remain **unseen by all beings in the hermitage, living on air, lying on ash** until Rama comes (VR 1.48, vulgate) | Adhyātma Rāmāyaṇa and later retellings | [valmikiramayan.net 1.48](https://www.valmikiramayan.net/utf8/baala/sarga48/balaitrans48.htm); [Hindupedia](https://hindupedia.com/en/Ahalya) |
| **Shabari's tasted berries** | Shabari offers roots and fruits as hospitality; **no tasting** (Araṇya Kāṇḍa) | Probably the Adhyātma Rāmāyaṇa or the Odia Dandi Ramayana (Balaram Das); Kamban and Ranganatha don't have it | [Devdutt Pattanaik](https://devdutt.com/did-shabari-actually-feed-ram-tasted-berries/); [Wikipedia: Shabari](https://en.wikipedia.org/wiki/Shabari) |
| **Sita swayamvara** with assembled kings | Janaka declared Sita *vīryaśulkā* (won by valour). Kings had come and failed **individually** before; Rama breaks the bow on Vishvamitra's visit. Sudhanvan once besieged Mithila for bow and bride. | Ramcharitmanas staging, TV | [Wikipedia: Sita Swayamvara](https://en.wikipedia.org/wiki/Sita_Swayamvara) (contested in parts) |
| **Ravana lifts Sita with the earth, without touching her** | Ravana physically seizes Sita and carries her in his aerial chariot | **Kamba Ramayanam** (Tamil); the reason differs by source | [Devdutt: A Tamil reimagining](https://devdutt.com/a-tamil-reimagining-of-the-ramayana/); [Hindu Blog](https://www.hindu-blog.com/2017/10/difference-between-kamba-ramayana-and.html) |
| **Maya Sita** (the real Sita hidden in fire) | Absent | Bhakti retellings (Adhyātma, Ramcharitmanas) | [ThePrint excerpt](https://theprint.in/pageturner/excerpt/ravana-touching-sita-bhakti-poets-created-maya-sita/2489460) |

**[U] Not verified this session:** the squirrel at the setu, Hanuman's *gada* as signature weapon (in Valmiki he mostly fights with trees, rocks and fists), and the "Kodanda" bow name. Check each in the text before use.

**Regional retellings the language audiences know [F]**
- **Hindi:** Tulsidas' *Ramcharitmanas* (16th c., Awadhi) renames Yuddha Kāṇḍa as Laṅkā Kāṇḍa ([Scroll](https://scroll.in/article/981115/what-can-notions-of-dharma-and-contemporary-law-tell-us-about-the-ramayana-two-books-investigate)).
- **Tamil:** Kamban's *Ramavataram*.
- **Telugu:** *Molla Ramayanam* by Atukuri Molla (late 15th or 16th c.), in accessible Telugu and kandam metre, hence "Kanda Ramayanam" ([Wikipedia](https://en.wikipedia.org/wiki/Molla_Ramayanam)). Also the Ranganatha Ramayanam.
- **Gujarati:** Giridhar's *Ramayan* (1835 or 1837; poet 1787–1852), drawn mainly from Valmiki and the *Hanumannāṭaka* ([Wikipedia: Girdhar](https://en.wikipedia.org/wiki/Girdhar)).
- **Television:** Ramanand Sagar's *Ramayan* (1987) is primarily based on Valmiki and the Ramcharitmanas, and partly on Kamban and other regional versions ([Wikipedia](https://wikipedia.com/wiki/Ramayana_(TV_series))). Most viewers' "default" Ramayana is therefore a blend.

**[R] How to use the differences without offending anyone**
- Frame them as "**In Valmiki's telling…**", never "the real story" or "myth busted". Name the later tradition with respect: "Tulsidas, centuries later, added…".
- Use differences as **hooks** sparingly, at most one per 4–5 episodes. Each must be accurate in both directions: do not say "Tulsidas invented the Lakshman Rekha" when he only mentions it in Laṅkā Kāṇḍa.
- In the gu and te versions, a light nod to Giridhar or Molla where they agree with Valmiki builds resonance. Where they differ, follow Valmiki and stay silent unless the episode is about the difference.

### 2.3 Avoiding invented quotes [R]
- Reported speech is safe ("Rama told Lakshmana he could not kill her"). Direct speech in quotation marks must map to a located verse; record the locator in `sources` next to the scene number.
- Never use famous TV-serial dialogue or Ramcharitmanas chaupais as if they were Valmiki.
- Paraphrase must not add motives the text lacks. For example, Valmiki gives Dasharatha's fear and his "not yet sixteen" line (1.20.2), not modern feelings about "a father's heartbreak". Keep adjectives modest.
- Add a script QA check: every `"` in narration needs a `quote_src` field.

### 2.4 Sanskrit and name pronunciation [F/R]
**[F]** Sanskrit keeps the final inherent *a* (Rāma [raːmɐ]). Hindi drops it (राम = Rām); the spelling is the same, so readers must know the rule. Dravidian languages (Telugu among them) and Odia keep the schwa; Bengali drops it ([American Kahani](https://americankahani.com/perspectives/ram-or-rama-the-linguistic-story-behind-a-sensationalized-debate-triggered-by-amitabh-bachchan/); [ACL 2020 schwa paper](https://aclanthology.org/2020.acl-main.696)).

**[R] Per-language rules**
- **hi:** natural Hindi forms in narration (राम, लक्ष्मण, दशरथ, विश्वामित्र, ताड़का). Recite verses with Sanskrit schwa retained (no deletion inside a shloka). The ज्ञ↔ग्य QA normalisation already exists.
- **te:** schwa retained naturally (Rāmuḍu, Sīta, Lakṣmaṇuḍu in Telugu forms). Follow the Telugu script's own spelling.
- **gu:** schwa largely deleted, like Hindi (રામ, લક્ષ્મણ).
- **en (Kokoro):** use the existing per-scene `tts` override (in `studio.py`, `sc.get("tts", sc["narration"])`). Keep captions in standard spelling and put phonetic respellings in `tts`.

**[R] English TTS respelling table** (starting point; confirm by ear)
| Name (IAST) | Caption | `tts` respelling to try | Watch for |
|---|---|---|---|
| Rāma | Rama | "Raama" | not "Ray-ma" |
| Sītā | Sita | "Seetaa" | |
| Lakṣmaṇa | Lakshmana | "Luck-shmun" or "Lukshmana" | retroflex ṇ cannot be rendered; accept |
| Daśaratha | Dasharatha | "Dusha-ratha" | |
| Viśvāmitra | Vishvamitra | "Vishwaa-mitra" | |
| Vasiṣṭha | Vasishtha | "Vasish-tha" | |
| Rāvaṇa | Ravana | "Raavana" | not "Ruh-vah-na" |
| Tāṭakā | Tataka | "Taa-taka" | |
| Mārīca | Maricha | "Maareecha" | not "Ma-rika" |
| Ayodhyā | Ayodhya | "Ayodh-yaa" | |
| Laṅkā | Lanka | "Lunka" | |
| Hanumān | Hanuman | "Hanu-maan" | |

### 2.5 Portraying Ravana with depth, without contradicting the text [F/R]
**[F] Textual anchors (vulgate numbering)**
- **5.49.17–18.** Hanuman, seeing Ravana enthroned: "Ah, what form! What courage! What strength! What radiance! … endowed with every auspicious mark." Then: "If this lord of rakshasas were not so strong in adharma, he could be the protector even of the gods' world, with Indra." ([valmikiramayan.net 5.49](https://www.valmikiramayan.net/sundara/sarga49/sundarasans49.htm))
- **5.18.2–3.** Before dawn in Ravana's realm, Hanuman hears the Vedic chanting of brahma-rakshasas versed in the six Vedāṅgas. Ravana wakes to auspicious music. ([valmikiramayan.net 5.18](https://www.valmikiramayan.net/utf8/sundara/sarga18/sundaraitrans18.htm))
- **3.35.9.** Ravana is ten-necked and twenty-armed, splendidly attired. **6.71.27** uses the name *Daśagrīva*. Sundara Kāṇḍa 49 describes ten heads with ornaments on a crystal throne. ([vedapath 3.35.9](https://vedapath.app/en/ramayana/aranya-kanda/35/3.35.9); [vedapath 6.71.27](https://vedapath.app/es/ramayana/yuddha-kanda/71/27))
- **[U]** Lanka as a splendid golden city: described across Sundara Kāṇḍa sargas 2–9. Exact verses not pulled this session.

**[R] Portrayal rules**
- **Text-backed depth.** Show splendour, learning, music, power and *choice*. 5.49.18 is the ideal frame: greatness undone by adharma. That is depth taken from Valmiki himself, not a modern revisionist "misunderstood Ravana".
- **Do not adopt** Ravana-as-hero readings (some Dravidian-movement or other traditions) in this Valmiki series. If they are ever mentioned, label them as later readings.
- **Visual (update to the character bible).** The existing rule "symbolic only, never multi-armed or third-eyed (reads as Bhairava or Kali)" stays. Proposed evolution once the owner approves:
  - ten crowned heads as a layered silhouette row (text-supported), two visible arms, no third eye;
  - ancient Indian royal ornaments and crowns;
  - no Mughal-coded costume, kohl or modern hair. The *Adipurush* (2023) backlash targeted exactly a "Mughal-style" Ravana, crude dialogue and an "angry" Rama ([The News Minute](https://www.thenewsminute.com/news/adipurush-and-controversies-here-s-whom-film-managed-offend-so-far-178761); [Eastern Eye](https://www.easterneye.biz/adipurush-director-responds-to-controversy-over-saif-ali-khans-islamised-look-as-ravana-its-got-nothing-to-do-with-any-khiljis-nadir-shahs-genghis-khans)).

### 2.6 Cultural sensitivity checklist (India) [F/R]
- **[F]** Scholarly framing of "many Ramayanas" is itself contested. A. K. Ramanujan's essay "Three Hundred Ramayanas" was dropped from Delhi University's syllabus in Oct 2011 after protests ([Wikipedia](https://en.wikipedia.org/wiki/A._K._Ramanujan)).
- **[F]** *Adipurush* drew PILs, rewrites of Hanuman's dialogue and a halt to screenings in Kathmandu over a Sita-birthplace line ([The News Minute](https://www.thenewsminute.com/news/adipurush-makers-modify-jalegi-tere-baap-ki-dialogue-after-backlash-178653)).
- **[R] Checklist**
  - Rama is *maryādā puruṣottama* in tone: calm, never snarky.
  - Sita is never sexualised. The Śūrpaṇakhā mutilation and battle gore happen off-screen (shadow, cut-away) to stay within YouTube's violence policy and audience comfort.
  - Hanuman is never comic.
  - Deities appear as symbols (an existing rule). No deity's feet or face as a joke or meme, and no deity art used for "sound-on trend" Reels.
  - No political or current-events tie-ins.
  - Birthplaces and pilgrimage sites (Ayodhya, Janakpur or Sitamarhi for Mithila, Panchavati) are named neutrally and not disputed.
  - Hindi uses respectful forms (श्रीराम where the audience expects it; the C0003 hook used "Shri Ram").

---

## 3. Cinematography for animated stills

### 3.1 What the engine does today [M]
- `chalk.render()` gives each scene one still with a stroke-by-stroke reveal (`plan()`: first scene 1.6 s, verse 2.6–5.5 s, others 2.0–3.6 s).
- Camera moves are a gentle zoom between 1.00 and 1.10, alternating per scene, a focus drift toward the drawing's centre of mass, and a ±2.5 px sinusoidal jitter.
- Every transition is a 0.55 s streak-erase, and the previous image leaves a "ghost" at 11%.
- Chalk-dust particles follow the stick tip, plus 70 ambient motes. Titles chalk on at the top.
- Canvas is 1188×2112 (10% overscan) for 1080×1920 output, and the source still is 768×1344.
- Consequence: every shot has the same grammar (draw, slow zoom, erase). At 3–4 s per shot this becomes monotonous and the draw consumes the shot.

### 3.2 Shot vocabulary and how to fake each with a still [F/R]
**[F]** The angle conventions in the table are standard film grammar: low angle reads as power, high angle as vulnerability, Dutch tilt as disorientation ([NFI](https://www.nfi.edu/camera-angles/2/); [Wolfcrow](https://wolfcrow.com/15-essential-camera-shots-angles-and-movements/)). The table's "how to fake it" column is **[R]**.

| Shot | Purpose | Prompt keywords (Z-Image) | Fake with stills | Typical duration |
|---|---|---|---|---|
| **EWS** (extreme wide, establishing) | place, scale, awe | "vast panoramic view, tiny figures, towering…" | tilt (9:16 suits vertical tilts) or slow pull-out; 2–3 depth layers | 3–5 s |
| **WS** (wide) | action geography | "full figure, surroundings visible" | slow truck (lateral move) with parallax | 2.5–4 s |
| **MS** (medium) | conversation, explanation | "waist-up" | gentle push 1.00→1.08 | 2.5–4 s |
| **CU** (close-up) | emotion, decision | "close portrait, expression" | push 1.05→1.15; or crop from the MS still | 2–3 s |
| **ECU** (extreme close-up) | detail, tension (eyes, bowstring, arrow tip, hands, fire) | "extreme close-up of hand drawing a bowstring" | generate dedicated *insert* stills (cheap, 1 per hero beat), or crop 2–2.5× from a still + upscale | 0.8–2 s |
| **Low-angle hero** | power, resolve (Rama, Vishvamitra rising) | "low angle looking up, towering against sky" | slight upward tilt plus push; prompt must carry the angle | 2–3 s |
| **High-angle** | vulnerability, smallness (Dasharatha fainting; Sita alone) | "seen from high above, small figure" | slow pull-out (the subject shrinks) | 3–4 s |
| **OTS / from behind** | point of view, mystery; **already the house rule for Rama** | "seen from behind, over his shoulder, facing…" | push toward the subject's target, not the subject | 2–4 s |
| **POV** | immersion (the arrow's path, Hanuman scanning Lanka) | "first-person view of…" | fast push, slight shake | 1–2 s |
| **Silhouette** | menace, symbolism, depiction-safe (Ravana, Tataka, deities) | "solid black silhouette against glowing sky" | the chalk renderer suits this well; rim-light sweep overlay | 2–4 s |
| **Insert / detail** | clarity of a story object (payasa vessel, bow, ring) | "single object on dark board" | instant reveal, micro-push | 1–1.5 s |
| **Top-down map** | journeys, geography | "map of rivers and forests, top-down" | animated chalk line along a route | 3–5 s |
| **Dutch tilt** | disorientation (illusion, curse) | not prompted | rotate the canvas 4–8° in the camera matrix | ≤2 s, rare |

**Camera moves [R]** (implementable in `cam_matrix` and a layer compositor)
- **Push-in** (z 1.00→1.20 ease-in-out): intensifying emotion. **Pull-out:** reveal scale or isolation.
- **Tilt up/down** (focus y moves along the 2112 px canvas): towering subjects; revealing a fortress top to bottom.
- **Truck/track** (focus x moves with depth layers at different speeds): travel, chase.
- **Parallax 2.5D:** split the still into 2–3 depth layers with Depth Anything V2 *Small* (Apache-2.0; larger checkpoints are CC-BY-NC), or with Depth Pro in mflux. Move them at different rates. This is the "Kid Stays in the Picture" technique **[F]** ([Vice/Creators Project](https://thecreatorsproject.vice.com/blog/joe-fellows-teaches-us-how-to-master-25D-photography); [ProVideo Coalition](https://www.provideocoalition.com/animating-parallax-images-in-after-effects-and-apple-motion/)). Fill holes behind the foreground by inpainting, or hide them with chalk ghosting, which suits the style. Tooling and licences are in `visual_animation_tools.md` Q4.
- **Dolly-zoom (vertigo):** foreground layer constant, background layer scales up. Use once per series arc for shock (Dasharatha hearing "Ravana").
- **Shake:** 4–10 px decaying noise for 0.3–0.5 s on impacts (bowstring, arrow, rock rain).
- **Whip:** horizontal motion blur of 6–10 frames as a transition between action shots.
- **Rack focus:** blur the background layer in, the foreground out (needs depth layers).
- **Light and atmosphere overlays:** additive chalk-dust drift (exists), embers (Lanka, battle), smoke wisps (Lanka, yajña fire), falling petals (gods rejoicing, 1.26.27), rain/dust storm (Tataka 1.26.15–20), god-ray sweep (divine reveal). All are cheap numpy layers.

### 3.3 Reveal modes (a new axis specific to chalk) [R]
| Mode | Draw time | Use |
|---|---|---|
| `draw` (current) | 2.0–3.6 s | 2–3 hero reveals per episode: first appearance of a character, the verse card, the final image |
| `fast` | 0.5–0.8 s | default for story shots |
| `instant` | 0 (dust puff covers the cut) | frame 0, action beats, inserts |
| `ghost` | previous image's ghost morphs into the new one over 0.4 s | "meanwhile", memory, tale-within-tale |

**Frame-0 rule:** scene 1 uses `instant` or starts ≥70% drawn. This fixes the current blank-board first frame.

### 3.4 Transitions and motivation [R]
| Transition | Meaning | When |
|---|---|---|
| **Hard cut** | continuity within a sequence | default inside a beat; chalk texture keeps the identity |
| **Erase** (signature) | time or place jump, chapter break | ≤3 per episode: after the hook, at the Turn, before Next |
| **Match cut** | thematic link | shape match (drawn bow arc → crescent moon at dusk), motion match (falling arrow → falling rock), idea match (curse word → withered forest) |
| **Dust blow-out** | action continuity | the chalk dust burst of an impact covers the cut |
| **Flash white** (6 frames) | divine or supernatural | the radiant being rising from the fire (1.16) |
| **Dip to black** (0.4–0.8 s) | death, grief, curse | Dasharatha's death (Ayodhyā), Jatayu |
| **Whip** | speed, chase | battle |
| **Chalk-stroke wipe** | narrative "turn the page" | journeys, map scenes |

**Screen direction [R]:** Rama's party travels left → right (toward the future and Lanka). Threats enter right → left. Keep this consistent across episodes; it is invisible continuity that eye-trace rewards (Murch's 7%).

### 3.5 Pacing per emotion [R]
| Emotion | Avg shot | Move | Reveal | Sound |
|---|---|---|---|---|
| Awe / establishing | 3.5–5 s | slow tilt or pull-out | draw (hero) or fast | swell, drone |
| Explanation / context | 2.5–3.5 s | gentle push | fast | calm bed |
| Suspense | 2–3 s, then one held 4 s shot | slow push, no jitter | fast | drone only, melody removed |
| Action / battle | 0.8–1.5 s | shake, whip, POV | instant | percussion and hits on cuts |
| Revelation / turn | hold 0.4 s silence, then 2–3 s | snap push (0.2 s) | instant | hit, then silence |
| Grief | 4–6 s | static or very slow pull-out | ghost | thin bansuri or sarangi; no drums |
| Divine | 3–4 s | slow push with god-ray sweep | draw | swarmandal glissando and bell |
| Cliffhanger | 2.5–4 s | slow push on a face or object, then hard cut to black or the Next card | fast | unresolved note |

### 3.6 Per-scene shot grammar the pipeline can encode [R]
Proposed additions to the `script.json` scene object. All are optional with backward-compatible defaults, and none of the existing fields change.

```json
{
  "narration": "...",
  "shot": "ECU",
  "angle": "low",
  "image": "s01",
  "crop": [0.30, 0.18, 0.45],
  "move": {"type": "push", "z": [1.0, 1.18], "ease": "inout"},
  "reveal": "instant",
  "transition": "cut",
  "dur_hint": 2.0,
  "hit": {"name": "impact", "at": 0.0},
  "sfx": [{"name": "bowstring", "word": "bow"}],
  "music": {"cue": "drop", "leitmotif": "rama"},
  "overlay": ["dust", "embers"],
  "accent": "crimson"
}
```

Field semantics:
- `image` + `crop` (cx, cy, width-fraction) let several shots reuse one still. A wide still yields MS and CU crops at no extra model time (about 100 s per image saved) **[M]**, from the PROJECT_CONTEXT §8b rate. ECU crops beyond 2× need dedicated insert stills or an upscaler (SeedVR2 is in mflux, per `visual_animation_tools.md`), because 768 px source width is the limit.
- `move.type`: `static | push | pull | tilt | truck | parallax | dollyzoom | shake | whip`.
- `transition`: `cut | erase | match | dust | flash | black | whip | wipe`.
- `accent` picks the per-world palette hue (§4.2). It requires `restrict_palette()` to accept a per-scene hue set instead of the global `PALETTE_HUES = [27, 42, 95]`.

**Validator rules** (proposed for `pipeline qa` or a pre-render lint):
1. Estimated duration ≤ 57 s, and planned words ≤ the budget for the language (§1.4).
2. Scene 1: `reveal` ∈ {instant, ≥70% drawn}, a `hit` at 0.0, and first narration word at ≤0.3 s.
3. At least 3 distinct `shot` sizes per episode, and no more than 2 consecutive shots with the same `shot` + `move`.
4. `erase` used 1–3 times; `draw` reveal used ≤3 times.
5. A pattern interrupt (change of shot size, accent, bed or rhythm) at least every 8 s.
6. Final shot: `music.cue = unresolved`, and the composition matches scene 1 (same `image` or the same shot/angle).
7. Every quoted line has a `quote_src`, and every verse card has a `source` with its edition.

### 3.7 Worked example: Ep05 (Tataka) rebuilt at about 45 s [R]
Facts and locators come from the approved `content/C0005/en/script.md`. This is illustration only, not a replacement script: any new version still needs G1.

| # | t (s) | Shot / angle / move | Reveal / transition | Narration (EN) | Words | Sound |
|---|---|---|---|---|---|---|
| 1 | 0–2.0 | ECU silhouette of Tataka's glinting eyes and fangs, low, push 1.0→1.15 | instant / — | Rama's first enemy had the strength of a thousand elephants. | 10 | impact hit at 0.0, wind |
| 2 | 2.0–4.5 | OTS young Rama from behind, eye level, slow push | fast / cut | And he did not want to kill her. | 8 | drone, music drops out |
| 3 | 4.5–8.5 | EWS dark tangled forest, tilt down | draw (hero) / erase | Vishvamitra led the princes to a forest no one dared enter. | 11 | wind bed |
| 4 | 8.5–12 | WS ruined fields, Tataka's shadow sweeping, truck right→left | fast / cut | Once rich land, laid waste by the yakshi Tataka. | 9 | low rumble |
| 5 | 12–17 | MS Vishvamitra explaining; insert of a lotus of light (Brahma, symbolic) | fast / match | Her strength was a boon from Brahma. Her hunger for men, a curse from Agastya. | 15 | bell (Brahma) |
| 6 | 17–21 | verse card 1.25.18 | draw / erase | To protect the people, said the sage, a protector must act. | 11 | tanpura, sparse |
| 7 | 21–23 | ECU fingers drawing the bowstring, low | instant / cut | Rama twanged his bowstring. | 4 | bowstring twang, shake |
| 8 | 23–25.5 | low-angle WS Tataka bursting from dust | instant / dust | The forest shook, and she charged. | 6 | rumble, drums enter |
| 9 | 25.5–29.5 | CU Rama's hand easing the draw, eye level | fast / cut | Still he told Lakshmana, I will only stop her. | 9 | drums drop out |
| 10 | 29.5–33.5 | WS dust storm, rock rain, she dissolves; Dutch 5° | fast / whip | She raised a storm of dust and rocks, then vanished into illusion. | 12 | wind, rocks |
| 11 | 33.5–37 | near-black frame, dusk ember sky, slow push | instant / black | Dusk was falling. Rama aimed by sound alone. | 8 | silence 0.5 s, then heartbeat drum |
| 12 | 37–39 | POV arrow streak into darkness | instant / whip | One arrow. | 2 | arrow, impact, silence |
| 13 | 39–45 | EWS same framing as #1, forest blooming, petals, pull-out; "Next: Divine Weapons" | draw / cut | The cursed forest bloomed again. And next morning, the sage gave Rama divine weapons. | 15 | bird bed, unresolved bansuri |

Totals: about 120 words at 2.6 w/s ≈ 46 s. 13 shots from about 10 stills (#1 and #13 share a composition; #7 and #12 are inserts). 3 erases and 3 draw reveals. Accuracy notes:
- "hunger for men" reflects the man-eater curse in 1.25.10–13. Confirm the wording at G1.
- Valmiki's account of how Rama "stopped" her (1.26.12–18) involves maiming. The approved script's softer "I will only stop her" is kept; any added detail must cite 1.26.17–18.

---

## 4. Visual identity bible

### 4.1 Constants (never vary) [M/R]
- Black procedural board, chalk texture and stroke reveal from `chalk.py`.
- Palette: chalk white plus at most two accents from the house set (saffron, muted gold, earthy green; `PALETTE_HUES` 27/42/95), and `CHALK_SFX_GAIN = 0.035`.
- Chalkduster titles with dark halo, gold title colour (226,190,112). ChalkboardSE captions at y = 0.75, with saffron (246,168,82) keywords.
- Composition: title headroom in the top 12%, captions in the lower 25%, subject centred. No frames or borders, no text in images, ancient Indian architecture (no onion domes or minarets), deities symbolic, Rama from behind (character bible rules).

### 4.2 World palettes (accent only; the board stays black) [R]
| World | Mood words | Accent hues | Prompt add-ons | Overlays | Light |
|---|---|---|---|---|---|
| **Ayodhya** | golden, serene, majestic, ordered | gold + saffron (existing) | "carved stone gateways, stepped shikhara towers, pillared halls, Sarayu river, banners, symmetrical" | soft motes, banner flutter | morning, from the top-left |
| **Forest / ashram** | living, sacred, quiet; dangerous at dusk | earthy green + white, gold for the yajña fire | "thatched huts, sacred fire altar, banyan and sal trees, deer" | leaves, fire smoke, fireflies at night | dappled; dusk shifts to orange |
| **Mithila** | festive, cultured, feminine grace | saffron + green, plus Madhubani-style (Mithila painting) **pattern fills inside objects**: fish, lotus, double-line fills. **Not** as a border. | "Mithila palace courtyard, painted walls with fish and lotus motifs" | petals | warm, even |
| **Lanka** | monumental, splendid, learned, smoky, ominous; **not cartoon-evil** | **crimson (new hue ≈ 0–8)** + gold; green reserved for Ashoka grove scenes | "towering golden fortress city on a sea cliff, vast pillared halls, lamps, smoke" | embers, smoke, sea spray | low, from below (lamp and fire light); dawn chanting scenes show warm gold (5.18.2) |
| **Battle** | kinetic, dusty, dusk | saffron-orange + crimson, dust grey | "dust clouds, banners, arrows in flight, chariots" | dust storm, embers, arrow streaks | backlit dusk silhouettes |
| **Divine** | radiant, abstract | gold + white glow | "radiant lotus of light, rays" (existing rule) | god rays, flash-white | central bloom |

**Engineering note [M]:** `restrict_palette()` quantises to the global `PALETTE_HUES`. Adding Lanka crimson means passing per-scene hue sets. Keep it to ≤3 accent hues per frame.

### 4.3 Complementary treatments without breaking identity [R]
Each treatment stays on the black board with chalk texture, house captions and fonts. Only the *line language* changes, and each has a semantic rule so viewers learn what it means.

| Treatment | Meaning (when to use) | How in the pipeline | Precedent [F] |
|---|---|---|---|
| **Detailed chalk** (default) | the main narrative present | current prefix | — |
| **Kalamkari / Pattachitra-line chalk** | *tale within the tale*: a sage narrating backstory (Tataka's origin 1.25, Ahalya 1.48, Vishvamitra's lineage), or divine and Puranic flashback | prompt add-on: "flat ornamental figures, flowing outlines, decorative patterned garments, profile faces, in the style of Kalamkari temple cloth, drawn in chalk"; flat, no shading; `reveal: ghost` | Srikalahasti Kalamkari depicts Ramayana scenes on temple cloths and scrolls with pen-drawn narrative panels ([Google Arts & Culture](https://artsandculture.google.com/asset/kalamkari-temple-cloth-depicting-scenes-from-the-ramayana/EQGH39mhzgMu7w?hl=en); [Wikipedia: Kalamkari](https://en.wikipedia.org/wiki/Kalamkari)) |
| **Mewar-miniature continuous narration** | journeys and multi-event summaries ("recap in one image") | one tall 9:16 still with 3–4 events stacked top to bottom; a slow tilt passes through them in order; one still covers 8–10 s | The Mewar Ramayana (Udaipur, 1649–1653, 400+ paintings, mostly at the British Library) uses continuous narrative, showing many events in one composition ([Caleidoscope](https://www.caleidoscope.in/art-culture/the-mewar-ramayana); [Oaklores: Battle of Lanka](https://oaklores.com/artwork/painting/battle-at-lanka-yuddha-kanda-book-of-war-ramayana)) |
| **Motion-comic panels** | confrontation or dialogue, simultaneous action (Rama vs Tataka; Dasharatha vs Vishvamitra) | 2–3 chalk-ruled panels inside the frame, drawn sequentially; reuses crops of existing stills | — |
| **Cinematic chalk (impact frames)** | the 1–2 biggest action beats | heavy contrast, speed lines in chalk, ECU, shake. **Do not** prompt "anime": the house negative prompt excludes it because it breaks period gravity. | — |

**Budget rule [R]:** ≤1 non-default treatment per episode, ≤25% of runtime. Always return to detailed chalk for the payoff.

### 4.4 Character design system [R]
- **Silhouette-first.** Each recurring character must be identifiable as a solid black silhouette: Vishvamitra (staff, matted hair, deerskin), Valmiki (white beard, topknot), Vasishtha (smooth silver beard, shawl), Dasharatha (crown, short beard), Rama (bow on shoulder, long hair tied back, from behind), Lakshmana (bow and quiver, alert stance), Tataka (wild hair, two arms, fangs; existing negatives), Ravana (row of crowns or heads, §2.5).
- **Accent ownership.** Rama: saffron sash. Lakshmana: green. Sita: gold. Sages: white or ochre. Dasharatha: gold. Kaikeyi: crimson-gold (existing prompt "deep red and gold"). Ravana: crimson + gold. Accents carry identity across shot sizes and crops.
- **Prop signatures.** Rama's bow, Vishvamitra's staff, Valmiki's beads, Narada's veena, Agastya's kamandalu. Prompt the prop in every shot where the character appears, including inserts.
- **Age tracks.** Use `rama_teen` / `lakshmana_teen` until the marriage arc, then add `rama_adult` with the same accent and props. Write the prompts before the episodes need them.
- **Bible maintenance.** One canonical prompt (verbatim), negatives, 2–3 seeds that worked, and three reference stills (from behind, three-quarter, silhouette) stored under `profiles/characters/refs/`. The next consistency step, per `visual_animation_tools.md`, is multi-reference generation with FLUX.2 [klein] 4B (Apache-2.0).
- **Depiction guardrails** (existing, keep): Brahma and Vishnu symbolic; Rama from behind; Ravana symbolic; Tataka two-armed silhouette, not a goddess.

---

## 5. Sound direction

### 5.1 Facts [F]
- YouTube Shorts over 1 minute with *any* Content ID claim are blocked globally ([YouTube Help](https://support.google.com/youtube/answer/15424877?hl=en)). Self-generated procedural music (the current `chalk.music()`) carries zero claim risk. Third-party "royalty-free" libraries can still trigger claims (see `audio_automation_skills.md` on Pixabay).
- Broadcast and streaming practice anchors loudness to *dialogue*. Netflix specifies −27 LKFS ±2 LU dialog-gated, with true peak ≤ −2 dBTP ([Netflix Partner Help](https://backlothelp.netflix.com/hc/en-us/articles/360001794307-Netflix-Sound-Mix-Specifications-Best-Practices-v1-5)). The shorts target stays −14 LUFS integrated (PROJECT_CONTEXT §9). The *principle*, that narration is the anchor and everything else sits under it, transfers.
- Rasa theory (Natyashastra) classifies emotional states, including karuṇa (pathos), raudra (fury), bhayānaka (fear), vīra (heroism), adbhuta (wonder) and śānta (peace). Ragas have traditionally been associated with rasas, e.g. Darbari Kanada with karuṇa and Desh with śṛṅgāra. Sources caution it is "not an exact science" ([Caleidoscope](https://www.caleidoscope.in/featured/rasas-in-bharata-munis-natya-shastra); [darbar.org](https://darbar.org/rasa-and-bhava-an-explainer-guide/)).

### 5.2 Audio hierarchy [R]
1. **Narration** is always intelligible and is the loudness anchor.
2. **SFX** are synced to visual events. Put them *between* narration phrases where possible; one-shots under speech are kept short.
3. **Music** is a bed under speech, swelling only in narration gaps.

**[R] Mix targets**
- Music at about −18 to −22 dB under narration during speech, rising 4–6 dB in gaps (sidechain ducking keyed from the narration stem).
- SFX one-shots peak about 3–6 dB under narration peaks.
- Chalk SFX stay at `CHALK_SFX_GAIN = 0.035` (approved, do not change).
- Keep `music_gain` 0.25 as the baseline and add ducking rather than lowering it globally.

### 5.3 SFX sync rules [R]
- Cue on the **visual frame** of the event (bowstring at the frame the string releases), not on the narration word, unless the narration *names* the sound. The existing `word` + `offset` mechanism then applies, and the C0005 arrow cue uses −0.35 s.
- An impact hit always lands on a cut.
- Ambience beds (wind, river, birds) fade in over 0.5 s at the shot start (already implemented) and must change at least at every erase, to mark place changes.
- **New one-shots needed:** `impact` (low drum + sub), `bowstring` (twang), `whoosh` (whip), `rumble` (earth), `rocks`, `conch`, `bell` (exists), `swarm` (glissando shimmer for divine), `heartbeat` (low pakhawaj-like thump), `fire` (crackle bed), `crowd`/`army` bed, `sea` bed (Lanka). All can be procedural numpy like the existing ones.

### 5.4 Per-moment recipes [R]
| Moment | Recipe |
|---|---|
| **Opening impact (0.0 s)** | Low drum hit + chalk snap at frame 0. Tanpura starts *with* the hit (no fade-in). First word at 0.2–0.3 s. The intro bansuri phrase enters after the hook line, not under it. |
| **Divine reveal** | 0.4 s pre-silence (all beds out), then a swarmandal-style upward glissando, a bell, a phrase resolving to Sa, a flash-white transition and a god-ray overlay. |
| **Suspense** | Remove melody. Tanpura drone plus a low pulse (heartbeat drum at about 60–70 bpm) and a wind bed. Shorten narration phrases. End on silence before the reveal. |
| **Battle** | Percussion ostinato (nagada/dhol-like, about 120–140 bpm). Whooshes and impacts on cuts. Music ducks hard under each line. Drop everything for 0.3 s before the killing blow, then a single hit. |
| **Grief** | No percussion. A slow bansuri phrase in the low register (or a sarangi-like bowed timbre). Longer pauses (`pause` 0.5–0.8). Dip-to-black transitions. Music slightly lower overall. |
| **Royal / auspicious** (Ayodhya court, Mithila wedding) | Shehnai-like reed phrase and a bell; brighter scale. |
| **Illusion / magic** (Tataka's vanishing, Maricha's golden deer) | Detuned shimmer, reversed swells, stereo widening. |
| **Cliffhanger / end** | Phrase ends on an unresolved degree (Re or Ma, not Sa), then a hard cut to the 0.5 s series sting. |

### 5.5 Leitmotifs with Indian timbres [R]
Built on `chalk.music()`, which already plays scale-degree phrases (Bhairavi-coloured) over a Sa = 146.83 Hz tanpura.

| Character / world | Motif idea | Timbre (procedural or ACE-Step bed) | Rasa |
|---|---|---|---|
| Rama | Rising 4-note phrase, calm and resolved (Sa Re Ga Pa / Pa Ga Re Sa) | bansuri (exists) | vīra, śānta |
| Sita | A gentle, ornamented phrase, higher register | bansuri or santoor-like plucks | śṛṅgāra, karuṇa |
| Lakshmana | Rama's motif in rhythm, a step behind (canon at 1 beat) | plucked veena-like | vīra |
| Vishvamitra / sages | Drone plus a single bell, sparse | tanpura + bell | śānta, adbhuta |
| Ravana / Lanka | Low-register descending phrase with komal degrees (Malkauns or Darbari colour) | low bowed drone, rudra-veena-like; never "villain synth" | raudra, bhayānaka; also grandeur |
| Hanuman | Energetic rising run with a rhythmic pulse | percussion + bansuri | vīra, adbhuta |
| Ayodhya | Auspicious reed phrase | shehnai-like | śānta, śṛṅgāra |
| Battle | Ostinato in 7 or 8 beats | drums | vīra, raudra |

**[R] Implementation**
- Add `leitmotif` to the `phrases` dictionary in `music()` as additional named phrases. Keep the Sa constant across the series so motifs stay recognisable.
- Timbres beyond bansuri and tanpura (shehnai, sarangi, nagada) are hard to synthesise convincingly. Options: (a) keep procedural percussion only; (b) render beds with ACE-Step 1.5 (MIT, outputs commercial, per `audio_automation_skills.md`) after listening tests, since it documents no raga ability; (c) record CC0 one-shots (Freesound filtered to CC0 only).
- Never run ACE-Step at the same time as Z-Image or the voice models (memory rule).

### 5.6 Silence as a tool [R]
Use 2–3 planned silences per episode (0.3–0.8 s): before the Turn, before the payoff, and optionally before "Next". In short-form these are the strongest pattern interrupts available, and they cost no words.

---

## 6. Adoption order (suggested; each change needs owner approval because the style is approved)

1. **No engine change:** apply the 35–55 s beat templates, word budgets, the citation-edition label and the `tts` respellings to the next script, and use the reveal and frame-0 rule manually through scene ordering.
2. **Small engine change:**
   - frame-0 `instant` reveal;
   - per-scene `reveal`;
   - `transition` ∈ {cut, erase, black, flash};
   - `move` push/pull/tilt with a larger zoom range;
   - shake;
   - `image` + `crop` reuse;
   - new procedural SFX and `hit`;
   - music ducking.
3. **Medium:** depth-layer parallax (DA-V2 Small or Depth Pro), overlays (embers, smoke, petals, god rays), per-scene `accent` hues, and a pre-render lint for the validator rules.
4. **Later:** leitmotif library, alternative line treatments (Kalamkari, Mewar continuous), motion-comic panels, and the A/B test of 45 s vs 55 s once analytics confidence reaches medium (PROJECT_CONTEXT §15).

## 7. Open questions and gaps
- Official YouTube guidance on loops or ideal length beyond "tell the story" was not found. The blog benchmarks are unverified.
- Mosseri's January 2025 statement was seen only in secondary coverage.
- CE vs vulgate numbers for the verses already used in C0001–C0005 were not mapped this session. That needs Goldman volumes I (Bāla) and V (Sundara) or the CE PDFs.
- Lanka's golden-city verses, the squirrel, Hanuman's gada and the Kodanda name need text checks.
- Hindi syllable rate norms were not found in the literature. The internal measurements (§1.4) are the best available evidence.
- Pattachitra-specific conventions were not sourced; only Kalamkari was.

## 8. Sources (accessed 2026-11-16)
**Platforms**
- TechCrunch, Shorts view counting: https://techcrunch.com/2025/03/26/youtube-is-changing-how-youtube-shorts-views-are-counted
- YouTube Help, content performance and engaged views: https://support.google.com/youtube/answer/12220281
- YouTube Help, three-minute Shorts: https://support.google.com/youtube/answer/15424877?hl=en
- YouTube Blog, Shorts deep dive (Hoyos and Sherman): https://blog.youtube/creator-and-artist-stories/youtube-shorts-deep-dive/
- YouTube Blog, five tips (Jordan Howlett): https://blog.youtube/creator-and-artist-stories/five-tips-to-master-shorts/
- Search Engine Journal, Sherman interview: https://www.searchenginejournal.com/youtube-explains-how-shorts-algorithm-works/494953/
- Instagram, Ranking Explained: https://about.instagram.com/blog/announcements/instagram-ranking-explained
- Social Media Today, 3-minute Reels: https://www.socialmediatoday.com/news/instagram-officially-expands-reels-length-3-minutes/737766/
- Buffer, Instagram algorithm (secondary): https://buffer.com/resources//instagram-algorithms/

**Craft and psychology**
- Loewenstein 1994 summary: https://stafforini.com/works/loewenstein-1994-psychology-curiosity-review/
- Golman and Loewenstein, Information Gaps: https://www.cmu.edu/dietrich/sds/docs/golman/Information%20Gaps--Golman%20and%20Loewenstein.pdf
- Murch Rule of Six (UT Austin): https://wikis.utexas.edu/display/rtf318/Murch%27s+Rule+of+Six
- Camera angles (NFI): https://www.nfi.edu/camera-angles/2/
- Camera angles (Wolfcrow): https://wolfcrow.com/15-essential-camera-shots-angles-and-movements/
- 2.5D parallax (Creators Project): https://thecreatorsproject.vice.com/blog/joe-fellows-teaches-us-how-to-master-25D-photography
- 2.5D parallax (ProVideo Coalition): https://www.provideocoalition.com/animating-parallax-images-in-after-effects-and-apple-motion/
- Audiobook pace (secondary): https://bookfoundry.ai/audiobook-length-calculator/
- Netflix sound mix spec: https://backlothelp.netflix.com/hc/en-us/articles/360001794307-Netflix-Sound-Mix-Specifications-Best-Practices-v1-5

**Ramayana texts and scholarship**
- valmikiramayan.net: https://www.valmikiramayan.net/
- 5.49 (Hanuman on Ravana): https://www.valmikiramayan.net/sundara/sarga49/sundarasans49.htm
- 5.18 (Vedic chanting at dawn): https://www.valmikiramayan.net/utf8/sundara/sarga18/sundaraitrans18.htm
- 1.48 (Ahalya): https://www.valmikiramayan.net/utf8/baala/sarga48/balaitrans48.htm
- IIT Kanpur heritage, Valmiki: https://heritage.iitk.ac.in/valmiki/
- vedapath 3.35.9: https://vedapath.app/en/ramayana/aranya-kanda/35/3.35.9
- vedapath 6.71.27: https://vedapath.app/es/ramayana/yuddha-kanda/71/27
- Critical Edition review (Cambridge JRAS): https://www.cambridge.org/core/journals/journal-of-the-royal-asiatic-society/article/valmikiramayana-critical-edition-general-editor-g-h-bhatt-volume-ii-ayodhyakanda-edited-by-drp-l-vaidya-pp-iv-706-lxvi-oriental-institute-baroda-19611962/019DF2CE532AC9EF190497A43A065D26
- Free Press Journal, CE (1951–75, seven volumes): https://www.freepressjournal.in/book-reviews/the-ramayana-of-valmiki
- Clay Sanskrit Library, recensions: https://claysanskritlibrary.org/book-extras/ramayana-book-i-boyhood-ancilliaries-introduction/
- INDOLOGY list, mā niṣāda 1.2.14 (CE): https://list.indology.info/pipermail/indology/2016-November/044710.html
- Princeton UP, Goldman vol. VII: https://press.princeton.edu/books/hardcover/9780691168845/the-ramayana-of-valmiki-an-epic-of-ancient-india-volume-vii
- vLex review, Goldman series: https://law-journals-books.vlex.com/vid/the-ramayana-of-valmiki-730754705
- Lakshmana rekha (Wikipedia): https://en.wikipedia.org/wiki/Lakshmana_rekha
- Scroll, Ramayana and dharma: https://scroll.in/article/981115/what-can-notions-of-dharma-and-contemporary-law-tell-us-about-the-ramayana-two-books-investigate
- Hindupedia, Ahalya: https://hindupedia.com/en/Ahalya
- Devdutt Pattanaik, Shabari: https://devdutt.com/did-shabari-actually-feed-ram-tasted-berries/
- Wikipedia, Shabari: https://en.wikipedia.org/wiki/Shabari
- Wikipedia, Sita Swayamvara: https://en.wikipedia.org/wiki/Sita_Swayamvara
- Devdutt Pattanaik, Kamban: https://devdutt.com/a-tamil-reimagining-of-the-ramayana/
- Hindu Blog, Kamba vs Valmiki: https://www.hindu-blog.com/2017/10/difference-between-kamba-ramayana-and.html
- ThePrint, Maya Sita: https://theprint.in/pageturner/excerpt/ravana-touching-sita-bhakti-poets-created-maya-sita/2489460
- Wikipedia, Molla Ramayanam: https://en.wikipedia.org/wiki/Molla_Ramayanam
- Wikipedia, Girdhar: https://en.wikipedia.org/wiki/Girdhar
- Wikipedia, Ramayan (1987): https://wikipedia.com/wiki/Ramayana_(TV_series)
- Wikipedia, A. K. Ramanujan: https://en.wikipedia.org/wiki/A._K._Ramanujan
- The News Minute, Adipurush controversies: https://www.thenewsminute.com/news/adipurush-and-controversies-here-s-whom-film-managed-offend-so-far-178761
- The News Minute, dialogue change: https://www.thenewsminute.com/news/adipurush-makers-modify-jalegi-tere-baap-ki-dialogue-after-backlash-178653
- Eastern Eye, Ravana look: https://www.easterneye.biz/adipurush-director-responds-to-controversy-over-saif-ali-khans-islamised-look-as-ravana-its-got-nothing-to-do-with-any-khiljis-nadir-shahs-genghis-khans
- American Kahani, Ram vs Rama: https://americankahani.com/perspectives/ram-or-rama-the-linguistic-story-behind-a-sensationalized-debate-triggered-by-amitabh-bachchan/
- ACL 2020, Hindi schwa deletion: https://aclanthology.org/2020.acl-main.696

**Art traditions and music**
- Kalamkari Ramayana temple cloth: https://artsandculture.google.com/asset/kalamkari-temple-cloth-depicting-scenes-from-the-ramayana/EQGH39mhzgMu7w?hl=en
- Wikipedia, Kalamkari: https://en.wikipedia.org/wiki/Kalamkari
- Mewar Ramayana (Caleidoscope): https://www.caleidoscope.in/art-culture/the-mewar-ramayana
- Battle of Lanka (Oaklores): https://oaklores.com/artwork/painting/battle-at-lanka-yuddha-kanda-book-of-war-ramayana
- Rasa theory (Caleidoscope): https://www.caleidoscope.in/featured/rasas-in-bharata-munis-natya-shastra
- Rasa and bhava (darbar.org): https://darbar.org/rasa-and-bhava-an-explainer-guide/

**Repo evidence:** `content/C000{2..5}/{en,hi,gu,te}/script.json` (word counts), `.../qa.md` (rendered seconds), `chalk.py` (`plan`, `render`, `music`, `sound`, `PALETTE_HUES`, `ERASE`), `studio.py` (`tts` override), `styles.py` (chalk preset), `profiles/characters/ramayana.json`.
