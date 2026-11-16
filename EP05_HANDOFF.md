# Episode 05 handoff: Tataka, in four languages (en, hi, gu, te)

Use this file to start a fresh Claude Code chat in `~/Desktop/work/shorts-studio` with:

> Read `EP05_HANDOFF.md` and produce Episode 05, following it step by step.

It is self-contained, but it does not replace the standing rules. Read these first, in order:

1. `CLAUDE.md`: the non-negotiables.
2. `PROJECT_CONTEXT.md`: all of it, especially §22 (status) and §23 (next steps).
3. `.claude/skills/content-pipeline/SKILL.md`: the runbook and memory rules.
4. `.claude/skills/storytelling/SKILL.md`: the hook rubric and script schema.

Then run `python -m pipeline status`.

---

## 0. Where things stand (2026-11-16)

| Episode | ID | Status |
|---|---|---|
| 01 Valmiki | C0001 | Published (en, hi) |
| 02 Who was Shri Ram | C0002 | Scheduled for Nov 16 (HI 20:30, EN 21:30 IST) |
| 03 How Shri Ram was born | C0003 | Scheduled for Nov 17 (HI 20:30, EN 21:30) |
| 04 The sage who asked for Rama | C0004 | Scheduled for Nov 18 (HI 20:30 `tuDnAZuQyGk`, EN 21:30 `YgLlg2_Do7I`) |
| **05 Tataka** | **C0005 (to create)** | **This handoff** |

The Episode 04 teaser promised Tataka: "a demoness with the strength of a thousand elephants" (Valmiki 1.24.26). Episode 05 pays that off.

**What's new this episode:** two more languages, **Gujarati (gu)** and **Telugu (te)**. Neither has an approved voice, a speaker reference or a production run yet, so treat them as a pilot (see §3).

**Running in parallel:** another Claude Code chat is working on **Instagram connect** (`publish.py`, `docs/PUBLISHING.md`, and possibly new Instagram modules). In this chat:
- Do **not** edit Instagram-related code.
- Before every commit, run `git pull --rebase`.
- Stage only your own files. Never use `git add -A`.

---

## 1. Non-negotiables

- **Zero cost:** no paid APIs. Commercial-use licenses only, so no macOS system voices.
- **Human gates:** never skip one, and never treat a gate as approved unless the owner typed it in this chat.
  - **G1:** scripts, all 4 languages.
  - **Voice gate:** gu and te voices must be approved by ear (§3). This is a new gate for new languages.
  - **G2:** final videos.
  - **G3:** publish (video + metadata + exact time, per language).
- **Progress updates:** every 3–5 minutes during voice, image and render runs, using `python -m pipeline progress C0005 --oneline` through a Monitor loop.
  - Each update gives the current step, time left on that step, total time left and the finish time.
  - The progress tool's estimate runs optimistic during the image step, so cross-check it against the image count (`ls content/C0005/en/img | wc -l`).
- **Memory (16 GB):** one heavy model at a time. Run languages **sequentially**, never in parallel. The Instagram chat does no model work.
- **Style:** keep the approved chalk style and `chalk.CHALK_SFX_GAIN = 0.035`.
- **Code style:** no code comments in any code.
- **No fabrication:** no invented analytics or trends. Cite the verse references you actually verified.
- **Git:**
  - Repo-local identity and credential helper are already set.
  - The pre-commit hook scans for secrets and media.
  - Never commit `secrets/`, `data/`, `models/`, `out/` or media.
  - Each commit message ends with the Co-Authored-By line.

---

## 2. Story: Valmiki Ramayana, Bala Kanda sargas 24–26

Verify every fact on **sa.wikisource.org रामायणम्/बालकाण्डम्** before writing, as done for Episode 04 (`content/C0004/research/report.md` shows the format).

Story beats to check (sarga numbers are approximate; confirm each one):

1. Crossing the Ganga with Vishvamitra; the roar of the waters (sarga 24).
2. They reach a dreadful, deserted forest, once the prosperous lands of Malada and Karusha (sarga 24).
3. **Teaser verse 1.24.26:** Tataka has the strength of a thousand elephants ("बलं नागसहस्रस्य").
4. Her origin: a yakshi, daughter of Suketu; mother of **Maricha**; cursed by sage Agastya to become a rakshasi (sarga 25).
5. **Rama hesitates to kill a woman.** Vishvamitra says protecting people is a king's dharma and cites precedents (sarga 25). This is the emotional core.
6. The fight: Tataka hurls rocks and uses illusion and dust. Rama and Lakshmana disable her before Rama's arrow strikes (sarga 26). **No gore.**
7. The gods are pleased; Vishvamitra prepares to give Rama divine weapons (end of sarga 26 to 27).
8. **Teaser for Episode 06:** the divine astras, or the yajna at Siddhashrama where Maricha and Subahu return (Episode 04 set up that pair).

**On-screen Sanskrit verse:** one verified shloka, ideally Vishvamitra's dharma argument in sarga 25 or the teaser verse 1.24.26. For gu and te, the verse card should be written in that language's script (profile rule: "Sanskrit verses stay in Sanskrit, in this script"). Check that it renders correctly. If it doesn't, fall back to Devanagari and say so at G2.

**Depiction rules** (`profiles/characters/ramayana.json` plus what Episodes 03–04 taught us):
- **Tataka:**
  - An Indian rakshasi in the style of temple murals: huge, dark, wild hair, fangs, ornaments.
  - Show her as a looming shadow or silhouette rather than a monster close-up.
  - **No Western fantasy:** no bat wings, horns, gargoyles or dragons. Episode 04 scene 4 came out as bat-winged gargoyles on the first retry.
- **Rama** stays **seen from behind**, as a teenage prince (`rama_teen`). Lakshmana uses `lakshmana_teen`; Vishvamitra uses `vishvamitra`. All three are already in the character list.
- **Ravana:** symbolic only, if he appears at all.
- **Settings:** ancient Indian only, with no domes or minarets.
- **Every image:** full-bleed chalkboard, no border, no white margin. Borders still happen. If only a thin edge appears, crop it (`im.crop((24,42,744,1302)).resize((768,1344))`) instead of regenerating.

---

## 3. Gujarati and Telugu: voice pilot (do this before G1 so it runs in parallel with script review)

**Facts already checked:**
- **Maya 2 Native** (`maya-research/maya2-native`, Apache-2.0, already downloaded and in use for Hindi) supports `as, bn, en, gu, hi, kn, ml, mr, or, pa, ta, te`.
- It has 20 voices, including Malini (our approved Hindi voice), Ahana, Vaidehi, Charvi, Jahnavi, Nivedita, Ishwari, Vrinda and Sreekar (full list in `mlx_audio/tts/models/maya2/maya2.py`, `VOICES`).
- **Svara** (`mlx-community/svara-tts-v1-4bit`, Apache-2.0, already downloaded) covers both languages with one voice per gender: `Gujarati (Female)`, `Gujarati (Male)`, `Telugu (Female)` and `Telugu (Male)` (confirmed in its model card).
- Engines live in `pipeline/voicepack.py`. `studio.py` routes the `maya2:` and `svara:` prefixes there and passes the script's `language` as `lang_code`.
- `profiles/voices.json`: gu and te are `untested`. `pipeline produce` refuses any voice whose status isn't `approved`.

**Steps:**

1. Write 4 test lines per language **originally in that language** (not translated). Include:
   - names: राम/Rama, विश्वामित्र/Vishvamitra, ताटका/Tataka, लक्ष्मण/Lakshmana, अगस्त्य/Agastya;
   - one number written as words;
   - one emotional line.

   Save them to `content/C0005/voicepack/gu_lines.txt` and `te_lines.txt`.
2. Build listening packs, **one language at a time**:
   ```
   python -m pipeline voicepack --lang gu --lines content/C0005/voicepack/gu_lines.txt --voices maya2:Malini,maya2:Vaidehi,maya2:Ahana,"svara:Gujarati (Female)" --out content/C0005/voicepack/gu
   python -m pipeline voicepack --lang te --lines content/C0005/voicepack/te_lines.txt --voices maya2:Malini,maya2:Vaidehi,maya2:Sreekar,"svara:Telugu (Female)" --out content/C0005/voicepack/te
   ```
   Check the exact flag names with `python -m pipeline voicepack --help`. If a Svara voice name is wrong, drop it and say so.
3. **Recommend Malini for both if it's good.** One narrator across hi, gu and te matches the series identity. Show each language's CER table, and be clear that CER is secondary: the owner's ear overruled CER twice before.
4. **The owner probably doesn't speak Gujarati or Telugu.** Say this plainly at the voice gate and at G1:
   - ask whether they have a native speaker who can listen to the packs and read the scripts;
   - if not, the fallback evidence is the Whisper CER plus the `language-qa` agent's review, and it is **weaker**.
   - Never claim native-level correctness.
5. On approval, for each approved voice:
   - **Update `profiles/voices.json`:** set gu/te `voice`, status `approved`, an evidence note, and the approval date.
   - **Build the speaker reference:** the centroid of that voice's pack line embeddings, saved as `profiles/voices/<lang>_<Name>_ref.npy`. Use `pipeline.speaker.embed`, average, then L2-normalize, as done for `hi_Malini_ref.npy` and `en_af_heart_ref.npy`.
   - **Thresholds:** add a `_speaker_thresholds` entry. Start from Malini's `{window: 0.45, scene: 0.6}`, then check that each pack line's windows clear it. If the same voice id is used in several languages, the thresholds key is shared; that's fine.
   - The reference `.npy` files are tracked in git (the pre-commit hook allows them). Commit them.

---

## 4. Scripts (G1)

1. Create the content piece:
   ```
   python -m pipeline new --topic "Ramayana Episode 05: Tataka" --series "RAMAYANA — The Epic in Chalk" --episode 5 --category mythology --style chalk --langs en,hi,gu,te
   ```
   Check that `manifest.json` has `primary_language: en`; images are generated once in en and shared.
2. Write `research/report.md` (verified verse table), `strategy.md` and `audience.md`, with a section per language. gu and te viewers know the Ramayana through their own traditions: for Telugu, the Ranganatha and Molla Ramayanams; for Gujarati, Giridhar's Ramayan (verify before mentioning).
3. Write `en|hi|gu|te/script.json` with **the same scene count and the same `visual` per scene** (images are shared), and **narration written originally per language**.
   - The Episode 04 builder is the template. It's not in the repo; `content/C0004/en/script.json` shows the schema.
   - **Scene fields:** `narration`, `keywords` (exact tokens as they appear in the narration, including trailing punctuation), `emphasis` (the title card text), `visual`, `pause`, `sfx`, `melody`, `swell`. The verse scene also has `kind: verse`, `devanagari: [4 lines]` and `source`.
   - **No digits in gu/te narration.** Write numbers as words: `pipeline/numwords.py` only handles hi/mr and en.
   - **Target:** 13 scenes, 75–95 s, under about 220 words.
   - **Thumbnail:** scene index of the strongest image; headline 3–4 words in each language.
4. Add `hooks.json` per language:
   - 6 hooks, scored with the rubric (curiosity, emotion, specificity, speed, resonance, accuracy, out of 30).
   - Run `python3 -I .claude/skills/yt-script/hookscore.py --json <file>` on the English hooks and report any disagreement with the rubric. Choose by the rubric total; never pick against your own rubric.
5. Lint the titles with `python3 -I .claude/skills/yt-package/title.py --title "…" --thumb "…"`.
6. Generate a `script.md` per language (title, thumbnail, hooks, scenes, sources).
7. Mark the stages done:
   - `python -m pipeline done C0005 research`, then the same for `strategy`;
   - `python -m pipeline done C0005 script --lang <l>` for each language.
8. Commit, then **stop at G1.** Show the owner a side-by-side table of all 4 languages, and say which languages lack native review.

---

## 5. Production (only after G1 and the voice gate)

Run sequentially and post progress every 3–5 minutes:

```
python -m pipeline approve C0005 script
python -m pipeline produce C0005 --lang en --steps voice,images,render
python -m pipeline produce C0005 --lang hi --steps voice,images,render
python -m pipeline produce C0005 --lang gu --steps voice,images,render
python -m pipeline produce C0005 --lang te --steps voice,images,render
```

- English images take about 1 minute each. Other languages reuse them (`share_images` skips verse scenes, which are re-rendered as text per language).
- Expect roughly 25 minutes for English and 6–8 minutes for each other language.
- **Before the other languages, review the English images by hand.**
  - Build a contact sheet from `content/C0005/en/img/NN_raw.png` and look at it.
  - To fix an image: move the bad `NN_raw.png` to the scratchpad, delete the same file in the other languages' `img/`, set a new `"seed"` and a sharper `visual` on that scene in **all 4** scripts, rerun `--steps images` for en, then render.
- **Fixing one voice scene** (Maya 2 has no seed, so just regenerate):
  - generate up to 6 takes with `voicepack.speak`;
  - keep the first with no pitch outlier (>7 semitones from the narration's median), lowest window similarity ≥ threshold and scene similarity ≥ 0.6;
  - write it to `audio/NN.wav`, delete `audio/NN.words.json`, re-render.

  This exact loop was used for Episode 04 Hindi scene 12.

**QA:** run `python -m pipeline qa C0005 --lang <l>` for each language. It must pass, including `speaker_consistency` against that language's reference.
- If a language has no reference, QA falls back to comparing against scene 1 and produces false flags. Build the reference first (§3).
- gu/te speech-recognition scores may be inflated, because the normalization is tuned for Hindi. Review flagged scenes by ear rather than loosening thresholds.
- Look at each `C0005-<l>.qa.png` contact sheet and each thumbnail. Check that captions render in the gu/te scripts, with no missing-glyph boxes.

Then mark `voice_qa`, `video_qa`, `metadata` and `schedule` done per language, with notes saying what was fixed.

---

## 6. Metadata and schedule (G2 + G3)

- Write `publish.json` per language, copying the C0004 format: YouTube title, description, tags, playlist "Valmiki Ramayana", category 27, language, `synthetic: false`, pinned comment, Instagram caption.
  - Descriptions follow the C0004 pattern: hook, story, the on-screen verse (in that script, plus a translation for en), series line, previous/next episode, a comment question, source, hashtags.
- Write `schedule.json` per language.
  - Proposed date: **Thu 2026-11-19**, one day after Episode 04, keeping one episode per day.
  - Proposed slots: **TE 18:30, GU 19:30, HI 20:30, EN 21:30 IST**. 18:30 and 20:30 are among the gu/te profile candidate slots; staggering avoids self-competition.
  - Label the reason as a hypothesis, not evidence: no channel analytics yet, because the Analytics API is still disabled.
- **Ask the owner** whether gu and te go to **the same YouTube channel** as en and hi, or somewhere else. Don't assume.
- Present G2 and G3 together, as for Episode 04: video paths, QA summary, fixes, what to check by ear or eye, and a table of title + time per language.
- On approval:
  ```
  python -m pipeline approve C0005 final --langs en,hi,gu,te --note "owner approved in chat <date>"
  python -m pipeline approve C0005 publish --langs en,hi,gu,te --note "<times>"
  python -m pipeline publish C0005 --lang te --at 2026-11-19T18:30:00+05:30 --yes
  ```
  Then do the same for gu, hi and en.
- Confirm each `published.json` `verified.publishAt` in UTC (IST = UTC+5:30).
- Uploads arrive private and go public at `publishAt`.
- Only approved languages get published. If the owner approves a subset, publish only those.
- **Instagram:** follow whatever the Instagram chat has finished at that point (check `docs/PUBLISHING.md` and git log). If Instagram publishing isn't ready, skip it and say so.

---

## 7. Closing the episode

- Update `PROJECT_CONTEXT.md`:
  - §22: the C0005 status, IDs, fixes and the gu/te voice decision;
  - §23: Episode 06 next steps.
- Update `profiles/languages/gu.json` and `te.json`: the status after native review, and what was learned.
- Commit, `git pull --rebase`, push.
- Tell the owner the manual steps: pinned comments and Related-video links after go-live, and the outstanding Analytics API enablement (`https://console.developers.google.com/apis/api/youtubeanalytics.googleapis.com/overview?project=145069760719`).

---

## 8. Known gotchas (from Episodes 03–04)

| Symptom | Cause / fix |
|---|---|
| Render crash `operands could not be broadcast` in `step_audio` | Fixed: music is padded to the voice length (`studio.py`) |
| Caption "too wide" warnings | Fixed: chunks split until they fit `caption_max_chars` |
| Speaker QA false flags on a voice | Missing `profiles/voices/<lang>_<name>_ref.npy`; build it from approved audio |
| Final mp4 named oddly (e.g. `3.mp4`) when running `studio.py` directly | Use `pipeline produce`, which renames to `<ID>-<lang>.mp4` |
| Image borders, Western demons, bearded young characters, frontal Rama, Mughal domes | Regenerate with a new `seed` and an explicit negative phrasing in `visual`; crop thin edges |
| Veena lead-in syllable | Veena is retired for Hindi; don't use it |
| Deleting files with variables blocked by the guard | Use `"${VAR:?}"` or literal paths |
| OAuth token expired (Testing mode, about 7 days) | The next publish command opens the browser sign-in |
