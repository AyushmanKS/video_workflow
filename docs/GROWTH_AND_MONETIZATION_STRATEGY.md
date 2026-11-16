# Growth, account and monetization strategy: RAMAYANA, The Epic in Chalk

**Research date:** 2026-11-16. All web sources were fetched or searched on this date. Platform rules change often, so re-check every **[VERIFIED]** item before acting on it, and re-check the whole document before each new phase.

**Scope:** This document covers a faceless, AI-assisted short-form storytelling studio based in India. It has one YouTube channel with Shorts in four languages (en, hi, gu, te) and the playlist "Valmiki Ramayana". It has one Instagram creator account, @mr.aks.tale, with Reels in the same four languages. Images are AI-generated (Z-Image Turbo). Narration is AI TTS (Kokoro for English, Maya 2 Malini for Indic languages). Scripts are original and cite the Valmiki Ramayana.

**What this document does not contain:** private analytics, invented numbers or earnings forecasts. Nothing here promises income. Where a number appears, it is a platform rule or a cited public figure. It never describes this account's performance.

**Evidence labels**

| Label | Meaning |
|---|---|
| **[VERIFIED]** | Read on an official page (support.google.com, blog.youtube, creators.instagram.com, about.fb.com, a government or Amazon page) on the research date. Linked. |
| **[SECONDARY]** | Reported by credible press, law firms or trade media, but not confirmed on the primary page. Linked. |
| **[UNVERIFIED]** | Sources conflict, or no primary page could be read. Check in Studio, the app or a primary page before relying on it. |
| **[REC]** | Recommendation or inference by this document. It is not a platform statement. |

Earlier repo research is reused, not repeated: `reports/Instagram Reels Ep01 audience strategy.md` and `reports/Instagram creator profile setup.md`.

---

## 0. Executive summary

1. **Keep one YouTube channel and one Instagram account for now. [REC]**
   - YouTube's own help page lists both one multilingual channel and separate language channels as valid options ([VERIFIED](https://support.google.com/youtube/answer/6070467?hl=en)).
   - Every monetization threshold is counted **per channel**, so splitting four ways now would divide progress toward each one by four.
   - Split a language off only when the triggers in §2.5 are met.
2. **The YouTube Partner Program changes on 1 February 2027 ([VERIFIED](https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/), announced 10 Aug 2026).**
   - New applicants for ad revenue will need 1,000 subscribers plus either **8,000 watch hours in 365 days** or **20 million Shorts views in 90 days**.
   - Even after a channel is admitted, it earns Shorts ad revenue only in months when it has **10 million qualified Shorts views over the past 90 days**.
   - The fan-funding and Shopping thresholds stay the same.
   - **[REC]** For a Shorts-only channel, the realistic first goal is the **fan-funding tier**, not ad revenue. Long-form compilations matter because watch hours from the Shorts feed do not count toward the 4,000- or 8,000-hour route ([VERIFIED](https://support.google.com/youtube/answer/72851?hl=en)).
3. **The biggest policy risk is YouTube's "inauthentic content" policy, not copyright.**
   - The policy was renamed from "repetitious content" on 15 July 2025.
   - It excludes "AI-generated content made with generic or unoriginal templates" and "image slideshows, templated storylines" from monetization ([VERIFIED](https://support.google.com/youtube/answer/1311392?hl=en)).
   - A channel built from AI images, a TTS voice and a fixed template, posting four language copies of each visual, looks like that pattern on paper.
   - The mitigations are in §3.4. The four-copies-per-episode pattern is one of the strongest arguments for eventually giving each language its own channel (§2).
4. **Fix three compliance items before applying for any monetization. [REC]**
   - **AI disclosure is inconsistent.** The YouTube `publish.json` files say `synthetic: false`, while Instagram sends `is_ai_generated=true`.
   - **The fonts are macOS system fonts (Chalkduster and others).** Their licence clearly covers display and printing. It does not clearly cover commercial video ([SECONDARY](https://discussions.apple.com/thread/7493969)).
   - **The audience setting must be "not made for kids",** and the content must honestly be made for a general audience.
5. **First revenue to aim for, in order. [REC]**
   1. Instagram Gifts (500 followers; India is on the supported list).
   2. YouTube fan funding (Super Thanks and memberships) once the expanded-tier threshold is met.
   3. Book affiliate links. Amazon.in pays **4.72% on Books** and nothing on Kindle e-books ([VERIFIED](https://affiliate-program.amazon.in/help/node/topic/GRXPHT8U84RAYDXZ)).
   4. Devotional and education sponsorships once the audience is visible.
   5. YouTube ad revenue last.
6. **Languages.** Do not add a fifth language until each current language has at least five episodes of comparable data.
   - Tamil, Marathi and Bengali are the next candidates by speaker base and platform tool support.
   - Each needs its own regional-tradition brief (Kamba, Bhavartha, Krittivasi; see §6), a native-speaker review and a voice that passes QA.

---

## 1. Growth: how the two platforms recommend short videos

### 1.1 YouTube Shorts: what the system measures

**[VERIFIED]** YouTube's Shorts discovery help page says ([source](https://support.google.com/youtube/answer/11914225?hl=en&co=YOUTUBE._YTVideoType%3Dshorts)):
- Shorts are ranked by "performance and viewer personalization".
- When a Short is recommended, the system checks whether viewers "choose to watch it, ignore it, or click 'not interested'".
- Ranking uses the "% of viewers who chose to view, avg. view duration and avg. % viewed", plus likes and post-watch survey results.
- Search ranking depends on how well the metadata matches the query and whether viewers click and watch.
- There is "no minimum posting frequency needed for good performance".
- Shorts do not hurt long-form recommendations.
- Topic interest, competition and seasonality all affect reach.

**[VERIFIED]** The Studio metric is "Viewed (vs. swiped away)", which YouTube describes as "the percentage of times viewers viewed your Shorts versus swiped away" ([content analytics help](https://support.google.com/youtube/answer/12220281); [Shorts analytics tips](https://support.google.com/youtube/answer/12942217?hl=en&co=YOUTUBE._YTVideoType%3Dshorts)).

**[VERIFIED]** On 24 August 2026 YouTube made a "view" count from the first frame in every format. The older definition is now called an **engaged view**: playback that continues "some seconds" past the first frame. CTR, average view duration and retention are still calculated mainly from engaged views, and YPP earnings are based on engaged views ([blog.youtube, 19 Aug 2026](https://blog.youtube/inside-youtube/engaged-views-youtube-explained/)). YouTube had already applied this split to Shorts on 31 March 2025 ([SECONDARY](https://www.tubefilter.com/2025/03/26/youtube-shorts-views-counting-stats/)).
- **[REC]** Compare videos only on engaged views. The public view count overstates real viewing and is not comparable across that date.

**[SECONDARY]** YouTube's Shorts lead Todd Sherman said in a 2023 Creator Insider Q&A:
- "The audience is the algorithm."
- The system tries to "find a set of people that may enjoy your video".
- "There is nothing in our systems that's like when you hit the five video or 10 short threshold."
- Hashtags are not required.

These come from an auto-generated transcript, as quoted by [OutlierKit](https://outlierkit.com/resources/youtube-shorts-algorithm/) (source video: [Creator Insider](https://www.youtube.com/watch?v=n3jsYK_-aRU)).

**[UNVERIFIED]** YouTube has not published weights for these signals. Figures circulating in blogs, such as "aim for 70–80% viewed", are vendor rules of thumb, not YouTube targets.

### 1.2 Instagram Reels: what the system measures

**[VERIFIED]** Instagram first shows an eligible Reel to a small audience that includes non-followers, then widens it as people interact. Recommended content must not show a watermark. For near-duplicates, only the original is recommended. "Adding a new voiceover" is listed as a substantial change ([creators.instagram.com](https://creators.instagram.com/recommendations-and-originality)).

**[SECONDARY]** Adam Mosseri named **watch time, likes per reach and sends per reach** as the most important signals. Sends count slightly more for reaching non-followers ([Buffer](https://buffer.com/resources/instagram-algorithms/)). Hashtags are capped at 5 per post (since December 2025) and do not raise reach on their own ([Business Today](https://www.businesstoday.in/technology/news/story/no-more-hashtag-stuffing-instagram-limits-hashtag-usage-to-just-5-per-reel-and-post-507444-2025-12-19)). Both points are covered in detail in the repo report `reports/Instagram Reels Ep01 audience strategy.md`.

**[SECONDARY]** On 30 April 2026, the originality rules were extended to photos and carousels. Accounts that mostly repost content they did not make stop being recommended to non-followers ([PetaPixel](https://petapixel.com/2026/04/30/new-instagram-policies-target-reposted-content/); [Tubefilter](https://tubefilter.com/2026/04/30/instagram-removes-algorithm-recommendations-repost-content-aggregator)).

### 1.3 Which metrics matter, and what each one should change in the next video [REC]

Read each metric only on like-for-like windows (48 h and 7 d), as `performance-analyst` already does. With fewer than 5 videos per language, every pattern is an anecdote (PROJECT_CONTEXT §15).

| Signal | Where | What it diagnoses | Change in the next video |
|---|---|---|---|
| Viewed vs swiped away (YT) / early drop in watch time (IG) | Studio Shorts analytics; IG Insights | The **opening frame and the first 1–2 seconds** | Open on the most striking chalk image already drawn, not a blank board. Speak the hook line in the first second. Put no title card before the hook. |
| Average % viewed / retention curve | Studio; `python -m pipeline retention-csv` → `yt-retention` | Where the story loses people | Map each drop to a scene using `chalk.plan` timings. Tighten or cut that scene. Keep 60–95 s unless retention supports longer. |
| Rewatches (APV above 100%, or a loop) | Studio | Whether the ending loops back into the opening | End on a line that answers or echoes the hook, so the replay feels natural. |
| Shares / sends | Studio; IG Insights (sends) | Whether the video gives viewers a reason to forward it | Use a "send this to the person who told you Ramayana stories" CTA. Add one surprising, verifiable fact with a verse citation. |
| Saves | IG Insights | Reference value | Show the shloka card with its book.chapter.verse citation. Add a "save for the next episode" line. |
| Comments | Both | Curiosity and disagreement | Ask a genuine question, not "comment Jai Shri Ram". Version disputes (Valmiki vs. Tulsidas vs. TV) give natural material for pinned comments. |
| Subscribers / follows per 1,000 engaged views | Studio; IG Insights | Whether the series is worth following | Use serial cliffhangers and a consistent "Ep N" title. Use the related-video link to the next episode. |
| Traffic source (Shorts feed vs. search vs. playlist) | Studio | Discovery path | A high search share means titles are working. A low playlist share means the series navigation is weak. |
| Audio language / geography | Studio | Which language versions find their audience | Feeds the split triggers in §2.5. |

**[VERIFIED]** The YouTube Analytics API may not return every Studio metric for Shorts (PROJECT_CONTEXT §21). Viewed-vs-swiped is read in Studio, by hand if necessary.

### 1.4 Series formats, playlists, links and pinned comments

- **[VERIFIED] Shorts "shows".** A playlist made only of Shorts (portrait or square, at most 180 s) can become a show.
  - A **serial** show lists episodes oldest to newest. Viewers who meet an episode in the feed get a "watch series" button that opens a dedicated series feed.
  - Shows "may be eligible to appear in search, under 'Recommended shows,' and under 'Continue watching'" ([help](https://support.google.com/youtube/answer/16590581?hl=en)).
  - Standard "official series" playlists need a verified account, and a video can belong to only one series playlist ([help](https://support.google.com/youtube/answer/6084043)).
  - **[REC]** Make **one serial show per language** ("Valmiki Ramayana · हिंदी", "… · English", and so on), not one mixed playlist. A mixed serial feed would play Hindi, then English, then Gujarati versions of the same episode in a row.
- **[VERIFIED] Related video on a Short.** You can add one clickable link, below the channel handle, to a video, Short or live stream from your own channel. It needs advanced-features access, and the target must be public or unlisted ([help](https://support.google.com/youtube/answer/14075157?hl=en)). Links in Shorts descriptions and comments are not clickable ([SECONDARY](https://searchenginejournal.com/youtube-adds-shorts-links-limits-links-elsewhere/495463)). The publishing API reportedly cannot set this field ([SECONDARY](https://help.opus.pro/docs/article/link-shorts-to-original-video)), which matches the manual step in PROJECT_CONTEXT §13.
  - **[REC]** Link each episode to the **previous episode in the same language** until the next one is live, then switch it to the next episode. Once compilations exist (§3.6), link to the language's long-form compilation.
- **[REC] Pinned comment.** Post one line in the video's language with the verse citation, a genuine question and "Ep N+1: <date>". YouTube pinned comments are manual. On Instagram, pin a comment in the app.
- **[REC] Opening frame.**
  - The first frame is what the "viewed vs swiped" decision is made on. It should already show a recognisable figure or object (bow, river, bird), with the hook as large captions.
  - Do not open with the series logo.
  - On Instagram, use a custom `cover_url` whose native-script title sits inside the central 3:4 area (see the repo report).
- **[REC] Titles and captions.**
  - On YouTube, put the subject in the first 40 characters. For Indic titles, use native script plus one romanized keyword. Lint every title with `yt-package/title.py` (already in `publishing-manager`).
  - On Instagram, the caption is a search document: a hook of 55 characters or less, story keywords, one romanized line and at most 5 hashtags (repo report).
- **[VERIFIED] Posting cadence.** YouTube says there is no minimum posting frequency. **[SECONDARY]** Mosseri recommends whatever cadence you can sustain.
  - **[REC]** Keep the current pattern of one episode per day per language only if QA and native review can keep up. A steady, predictable rhythm matters more than volume, and a missed G2 check is worse than a missed day.

### 1.5 Cross-platform repurposing without duplicate penalties

- **[VERIFIED] Instagram.** Recommended content must have no visible watermark. Near-duplicates are matched on "audio and visual signals", and only the original is recommended ([creators.instagram.com](https://creators.instagram.com/recommendations-and-originality)). The rules target content that is not yours, or that you have not substantially changed.
  - **[UNVERIFIED]** No official text covers cross-posting your own YouTube video to Instagram.
  - **[REC]** Always upload the **clean master render** (`content/<ID>/<lang>/<ID>-<lang>.mp4`). Never upload a downloaded Short, and never include a YouTube end card or logo.
- **[VERIFIED] YouTube.** The Shorts revenue page lists "reuploads and compilations with no original content added" as ineligible, along with unedited clips of others' films or TV ([help](https://support.google.com/youtube/answer/12504220?hl=en)). A YouTube Help Community post titled "Prioritizing original content on Shorts" (reported as 1 Oct 2026) concerns re-uploads from *other* creators. Its full text could not be read, so it is **[UNVERIFIED]**.
- **[REC] Four language versions with the same visuals.** Neither platform documents how it treats one creator posting dubbed versions of identical visuals.
  - On Instagram, a new voiceover is named as a substantial change, which helps.
  - On YouTube, there is no equivalent statement.
  - Mitigations already in the pipeline: each language is written originally, the shloka card and captions are in that language's script, and versions are spaced out in time.
  - Additional mitigation: vary at least the **opening frame and cover** per language. Also watch for the cannibalisation signature: one language gets normal reach while the others stall near zero across several episodes.

### 1.6 Localization levers on a single channel

- **[VERIFIED]** Translated titles and descriptions help viewers find videos in their language through search. Localized thumbnails exist for long-form videos ([multi-language audio help](https://support.google.com/youtube/answer/13338784?hl=en)).
- **[VERIFIED] Auto-dubbing** is "enabled by default for eligible creators". Supported Indian-language directions are:
  - English into Bengali, Hindi, Malayalam, Punjabi, Tamil and Telugu.
  - Hindi into Bengali and English.
  - Bengali, Telugu, Tamil, Punjabi and Malayalam into English only.
  - Gujarati, Marathi and Kannada are not listed ([help](https://support.google.com/youtube/answer/15569972?hl=en)).
  - The page does not say whether Shorts are dubbed.
  - **[REC]** Check Studio → Languages after every upload. Turn off or delete automatic dubs that compete with a native version you published separately; for example, an auto-Hindi dub of the English Short competes with your own Hindi Short. Keep auto-English dubs of the Telugu and Hindi versions only if the English version is not also on the channel.

---

## 2. Account strategy: one channel and one account, or one per language?

### 2.1 Verified platform facts

- **[VERIFIED] YouTube's three options** ([help](https://support.google.com/youtube/answer/6070467?hl=en)):

  | Option | YouTube's stated pros | YouTube's stated cons |
  |---|---|---|
  | One multilingual channel | "Consolidates your viewership and subscribers"; consistent branding; simpler management | Posts and comments "in many different languages… may be confusing for your audience" |
  | Separate language channels | "Focused communication"; viewers "less likely to get confused or disengaged" | Each channel "will need ongoing maintenance and attention" |
  | Global channel plus local channels | Consistent but localized | "Requires the most time and effort" |

- **[VERIFIED] Multi-language audio tracks.**
  - Available to creators with advanced-features access, on "a single video or Short".
  - You upload your own dub as an audio-only file of roughly the same length.
  - Analytics break down views and watch time by audio language.
  - YouTube says creators who added tracks saw "over 25% of watch time" come from non-primary languages ([help](https://support.google.com/youtube/answer/13338784?hl=en)). This is YouTube's aggregate claim, not a forecast for this channel.
- **[VERIFIED] Meta AI translations for Reels.**
  - Bengali, Tamil, Telugu, Kannada and Marathi were added to Hindi, English, Spanish and Portuguese. The rollout to everyone was announced on 16 Jan 2026.
  - It offers optional lip-sync and keeps the creator's own voice sound.
  - **Gujarati is not supported** ([Meta Newsroom](https://about.fb.com/news/2025/11/instagram-empowers-creators-to-go-global-with-local-voice-translations-and-fonts/)).
  - **[UNVERIFIED]** Instagram's eligibility rule conflicts across sources: "all public accounts" or "more than 1,000 followers" ([SECONDARY](https://9to5mac.com/2025/08/19/facebook-and-instagram-now-offer-ai-powered-dubbing-for-video-creators); [SECONDARY](https://www.socialmediatoday.com/news/instagram-reels-adds-more-ai-translations/825258/)).
- **[VERIFIED] Every threshold is per channel or account:**
  - YPP: 1,000 subscribers plus watch hours or Shorts views ([help](https://support.google.com/youtube/answer/72851?hl=en)).
  - The Feb 2027 Shorts revenue rule: 10M views per 90 days per channel ([blog](https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/)).
  - Instagram Gifts: 500 followers ([help](https://help.instagram.com/738469380549477)).

### 2.2 Trade-offs for this studio

| Factor | One channel / one account (current) | One per language |
|---|---|---|
| Progress toward thresholds | All four languages add to one count. **[VERIFIED]** that thresholds are per channel. | Each channel starts at zero and must qualify on its own. After Feb 2027, a new channel needs 8,000 hours or 20M Shorts views. |
| Subscriber overlap | Mostly *not* additive: a Gujarati viewer rarely wants the Telugu version. Subscribers see posts in languages they don't speak. **[REC]** | Every subscriber gets only their language. Cleaner signals per language. |
| Language recommendation | **[UNVERIFIED]** YouTube does not document whether mixed-language channels confuse its systems. Its help page lists viewer confusion as the con. | Clear language identity per channel. Regional mythology pages on Instagram typically run one handle per language (repo report). |
| Inauthentic-content review | One channel shows four near-identical visuals per episode. **[REC]** A reviewer may read this as "templated" or "interchangeable" (§3.4). | Each channel shows one version per episode, which reads as a normal series. |
| Workload | One Studio, one set of pinned comments and links, one AdSense link. | 4× the channel admin: banners, playlists, pinned comments, related links, community posts, Studio checks. One AdSense account can serve several channels ([SECONDARY](https://www.xflowpay.com/blog/get-paid-from-adsense-in-india)). |
| Brand | **[REC]** The YouTube channel ("Knowledge PowerBank") and Instagram ("Ramayana in Chalk \| Mr AKS") do not match. Fix this regardless of the split decision. | Per-language names such as "Ramayana in Chalk · हिंदी". |

### 2.3 What multi-language audio would change (an option to test, not to adopt yet)

**[REC]** A single upload carrying four audio tracks would consolidate views, comments and watch time on one video, which helps every per-channel threshold. It would also remove the four-copies issue. However, the current renders have **burned-in, word-synced captions and a native-script shloka card**, so a Telugu audio track would play under Hindi captions. Using audio tracks would require:
1. A language-neutral visual master with no burned-in narration captions, and a shloka card shown in Sanskrit/Devanagari only.
2. Per-language closed captions uploaded as subtitle tracks.
3. Every track matched to the same length. Current versions differ (Hindi runs longer with verse recitation), so scene timing would have to be shared.

This trades the approved caption style for consolidation. It is a style change, so under PROJECT_CONTEXT §15 it needs owner approval. **Test it on one episode at most**, as an unlisted experiment, before deciding.
- **[UNVERIFIED]** Whether Shorts with extra audio tracks are recommended to speakers of the secondary language as often as native uploads are.
- **[UNVERIFIED]** Whether Instagram has an equivalent multi-track feature for Reels. None was found; Meta's answer is AI translation.

### 2.4 Recommendation for the current stage

**[REC] Keep one YouTube channel and one Instagram account, organised by language.**
- **YouTube:**
  - Use one serial Shorts show per language and set the video language on every upload.
  - Translate each title and description into the other three languages, so search can match them.
  - Make channel sections per language.
  - Use per-language related-video chains.
  - Put community posts in English plus one Indic language, or rotate languages.
- **Instagram:**
  - Use language Highlights (EN · HI · GU · TE).
  - Keep the language of the first caption line matched to the audio.
  - Keep Meta AI translation off while native versions exist (repo report).
- **Rename the YouTube channel** to match the series brand (for example "Ramayana in Chalk"), with the handle kept or aliased. **[REC]** YouTube limits how often names and handles can change, so check the limit in Studio before renaming.

### 2.5 Triggers for splitting a language into its own channel or account [REC]

Split a language when **at least two** of these hold for **5 or more consecutive episodes** (medium confidence under PROJECT_CONTEXT §15), and only with owner approval:

1. **Self-sufficiency.** That language alone produces most of the channel's engaged views, or is clearly on course for the fan-funding tier by itself.
2. **Cannibalisation.** The other language versions of the same episode get much lower reach than their own history while this one is normal, or the reverse.
3. **Audience separation.** Studio geography and audio-language data show that the language's viewers barely overlap with the rest. For example, Telugu views come mostly from AP, Telangana and the US, while Hindi views come from north India and the Gulf.
4. **Comment confusion.** Viewers comment on language mismatch ("why is this in Gujarati?"), or the language's comments are a distinct community.
5. **Policy pressure.** A YPP reviewer or a monetization rejection cites repetitive, inauthentic or reused content.
6. **Capacity.** The team can sustain a separate channel's admin without delaying G2 review.

**Sequencing.**
- Do **not** split during the YPP application window. Apply with the consolidated channel first, because existing partners keep YPP status under the 2027 rules ([SECONDARY](https://www.searchenginejournal.com/youtube-updates-partner-program-terms-shorts-payout-rules/585331/)).
- After admission, a split-off language channel must requalify on its own, so split only a language that can stand alone.
- On Instagram, the first candidates are Gujarati and Telugu: Gujarati has no AI-translation fallback, and neither language had a competing Ramayana creator in the repo's niche research.

---

## 3. YouTube monetization in India

### 3.1 Eligibility tiers

| Tier | Today (until 31 Jan 2027) | From 1 Feb 2027 | Source |
|---|---|---|---|
| Fan funding and Shopping (expanded YPP) | 500 subscribers, 3 public uploads in the last 90 days, and 3,000 public watch hours in 12 months **or** 3M public Shorts views in 90 days | Unchanged | [SECONDARY, SEJ](https://www.searchenginejournal.com/youtube-updates-partner-program-terms-shorts-payout-rules/585331/); the blog says fan-funding thresholds "remain unchanged" ([VERIFIED](https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/)) |
| Ad revenue (full YPP), new applicants | 1,000 subscribers and 4,000 watch hours in 12 months **or** 10M Shorts views in 90 days | 1,000 subscribers and **8,000** watch hours in 365 days **or 20M** Shorts views in 90 days | [VERIFIED, help](https://support.google.com/youtube/answer/72851?hl=en); [VERIFIED, blog](https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/) |
| Shorts ad and Premium revenue share | Accept the Shorts Monetization Module | Also needs **10M qualified Shorts views in the past 90 days**, checked monthly. Below that, the channel stays in YPP and earns from long-form only. | [VERIFIED, blog](https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/) |
| Activity rule | n/a | Active means 1,000 watch hours per year, 1M Shorts views per 90 days, or 2 long-form or 5 Shorts uploads per 90 days | [SECONDARY, SEJ](https://www.searchenginejournal.com/youtube-updates-partner-program-terms-shorts-payout-rules/585331/) |
| Other requirements | Follow monetization policies; no active Community Guidelines strike; 2-Step Verification; advanced features; one linked AdSense for YouTube account; live in a YPP country | Existing partners must accept the new terms by **31 Jan 2027** | [VERIFIED](https://support.google.com/youtube/answer/72851?hl=en) |

- **Watch hours:** Shorts-feed hours do **not** count toward the watch-hour route ([VERIFIED](https://support.google.com/youtube/answer/72851?hl=en)).
- **India:** India is a YPP country. **[UNVERIFIED]** The expanded fan-funding tier is reported as available in India ([SECONDARY](https://vidiq.com/blog/post/youtube-relaxes-monetization-rules/)). YouTube's country list page could not be read. Check the "Earn" tab in Studio.

**[REC] Practical reading for this channel.**
- If the channel wants to join before 1 Feb 2027, it must meet the current thresholds by then. Plan around the 2027 thresholds, and do not chase the deadline with anything that risks the policy review (bought views, engagement bait).
- The 3,000-hour route to fan funding is easier to reach with **long-form compilations** than with Shorts alone (§3.6).

### 3.2 How Shorts revenue sharing works

**[VERIFIED]** ([help](https://support.google.com/youtube/answer/12504220?hl=en)):
1. Each month, per country, ad revenue from ads shown between Shorts is pooled.
2. For Shorts **without music**, all associated revenue goes into the Creator Pool. With one music track, half goes to the pool; with two tracks, one third. The rest pays for music licensing.
3. Each creator's allocation is their share of engaged views from monetizing creators' Shorts in that country.
4. **The creator keeps 45%** of their allocation, with or without music.
5. Ineligible: non-original Shorts, re-uploads and compilations with nothing original added, artificial views, views that conflict with the advertiser-friendly guidelines, and Shorts over one minute with claimed content (these are blocked).

**[VERIFIED]** Premium revenue share: 30% of net Premium (60% for Premium Lite) goes into the pool, and creators get 55% for long-form and 45% for Shorts ([blog](https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/)).

**[REC]** This studio generates its own tanpura and bansuri score and uses no partner music. If it stays that way, the full Creator Pool allocation applies (step 2). Never add a licensed trending track to a Short.

### 3.3 Advertiser-friendliness for a war epic

**[VERIFIED]** ([help](https://support.google.com/youtube/answer/6162278?hl=en)):
- Dramatized non-graphic violence earns full ads.
- "Dramatized violence that results in serious injury where the aftermath or impact is visible" earns limited ads.
- The guidelines have no dedicated section on religion. Disparaging a protected group (religion is one) earns no ads.

**[REC]** For Tataka, Khara-Dushana and the Lanka war, keep the chalk violence symbolic: no blood and no visible wounds, especially in the thumbnail and the first seconds. This matches the existing Instagram recommendation-guideline advice.

### 3.4 Inauthentic and reused content: the main risk for an AI-assisted studio

**[VERIFIED]** ([help](https://support.google.com/youtube/answer/1311392?hl=en)):
- Renamed from "repetitious content" to "inauthentic content" on **15 July 2025**.
- Not allowed:
  - "AI-generated content made with generic or unoriginal templates", especially when it gives "the impression of mass production without adding the creator's original, authentic insights or perspective".
  - "Image slideshows, templated storylines, or scrolling text with minimal or no narrative, commentary, or educational value".
  - Content where videos feel interchangeable.
- Allowed: the same intro and outro "but the bulk of your content is different". A series is fine when each video has a distinct storyline.
- Reused content: repurposing material from YouTube or other sources is not allowed without a meaningful difference. If YouTube cannot tell that you made the content, "monetization may be removed from your entire channel".
- The page does not mention text-to-speech.

**[SECONDARY]** Neal Mohan's January 2026 letter named managing "AI slop" as a 2026 priority ([Tubefilter](https://www.tubefilter.com/2026/01/21/neal-mohans-2026-letter-to-creators-a-lot-of-ai-a-tiktok-shop-competitor-and-beautifully-produced-tv-to-compete-with-netflix/); [Variety](https://au.variety.com/2026/digital/news/youtube-channels-using-ai-tools-reduce-slop-neal-mohan-letter-32190/)).

**[REC] Evidence of authenticity to build before applying:**
1. **Visible authorship.** Each script is original, researched and cited (book.chapter.verse). Add a recurring "what Valmiki actually says vs. what TV showed" beat. That is commentary and educational value, which the policy rewards.
2. **A distinct storyline per episode.** A serial epic is naturally non-interchangeable. Avoid reusing the same hook sentence pattern every time (the `storytelling` hook rubric already varies hooks).
3. **Not a slideshow.** The chalk stroke reveal, erase transitions and word-synced captions are animation, not a static slideshow. Keep scene counts and motion high, and never ship a static-image cut.
4. **The four-copies issue on one channel** is the hardest to argue. Writing each language originally, using a native shloka card and using different covers all help. If a YPP review is rejected for inauthentic or repetitive content, that is split trigger 5 in §2.5.
5. **Human review on record.** G1, G2 and G3 approvals, `qa.md` and `voice_qa.md` exist for every video. These are internal evidence. No source says YouTube asks for them, but they document the human process if an appeal is needed.
6. **About page and descriptions.** State the workflow honestly: "Written and researched by <brand>; illustrations and narration made with AI tools; every script checked against the Valmiki Ramayana." Do not imply hand-drawn art.

### 3.5 AI disclosure ("altered or synthetic content")

**[VERIFIED]** ([help](https://support.google.com/youtube/answer/14328491?hl=en)):
- Disclosure is required for realistic AI content.
- It is not required for clearly unrealistic or animated content; YouTube's example is "an AI-generated or altered animation of a missile in a fully animated video".
- It is not required for production help such as AI-assisted scripts, or for "cloning one's own voice" for dubs.
- For non-photorealistic or animated content and for non-music AI audio, the label appears in the **expanded description**, not on the player.
- Creators who consistently fail to disclose may face labels added by YouTube, content removal or **suspension from YPP**.
- The page does not address generic AI narration voices.

**[SECONDARY] India.** The IT (Intermediary Guidelines) Amendment Rules 2026 (notified 10 Feb 2026, in force 20 Feb 2026) require platforms to label "synthetically generated information": AI audio or visuals likely to be perceived as indistinguishable from a real person or event. Large platforms must obtain and verify user declarations. A further draft (April 2026) proposing a persistent on-screen label is **[UNVERIFIED]** as to whether it was notified ([MediaNama](https://www.medianama.com/2026/02/223-meity-amendments-it-rules-synthetic-media-deepfakes/); [DSCI](https://www.dsci.in/resource/content/it-amendment-rules-2026)).

**[REC]** Set YouTube's altered-or-synthetic flag to **Yes** for every episode (`synthetic: true` in `publish.json`), matching Instagram's `is_ai_generated=true`.
- The chalk visuals alone would not require it. A realistic TTS narrator is the borderline case, and the cost of disclosing is small: for this content the label sits in the expanded description.
- Under-disclosure risks YPP suspension; over-disclosure has no documented penalty. This is an owner decision, because it changes approved metadata.

### 3.6 Long-form compilations

- **[VERIFIED]** Long-form watch hours count toward YPP thresholds; Shorts-feed hours do not ([help](https://support.google.com/youtube/answer/72851?hl=en)). Compilations "edited together with little or no narrative" are reused content ([help](https://support.google.com/youtube/answer/1311392?hl=en)). That rule is written about clips from others. **[UNVERIFIED]** It is not documented how a channel's compilation of its *own* Shorts is treated.
- **[REC]** Publish **one long-form per Kanda section per language** (for example "Bala Kanda, part 1: episodes 1–8", 10–15 minutes) only when it adds real value:
  - a new spoken introduction and bridges between episodes;
  - chapters;
  - the full verses with explanation;
  - possibly a "behind the verse" segment.
  - Render it as 16:9, or as 9:16 with a designed frame.
  - Link each Short's related video to the compilation.
  - This is also the path to the 3,000-hour fan-funding route and the 8,000-hour ad route.
  - Keep "Made for Kids" set to **No**, and make content for the actual audience: the repo's audience research describes viewers as mostly men aged 18–34. Made-for-kids content loses personalized ads, comments and memberships ([SECONDARY](https://subscribr.ai/youtube-strategy/youtube-made-for-kids-monetization-rules)), and mislabelling is a COPPA risk.

### 3.7 AdSense, tax and payments (high level; not tax advice)

- **AdSense for YouTube.**
  - One AdSense account linked to the channel ([VERIFIED](https://support.google.com/youtube/answer/72851?hl=en)).
  - The payment threshold is **US$100**, with US$10 address verification ([VERIFIED](https://support.google.com/adsense/answer/1709871?hl=en)). The INR row is not in Google's table, so the Payments page shows the local figure.
  - **[SECONDARY]** Payments to India are by wire transfer, around the 21st–26th of the month ([Xflow](https://www.xflowpay.com/blog/get-paid-from-adsense-in-india)).
  - **[REC]** Use a brand email and the owner's legal name and address in AdSense, as the identity verification requires. Do not share these with any third-party service.
- **US withholding** ([VERIFIED](https://support.google.com/youtube/answer/10391362?hl=en)).
  - All YPP creators must submit US tax information in AdSense.
  - Individuals who submit nothing: **24% of total worldwide earnings** is withheld.
  - With valid tax info and a treaty claim, only **US-viewer earnings** are withheld, at the treaty rate. YouTube's own example lists **India at 15%**, against 30% without a treaty.
  - For an individual outside the US, this is normally Form W-8BEN; the page does not name the form, and the tool chooses it. Withholding covers US-viewer ads, Premium, Super Chat, Super Stickers, Super Thanks and memberships. Form 1042-S is issued by mid-April.
- **Indian GST** **[SECONDARY]** ([ClearTax](https://cleartax.in/s/gst-on-youtube-income); [TaxGuru](https://taxguru.in/goods-and-service-tax/gst-implications-youtuber-revenue.html)):
  - AdSense paid in foreign currency by Google entities abroad is generally treated as an **export of services**, which is zero-rated. Exporters usually file a **Letter of Undertaking (LUT)** to export without paying IGST.
  - Registration is required above ₹20 lakh aggregate turnover (₹10 lakh in special-category states), and export turnover counts toward that.
  - Domestic sponsorships carry 18% GST once registered.
  - Treatment of Indian viewers' Super Chats and memberships differs between sources.
  - **Check with a CA before registering.**
- **Indian income tax** **[SECONDARY]**:
  - Creator income is taxable business or professional income.
  - The ITR utility has a "social media influencer" profession code (16021) since AY 2024-25; which forms it applies to is disputed ([Taxscan](https://www.taxscan.in/top-stories/cbdt-introduces-new-itr-code-for-social-media-influencers-sparking-debate-among-tax-experts-1428531)).
  - Section 194R TDS applies to brand freebies and benefits above ₹20,000 a year from one payer ([exchange4media](https://www.exchange4media.com/influence-zone-news/influencers-now-have-a-dedicated-itr-code-heres-how-they-should-file-returns-146024.html)).
  - US tax withheld on US-viewer earnings may be creditable in India under the treaty. **[UNVERIFIED]** Ask a CA about Form 67 and the credit mechanics.

---

## 4. Instagram monetization in India

| Feature | Eligibility | India? | Evidence |
|---|---|---|---|
| **Gifts** (viewers send Stars on Reels) | Professional account, 18+, **500 followers**, a payout account set up. Not for collab posts or children-focused accounts. | India is on the supported-country list | [VERIFIED, help](https://help.instagram.com/738469380549477) (page metadata is old, so re-check in the Professional Dashboard) |
| **Subscriptions** | **[SECONDARY]** 10,000 followers, 18+, professional account | India listed in the 20 Sep 2023 update | [VERIFIED, creators blog](https://creators.instagram.com/blog/bringing-subscriptions-to-more-creators-on-instagram); threshold via [SECONDARY](https://www.kudozz.in/blog/instagram-creator-monetization) |
| **Creator Marketplace** (brands find creators; partnership ads) | Invitation and eligibility in the dashboard | Expanded to India in Feb 2024 | [SECONDARY, Business Today](https://businesstoday.in/technology/news/story/instagrams-creator-marketplace-comes-to-india-other-new-markets-platform-tests-smarter-recommendations-418623-2024-02-22); [afaqs](https://www.afaqs.com/news/social-media/instagram-creator-marketplace-launches-in-india) |
| **Branded content tools** (paid-partnership label, partnership ads) | Professional account; must follow the Branded Content Policies | Available | **[UNVERIFIED]** The help pages could not be read on the research date. In India, ASCI disclosure rules apply anyway (§5.1). |
| **Reels bonuses / ads on Reels** | Invite-only where offered | **[UNVERIFIED]** Sources conflict on whether any Reels bonus runs in India in 2026 | [SECONDARY, conflicting](https://www.lilachbullock.com/how-much-does-instagram-pay-for-reels-views-in-india/) |
| **Meta Verified** | Paid subscription | n/a | Excluded by the zero-cost rule |

**[REC]** Gifts at 500 followers is the first Instagram revenue tool. Set up the payout account as soon as the account becomes eligible. Brand deals through the Creator Marketplace come later and depend on visible engagement. Do not plan around bonuses.

---

## 5. Other revenue

### 5.1 Sponsorships: devotional, publishing and education brands

- **Fit [REC].** Book publishers (Ramayana translations and retellings), devotional and puja brands, Sanskrit and education apps, spiritual tourism, and kids-learning brands (careful: the audience is adult).
- **Disclosure [VERIFIED/SECONDARY].**
  - ASCI's influencer guidelines require upfront, prominent disclosure of material connections ([ASCI PDF](https://www.ascionline.in/social/wp-content/uploads/2025/04/ASCI-Influencer-Guidelines.pdf)).
  - Virtual influencers must also disclose that they are not real people.
  - A 2026 ASCI draft on AI labelling in ads, which closed for comments on 13 June 2026, is **[UNVERIFIED]** as to final status ([ASCI draft](https://www.ascionline.in/wp-content/uploads/2026/05/AI-Draft-Guidelines-1.pdf)).
  - Use YouTube's "includes paid promotion" checkbox and Instagram's paid-partnership label.
- **Tax.** 18% GST on domestic sponsorship once registered, and 194R TDS on products in kind (§3.7).
- **[REC] Guardrails.**
  - No sponsor inside the story narration.
  - Sponsor segments go at the end, or in the description and pinned comment.
  - No astrology or "miracle" product claims attached to scripture.
  - Never alter the story for a sponsor.

### 5.2 Affiliate links: books

- **[VERIFIED] Amazon Associates India:** Books earn **4.72%**; **Kindle e-books earn nothing** ([fee schedule](https://affiliate-program.amazon.in/help/node/topic/GRXPHT8U84RAYDXZ)).
  - **[UNVERIFIED]** The qualifying-sales window for new associates, the payout minimum and the cookie window: sources conflict, so read the Operating Agreement.
  - Links are not clickable in Shorts descriptions. They work in long-form descriptions and Instagram link-in-bio.
- **[SECONDARY] YouTube Shopping affiliate in India.**
  - Launched in Oct 2024 with Flipkart and Myntra. Nykaa and Purplle were announced in Oct 2025 ([Google India blog](https://blog.google/intl/en-in/products/platforms/fueling-the-next-era-of-creator-led-shopping-experiences-in-india/)).
  - The launch-era requirement was YPP plus 10,000 subscribers ([YourStory](https://yourstory.com/2024/10/youtube-expands-shopping-programme-india)). A reported 2026 cut to 500 subscribers and an Amazon partnership are **[UNVERIFIED]** ([exchange4media](https://www.exchange4media.com/digital-news/youtube-wants-a-share-of-indias-shopping-carts-will-ad-budgets-follow-159258.html)).
  - Product tags work on Shorts.
- **[REC] What to recommend.** A short, honest list: critical-edition translations (for example Bibek Debroy's Valmiki Ramayana, Penguin) and regional classics in each language. Only list books the owner can vouch for.

### 5.3 Digital products: e-books and prints of the art

- **[VERIFIED/SECONDARY] Copyright in AI images.**
  - **US:** human authorship is required. The Supreme Court denied certiorari in *Thaler v. Perlmutter* on 2 March 2026 ([Mayer Brown](https://www.mayerbrown.com/en/insights/publications/2026/03/supreme-court-denies-review-in-ai-authorship-case)). The Copyright Office's Part 2 report (29 Jan 2025) covers AI outputs ([copyright.gov](https://www.copyright.gov/ai/)). Prompts alone generally do not make the user an author; human selection, arrangement and modification can be protected.
  - **India:** the author of a computer-generated work is "the person who causes the work to be created" (s.2(d)(vi)). In Sept 2026 the Copyright Office accepted an AI work as original but refused to list the AI (DABUS) as author ([MediaNama](https://www.medianama.com/2026/09/223-ai-art-copyright-india-author-dabus/)). DPIIT's working paper Part 1 (Dec 2025) is about training data ([DPIIT PDF](https://www.dpiit.gov.in/static/uploads/2025/12/ff266bbeed10c48e3479c941484f3525.pdf)). Part 2, on outputs, was not published as of Sept 2026.
- **[REC]** The defensible assets are the **scripts, translations into each language, verse explanations, arrangement and series design**, which are human-written. Raw single AI frames may have thin or no protection, so others may copy them.
  - Sell bundles where the human contribution dominates: an illustrated e-book of the scripts with verse notes, or a printable "Kanda map".
  - Do not market prints of individual frames as exclusive art.
  - Z-Image Turbo (Apache-2.0) permits commercial use of outputs (PROJECT_CONTEXT §6).
  - Payment rails need GST and income-tax treatment (§3.7).

### 5.4 Licensing to schools and ed-tech

**[REC]**
- Offer **non-exclusive** licences of language-specific episodes or compilations to schools, Sanskrit or value-education programmes and ed-tech apps.
- Requirements:
  - a clean chain of rights (all model licences commercial, fonts licensed; see §5.7);
  - a note on the AI process;
  - age-appropriate cuts (symbolic violence).
- No public pricing data was found, so this is a negotiation, not a forecast. It works best after the series has visible traction and a complete Kanda.

### 5.5 Memberships and Patreon

- **YouTube memberships and Super Thanks** become available at the fan-funding tier (§3.1). They keep fans on-platform and make no extra demands on content.
- **[SECONDARY] Patreon** pays out to India (Payoneer or PayPal) and needs a W-8BEN ([Karbon](https://www.karboncard.com/blog/patreon-india-payouts-paypal-payoneer)).
- **[REC]** Use one platform only, and start with YouTube memberships because they need no extra infrastructure.
  - Member perks that cost little: early access to the next episode, verse-by-verse notes, and polls on which episode to make next.
  - Never put core story episodes behind the paywall.

### 5.6 What to monetize first [REC]

1. **Now (0 revenue):** fix the compliance hygiene in §5.7, build the series navigation (§1.4), and set up compilations (§3.6).
2. **First money:** Instagram Gifts (500 followers), then YouTube Super Thanks and memberships (expanded tier). Add Amazon book links in long-form descriptions and link-in-bio when there is a reason to recommend a book.
3. **Next:** small sponsorships from aligned publishers or education brands, then YouTube Shopping if eligible.
4. **Later:** YouTube ad revenue (full YPP), the e-book and licensing.
5. **Only at scale:** Shorts ad revenue (10M Shorts views per 90 days from Feb 2027).

### 5.7 Mistakes that block monetization (checklist)

| Mistake | Why it blocks | Status here |
|---|---|---|
| Copyrighted music or trending tracks | Content ID claims. Shorts over 1 minute with claimed content are blocked from monetization ([VERIFIED](https://support.google.com/youtube/answer/12504220?hl=en)). | OK: score generated in-house |
| TV-serial clips (for example Ramanand Sagar's *Ramayan*), film stills, others' artwork | Copyright strikes and reused content ([VERIFIED](https://support.google.com/youtube/answer/1311392?hl=en)) | OK: never use them |
| Modern translations quoted at length | Translations are copyrighted, while the Sanskrit original is not. **[REC]** Quote Sanskrit and write your own explanation. Cite translations, don't copy them. | Keep current practice |
| **Unlicensed fonts** | macOS fonts are licensed to "display and print content" on the Mac. Commercial video use is not clearly covered ([SECONDARY](https://discussions.apple.com/thread/7493969); older SLA text [apple.com](https://www.apple.com/legal/sla/docs/macosx1072.pdf)). | **Risk:** Chalkduster, Chalkboard SE, Kohinoor, ITF Devanagari and Sangam MN are used. **[REC]** Move to SIL-OFL fonts (Noto Sans/Serif Devanagari, Gujarati and Telugu; an OFL chalk or hand-drawn display face) before YPP or any licensing. This changes the approved look, so it needs owner approval and a side-by-side check. |
| Non-commercial model licences | FLUX-dev, MusicGen (CC-BY-NC), IndicF5 and macOS `say` voices taint commercial use | OK: already excluded (PROJECT_CONTEXT §6). Check the licence of any future model or voice before use. |
| Undisclosed realistic synthetic media | YouTube: labels, removal or YPP suspension ([VERIFIED](https://support.google.com/youtube/answer/14328491?hl=en)). Meta: penalties for non-disclosure. India: platform labelling duty. | **Fix:** set `synthetic: true` (§3.5) |
| Template or slideshow feel, interchangeable videos | Inauthentic content: channel-wide demonetization possible | Mitigate per §3.4 |
| Wrong "Made for Kids" setting | Lost features or ads; COPPA exposure | Set "No" honestly (§3.6) |
| Engagement bait, bought views or subscribers, sub-for-sub | Artificial views are ineligible; risk to Community Guidelines | Never |
| Graphic violence in thumbnails or the first seconds | Limited or no ads ([VERIFIED](https://support.google.com/youtube/answer/6162278?hl=en)) | Keep chalk violence symbolic |
| Deity-depiction controversy | Not a platform rule, but complaints and FIRs in India (repo report: BNS s.299 context) | Keep the chalk stylisation and iconographic review at G2 |

---

## 6. Multilingual strategy

### 6.1 Audience size by language (first-language speakers, Census 2011)

The figures below are those recorded in `profiles/languages/*.json` from Census of India 2011, Paper 1 of 2018. They are the most recent official language data and are 15 years old. **No official YouTube or Instagram user counts by language exist [VERIFIED absence: no figures found].**

| Lang | Speakers (India, L1) | Meta AI Reel translation | YouTube auto-dub | Regional Ramayana anchor |
|---|---|---|---|---|
| hi | ~528 M | Yes | en→hi, hi→en/bn | Tulsidas's *Ramcharitmanas* (Awadhi, 16th c.); Ramanand Sagar's TV *Ramayan* (1987) |
| bn | ~97 M (plus Bangladesh) | Yes | en→bn, hi→bn, bn→en | *Krittivasi Ramayan*, Krittibas Ojha (15th c.) |
| mr | ~83 M | Yes | Not listed | Sant Eknath's *Bhavartha Ramayana* (16th c.); *Geet Ramayan* (1955–56, verify) |
| te | ~81 M | Yes | en→te, te→en | *Sri Ranganatha Ramayanam*, Gona Budda Reddy (c. 1300–1310); *Molla Ramayanamu* |
| ta | ~69 M (plus diaspora) | Yes | en→ta, ta→en | Kamban's *Kambaramayanam* (12th c.) |
| gu | ~55 M (plus UK, US and East African diaspora) | **No** | Not listed | *Giradhara Ramayana*, Giradhara (18th c. per Wikipedia; the profile says 19th c., so verify); Premanand Swami's *Tulsi-Krta Ramayana* (17th c.) |
| kn | ~44 M | Yes | Not listed | Kumara-Valmiki's *Torave Ramayana* (16th c.); Kuvempu's *Sri Ramayana Darshanam* (1949/1957; Jnanpith) |
| ml | ~35 M | No | en→ml, ml→en | Thunchaththu Ezhuthachan's *Adhyathmaramayanam Kilippattu* (16th c.); Karkidakam "Ramayana masam" (Jul–Aug) |
| pa | ~33 M | No | en→pa, pa→en | *Ram Avtar* in the Dasam Granth (Braj, completed 1698 CE; authorship debated) ([SECONDARY, SikhiWiki](https://www.sikhiwiki.org/index.php/Ram_Avtar)); Valmiki Tirath, Amritsar (verify) |
| en | ~0.26 M L1 / ~129 M total speakers | Yes | Source | Valmiki in translation |

Sources: translation languages from [Meta Newsroom](https://about.fb.com/news/2025/11/instagram-empowers-creators-to-go-global-with-local-voice-translations-and-fonts/); dubbing directions from [YouTube help](https://support.google.com/youtube/answer/15569972?hl=en); regional versions from [Wikipedia: Versions of the Ramayana](https://en.wikipedia.org/wiki/Versions_of_the_Ramayana) (secondary; check each against a scholarly source before citing it on screen) and [Wikipedia: Sri Ramayana Darshanam](https://en.wikipedia.org/wiki/Sri_Ramayana_Darshanam).

**[SECONDARY] Market context:**
- IAMAI–Kantar reported 886 M active internet users in 2024, with 98% accessing content in Indic languages, and named Tamil, Telugu and Malayalam among the most popular ([Business Today](https://www.businesstoday.in/amp/technology/news/story/indias-internet-revolution-key-insights-from-kantar-and-iamai-report-461043-2025-01-16)).
- YouTube's India Impact Report 2025 says over 15% of watch time on Indian channels comes from outside India ([Business Today](https://www.businesstoday.in/jobs/story/youtubes-india-creator-ecosystem-generates-9-6-lakh-jobs-rs18000-crore-economic-value-report-558620-2026-09-29)).
- YouTube says 77% of Gen Z in India watched creators in translated formats ([Social Samosa](https://www.socialsamosa.com/industry-updates/77gen-z-india-watched-dubbed-content-10892203)).

**[UNVERIFIED] Competition for mythology content by language.** No public dataset measures it. **[REC]** Measure it with the repo's own tools rather than guess: `python -m pipeline research <ID> --langs …` gives YouTube search competition and Wikipedia pageviews per language. Record the results in each profile's evidence before choosing a language.

### 6.2 Rollout order without making ten versions of everything [REC]

- **Tier A (always): English and Hindi.** Largest reach. English serves urban and diaspora viewers; Hindi is the largest Indic pool.
- **Tier B (current test): Gujarati and Telugu.** Keep both for at least 5 more episodes, then decide on evidence (per-language engaged views, viewed-vs-swiped, sends and follows per 1,000 views). Gujarati has no Meta translation, so a native version is its only route to Gujarati-language discovery. Telugu has a large, young US diaspora (repo report).
- **Tier C (next candidates, one at a time): Tamil, then Marathi or Bengali.** Choose by the measured competition gap and by voice QA.
  - Tamil and Bengali have both Meta translation and YouTube dubbing tools, so viewers already see machine versions. A native version needs to be clearly better to matter.
  - Marathi has Meta translation but no YouTube auto-dub, so a native version faces less machine competition on YouTube.
- **Tier D (only after a split): Kannada, Malayalam and Punjabi.** Malayalam's Karkidakam window (Jul–Aug) is a natural one-off launch moment.
- **Scaling rule.** Add a language only when:
  1. A voice passes `speaker_consistency` QA, and a native speaker approves pronunciation. PROJECT_CONTEXT §6 lists Maya 2 as covering 11 Indian languages plus English; this is untested for the new languages.
  2. A native reviewer is available for G1 and G2.
  3. The language has a regional-tradition brief (§6.4).
  4. The team can absorb one more version per episode without slipping G2 review.
- **Not everything needs every language.** Make Tier C and D languages **"season-only"** versions: one Kanda arc or the 10 strongest episodes, chosen from Tier A and B performance. Do not make every episode in every language.

### 6.3 Original writing vs. translation [REC]

- Keep the house rule: every version is **written originally** from an audience brief, not machine-translated (PROJECT_CONTEXT §10). This serves quality, and it also produces the material differences that help on originality and inauthentic-content review.
- A translation-assisted draft is acceptable as a starting point for Tier C and D only if a native writer rewrites it and the hooks are scored freshly in that language.
- Sanskrit verses stay in Sanskrit, written in the language's own script, followed by a natural explanation (already implemented).

### 6.4 Dialect, pronunciation and cultural adaptation per language [REC]

| Lang | Register and pronunciation | Cultural adaptation |
|---|---|---|
| hi | Standard Hindi with natural tatsama words where Valmiki's names need them. Avoid heavy Sanskritisation. Watch ज्ञ/ग्य (QA already normalises). | Many viewers know the *Manas* and TV versions. Mark Valmiki-vs-Tulsidas differences explicitly; this is a strong comment driver. |
| gu | Standard Gujarati with Gujarat-neutral vocabulary. Diaspora viewers may read Gujarati poorly, so the romanized caption line matters. | Name Gujarati poet traditions sparingly. The diaspora watches at different hours (repo report). |
| te | Standard Telugu that works for both Andhra and Telangana audiences. Respectful verb forms for divine characters. | Ranganatha and Molla versions are well known. Avoid presenting Valmiki as "the only correct" version. |
| ta | Formal-but-spoken Tamil. Careful transliteration of Sanskrit names (Tamil script has fewer aspirates). | Kamban is the cultural reference and differs from Valmiki in places; say "in Valmiki's version". **[REC/UNVERIFIED]** The Ramayana has been read critically within Tamil Nadu's Dravidian movement, so expect debate and keep framing scholarly, not devotional-only. Get a native reviewer's view before launch. |
| bn | Standard Bengali (Kolkata). Decide whether to count Bangladesh viewers as an audience for devotional framing. | Krittivasi episodes (for example the Ahiravan/Mahiravan story) are not in Valmiki. Label them if you mention them. Durga Puja's link to Rama's *akal bodhan* is a Krittivasi tradition, so date such content carefully. |
| mr | Standard Marathi (Pune/Mumbai). | *Geet Ramayan* is a cultural landmark. Never use its songs (copyright), but a verbal reference is fine. Eknath's *Bhavartha* is the classical anchor. |
| kn | Standard Kannada. | Kuvempu's modern epic is a Jnanpith work, so refer to it but do not quote it (in copyright). |
| ml | Standard Malayalam. | Ezhuthachan's *Kilippattu* is read daily in Karkidakam, which gives a seasonal tie-in. |
| pa | Gurmukhi script. Consider bilingual Hindi/Punjabi framing. | Sikh, Valmiki-community and Hindu traditions all relate to the epic differently. Get community-sensitive review before any Punjabi launch. |

Every row above needs a native-speaker review. The `audience-localizer` agent owns these profiles, and all eight non-en/hi profiles are still drafts.

---

## 7. Phased roadmap

No timelines are attached to revenue, because none can be forecast honestly. Phases advance on **platform thresholds and evidence**, not dates.

### Phase 0: Hygiene (now, before more scale)
- Set `synthetic: true` on YouTube (owner decision, §3.5).
- Set Made for Kids to No on the channel and every video.
- Decide on the font licence: switch to OFL fonts, or get written confirmation that the current fonts are licensed for commercial video (§5.7).
- Align the brand: rename the YouTube channel to match the series (§2.4).
- Create one serial Shorts show per language, and add title and description translations.
- Review auto-dubbing in Studio (§1.6).
- Rewrite the About page and descriptions with an honest workflow statement (§3.4).

### Phase 1: Build the series and the data (from 0 to the fan-funding thresholds)
- Keep posting on a sustainable cadence. Read the §1.3 metrics at 48 h and 7 d, and change one variable per episode.
- Start long-form Kanda compilations per language (§3.6).
- Reach 500 Instagram followers, then enable **Gifts**.
- After 5 or more episodes per language, decide whether Gujarati and Telugu continue, stop, or split (§2.5).

### Phase 2: Fan funding (500 subscribers, 3 uploads per 90 days, and 3,000 hours or 3M Shorts views per 90 days)
- Apply for the expanded YPP. Turn on **Super Thanks** and **memberships** with low-cost perks.
- Submit US tax info (W-8BEN treaty claim) in AdSense. Talk to a CA about GST (LUT) and the ITR.
- Add Amazon.in book links in long-form descriptions and link-in-bio. Check YouTube Shopping eligibility.

### Phase 3: Brand and sponsorship
- With visible engagement, pitch publishers and education brands. Use ASCI-compliant disclosure, the paid-promotion flag and GST invoices.
- Join or respond in Instagram's Creator Marketplace if invited.

### Phase 4: Ad revenue (1,000 subscribers and 8,000 hours or 20M Shorts views per 90 days for applications from 1 Feb 2027)
- Apply with the consolidated channel. Accept the new terms.
- Shorts ad share only in months with 10M or more Shorts views per 90 days. Long-form compilations earn regardless.

### Phase 5: Scale out
- Split a language channel or account when the §2.5 triggers hold.
- Add Tier C languages as season-only versions (§6.2).
- Offer the illustrated script e-book and non-exclusive school and ed-tech licences (§5.3–5.4).

---

## 8. Open items to verify before acting

1. The expanded-YPP country list includes India: check the Studio "Earn" tab.
2. The Feb 2027 YPP terms: read them in Studio, and confirm the activity rules quoted by SEJ.
3. Whether Shorts are auto-dubbed, and whether multi-audio Shorts are recommended to secondary-language viewers.
4. Instagram's AI-translation eligibility (public accounts vs. more than 1,000 followers) and the Subscriptions threshold.
5. Instagram Reels bonus status in India: check the Professional Dashboard.
6. Amazon Associates India: new-associate qualifying-sales rule, payout minimum and disclosure text, from the Operating Agreement.
7. YouTube Shopping affiliate eligibility in India: the reported 500-subscriber change.
8. The macOS font licence (current Tahoe SLA text) for commercial video.
9. Whether MeitY's April 2026 persistent-label draft was notified, and ASCI's final AI-labelling guideline.
10. The full text of the 1 Oct 2026 "Prioritizing original content on Shorts" post.
11. Regional-tradition details marked "verify" in §6 (Giradhara date, Geet Ramayan, Valmiki Tirath, Punjabi traditions): check with native reviewers or scholarly sources.

---

## 9. Source list (accessed 2026-11-16)

**Official: YouTube and Google**
- YPP overview and eligibility: https://support.google.com/youtube/answer/72851
- YPP 2027 changes (blog, 10 Aug 2026): https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/
- Shorts monetization policies and revenue sharing: https://support.google.com/youtube/answer/12504220
- Channel monetization policies (inauthentic and reused content): https://support.google.com/youtube/answer/1311392
- Altered or synthetic content disclosure: https://support.google.com/youtube/answer/14328491
- Advertiser-friendly content guidelines: https://support.google.com/youtube/answer/6162278
- Multi-language audio: https://support.google.com/youtube/answer/13338784
- Automatic dubbing: https://support.google.com/youtube/answer/15569972
- Global audience strategies: https://support.google.com/youtube/answer/6070467
- Shorts search and discovery tips: https://support.google.com/youtube/answer/11914225
- Content performance metrics: https://support.google.com/youtube/answer/12220281
- Shows from Shorts: https://support.google.com/youtube/answer/16590581
- Series playlists: https://support.google.com/youtube/answer/6084043
- Related video on Shorts: https://support.google.com/youtube/answer/14075157
- Engaged views (blog, 19 Aug 2026): https://blog.youtube/inside-youtube/engaged-views-youtube-explained/
- US tax for creators: https://support.google.com/youtube/answer/10391362
- AdSense payment thresholds: https://support.google.com/adsense/answer/1709871
- Google India Shopping blog (10 Oct 2025): https://blog.google/intl/en-in/products/platforms/fueling-the-next-era-of-creator-led-shopping-experiences-in-india/

**Official: Instagram and Meta**
- Recommendations and originality: https://creators.instagram.com/recommendations-and-originality
- Gifts eligibility: https://help.instagram.com/738469380549477
- Subscriptions expansion (2023): https://creators.instagram.com/blog/bringing-subscriptions-to-more-creators-on-instagram
- Meta AI translations, Indian languages (Nov 2025 / Jan 2026): https://about.fb.com/news/2025/11/instagram-empowers-creators-to-go-global-with-local-voice-translations-and-fonts/
- Meta AI content labelling: https://transparency.meta.com/governance/tracking-impact/labeling-ai-content

**Official: other**
- Amazon Associates India fee schedule: https://affiliate-program.amazon.in/help/node/topic/GRXPHT8U84RAYDXZ
- US Copyright Office AI: https://www.copyright.gov/ai/
- DPIIT working paper on generative AI and copyright, Part 1: https://www.dpiit.gov.in/static/uploads/2025/12/ff266bbeed10c48e3479c941484f3525.pdf
- ASCI influencer guidelines: https://www.ascionline.in/social/wp-content/uploads/2025/04/ASCI-Influencer-Guidelines.pdf
- ASCI AI labelling draft (2026): https://www.ascionline.in/wp-content/uploads/2026/05/AI-Draft-Guidelines-1.pdf

**Secondary (credible press, law firms, trade media)**
- SEJ on YPP terms: https://www.searchenginejournal.com/youtube-updates-partner-program-terms-shorts-payout-rules/585331/
- Tubefilter on the Shorts view count change: https://www.tubefilter.com/2025/03/26/youtube-shorts-views-counting-stats/
- OutlierKit on Creator Insider quotes: https://outlierkit.com/resources/youtube-shorts-algorithm/
- Tubefilter and Variety on Mohan's 2026 letter: https://www.tubefilter.com/2026/01/21/neal-mohans-2026-letter-to-creators-a-lot-of-ai-a-tiktok-shop-competitor-and-beautifully-produced-tv-to-compete-with-netflix/ ; https://au.variety.com/2026/digital/news/youtube-channels-using-ai-tools-reduce-slop-neal-mohan-letter-32190/
- PetaPixel and Tubefilter on the Instagram originality expansion (30 Apr 2026): https://petapixel.com/2026/04/30/new-instagram-policies-target-reposted-content/ ; https://tubefilter.com/2026/04/30/instagram-removes-algorithm-recommendations-repost-content-aggregator
- Buffer on Instagram ranking signals: https://buffer.com/resources/instagram-algorithms/
- Business Today on the 5-hashtag cap: https://www.businesstoday.in/technology/news/story/no-more-hashtag-stuffing-instagram-limits-hashtag-usage-to-just-5-per-reel-and-post-507444-2025-12-19
- Creator Marketplace in India: https://businesstoday.in/technology/news/story/instagrams-creator-marketplace-comes-to-india-other-new-markets-platform-tests-smarter-recommendations-418623-2024-02-22
- MediaNama on the IT Rules 2026: https://www.medianama.com/2026/02/223-meity-amendments-it-rules-synthetic-media-deepfakes/
- MediaNama on AI art copyright in India (Sept 2026): https://www.medianama.com/2026/09/223-ai-art-copyright-india-author-dabus/
- Mayer Brown on Thaler cert denial: https://www.mayerbrown.com/en/insights/publications/2026/03/supreme-court-denies-review-in-ai-authorship-case
- ClearTax and TaxGuru on GST for YouTube income: https://cleartax.in/s/gst-on-youtube-income ; https://taxguru.in/goods-and-service-tax/gst-implications-youtuber-revenue.html
- Taxscan on the influencer ITR code: https://www.taxscan.in/top-stories/cbdt-introduces-new-itr-code-for-social-media-influencers-sparking-debate-among-tax-experts-1428531
- YourStory on YouTube Shopping in India: https://yourstory.com/2024/10/youtube-expands-shopping-programme-india
- IAMAI–Kantar via Business Today: https://www.businesstoday.in/amp/technology/news/story/indias-internet-revolution-key-insights-from-kantar-and-iamai-report-461043-2025-01-16
- Wikipedia, Versions of the Ramayana: https://en.wikipedia.org/wiki/Versions_of_the_Ramayana
- Apple Community thread on macOS fonts in commercial video: https://discussions.apple.com/thread/7493969
