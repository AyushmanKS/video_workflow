## C0006 mr — Story QA (before G1)

**Review status:** the profile status is draft, with no `review_status` field yet. A model did this review, not a native Marathi speaker, so it is not native-level evidence. A native read and listen are required.

**Scores:** Story **79/100**. Visual and audio are not reviewed yet.

**Automatic verdict:** `mr/lint.json` `"verdict": "pass"`, `"total": 44.96`, basis words, rate 2.3 (uncalibrated fallback), `"findings": []`. The scriptwriter's figure at the Hindi Malini letter rate is about 55.5 s, so the final QA duration decides. Fixes 1 and 4 cut length.

| Check | Score | Notes |
|---|---|---|
| Hook strength | 4/5 | "अस्त्रे श्रीरामांपुढे झुकली." The agreement is correct. झुकली leans Hindi; नतमस्तक झाली is the native's call (fix 5). |
| Beat structure | 5/5 | — |
| Accuracy | 4/5 | "इंद्राचे वज्र" in scene 3 (fix 1). No Geet Ramayan lines. |
| Honorifics | 5/5 | — |
| Marathi register | 4/5 | Reads as written in Marathi, not transliterated Hindi. बोलवायला is mis-spelled (fix 3). |
| गरजेला | keep | Idiomatic Marathi. |
| Parity with en | 4/5 | Scene 3 adds "त्यांनी नावे घेतली —" (fix 4). |

**Numbered fixes**
1. Scene 3: `इंद्राचे वज्र.` → `वज्रास्त्र.` (keyword `वज्र.` → `वज्रास्त्र.`).
2. script.md: add `## Applied learnings`.
3. Scene 8: `पण परत बोलवायलाही शिकवा.` → `पण परत बोलावायलाही शिकवा.` (keyword updated to match).
4. Scene 3: drop the opener, `त्यांनी नावे घेतली — ` → (removed).
5. Hook (native's call): `झुकली.` → `नतमस्तक झाली.` If taken, update scene 9, the title and the thumbnail to match.
6. Scene 11 emphasis: `पुढील भाग: मारीच, सुबाहू` → `पुढे: मारीच, सुबाहू`.
7. TTS listen list: ऋषींनी, देवदुर्लभ, बोलावायलाही, येणाऱ्या, सिद्धाश्रम.

**Waiver requests:** none.
