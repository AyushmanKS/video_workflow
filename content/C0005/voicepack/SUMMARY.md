# C0005 voice pilot: Gujarati and Telugu (2026-11-16)

Engines: Maya 2 Native (Apache-2.0) and Svara v1 4-bit (Apache-2.0). 4 test lines per language, written originally in that language (`gu_lines.txt`, `te_lines.txt`).

## Line CER (Whisper large-v3-turbo; secondary signal)

| Voice | gu L1–L4 | te L1–L4 |
|---|---|---|
| maya2:Malini | 0.05 / 0.10 / 0.17 / 0.13 | 0.06 / 0.13 / 0.08 / 0.02 |
| maya2:Vaidehi | 0.05 / 0.19 / 0.09 / 0.17 | 0.06 / 0.10 / 0.05 / 0.02 |
| maya2:Ahana | 0.07 / 0.16 / 0.14 / 0.17 | — |
| maya2:Sreekar (male) | — | 0.10 / 0.07 / 0.03 / 0.08 |
| svara Female | 0.10 / 0.00 / 0.23 / 0.17 | 0.14 / 0.10 / 0.13 / 0.10 |

Gujarati CER is inflated by:
- Whisper spelling ઋષિ as રુશી, which is how Gujarati speakers say it.
- Colloquial spellings (રેતી for રહેતી).
- Whisper truncating line 4. A re-transcription of the last 3.5 s confirms every voice says the full "…રાજાનો ધર્મ છે".

**To check by ear:** "એક હજાર" came back as "એ ખજાર" for all Maya voices; it could be co-articulation or a real slip.

## Speaker similarity to the approved Hindi Malini reference (`hi_Malini_ref.npy`, ECAPA cosine)

| Voice | gu | te |
|---|---|---|
| maya2:Malini | 0.77 0.78 0.81 0.73 | 0.83 0.68 0.84 0.74 |
| maya2:Vaidehi | 0.59 0.59 0.68 0.42 | 0.57 0.57 0.48 0.48 |
| maya2:Ahana | 0.64 0.61 0.61 0.58 | — |
| maya2:Sreekar | — | 0.16 0.21 0.22 0.20 |
| svara Female | 0.34 0.40 0.36 0.34 | 0.31 0.35 0.33 0.36 |

Malini keeps the same identity across hi, gu and te (0.68–0.84, against a Hindi self-window median of 0.62).

**Speed:** Maya is about real-time; Svara is about 1.7× slower than real-time.

**Recommendation:** maya2:Malini for both gu and te (one series narrator). No native speaker has listened yet.
