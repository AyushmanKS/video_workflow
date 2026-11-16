# C0006 voice pilot: Marathi (2026-11-16)

Engine: Maya 2 Native (Apache-2.0). 4 test lines written in Marathi (`mr_lines.txt`). Audio: `mr/maya2_<voice>_line<N>.wav`.

## Line CER (Whisper large-v3-turbo; secondary signal)

| Voice | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| maya2:Malini | 0.10 | 0.16 | 0.19 | 0.15 |
| maya2:Vaidehi | 0.10 | 0.26 | 0.19 | 0.18 |
| maya2:Ahana | 0.14 | 0.16 | 0.15 | 0.15 |

Whisper's Marathi output drifts toward Hindi spellings for every voice:
- बळ came back as "बढ़";
- आहे came back as "है";
- म्हणाले came back as "महनाले".

That could be a Whisper bias or a Hindi-accented delivery. Only a Marathi ear can tell. Both लक्ष्मणाला and ऋषी came back with their usual spoken spellings.

## Speaker similarity to the approved Hindi Malini reference (ECAPA cosine)

| Voice | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| maya2:Malini | 0.76 | 0.72 | 0.68 | 0.79 |
| maya2:Vaidehi | 0.59 | 0.56 | 0.45 | 0.33 |
| maya2:Ahana | 0.64 | 0.58 | 0.44 | 0.58 |

Malini keeps the series narrator's identity in Marathi (0.68–0.79), in the same range as gu (0.73–0.81) and te (0.68–0.84).

**Recommendation:** maya2:Malini for mr, so the series keeps one narrator. Not yet approved. It needs the owner's listen, and Marathi stays in the unreviewed-language cohort until a native speaker signs off. Listen especially for आहे, बळ and म्हणाले.
