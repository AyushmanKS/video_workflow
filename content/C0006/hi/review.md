## C0006 hi — Story QA (before G1)

**Scores:** Story **85/100**. Visual and audio are not reviewed yet (they are G2 inputs).

**Automatic verdict:** `hi/lint.json` `"verdict": "pass"`, `"total": 53.35`, `"words": 123`, `"findings": []`. Profile status: in use.

| Check | Score | Notes |
|---|---|---|
| Hook strength | 5/5 | "श्रीराम के आगे झुके अस्त्र।" (2.11 s). Same accuracy note as en: acceptable. |
| Hook word order | keep | Verb before subject is an established Hindi headline order, and the hook ends on the surprise word अस्त्र. Optional variant: "श्रीराम के आगे झुक गए अस्त्र।". Check the prosody at audio QA. |
| Beat structure | 5/5 | Same beats as en. |
| Accuracy | 4/5 | "इंद्र का वज्र" in scene 3 goes beyond 1.27.5 (fix 1). लौटाना instead of संहार is a good choice. |
| Honorifics | 5/5 | Consistent with hi.json. |
| Naturalness | 4/5 | "अभी जाओ" is curt for a calm Rama (fix 2). |
| Parity with en | 5/5 | — |

**Numbered fixes**
1. Scene 3: `धर्मचक्र, कालचक्र, इंद्र का वज्र।` → `धर्मचक्र, कालचक्र, वज्रास्त्र।` (keyword `वज्र।` → `वज्रास्त्र।`).
2. Scene 10: `राम ने कहा — अभी जाओ।` → `राम ने कहा — जहाँ चाहो, जाओ।` (1.28.14 यथासुखम्). Re-run lint.
3. Scene 9 (optional): `वे शक्तियाँ भी झुककर आईं` → `लौटाने की वे शक्तियाँ भी झुककर आईं`.
4. Scene 11 emphasis: `अगला भाग: मारीच, सुबाहु` → `आगे: मारीच, सुबाहु`.
5. script.md: add `## Applied learnings`, as in en.

**Waiver requests:** none.
