# C0011 · Bala Kanda Part 1 (long-form, English, primary)

**Format:** YouTube long-form, 16:9, engine v3 (chalk puppet). This is **not a Short**: the 35–55 s rules don't apply, and the long-form section of the storytelling skill does.
**Working title:** Ramayana · Bala Kanda Part 1: From Valmiki's First Verse to Rama's First Battle (the packager decides the final title).
**Scope:** VR 1.1–1.30 (vulgate), with the cliff from 1.31.1–19.
**Estimate (`pipeline lint`, letter rate 12.04/s, calibrated):** **587 s ≈ 9 min 47 s**, 1,623 words, 50 scenes. The word-rate cross-check (1,623 / 2.82 w/s + 27.7 s pauses + 1.15 s lead/tail) gives about 604 s ≈ 10 min 4 s.
**Lint:** PASS, no findings (after the reviewer's fixes, listed below).

## Cold open (scenes 1–4, about 32 s including the title scene)
> His father said he was too young to fight rakshasas, and on the sixth day, they came.
> For six days and nights Rama and his brother had guarded a sacred fire without sleep, and now, like monsoon clouds, the rakshasas came sweeping down upon the altar.
> Yet the boy his father had trembled for now carried weapons that even the gods could hardly hope to own.
> *(Title: Bala Kanda · Part 1)* But this story begins long before that day, beside a quiet river, with a poet, a question, and two birds.

- **First line:** estimated 5.5 s, stakes-first (selected from 4 options in `hooks.json`, rubric 27/30).
- **Bookend:** the closing line (scene 47) answers it: "the prince his father had called too young for battle…".

## Chapters and timings (estimated)
| # | Chapter title | Scenes | Starts | Length | Sargas | Re-hook inside the chapter |
|---|---|---|---|---|---|---|
| – | Cold open + part title | 1–4 | 0:00 | 32 s | 1.20, 1.27–1.30 | the hook itself |
| 1 | The Birth of Poetry | 5–12 | 0:32 | 98 s | 1.1–1.2 | "one man has them all" (0:52); the hunter's arrow (1:17) |
| 2 | The King's Long Wait | 13–21 | 2:09 | 113 s | 1.5–1.18 | Ravana makes even the sun afraid (2:38); the being from the fire (3:07); a pull to the gate (end) |
| 3 | The Sage at the Gate | 22–30 | 4:02 | 111 s | 1.18–1.24 | "give me Rama" (4:12); the earth trembles (4:45); a pull to the dreadful forest (end) |
| 4 | Tataka and the Gift | 31–39 | 5:53 | 114 s | 1.23–1.29 | Rama will not kill her (6:29); the weapons bow to him (7:04) |
| 5 | Six Nights of Fire, closing and end board | 40–50 | 7:47 | 118 s | 1.29–1.31 | the sky roars (7:59); Maricha hurled into the sea (8:16) |

Chapter 5 breaks down as story 7:47–8:51 (64 s), **closing 8:51–9:29 (38 s)** and **end board 9:29–9:46 (about 17 s: 10.4 s of soft narration plus a 6 s music-only hold)**.

`chapters[].first_scene` in script.json is **1-based** (5, 13, 22, 31, 40). The render adds "Chapter N ·" itself (`puppetstudio.CHAPTER_WORD`), so each `chapter_title` holds only the title.

## Full narration
1. His father said he was too young to fight rakshasas, and on the sixth day, they came.
2. For six days and nights Rama and his brother had guarded a sacred fire without sleep, and now, like monsoon clouds, the rakshasas came sweeping down upon the altar.
3. Yet the boy his father had trembled for now carried weapons that even the gods could hardly hope to own.
4. But this story begins long before that day, beside a quiet river, with a poet, a question, and two birds.

### Chapter 1 · The Birth of Poetry
5. Long ago, the sage Valmiki put a question to Narada, the wandering seer of the gods and the finest of all who speak.
6. Is there anyone in this world today, he asked, who is good and brave, who knows dharma, who is truthful and firm in his vows, who has conquered anger, and whom even the gods fear in battle? *(verse slide: Valmiki Ramayana 1.1.2 (vulgate))*
7. Narada was glad at heart. Such qualities are rare, he said, yet one man has them all; he was born in the line of Ikshvaku, and the people call him Rama.
8. Then he told Valmiki the whole of Rama's story and rose into the sky. Valmiki went down to the Tamasa river, and there, wandering the bank, he saw a pair of krauncha birds singing sweetly, never leaving one another's side.
9. But before his eyes, a hunter with a heart full of malice shot down the male bird, and his mate, seeing him fallen on the earth, cried out in grief.
10. Pity filled the sage's heart, and these words broke from him: hunter, may you never find rest through endless years, for you have struck down one of a pair lost in love. *(verse slide: Valmiki Ramayana 1.2.15 (vulgate))*
11. Afterwards he wondered at his own words, for they had come out in four even lines, fit to be sung to the strings, and he said that this verse, born of sorrow, should be called a shloka.
12. Later Brahma, the creator of the worlds, came to him and said: it was my will that this speech came to you, so tell all of Rama's story, and as long as mountains stand and rivers flow, it will be told. And so one sage's sorrow became a shloka, and the shloka became the Ramayana.

### Chapter 2 · The King's Long Wait
13. The story he sang begins in Ayodhya, a city on the Sarayu built by Manu himself, and its king, Dasharatha, was truthful and wise and dear to all his people.
14. Yet this great king had no son to carry on his line, and without one, he said, there was no joy for him.
15. So he resolved on the great horse sacrifice; his priests, led by Vasishtha, blessed the plan, and the young sage Rishyashringa came to lead the rites on the bank of the Sarayu.
16. When it was done, Rishyashringa lit one more fire for the birth of sons. The gods who gathered there for their share cried to Brahma in fear, for the rakshasa king Ravana, proud of his boon, was tormenting all three worlds, and even the sun dared not scorch him.
17. He had asked to be safe from gods and demons, but in his scorn he never thought of men; and so the god Vishnu agreed to be born as a man, as the son of King Dasharatha.
18. Then from the fire rose a radiant being, bright as the sun, holding a golden vessel of payasa made by the gods; give it to your queens, he said, and you will have sons.
19. The king, like a poor man who has found treasure, gave half to Kausalya, half of what was left to Sumitra, half of the rest to Kaikeyi, and, after a moment's thought, the last share to Sumitra again. *(verse slide: Valmiki Ramayana 1.16.27 (vulgate))*
20. In the spring month of Chaitra, on the ninth day, Kausalya gave birth to Rama; Kaikeyi bore Bharata, and Sumitra bore Lakshmana and Shatrughna, and all Ayodhya filled with singing and dancing.
21. The four princes grew in learning and in archery, and Lakshmana was like Rama's second life; Rama would not even sleep without him. And as the princes came of age, the king began to think of their weddings, never guessing who was about to come to his gate.

### Chapter 3 · The Sage at the Gate
22. It was then that the great sage Vishvamitra came to the palace, and Dasharatha, overjoyed, went out to meet him and promised to do whatever he might ask.
23. I am keeping a sacred vow, the sage said, and two rakshasas, Maricha and Subahu, rain flesh and blood upon my altar; while the vow lasts I may not curse them, so give me Rama for ten nights.
24. The king fell senseless, and when he came to himself he said: my lotus-eyed Rama is not yet sixteen, and I do not see him fit to fight rakshasas. *(verse slide: Valmiki Ramayana 1.20.2 (vulgate))*
25. Take my army instead, he begged, take me, for I cannot live a moment without Rama; and when he heard that Ravana stood behind these rakshasas, his fear only grew.
26. Then Vishvamitra's anger blazed like a fire fed with ghee; he said it was unworthy of Raghu's line for a king to break his word, and as he spoke, the whole earth trembled.
27. It was the guru Vasishtha who steadied the king: you were born in Ikshvaku's line, he said, so do not abandon dharma now, for guarded by this sage, Rama is as safe as nectar guarded by fire.
28. So, with his mother's blessing, Dasharatha kissed his son's head and gave him to the sage; a gentle wind blew, flowers fell from the sky, and Lakshmana walked behind his brother.
29. On the bank of the Sarayu the sage gave Rama two mantras, Bala and Atibala, so that no weariness or hunger would touch him; and that night the princes slept on beds of grass.
30. At dawn the sage woke him gently: Kausalya is blessed in her son, Rama, the twilight is here, so rise, tiger among men; centuries later a temple hymn would open with these words. That morning they walked on toward the Ganga, and beyond it lay a dreadful forest, and the one who had laid it waste. *(verse slide: Valmiki Ramayana 1.23.2 (vulgate))*

### Chapter 4 · Tataka and the Gift
31. They crossed the Ganga to a dreadful forest, once the rich land of Malada and Karusha, which a yakshi named Tataka, with the strength of a thousand elephants, had laid to waste.
32. How could a yakshi hold such strength, Rama asked; it was Brahma's boon, said the sage, and when she and her son Maricha attacked the sage Agastya, his curse made her a man-eating rakshasi.
33. Do not shrink from this because she is a woman, the sage told him; those who protect the people must act, cruel as the deed may seem, for that is the lasting duty of all who rule. *(verse slide: Valmiki Ramayana 1.25.18 (vulgate))*
34. Rama twanged his bowstring and Tataka came charging, yet even then he told Lakshmana he had no heart to kill her, and meant only to stop her.
35. But she raised a storm of dust, rained down rocks and vanished into illusion, and the sage cried: enough of this pity, Rama, dusk is near, when rakshasas cannot be beaten.
36. With arrows aimed by sound alone, Rama checked her rain of stones, and as she rushed at him, he struck her chest with a single arrow, and she fell; the gods praised him, and the cursed forest bloomed again.
37. Next morning the sage smiled and gave Rama all his weapons, the discus of Time, the thunderbolt, the Brahma weapon, fire and wind and even sleep, and they stood before him with joined palms, saying, we are your servants.
38. Rama touched them and bade them dwell in his mind; then he asked the sage, now that not even the gods can overcome me, how do I call these weapons back? And the sage taught him that too. *(verse slide: Valmiki Ramayana 1.28.2 (vulgate))*
39. At last they reached Siddhashrama, the Hermitage of Fulfilment, a grove like a cloud beside a mountain; here, the sage said, the rakshasas come to wreck my sacrifice, and here, tiger among men, you must strike them down.

### Chapter 5 · Six Nights of Fire
40. That day Vishvamitra entered his vow of silence, and the sages asked the princes to guard him; so for six days and nights, without sleep, Rama and Lakshmana stood watch beside him.
41. On the sixth day Rama told Lakshmana to be ready, and as he spoke, the altar fire blazed up, and a terrible sound filled the sky.
42. Like monsoon clouds the rakshasas swept in, and Maricha and Subahu poured streams of blood upon the altar.
43. Rama fitted the shining Manava weapon to his bow and loosed it at Maricha's chest, and it hurled him a full hundred yojanas into the surging ocean.
44. See, Lakshmana, Rama said, this cold arrow of Manu stuns him and carries him away, but it does not take his life. *(verse slide: Valmiki Ramayana 1.30.20 (vulgate))*
45. Then with the fire weapon he struck Subahu, who fell to the earth, and with the wind weapon he swept away all the rest.
46. The sacrifice was complete, and Vishvamitra said: my purpose is fulfilled, and you have made Siddhashrama true to its name.
47. And so the prince his father had called too young for battle did as his gurus asked, keeping a sage's fire safe through six sleepless days, and even in battle he spared a life.
48. Next morning the sages, with Vishvamitra at their head, spoke of King Janaka's sacrifice in Mithila, and of a wondrous bow there that no god, no asura, no rakshasa, still less any man, could string. *(verse slide: Valmiki Ramayana 1.31.9 (vulgate))*
49. Mighty princes had tried it and failed; and so Vishvamitra turned north, the deer and birds of Siddhashrama following him a while, toward Mithila, where that bow was waiting.
50. Here the first part of the Bala Kanda comes to rest. The sacred fire burns quietly now, and the road to Mithila lies open before the next part of Rama's story.


## Scene table
Every scene's `visual` in script.json is **direction** for wide 16:9 drawings. The creative-director writes the final prompts, seeds and rig tiers. Each direction names who is in the scene, the key pose, the setting, and what moves ("Moves:"). Characters are in side or three-quarter view with limbs, hair and props clear of the body and scenery. Every recurring character is a bible `{token}`.

| # | Ch | Start | Speech s | Pause | Segment | Locator | Visual direction (summary) | Moves |
|---|---|---|---|---|---|---|---|---|
| 1 | – | 0:00 | 5.5 | 0.25 | cold_open | VR 1.20.2, 1.20.7, 1.30.7–10 (vulgate) | wide night scene at a forest hermitage altar, the sacred fire blazing tall at the left third with flames leapi… | flames leaping, both princes' heads turning upward, clouds rolling |
| 2 | – | 0:05 | 11.0 | 0.25 | cold_open | VR 1.30.5–6, 1.30.11–12 (vulgate) | wide shot from low behind the altar, the fire small at the lower left, two huge shadow silhouettes {maricha} a… | the silhouettes descending, clouds swirling, flames flaring |
| 3 | – | 0:17 | 7.0 | 0.5 | cold_open | VR 1.19.21, 1.20.2, 1.27.23, 1.28.2 (vulgate) | medium wide side view of {rama_teen} at the left third drawing his bow, his drawing arm and elbow held clear o… | Rama's drawing arm pulling back, the arrow glow pulsing |
| 4 | – | 0:24 | 6.7 | 0.9 | title | VR 1.2.3–9 (vulgate) | calm wide river landscape at dawn, a quiet river curving across the lower half, reeds on the bank at the right… | water rippling, reeds swaying, the two birds lifting their heads |
| 5 | 1 | 0:32 | 7.6 | 0.25 |  | VR 1.1.1, 1.2.2 (vulgate) | wide hermitage clearing, {valmiki} seated on the left in three-quarter view with one hand raised in a question… | Valmiki's raised hand, Narada's head turning, leaves stirring |
| 6 | 1 | 0:40 | 12.1 | 0.5 | verse | VR 1.1.2–4 (vulgate) | verse slide: Valmiki Ramayana 1.1.2 (vulgate) |  |
| 7 | 1 | 0:52 | 9.6 | 0.25 |  | VR 1.1.6–8 (vulgate) | wide shot, {narada} on the right in three-quarter view, smiling, his right arm extended toward open board wher… | Narada's extended arm, the glowing outline brightening |
| 8 | 1 | 1:02 | 14.5 | 0.25 |  | VR 1.1 (Narada's summary), 1.2.2–9 (vulgate) | wide river bank, {narada} small at the upper right rising into the sky on a faint trail of light, {valmiki} st… | Narada rising, the birds' necks bobbing, water rippling |
| 9 | 1 | 1:17 | 9.5 | 0.6 |  | VR 1.2.10–12 (vulgate) | wide shot, a single arrow in flight across open board from a distant dark hunter silhouette half hidden among … | the arrow streaking, the falling bird, the female's neck rising |
| 10 | 1 | 1:27 | 11.0 | 0.7 | verse | VR 1.2.13–15 (vulgate) | verse slide: Valmiki Ramayana 1.2.15 (vulgate) |  |
| 11 | 1 | 1:39 | 11.9 | 0.25 |  | VR 1.2.16–19 (vulgate) | medium wide, {valmiki} standing at the river's edge at the left third in three-quarter view, one hand at his c… | the four lines of light shimmering, Valmiki's open hand, water lapping |
| 12 | 1 | 1:51 | 17.8 | 0.9 |  | VR 1.2.22–24, 1.2.31–37, 1.2.40–41 (vulgate) | wide landscape, snowy mountains along the top third and a long river winding across the board, at the right th… | the light rays pulsing, the lines of verse drifting, the river flowing |
| 13 | 2 | 2:09 | 10.1 | 0.25 |  | VR 1.5.5–9, 1.6.1–6 (vulgate) | wide city view of ancient Ayodhya along a river, carved stone gateways and stepped shikhara towers across the … | flags fluttering, the river flowing, a few petals drifting |
| 14 | 2 | 2:20 | 6.5 | 0.25 |  | VR 1.8.1, 1.8.8 (vulgate) | wide pillared hall, {dasharatha} seated on a throne at the left third in three-quarter view, chin lowered, one… | the lamp flame flickering, the king's head slowly lowering |
| 15 | 2 | 2:26 | 11.6 | 0.25 |  | VR 1.8.2–12, sargas 1.9–1.14 (vulgate) | wide sacrificial ground beside a river, {vasishtha} standing at the left in three-quarter view with one hand r… | the fire, Vasishtha's raised hand, Rishyashringa's ladle tipping |
| 16 | 2 | 2:38 | 17.2 | 0.25 |  | VR 1.15.1–10 (vulgate) | wide split sky, at the lower left {rishyashringa} pouring an offering into the altar fire, above the fire {dev… | the fire rising, the orbs trembling, the shadow swelling slightly |
| 17 | 2 | 2:56 | 10.6 | 0.5 |  | VR 1.15.13–14, 1.16.3–8 (vulgate) | wide sky scene, a great column of soft golden light descending from the upper left toward a tiny palace of Ayo… | the column of light descending, the palace lamps brightening |
| 18 | 2 | 3:07 | 10.7 | 0.25 |  | VR 1.16.11–20 (vulgate) | wide shot, a tall glowing figure of flame-light with a smooth featureless face rising from the altar fire at t… | the being's arms extending the vessel, flames leaping, the king's hands rising |
| 19 | 2 | 3:18 | 12.7 | 0.5 | verse | VR 1.16.23, 1.16.27–29 (vulgate) | verse slide: Valmiki Ramayana 1.16.27 (vulgate) |  |
| 20 | 2 | 3:31 | 12.9 | 0.25 |  | VR 1.18.8–14, 1.18.17–19 (vulgate) | wide palace courtyard at festival time, {kausalya} on the left in three-quarter view looking down at a cradle … | petals falling, the queens' heads bending, a drum beating |
| 21 | 2 | 3:44 | 16.8 | 0.9 |  | VR 1.18.29–31, 1.18.36–39 (vulgate) | wide open field at the forest edge, {rama_teen} riding a horse at a walk from left to right in side view, {lak… | the horse's legs walking, Lakshmana's stride, treetops swaying |
| 22 | 3 | 4:02 | 10.1 | 0.25 |  | VR 1.18.38–58 (vulgate) | wide carved stone palace gateway, {vishvamitra} standing at the left third in side view with his staff planted… | the king's steps, the sage's staff tapping down, the flag fluttering |
| 23 | 3 | 4:12 | 12.1 | 0.25 |  | VR 1.19.4–9, 1.19.18 (vulgate) | wide hall, {vishvamitra} at the left third in three-quarter view speaking, his right hand raised palm out clea… | the sage's raised hand, the faint red rain falling |
| 24 | 3 | 4:25 | 9.3 | 0.6 | verse | VR 1.19.21, 1.20.1–2 (vulgate) | verse slide: Valmiki Ramayana 1.20.2 (vulgate) |  |
| 25 | 3 | 4:35 | 10.6 | 0.25 |  | VR 1.20.3–9, 1.20.16–25 (vulgate) | wide hall, {dasharatha} half risen from his throne at the right third, both arms reaching forward in a pleadin… | the king's arms reaching, the shadow darkening |
| 26 | 3 | 4:45 | 11.1 | 0.5 |  | VR 1.20.28, 1.21.1–4 (vulgate) | wide hall, {vishvamitra} at the left third turning away in side view, staff swung forward clear of his body, m… | the sage turning, flames flaring, the floor shaking |
| 27 | 3 | 4:57 | 12.2 | 0.25 |  | VR 1.21.5–9 (vulgate) | wide hall, {vasishtha} standing at the right third in three-quarter view, one hand resting gently on the shoul… | Vasishtha's raised hand, the king lifting his head |
| 28 | 3 | 5:09 | 11.6 | 0.25 |  | VR 1.22.1–6 (vulgate) | wide palace steps, {dasharatha} on the left in three-quarter view bending to kiss the head of {rama_teen}, {ka… | the king bending, flowers falling, the sage's cloth stirring in the wind |
| 29 | 3 | 5:21 | 11.4 | 0.25 |  | VR 1.22.11–18, 1.22.23–24 (vulgate) | wide riverbank at dusk, {vishvamitra} on the left in side view with one hand raised over water cupped in the h… | the sage's raised hand, water trickling from Rama's hands, the river flowing |
| 30 | 3 | 5:33 | 19.2 | 0.9 | verse | VR 1.23.1–2, 1.23.5, 1.24.12–28 (vulgate); Venkatesha Suprabhatam opening (later tradition, Wikipedia 'Suprabhatam', accessed 2026-11-18) | verse slide: Valmiki Ramayana 1.23.2 (vulgate) |  |
| 31 | 4 | 5:53 | 11.7 | 0.25 |  | VR 1.23.5, 1.24.2–5, 1.24.12–32 (vulgate) | wide river crossing, a small boat at the left third carrying {vishvamitra}, {rama_teen} and {lakshmana_teen} s… | the boat rocking, waves curling, Tataka's hair streaming |
| 32 | 4 | 6:05 | 12.3 | 0.25 |  | VR 1.25.2, 1.25.5–13 (vulgate) | wide forest clearing at dusk, {agastya} standing at the left third in side view with his kamandalu held clear … | Agastya's raised hand, the shadows shrinking back, wind in the trees |
| 33 | 4 | 6:17 | 11.5 | 0.6 | verse | VR 1.25.17–19 (vulgate) | verse slide: Valmiki Ramayana 1.25.18 (vulgate) |  |
| 34 | 4 | 6:29 | 9.3 | 0.25 |  | VR 1.26.6–8, 1.26.12 (vulgate) | wide forest, {rama_teen} at the left third in side view plucking his bowstring with his arm clear of his body,… | the bowstring vibrating, Tataka's charge, trees bending |
| 35 | 4 | 6:39 | 11.1 | 0.25 |  | VR 1.26.15–23 (vulgate) | wide forest in a whirling dust storm, rocks falling from a dark sky at the right, the shadow {tataka} fading i… | dust swirling, rocks falling, the sage's raised arm |
| 36 | 4 | 6:50 | 13.4 | 0.7 |  | VR 1.26.23–28, 1.26.35 (vulgate) | wide forest at sunset after the storm, {rama_teen} at the left third in side view with his bow lowered, an arr… | the light trail fading, flowers blooming, birds returning |
| 37 | 4 | 7:04 | 14.4 | 0.25 |  | VR 1.27.1–15, 1.27.22–26 (vulgate) | wide morning clearing, {vishvamitra} seated facing east at the left, smiling, both hands raised in blessing cl… | the symbols circling slowly, the light figures bowing, morning rays |
| 38 | 4 | 7:19 | 12.0 | 0.6 | verse | VR 1.27.27, 1.28.2–3 (vulgate) | verse slide: Valmiki Ramayana 1.28.2 (vulgate) |  |
| 39 | 4 | 7:32 | 14.4 | 0.9 |  | VR 1.28.17–22, 1.29.3–4, 1.29.23 (vulgate) | wide landscape, a peaceful hermitage grove at the right third under a mountain, thatched huts and a smoking al… | altar smoke rising, the sage's pointing arm, treetops swaying |
| 40 | 5 | 7:47 | 12.0 | 0.25 |  | VR 1.29.26–30, 1.30.4–6 (vulgate) | wide hermitage altar at dusk, {vishvamitra} seated in silence before the fire at the centre-left with eyes clo… | the fire flickering, the princes turning their heads to scan the sky, stars appearing |
| 41 | 5 | 7:59 | 8.3 | 0.25 |  | VR 1.30.7–10 (vulgate) | wide altar, the fire suddenly flaring tall at the right third, priests small around it, {rama_teen} at the lef… | the flames leaping high, Rama's raised hand, clouds gathering |
| 42 | 5 | 8:08 | 7.2 | 0.5 |  | VR 1.30.11–13 (vulgate) | wide sky over the hermitage, the shadow silhouettes {maricha} on the left and {subahu} on the right, well apar… | clouds churning, the silhouettes diving, Rama running |
| 43 | 5 | 8:16 | 9.8 | 0.6 |  | VR 1.30.16–18 (vulgate) | wide sweeping view, {rama_teen} at the left third in side view with the bow just released and his arm clear of… | the light streak, Maricha tumbling, waves rising |
| 44 | 5 | 8:26 | 7.2 | 0.6 | verse | VR 1.30.19–20 (vulgate) | verse slide: Valmiki Ramayana 1.30.20 (vulgate) |  |
| 45 | 5 | 8:34 | 7.7 | 0.25 |  | VR 1.30.22–23 (vulgate) | wide hermitage sky, {rama_teen} at the left third in side view releasing an arrow trailing chalk flame toward … | the flaming arrow, the wind lines sweeping, clouds breaking apart |
| 46 | 5 | 8:42 | 8.3 | 0.9 |  | VR 1.30.24–26 (vulgate) | wide calm dawn at the hermitage, the altar fire burning low and steady at the centre, {vishvamitra} at the rig… | the gentle fire, the sages' hands, morning birds |
| 47 | 5 | 8:51 | 11.5 | 0.25 | closing | VR 1.20.2, 1.30.5, 1.30.16–20, 1.30.26 (vulgate) | wide quiet morning, {rama_teen} sitting at the left third on a rock in side view, his bow laid flat across his… | mist drifting, Rama's head lifting, leaves stirring |
| 48 | 5 | 9:03 | 12.9 | 0.6 | closing | VR 1.31.1–9 (vulgate) | verse slide: Valmiki Ramayana 1.31.9 (vulgate) |  |
| 49 | 5 | 9:16 | 11.7 | 0.9 | closing | VR 1.31.10–11, 1.31.14–18 (vulgate) | wide road at sunrise heading north, {vishvamitra} walking left to right at the right third in side view, {rama… | the walkers striding, deer stepping, birds flying |
| 50 | 5 | 9:29 | 10.4 | 6.0 | end_board |  | calm wide end board, the hermitage altar fire burning low and gentle at the left third, a long empty road wind… | the low fire flickering, a few stars twinkling |


### Notes for the creative-director (visual direction only)
- **Tokens used:** {valmiki}, {narada}, {bharadvaja}, {rama_teaser}, {dasharatha}, {kausalya}, {sumitra}, {kaikeyi}, {rishyashringa}, {vasishtha}, {vishvamitra}, {rama_teen}, {lakshmana_teen}, {tataka}, {agastya}, {maricha}, {subahu}, {devas_light}.
- **No token yet:**
  - krauncha birds, the hunter (a distant silhouette, never a close figure, no caste coding), and the radiant being from the fire (a featureless figure of flame-light);
  - Brahma (a radiant lotus of light, bible rule) and Vishnu (a column of golden light);
  - Ravana (a looming crowned shadow over an island fortress, never multi-armed, bible rule);
  - the weapons and the withdrawals (figures of light with joined palms).
- **Sensitivity:**
  - The krauncha's death has no wound or blood on screen.
  - The rain of blood falls only on the stone altar.
  - Tataka's fall happens out of sight. Her mutilation (1.26.17–18) is neither narrated nor drawn.
  - The rakshasas follow the bible shadow rule.
- **Verse slides:** 9 in total, each `visual: "the verse written in chalk…"` with `devanagari`, `source` and `edition`.
- **End board (scene 50):** the right half and the lower part are left open for YouTube end-screen elements. The 6.0 s pause is deliberate: the music-only hold (skill: "15–20 s of soft narration or music only").
- **Extra field:** `segment` (cold_open, title, closing, end_board) is informational for the dashboard, packager and render; no code reads it yet.

## Sources (edition-labelled)
- **Text:** VR (vulgate, southern recension). Raw wikitext of sa.wikisource रामायणम्/बालकाण्डम्, sargas 1, 2, 5, 6, 8, 9, 15, 16, 18–23 and 31, fetched 2026-11-18.
- **Numbers cross-checked** on valmikiramayan.net via the Internet Archive copy (live site returned HTTP 500), sargas 2 and 23, accessed 2026-11-18:
  - 1.2.4, 1.2.9, 1.2.10, 1.2.15, 1.2.18, 1.2.31–32 (31b–32a there), 1.2.36–37 (36b–37a there), 1.2.40
  - 1.23.2, 1.23.5
- **Re-used verified tables:** sargas 24–31 from C0005, C0006 and C0007 (their numbering notes for sarga 29, 1.28.21–22 and 1.30.22–23 still apply). The verse cards 1.1.2, 1.16.27 and 1.20.2 are reused from C0002, C0003 and C0004.
- **Not checked:** the Critical Edition and Goldman, so no `[CE …]` tags are given.
- **Later tradition:** Wikipedia, "Suprabhatam" (https://en.wikipedia.org/wiki/Suprabhatam), accessed 2026-11-18. The Venkatesha Suprabhatam (composed 1420–1432 CE) opens with VR 1.23.2.
- The full claim-by-claim verse table is meant for `content/C0011/research/report.md`.

## Verse slides (9; meaning narrated, never recited)
| Scene | Chapter | Locator | Opening words |
|---|---|---|---|
| 6 | 1 | VR 1.1.2 (vulgate) | को न्वस्मिन् साम्प्रतं लोके |
| 10 | 1 | VR 1.2.15 (vulgate) | मा निषाद प्रतिष्ठां त्वम् |
| 19 | 2 | VR 1.16.27 (vulgate) | कौसल्यायै नरपतिः |
| 24 | 3 | VR 1.20.2 (vulgate) | ऊनषोडशवर्षो मे |
| 30 | 3 | VR 1.23.2 (vulgate) | कौसल्या सुप्रजा राम |
| 33 | 4 | VR 1.25.18 (vulgate) | नृशंसमनृशंसं वा |
| 38 | 4 | VR 1.28.2 (vulgate) | गृहीतास्त्रोऽस्मि भगवन् |
| 44 | 5 | VR 1.30.20 (vulgate) | पश्य लक्ष्मण शीतेषुं |
| 48 | 5 (closing) | VR 1.31.9 (vulgate) | नास्य देवा न गन्धर्वा |

## Accuracy notes
- **Who speaks of Mithila (1.31.5–7):** the sages, "placing Vishvamitra at their head", not Vishvamitra alone. The narration follows the text.
- **"On the sixth day", not "night":** the attack follows six days and nights of guard (1.30.5–7).
- **"Too young":** Dasharatha says "not yet sixteen… not fit to fight rakshasas" (1.20.2) and calls Rama "a boy, untrained" (1.20.7).
- **"He spared a life" (scene 47):** the text gives no motive. It records Rama saying he is "not eager to kill such ones" (1.30.16) and that the Manava "does not take his life" (1.30.20). All the other attackers die (1.30.22–24). The valmikiramayan.net note that Maricha is kept alive for the golden deer is commentary and is not used.
- **"I may not curse them" (scene 23):** "the observance is such that a curse cannot be uttered there" (1.19.7–8).
- **Tataka's fall (scene 36):** arrows aimed by sound check her rain of stones (1.26.23–24); as she rushes at the brothers, one arrow to the chest fells her (1.26.25–26).
- **The payasa fire** is the putriya ishti that follows the horse sacrifice (1.15.1–3, 1.16.11), so the narration says "one more fire for the birth of sons".
- **Lakshmana and Shatrughna:** "two sons" (1.18.14). "Twins" is not used.
- **"Like Rama's second life":** बहिःप्राण इवापरः, "like another life-breath outside him" (1.18.30).
- **Reported speech:** all speech is reported without quotation marks. Every scene carries its locator in `quote_src`. No dialogue or verse is invented. Paraphrases stay within the cited verses.
- **Scene 38's question** ("how do I call these weapons back?") reports 1.28.2's "I wish for their withdrawals (saṃhāra)". Saṃhāra here means withdrawal, not destruction (C0006 note). The Hindi writer should avoid संहार in narration.
- **Departure north (scene 49):** Vishvamitra announces he is going north to the Himalaya on the Ganga's north bank (1.31.15–16). The party's destination is Mithila (1.31.6–7, 1.31.11). The narration says "turned north… toward Mithila".
- **Deities:**
  - Brahma: radiant lotus of light.
  - Vishnu: column of light.
  - The gods: `{devas_light}` orbs.
  - Ravana: crowned shadow only.
- **Sensitivity:** Rama is calm throughout. His anger at 1.30.17 is not narrated. No gore.
- **Later tradition:** one labelled clause (scene 30, the Suprabhatam), framed as "centuries later". Nothing else from later retellings.
- **Chapter-end pulls (scenes 21 and 30):** the weddings come from 1.18.37–39. "Never guessing who was about to come" is narrative framing; it claims nothing about the text. The forest and "the one who had laid it waste" come from 1.24.12–28.

## Notes for the hi and te writers (scene list is fixed at 50)
- Keep all 50 scenes and every `visual`, `kind`, `devanagari` and `source` identical. Narration is written natively.
- **Budget:** hi about 1,430 words; te about 840 words. Telugu shortens every scene, never drops one, and uses no digits.
- **Scene 30:** te may name the Suprabhatam and Tirumala; it is labelled later tradition and verified above.
- **Scene 38:** hi should say लौटाना, not संहार.
- **Pauses:** keep the same `pause` values. Scene 50 keeps its 6.0 s music hold.

## Lint result (`.venv/bin/python -m pipeline lint C0011 --lang en`)
- Verdict **PASS** with no findings (matches `en/lint.json`).
- Estimate 586.8 s, 1,623 words (target 480–720 s, fail above 780).
- 50 scenes (35–60). 5 chapters of 98–118 s each (60–180). Cold open 32 s (20–40). First scene 5.5 s (warn above 6).
- All keywords present. Every verse card has a locator and an edition.
- The earlier silences warning no longer appears: the current lint applies the long-form pause rules to the 23 planned pauses.

## Review fixes applied (reviewer Story QA, `en/review.md`, 80/100)
- **MUST 1, scene 26:** the headline fragment is now prose: "he said it was unworthy of Raghu's line for a king to break his word, and as he spoke, the whole earth trembled."
- **MUST 2, scene 21:** now ends on a pull into chapter 3 (the king thinking of the princes' weddings, 1.18.37–39). The hunting clause was dropped to keep the scene at 16.8 s. Scene 22 now opens "It was then that…".
- **MUST 3, scene 30:** the Suprabhatam aside is shortened and the chapter now ends on a pull: "That morning they walked on toward the Ganga, and beyond it lay a dreadful forest, and the one who had laid it waste." (1.23.5, 1.24.12–28). Scene length is 19.2 s.
- **SHOULD fixes, all applied:**
  - scene 36: arrows aimed by sound check her rain of stones, then one arrow strikes her chest as she rushes at him (1.26.23–26);
  - scene 3: "had trembled for now carried" (1.19.21);
  - scene 16: split into two sentences, with "the rakshasa king Ravana";
  - scene 17: "the god Vishnu";
  - scene 8: split into two sentences; scene 9 now opens "But", scene 11 "Afterwards";
  - scene 39: "Siddhashrama, the Hermitage of Fulfilment";
  - scene 47: the double past perfect is smoothed ("did as his gurus asked… he spared a life");
  - scene 50: "lies open before the next part" replaces the repeated "waiting";
  - scene 20: "the spring month of Chaitra";
  - X1: this section and `hooks.json` `cold_open_s` (32) now agree with lint.
- **Unchanged:** every `visual`, `kind`, `pause`, verse slide and the scene count. Hindi and Telugu share them.

## Applied learnings
Source: `data/reports/latest_insights.json` (generated 2026-11-18T12:45:35+0530). All three actions come from Shorts; only the parts that transfer to long-form are applied. Approved rules (storytelling skill long-form section, lint) take precedence.

| Action | Tier · n | Applied? | Where and how |
|---|---|---|---|
| A1: prefer the 35 s beat shape (turn at 18–25 s) and state the stakes by H2 (F1) | anecdote · n=12 | **Partly** | The stakes are stated in the first sentence (scene 1), and the cold open lands its turn ("But this story begins long before…") at about 25 s. The 35 s shape and the 18–25 s turn are Shorts-only and not applied. |
| A2: hook ≤3.0 s, stakes in the first sentence, frame 0 ≥70% drawn, first line written natively short (F2) | anecdote · n=1 | **Yes, long-form version** | The first line is 17 words, estimated 5.5 s, under the long-form 6 s warning; the 3.0 s Shorts limit doesn't apply. The scene 1 frame-0 direction (two princes, a blazing altar, a roaring sky) reads muted. The hi and te writers should write their first lines natively short. |
| A3: ≤6-word engagement line as a share prompt with a real answer (F6) | anecdote · n=12 | **No** (in narration) | Long-form has no engagement line and no subscribe lines (skill). Suggested to the packager as a pinned comment: "Which bird's death made the first shloka?" (answer: the krauncha, VR 1.2.10–15). |

`script.json` carries these as top-level `learnings`.
