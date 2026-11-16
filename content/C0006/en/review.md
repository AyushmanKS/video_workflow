## C0006 en — Story QA (before G1)

**Scores:** Story **84/100**. Visual and audio are not reviewed yet (they are G2 inputs).

**Automatic verdict:** `en/lint.json` `"verdict": "pass"`, `"total": 51.23`, `"words": 136`, `"findings": []`.

**Checklist**
- Lint passes.
- 11 scenes (allowed 8–11).
- 3 planned silences (0.5, 0.6, 0.4 s).
- Composition loop; the Next card "Next: Maricha, Subahu" is 3 words.
- Hook 2.07 s (limit 3.0 s).
- Payoff at scene 9, about 80% of runtime.
- The `visual` strings are identical across all five languages.
- No engagement line in the video; the pinned-comment idea has a real answer (Manava, 1.27.16 → 1.30.17).

| Check | Score | Notes |
|---|---|---|
| Hook strength | 4/5 | "Rama's new weapons bowed to him." In the text the weapons join their palms (1.27.25 prāñjalayaḥ); only the withdrawal powers literally bow (1.28.12 prahva). Acceptable. The hookscore second opinion and insight A1 (anecdote, n=4) agree the stakes are thin; noted only. |
| Beat structure | 4/5 | H scene 1, C scenes 2–3, E scenes 4–7, T scene 8 (verse card), P scenes 9–10, N scene 11. |
| Accuracy | 4/5 | Every line maps to the verse table. Scene 3 attributes the vajra to Indra (fix 1). |
| Tone | 4/5 | "Not even gods can beat me now" sounds a little sporty (fix 3, optional). |
| Naturalness | 5/5 | — |

**Visual prompts: known failure modes**
- Borders: covered by the style prefix.
- Rama's face: Rama is shown from behind; scene 7 is a hand only.
- Multi-armed figures: every light figure is "exactly two arms each".
- Remaining risks:
  - the light figures could read as angels or deities (fix 4);
  - the eight-spoked wheel in scene 3 reads as the Dharmachakra or Ashoka Chakra (fix 5);
  - the crescent moon in scene 4 could be misread (fix 6).

**Numbered fixes**
1. Scene 3 (scriptwriter): `Indra's thunderbolt.` → `The Vajra thunderbolt.` In 1.27.5, "Indra's" belongs to the discus.
2. script.md (scriptwriter): add `## Applied learnings` from `data/reports/latest_insights.json`:
   - A1, A3 and A4: anecdote, n=4. A2: anecdote, n=1.
   - A3 not applied (51 s chosen, within 35–55 s).
   - A4: no engagement line in the video.
3. Scene 8 (optional, tone): `Not even gods can beat me now, Rama said.` → `Now not even gods can overcome me, Rama said.`
4. Scenes 1, 6 and 9 (creative-director):
   - In scenes 1 and 6, `simple flowing light garments` → `simple dhoti wraps drawn in light, bare shoulders, each figure marked by its own weapon emblem glowing at its chest`.
   - In scene 9, add the dhoti wraps.
   - `glowing Indian divine weapons` → `glowing Indian astra weapons`.
5. Scene 3 (creative-director): `a bright golden eight-spoked wheel discus radiating light` → `a bright golden spinning war discus with a serrated flaming rim radiating light`.
6. Scene 4 (optional): `a soft silver crescent moon wrapped in drifting curls of sleepy mist` → `an arrow wrapped in drifting curls of soft silver sleepy mist`.
7. Scene 6 (optional, parity): `Then the weapons stood before Rama, palms joined.` → `As he chanted, the weapons stood before Rama, palms joined.`

**Waiver requests:** none.
