## C0006 gu — Story QA (before G1)

**Review status:** `unreviewed-language`. A model did this review, not a native Gujarati speaker, so it is not native-level evidence. CER is warn-only. A native read and listen are still required.

**Scores:** Story **78/100**. Visual and audio are not reviewed yet.

**Automatic verdict:** `gu/lint.json` `"verdict": "pass"`, `"total": 54.61`, `"words": 104`, `"findings": []`. That is 0.39 s under the 55 s warning line, so use only fixes that keep the length or shorten it.

| Check | Score | Notes |
|---|---|---|
| Hook strength | 4/5 | "અસ્ત્રો રામ સામે ઝૂકી ગયાં." (2.06 s) |
| Dropping શ્રી | acceptable | The title and thumbnail carry શ્રીરામ. Restore it only together with fix 1. |
| Beat structure | 5/5 | — |
| Accuracy | 4/5 | "ઇન્દ્રનું વજ્ર" in scene 3 goes beyond 1.27.5 (fix 1). |
| Honorifics | 5/5 | Consistent with the C0005 lessons. |
| Naturalness (non-native) | 3/5 | See fixes 2 and 3. |
| Parity with en | 5/5 | — |

**Numbered fixes**
1. Scene 3: `ધર્મચક્ર, કાલચક્ર, ઇન્દ્રનું વજ્ર.` → `ધર્મચક્ર, કાલચક્ર, વજ્રાસ્ત્ર.` (keyword `વજ્ર.` → `વજ્રાસ્ત્ર.`).
2. Scene 8: `પણ આને પાછાં વાળતાં શીખવો.` → `પણ એમને પાછાં વાળતાં શીખવો.`
3. Scene 10: `રામે કહ્યું — હમણાં જાઓ.` → `રામે કહ્યું — હવે જાઓ.`
4. script.md: add `## Applied learnings`. A2 (anecdote, n=1) is applied with a native 2.06 s hook.
5. TTS listen list: પૂર્વાભિમુખ, બ્રહ્માસ્ત્ર, વજ્રાસ્ત્ર, સિદ્ધાશ્રમ, સૂર્ય-ચંદ્ર.

**Waiver requests:** none.
