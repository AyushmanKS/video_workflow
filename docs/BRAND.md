# Chalk Tales brand

The owner approved one brand name on both platforms: **Chalk Tales**. The machine-readable source of truth is `profiles/brand.json`. The pipeline reads it, and this document explains it. Change a value there first, then here.

Everything in this document was built locally. Nothing on the live accounts has been changed. The owner applies the changes using the checklist at the end.

## Positioning
**Chalk Tales tells India's great stories as chalkboard animation, under a minute each, in Indian languages.**

- **Now:** the Valmiki Ramayana, one episode at a time, with verses cited.
- **Next:** Indian history and science, told the same way.
- **Who it is for:** viewers in India and the diaspora who want the real story quickly. That means the Valmiki text rather than a TV serial version, told in their own language and short enough to send to family.
- **What makes it different:** the chalkboard look (no other mythology channel uses it), source citations, and five native-language versions of every episode.

## Voice and tone
- Calm, story-led and respectful. A storyteller, not a preacher and not a hype channel.
- Use honorifics (Shri Ram, Maharishi Valmiki) and say "according to Valmiki" where versions differ. Never use "myth", "fake" or "shocking secret".
- Ask a genuine question at the end. Do not use engagement bait such as "Comment Jai Shri Ram if…" or "Share to 5 people".
- Be honest about tools. Illustrations and narration are made with AI tools, and every script is written and checked by us. Never imply hand-drawn art or a human narrator (`docs/PUBLISHING.md`).
- Each language is written natively. Do not translate word for word.

## Names and handles
| Item | Value | Status |
|---|---|---|
| Brand name | Chalk Tales | approved |
| Instagram handle | `@aks.chalk.tales` (https://www.instagram.com/aks.chalk.tales/) | live |
| Instagram display name | `Chalk Tales · Ramayana & More` (29 characters, limit 30) | to apply (currently "chalk tales") |
| YouTube channel name | Knowledge PowerBank → **Chalk Tales** | rename pending (owner, in Studio) |
| YouTube handle | `@knowledgepowerbank` → `@aks.chalk.tales` if available | pending |
| Contact email | ayushman.k.singh@gmail.com | approved |

`profiles/brand.json → brand.youtube.active_url` is the one YouTube link the pipeline uses. It stays at the current URL until the owner confirms the rename. After that, change `active_url` (and `status`) and nothing else needs to change.

Why the display name has "Ramayana & More": Instagram search matches the typed query against usernames, names and bios. The keyword goes in the name, and "& More" keeps the name valid when the history and science series start (`reports/Instagram creator profile setup.md`).

## Colours
| Token | Hex | Use |
|---|---|---|
| slate | `#14191C` | backgrounds, the board |
| chalk | `#F2EFE6` | wordmark, rings, body text |
| saffron gold | `#E8BE6E` | logo mark, tagline, icons |
| saffron accent | `#F28C28` | small accents only (never large fills) |

## Fonts
The brand images use macOS system fonts, as the owner chose. The OFL alternatives are in `assets/fonts/`.
- Wordmark: Chalkduster
- Tagline: Chalkboard SE
- Indic scripts: ITF Devanagari Medium (Hindi, Marathi), Kohinoor Gujarati Medium, Kohinoor Telugu Medium

Every glyph is checked against each font's missing-glyph shape when the assets are built.

## Logo
- **Mark:** Rama's bow in saffron gold, drawn with chalk texture, an arrow through it pointing up, inside a thin chalk-white ring, on slate.
- No deity faces and no text inside the profile picture. Deity imagery is sensitive in India, and this mark avoids it.
- **Clear space:** keep at least the ring's stroke width × 4 free around the ring.
- **Minimum size:** 40 px (the profile picture's smallest display size). Below about 60 px only the bow outline reads.
- **Don't:** recolour the bow, add gradients or glow, rotate it, or put it on a light background without the slate disc.
- At a glance the vertical-arrow mark can read as an umbrella. This is the owner's current approved shape, so it is kept.

## Assets
The assets are local PNGs in `data/brand/` (gitignored). Regenerate them with `python -m pipeline.brandart`.

| File | Use |
|---|---|
| `youtube_banner_2560x1440.png` | YouTube banner (1.3 MB). All text and the logo sit inside the centred 1546×423 safe area |
| `youtube_banner_preview.png` | Review copy with the TV, desktop (2560×423), tablet (1855×423) and mobile/safe (1546×423) crop guides |
| `profile_bow_1080.png` | **Recommended** profile picture (Instagram and YouTube). Thicker strokes for 110 px and 40 px |
| `profile_bow_ct_1080.png` | Alternative with a "CT" monogram. The letters cannot be read at 40 px |
| `profile_preview.png` | Current, refined and CT versions at 110 px and 40 px, on dark and light backgrounds |
| `highlight_ramayana.png`, `highlight_new.png`, `highlight_behind_the_chalk.png`, `highlight_collabs.png` | Instagram highlight covers (1080×1920, icon inside the centre circle) |
| `brand_review.png` | Contact sheet of everything above |
| `instagram_profile_bow.png` | Current live Instagram picture (kept unchanged) |

## Instagram profile
**Display name:** `Chalk Tales · Ramayana & More`

**Bio** (144 characters, limit 150; the ✍️ emoji counts as 2):
```
Indian epics & history, drawn in chalk ✍️
Valmiki Ramayana · English · हिंदी · ગુજરાતી · తెలుగు · मराठी
Paid collabs: ayushman.k.singh@gmail.com
```

**Links:** link 1 is the YouTube channel (`brand.youtube.active_url`), titled "Watch the series in order". Links 2–5 can be the per-language playlists once they exist. Only link 1 shows on the profile.

**Contact:** turn on the Email button with the collab address. Add no phone number.

**Highlights,** in this order:
1. **Ramayana** (bow): one Story per episode, linking to the Reel.
2. **New** (spark): the latest episode and announcements.
3. **Behind the Chalk** (chalk stick): how an episode is made, with the AI-tools disclosure.
4. **Collabs** (envelope): partnership formats and the email address.

Add **History** and **Science** highlights only when those series start.

## YouTube channel
**Name:** Chalk Tales (after the rename). **Handle:** `@aks.chalk.tales` if available.

**Description** (797 characters; YouTube shows about the first 1,000, so all of it is visible):
```
Chalk Tales brings India's great stories to life as hand-drawn chalkboard animation, in under a minute each.

Now showing: the Valmiki Ramayana, episode by episode, from Maharishi Valmiki's first verse onward. Every script is checked against the Valmiki Ramayana and cites its verses; where later retellings differ, we say so.

Each episode is made in English, हिंदी, ગુજરાતી, తెలుగు and मराठी, with more Indian languages to come. Next: more Indian history and science, told the same way.

Subscribe for a new chapter every day, and watch the series in order in the playlists.

Instagram: https://www.instagram.com/aks.chalk.tales/

Paid collaborations & business inquiries: ayushman.k.singh@gmail.com

Illustrations and narration are made with AI tools; every script is written and checked by us.
```
> **Owner check:** the first line says "hand-drawn chalkboard animation". The house rule in `docs/PUBLISHING.md` is never to imply hand-drawn art, and the last line of this text says the illustrations are made with AI tools. Consider "hand-drawn-style chalkboard animation" or "chalkboard animation". The text above is kept exactly as supplied until the owner decides.

**Organisation:**
- **Playlists:** one per language, each set as a series in Studio, plus the existing "Valmiki Ramayana" playlist:
  - "Valmiki Ramayana · English"
  - "वाल्मीकि रामायण · हिंदी"
  - "વાલ્મીકિ રામાયણ · ગુજરાતી"
  - "వాల్మీకి రామాయణం · తెలుగు"
  - "वाल्मीकी रामायण · मराठी"
  - Set "Valmiki Ramayana" as a series only if each video can belong to just one series playlist; YouTube allows a video in only one series.
- **Home tab sections:**
  1. Latest (Shorts)
  2. one section per language playlist, in this order: हिंदी, English, ગુજરાતી, తెలుగు, मराठी
- **Featured Short:** Episode 1 in the visitor's most likely language. Use Hindi until analytics say otherwise.
- **Title pattern:** `<hook> | Ramayana Ep N`, or the language's own form, for example `… | रामायण भाग 6`. This is what the packager already writes.

## Cross-promotion rules
- **Automatic, in metadata only.** `python -m pipeline promo <ID> --apply` runs before G3. It adds:
  - an Instagram follow line and a collab line to every YouTube description
  - a suggested pinned comment carrying the episode question and the Instagram handle (the owner pins it by hand)
  - one "watch the full series in order on YouTube, link in profile" line to every Instagram caption, above the hashtags
- The text comes from `profiles/brand.json → brand.cta.<lang>`. gu, te and mr are marked "needs native review".
- **No spoken plug** in videos under 60 s. Every second goes to the story.
- **Optional:** an end-card handle (`@aks.chalk.tales`) drawn in chalk on the last frame. It needs a render change and owner approval, and it must never be a YouTube logo or a "Subscribe" card on Instagram (Instagram originality rules).
- Instagram captions never rely on a raw URL, because links in captions are not clickable.
- Limits are checked automatically: Instagram 2,200 characters and at most 5 hashtags; YouTube description 5,000 characters, with no `<` or `>`.
- Already approved, scheduled or live items are never changed automatically. See `data/reports/promo-audit-<date>.md` for proposed manual edits.

## Apply to the live accounts (owner checklist)
Do these in the apps. Claude does not change live accounts.

**Instagram (app → Edit profile)**
1. **Name:** `Chalk Tales · Ramayana & More`. You can change the name twice in 14 days, so paste it once and check the counter.
2. **Bio:** paste the three lines above. Check that the counter shows 150 or fewer.
3. **Profile picture:** upload `data/brand/profile_bow_1080.png`. Check it at small size on the profile and in comments.
4. **Links → Add external link:** `brand.youtube.active_url`, titled "Watch the series in order".
5. **Contact options:** Email = ayushman.k.singh@gmail.com, no phone. Category: Video creator, shown.
6. **Highlights:** create Ramayana, New, Behind the Chalk and Collabs from a Story each. Then Edit highlight → Edit cover → choose the matching `data/brand/highlight_*.png` (send them to the phone first).

**YouTube (Studio → Customisation)**
1. **Profile → Name:** Chalk Tales. YouTube limits how often the name and handle can change; Studio shows the limit.
2. **Profile → Handle:** `@aks.chalk.tales` if available. The old handle URL redirects for a while.
3. **Profile → Description:** paste the description above (797 characters).
4. **Profile → Contact info:** ayushman.k.singh@gmail.com. This is also the business email in Basic info.
5. **Profile → Links:** Instagram, https://www.instagram.com/aks.chalk.tales/ (shown on the banner).
6. **Profile → Banner image:** upload `data/brand/youtube_banner_2560x1440.png` (2560×1440, safe area 1546×423, 6 MB or smaller; this file is 1.3 MB). Check the device preview.
7. **Profile → Picture:** `data/brand/profile_bow_1080.png`.
8. **Content → Playlists:** create the five language playlists and tick "Set as official series" on each. Add the existing Shorts.
9. **Layout:** add the Featured Short and the sections Latest, then one per language.
10. **After the rename is confirmed,** tell Claude. Claude then changes `brand.youtube.active_url` and `status` in `profiles/brand.json`; nothing else needs to change.
11. **Live videos:** if you want the promo lines on already live or scheduled videos, paste the proposed text from `data/reports/promo-audit-<date>.md` in Studio (Content → video → Details) or in the Instagram app (Edit caption). The local `publish.json` files stay as approved.
