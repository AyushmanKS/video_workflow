# C0007 mr — Visual + Audio QA (before G2)

Not native-reviewed; the reviewer is not a native Marathi speaker. QA #66 WARN. Story 80 · Visual 58 · Audio 70. The झ→ज and ळ→ल patterns recur, so listen at 3.45–7.77 and 41–52 s. The hook's last word ends at 3.07 s against the 3.0 s rule; the owner decides.

## Shared visual findings and fixes (2026-11-16)

**Blocking:**
- **Frame 0 (img 00):** the shadow rakshasa has three arms.
- **Scene 9 (img 08):** disembodied extra hands, and the arrow is held like a torch.
- **Telugu verse card:** line 2 is clipped at the left edge.

The owner chose to fix all three before release.

**Fixes made:**
- **Frame 0:** new prompt. Maricha is small and two-armed, tumbling far out over the ocean; Rama stays small, seen from behind.
- **Scene 9:** new prompt. Smoke only with no figure, the flaming arrow in flight, Rama small.
- **Verse card (`chalk.py`):** the font now shrinks until the widest line fits (te 80 → 72). Other languages are unchanged.

**Owner calls:**
- **Scene 4 (img 03):** medium-size side profiles. Accepted, as in Ep06 img 01.
- **Scene 5:** the figures lean slightly comic but read as menacing.
- **Scene 6:** the red rain is faint at phone size.

**Checks that pass:**
- Captions are legible in all five languages.
- Each verse card is in its own script.
- The title zones are clear.
- No gore.
- Mithila reads as Indian.
- Vishvamitra matches Ep06.
