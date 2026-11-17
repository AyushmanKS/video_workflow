# राम का मुकुट तैयार था | रामायण · अयोध्या कांड, भाग 1 (AK01)

- Status: **DRAFT for review**, not linted, not in the pipeline. Lint and the reviewer's Story QA come before G1.
- Language: hi (Hindi), voice Maya 2 Native `maya2:Malini`. QA must pass `speaker_consistency`. 11 shots (the same shots and keyframes as `script.en.md`) · **126 words** · hand estimate **about 47–49 s** (hi 2.80 w/s speech + 1.15 s lead and tail + pauses). `python -m pipeline lint` is the arbiter. If the estimate runs above 50 s, trim shot 11 to "महल की छत से, मंथरा यह सब देख रही थी।"
- Written originally in Hindi, not translated: the hook, the simile and the cadence follow Hindi storytelling (कथा) rhythm. Names in their Hindi form: दशरथ, कैकेयी, मंथरा, पुष्य नक्षत्र.
- Edition: Valmiki Ramayana, vulgate, numbered as on valmikiramayan.net (accessed 2026-11-17). Sources and flags are the same as `script.en.md`.
- Loop: composition (shot 1 Dasharatha at the window ↔ shot 11 Manthara on the terrace).
- Silences: 0.5 s after shot 6, 0.4 s after shot 8, 0.3 s after shot 10.
- Engagement line (A4, share prompt): shot 10 title "उस दिन कौन दूर था?" Answer in the text: भरत (shot 8; 2.1.1–2, 2.4.25).
- Next card: "अगला: मंथरा की बात"

## Hook: selected

**राम का अभिषेक तय था, पर राजा डरे हुए थे।** (contrast, 10 short words, about 2.9 s [U, check with lint]; 27/30)

| # | Hook | Type | C | E | S | Sp | R | A | Total |
|---|---|---|---|---|---|---|---|---|---|
| 1 ✔ | राम का अभिषेक तय था, पर राजा डरे हुए थे। | contrast | 5 | 4 | 4 | 4 | 5 | 5 | 27 |
| 2 | राम का मुकुट तैयार था। पिता के मन में डर था। | contrast | 5 | 4 | 4 | 3 | 5 | 5 | 26 (longer) |
| 3 | राजा ने राम का अभिषेक इतनी जल्दी क्यों रखा? | question | 4 | 3 | 3 | 4 | 4 | 5 | 23 |
| 4 | मोर जैसे बादल देखकर कूकते हैं, वैसे अयोध्या गूँज उठी। | sensory | 3 | 4 | 4 | 2 | 5 | 5 | 23 |
| 5 | पूरी अयोध्या सज रही थी, और एक दासी ऊपर से देख रही थी। | contrast | 4 | 3 | 3 | 2 | 4 | 5 | 21 |
| 6 | दशरथ को डरावने सपने आ रहे थे। | forbidden detail | 4 | 4 | 4 | 5 | 4 | 5 | 26 |

If lint measures hook 1 above 3.0 s, use the fallback "अभिषेक तय था, पर राजा डरे थे।"

## Narration

1. राम का अभिषेक तय था, पर राजा डरे हुए थे।
2. वृद्ध राजा दशरथ, राजछत्र के नीचे राज करते-करते थक चुके थे।
3. सभा के सामने उन्होंने युवराज के लिए राम का नाम रखा।
4. सभा ऐसे गूँजी, जैसे बरसते बादल पर मोर कूक उठें।
5. सबने राम को सत्यवादी, कोमल और नीलकमल-सा श्यामल कहा।
6. राजा ने राम को गले लगाया, और पुष्य नक्षत्र का दिन चुना।
7. फिर राजा ने राम को दोबारा बुलाया, उन्हें डरावने सपने आ रहे थे।
8. बोले, अभिषेक कल ही हो, जब तक भरत नगर से दूर हैं।
9. उस रात राम और सीता ने व्रत रखा, और पूरी अयोध्या सजने लगी।
10. छतों पर पताकाएँ, राजमार्ग पर फूल, और रात के लिए दीप-वृक्ष।
11. और महल की छत से, कैकेयी की दासी मंथरा, यह सब देख रही थी।

Notes for Malini: no digits in the narration. "दीप-वृक्ष" is 2.6.18's *dīpavṛkṣa*; if Malini stresses it oddly, use the `tts` field with "दीपवृक्ष". "नीलकमल-सा श्यामल" is the people's *indīvara-śyāma* (2.2.53). "राजछत्र" is the white parasol (2.2.7). Check the joined pronunciation of "गूँजी" and "कूक" on the first take.

### Read in one breath
> राम का अभिषेक तय था, पर राजा डरे हुए थे। वृद्ध राजा दशरथ, राजछत्र के नीचे राज करते-करते थक चुके थे। सभा के सामने उन्होंने युवराज के लिए राम का नाम रखा। सभा ऐसे गूँजी, जैसे बरसते बादल पर मोर कूक उठें। सबने राम को सत्यवादी, कोमल और नीलकमल-सा श्यामल कहा। राजा ने राम को गले लगाया, और पुष्य नक्षत्र का दिन चुना। फिर राजा ने राम को दोबारा बुलाया, उन्हें डरावने सपने आ रहे थे। बोले, अभिषेक कल ही हो, जब तक भरत नगर से दूर हैं। उस रात राम और सीता ने व्रत रखा, और पूरी अयोध्या सजने लगी। छतों पर पताकाएँ, राजमार्ग पर फूल, और रात के लिए दीप-वृक्ष। और महल की छत से, कैकेयी की दासी मंथरा, यह सब देख रही थी।

Shot 8 ("बोले, …") is reported speech with a soft lead-in and no quotation marks (paraphrase of 2.4.22–25). Shot 5 is reported ("…कहा").

## Shot list (same keyframes and motion as `script.en.md`; Hindi timing)

Hand estimate at 2.80 w/s with a 0.18 s default gap.

| # | Beat | Time (s) | Shot / camera / what moves (summary; full spec in script.en.md) | On-screen text | Music · SFX |
|---|---|---|---|---|---|
| 1 | H1/H2 | 0.0–3.1 | MCU at the high window, push-in; the king's eyes lift, a meteor streaks the day sky, banners stir | **अयोध्या कांड** | impact + low drum at 0.0, bell; tanpura; `dasharatha` motif |
| 2 | C | 3.3–7.2 | WS throne hall, tilt down from the white parasol; fringe and chamara fans sway | — | tanpura, soft reed phrase |
| 3 | C | 7.4–11.1 | WS assembly, pull-back; the king extends an open palm, distant seated rows | "युवराज: राम" | reed continues, murmur |
| 4 | E | 11.3–14.8 | Insert: peacocks on the parapet spread their trains, rain cloud, petals | — | crowd roar swell + low thunder |
| 5 | E | 15.0–18.2 | MCU Rama in the lotus courtyard, push-in; head turns, eyes lower, shawl lifts | "नीलकमल-सा श्यामल" | `rama` leitmotif |
| 6 | E | 18.4–22.3 | MS two-shot on the terrace; the king draws Rama in, Rama bows his head | "पुष्य नक्षत्र" | warm swell; pause 0.5 s |
| 7 | T | 22.8–27.1 | CU in lamp light, static then snap push; the flame shudders, the king's eyes open | — | `drop`; drone + heartbeat + wind |
| 8 | T/P | 27.3–31.6 | MS two-shot by the window; the king grips Rama's forearm, an empty road west | verse overlay: श्व एव पुष्यो भविता श्वोऽभिषेच्यस्तु मे सुतः (वाल्मीकि रामायण 2.4.2) | `kaikeyi` motif, very quiet; pause 0.4 s |
| 9 | P | 32.0–36.3 | MS shrine: Rama and Sita on a kusha mat, fire flickers, eyes close | "व्रत" | bell + bansuri `calm`; fire bed |
| 10 | P2 | 36.5–40.4 | EWS crane-up over the royal road; banners unfurl, petals, lamp-trees light | **उस दिन कौन दूर था?** | celebration bed: `ayodhya` motif, nagada, conch; pause 0.3 s |
| 11 | N | 40.7–45.5 | MS Manthara on the white terrace (mirror of shot 1), push towards her back; head turns, sari end stirs | **अगला: मंथरा की बात** | `unresolved` motif on Re; hard cut to the chalk end sting |

Total about 45.5 s + 1.0 s tail ≈ **46–47 s**. The Turn starts at about 22.8 s.

## Sources
Same table as `script.en.md` § Sources (vulgate, valmikiramayan.net, accessed 2026-11-17). Hindi-specific mapping:
- Shot 2 "राजछत्र के नीचे … थक चुके थे": VR 2.2.7 (*pāṇḍurasyātapatrasya cchāyāyāṃ jaritaṃ mayā*), 2.2.9 (*pariśrānto'smi*).
- Shot 4 "मोर कूक उठें": VR 2.2.17 (*barhiṇa iva nardantaḥ*, peacocks crying at a raining cloud).
- Shot 5 "नीलकमल-सा श्यामल": VR 2.2.53.
- Shot 8 "जब तक भरत नगर से दूर हैं": VR 2.4.25 (*viproṣitaś ca bharato yāvad eva purād itaḥ*); guard: 2.4.26 calls Bharata devoted to his elder brother.
- Shot 10 "दीप-वृक्ष": VR 2.6.18.
- Shot 11 "कैकेयी की दासी मंथरा": VR 2.7.1–2 (*jñātidāsī*, attendant from Kaikeyi's birth home).

## Flags
The same flags as `script.en.md` (timeline compression in 2.6–2.7, shot 1 omen image, Yuvaraja versus full coronation, CE not checked). Hindi-specific: "अभिषेक" is used in the hook (accurate for *abhiṣeka*); the English hook says "crown" as the familiar word.

## Applied learnings (`data/reports/latest_insights.json`, 2026-11-17 11:40)
- **A1** (anecdote, n=8): stakes in the hook ("राजा डरे हुए थे"); Turn at about 22.8 s, inside 18–25 s.
- **A2** (anecdote, n=1): hook written natively short; frame 0 is a full keyframe.
- **A3** (anecdote, n=8): about 46–47 s, kept below 50 s.
- **A4** (anecdote, n=8): share-prompt engagement line with its answer in the text (भरत).
