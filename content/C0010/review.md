# C0010 "Ganga's Birth" — Story QA before G1 (en, hi, gu, te, mr)

Reviewer: independent `reviewer` agent (read-only; saved by the main session). Visual and audio QA happen at G2.

**Verdict:** all five scripts can go to G1 once the must-fixes are done. Accuracy is clean (every claim maps to 1.35.12–24; nothing from sarga 36 or later traditions; verse card text and split correct). gu, te and mr are `unreviewed-language`; notes on them are not native-level.

## Automatic checks (lint.json)
| Lang | Verdict | Total | Finding |
|---|---|---|---|
| en | warn | 53.14 | hook scene spoken 2.7 s > 2.2 s |
| hi | pass | 51.98 | none |
| gu | warn | 52.96 | hook scene spoken 2.2 s > 2.2 s |
| te | warn | 52.81 | hook scene spoken 2.4 s > 2.2 s |
| mr | warn | 52.76 | hook scene spoken 2.6 s > 2.2 s (rate from 1 render) |

## Scores (before fixes)
| Lang | Score | Flow | Hook | Accuracy |
|---|---|---|---|---|
| en | 88 | 4/5 | 4/5 | 5/5 |
| hi | 92 | 5/5 | 5/5 | 5/5 |
| gu | 88 | 4/5 | 5/5 | 5/5 (unreviewed) |
| te | 86 | 4/5 | 4/5 | 5/5 (unreviewed) |
| mr | 82 | 3/5 | 5/5 | 5/5 (unreviewed) |

Visual prompt direction: 78 now, about 90 after V1–V3.

## Verse card 1.35.18
ददौ धर्मेण हिमवांस् / तनयां लोकपावनीम्। / स्वच्छन्दपथगां गङ्गां / त्रैलोक्यहितकाम्यया॥ — matches sa.wikisource; four 8-syllable pādas; gu/te transliterations correct. G2: check line-final halant and the ङ्ग conjunct in the chalk fonts.

## Teaser and Next card
Keep "Next: Three Paths" over "Uma's Curse": it names the question that opens sarga 36 (1.36.1–3) and does not advertise its most sensitive part before a sensitivity plan is approved.

## Numbered fixes
Narration (scriptwriter):
1. F1 mr scene 4 (must-fix): verbless list → "त्यांची आई होती मेरूची कन्या मेना, आणि दोघींत थोरली होती गंगा, धाकटी उमा."
2. F2 en scene 4 (optional): "Mena, his dear queen, bore them both, the Ganga first and Uma after."
3. F3 en scene 3 (optional): "two daughters of matchless beauty" (रूपेणाप्रतिमं).
4. F4 mr scene 10 (optional): "ऋषी म्हणाले, या आहेत पर्वतराजाच्या दोन कन्या, गंगा आणि उमादेवी."
5. F5 hi (optional): scene 9 "और हिमवान ने उमा का ब्याह अनुपम रुद्र से कर दिया।"; scene 7 "तब देवता प्रसन्न मन से गंगा को स्वर्ग ले गए।"
6. F6 gu (optional): vary the repeated "ને"; align honorific in scene 5.
7. F7 te hook (optional): avoid a vocative reading of "గంగా, ఉమా" → "గంగ, ఉమ సొంత అక్కాచెల్లెళ్లు." or "గంగా ఉమలు సొంత అక్కాచెల్లెళ్లు."
8. F8 all scene 11 (optional): follow प्रथमं खं गता more closely ("went first to the sky").
9. F9 en hook (optional, owner's choice): "The river Ganga had a sister."
10. F10 en (optional): one capitalisation of "goddess Uma".
11. F11 script.md (optional): relabel "45 s shape" as "55 s two-beat shape".

Visual prompts (creative direction, before images):
12. V1 scenes 1 and 11 (must-fix): Uma large in the lower-right foreground (about half frame height), three-quarter side view, hands open on knees, open board around her head; river of light behind her on the left; EWS → WS; scene 11 same framing with the river rising into the starry sky.
13. V2 scene 7 (must-fix): drop the tiny Himavan, or draw him large in the lower-right foreground in three-quarter back view with his right arm raised in farewell against open board.
14. V3 scene 9 (must-fix): stagger in depth — Himavan large left foreground presenting, Uma centre middle ground with joined palms held away from her chest, Rudra silhouette on a higher rock right with open board around the trident; drop the fire or move it low with open board.
15. V4 scene 3 (optional): right arm hanging a little away from his side, open board between arm and robe.
16. V5 token `uma` (optional): sari end over both shoulders with topknot visible, or over her head; not both.

Series-planner:
17. N1: Ep11 opens on Rama's question (1.36.1–3) and says the answer begins with the younger sister's story.

## Waiver requests
None.
