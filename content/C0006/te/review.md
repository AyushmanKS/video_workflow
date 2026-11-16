## C0006 te — Story QA (before G1)

**Review status:** `unreviewed-language`. A model did this review, not a native Telugu speaker, so it is not native-level evidence. CER is warn-only. A native read and listen are still required.

**Scores:** Story **77/100**. Visual and audio are not reviewed yet.

**Automatic verdict:** `te/lint.json` `"verdict": "pass"`, `"total": 54.67`, `"words": 76`, `"findings": []`. That is 0.33 s under the 55 s warning line, so prefer fixes that shorten.

| Check | Score | Notes |
|---|---|---|
| Hook strength | 4/5 | "అస్త్రాలే రాముడికి మొక్కాయి." (2.19 s) |
| మొక్కు | keep | The joined-palms salute, used to elders as well as gods. It matches prāñjalayaḥ (1.27.25) and prahvāñjalipuṭāḥ (1.28.12). A native should confirm. |
| వెళ్ళి రండి | keep | The customary polite farewell; it fits "help me from my mind when needed" (1.28.14). |
| Beat structure | 5/5 | — |
| Accuracy | 4/5 | "ఇంద్రుడి వజ్రం" in scene 3 (fix 1). "పొగలా వెలుగుతూ" in scene 9 says smoke glows (fix 2). |
| Honorifics | 5/5 | Plural for the sage throughout. |
| Naturalness (non-native) | 3/5 | The bare stem వాయు in scene 4 needs a native check (fix 3). |
| Parity with en | 4/5 | — |

**Numbered fixes**
1. Scene 3: `ధర్మచక్రం, కాలచక్రం, ఇంద్రుడి వజ్రం.` → `ధర్మచక్రం, కాలచక్రం, వజ్రాస్త్రం.` (keyword `వజ్రం.` → `వజ్రాస్త్రం.`).
2. Scene 9: `ఆ శక్తులూ నిప్పుల్లా, పొగలా, సూర్యచంద్రుల్లా వెలుగుతూ మొక్కాయి.` → `ఆ శక్తులూ నిప్పుల్లా, పొగలా, సూర్యచంద్రుల్లా మొక్కాయి.`
3. Scene 4 (native check only): `బ్రహ్మాస్త్రం, అగ్ని, వాయు, నిద్రాస్త్రాలు.` → `బ్రహ్మాస్త్రం, ఆగ్నేయ, వాయవ్య, నిద్రాస్త్రాలు.`
4. script.md: add `## Applied learnings`. A2 is applied (2.4 s → 2.19 s hook).
5. TTS listen list: బ్రహ్మాస్త్రం, దేవదుర్లభ, ప్రత్యక్షమై, సిద్ధాశ్రమం, సంహరించాలి, మొక్కాయి.

**Waiver requests:** none.
