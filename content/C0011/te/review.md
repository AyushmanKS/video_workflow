# C0011 review: Story QA before G1 (Bala Kanda Part 1, long-form, en/hi/te)

Reviewer agent, 2026-11-18. The reviewer edited no files.

## Automatic checks
- **Lint:** all three pass with no findings. en 566.01 s and 1,561 words; hi 590.46 s and 1,522 words; te 558.49 s and 833 words.
- **Stale English notes:** `en/script.md`'s "Lint result" section still shows an old silences warning (fix X1).
- **Visual parity:** confirmed. 50 `visual`s and 9 verse slides in each language.
- **Applied learnings:** A1–A3 (anecdote tier) are quoted correctly. No anecdote overrides an approved rule.
- **Telugu:** `unreviewed-language`. Every Telugu judgement is non-native and provisional.

## Shared checks
- **Verse slides:** 9 in total, 1–2 per chapter, each with source and edition. The meaning is narrated and none is recited. 1.16.27 is weak but acceptable.
- **Re-hook cadence:** the longest gap is about 61 s, which is fine.
- **Chapter-end pulls:** Ch2 (scene 21) and Ch3 (scene 30) end with no pull, and Ch3 ends on a later-tradition aside. This is a **MUST** fix in all three languages.
- **Cold open:** 31, 33 and 32 s (en, hi, te). The first line is about 5.5 s, under the 6 s limit. The bookend in scene 47 works.
- **Sensitivity:** good throughout: Tataka, the hunter, Rama's calm, deities shown as light, Ravana as a shadow, blood only on the altar.
- **Accuracy:** strong overall. Scene 36 merges the sound-aimed volley (1.26.24–25) into the chest arrow (1.26.26). That is a SHOULD fix.
- **Owner decision at G1:** Part 1 ends at 1.30, not at "the divine weapons".

## English: 80/100. READY AFTER MUST FIXES
Scores: cold open 4 · flow 4 · chapter pull 3 · clarity 4 · accuracy 4 · sensitivity 5 · closing 5.
1. **MUST, scene 26:** headline fragment. Rewrite: "Then Vishvamitra's anger blazed like a fire fed with ghee; he said it was unworthy of Raghu's line for a king to break his word, and as he spoke, the whole earth trembled."
2. **MUST, scene 21:** pull out of Ch2. Append: "…And as the princes came of age, the king began to think of their weddings, never guessing who was about to come to his gate." Add VR 1.18.37–39 to the scene's sources. In scene 22, change "Then one day" to "It was then that the great sage Vishvamitra came…".
3. **MUST, scene 30:** end Ch3 on a pull. Append: "That morning they walked on toward the Ganga, and beyond its waters lay a dreadful forest, and the one who had laid it waste." (VR 1.23.5, 1.24.12)
4. **SHOULD, scene 36:** accuracy (sound-aimed volley, then one arrow).
5. **SHOULD, scene 3:** "feared for now held" can be misheard; reword.
6. **SHOULD, scene 16:** run-on, and introduce Ravana as "the rakshasa king Ravana".
7. **SHOULD, scene 17:** say "the god Vishnu".
8. **SHOULD, scene 8:** split the run-on; vary the "Then" openings in scenes 9 and 11.
9. **SHOULD, scene 39:** "Siddhashrama, the Hermitage of Fulfilment" (sets up the payoff in scene 46).
10. **SHOULD, scene 47:** smooth the double past perfect.
11. **SHOULD, scene 50:** "waiting" repeats from 49.
12. **SHOULD, scene 20:** "In the spring month of Chaitra".
13. **SHOULD, X1:** update script.md's Lint section; make hooks.json `cold_open_s` agree with script.md.

## Hindi: 82/100. READY AFTER MUST FIXES
Scores: cold open 4 · flow 5 · chapter pull 3 · clarity 4 · accuracy 4 · sensitivity 5 · native 4 · closing 5. The chapter titles are good.
1. **MUST, scenes 21 and 30:** chapter pulls (Hindi wording suggested in the reviewer's report).
2. **MUST, scene 38:** "लौटाऊँ" reads as "give the weapons back". Change it to "छोड़े हुए अस्त्रों को वापस कैसे बुलाऊँ" and update the keyword to "बुलाऊँ".
3. **SHOULD:**
   - 36: accuracy.
   - 47: "जान बख़्श दी" instead of "प्राण छोड़ दिए".
   - 17: clarify the boon (the gods and demons couldn't kill him).
   - 3/4: avoid "पर" twice in a row.
   - 10: curse register.
   - 24: optional naturalness.
   - 50: avoid repeating "प्रतीक्षा".
   - 30: optionally name "श्री वेंकटेश सुप्रभातम्".

## Telugu: 74/100 (provisional, non-native). READY AFTER MUST FIXES
Scores: cold open 4 · flow 3 · chapter pull 3 · clarity 4 · accuracy 4 · sensitivity 5 · native 4 (provisional) · closing 4.
1. **MUST:** `te/script.md`'s "Full narration" section contains the **Hindi** text. Regenerate it from `te/script.json` with Telugu headings.
2. **MUST, scenes 21 and 30:** chapter pulls. Scene 30 must stay at or under 20 s: trim the Suprabhatam clause to "పదిహేనో శతాబ్దపు", then add the pull.
3. **SHOULD:**
   - 36: accuracy.
   - 47 (high priority): "ప్రాణాన్ని విడిచిపెట్టాడు" may read as dying; use "ఒకరి ప్రాణం తీయకుండా వదిలాడు".
   - 50: end board under 15 s; raise the pause to 7.0 and avoid the repeated "waiting".
   - 3/4: avoid "కానీ" twice in a row.
   - 11, 26 and 33: join the choppy short sentences.
   - 18: honorific consistency.
   - 28: "ఆకాశం నుంచి పూలవాన కురిసింది".
- The owner must know at G1 that no native speaker has checked this Telugu.

## Waivers
None needed.
