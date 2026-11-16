# Reach drivers and content policies for a new, faceless Instagram account cross-posting AI-assisted Reels (status as of Nov 2026)

Context: @mr.aks.tale is new and faceless. It posts chalkboard-art Reels of the Valmiki Ramayana in EN, HI, GU and TE. Images come from a local AI model and narration is synthetic TTS. Each video goes to YouTube Shorts first, then to Instagram through the Content Publishing API.
Labels used below: **[OFFICIAL]** means Instagram or Meta said it, in its own pages or as reported by reputable press. **[INDUSTRY]** means third-party opinion or data. **[PRE-2024]** marks a source older than 2024.

## 1. Ranking signals for showing Reels to non-followers

### Takeaway
In January 2025 Mosseri named the top three signals: watch time, likes per reach and sends per reach. He said sends per reach weigh slightly more for reach to people who don't follow you. Since April 2024, Reels are first shown to a small test audience that includes non-followers, and the audience grows if the Reel performs well, so small accounts are not shut out. Instagram treats the first ~3 seconds as the hook. Reels over 3 minutes are reportedly not recommended to new audiences. Instagram has given no official posting-frequency number.

### Cited Findings
- [OFFICIAL, Jan 2025] Mosseri said "the top three signals" for ranking are watch time, likes and sends. He pointed creators to average watch time, likes per reach and sends per reach in Insights. He said likes matter slightly more for connected (follower) reach and sends matter slightly more for unconnected (non-follower) reach. Reported by — [Kompozy](https://kompozy.io/news/instagram-mosseri-ranking-signals-guidance); [Buffer](https://buffer.com/resources/instagram-algorithms/); [ZoomSphere](https://www.zoomsphere.com/blog/instagram-algorithm-2026-what-actually-gets-reach)
- [INDUSTRY] Claims that sends are worth "3–5x more than likes" or that watch time is "the single most important factor" have no primary Mosseri quote behind them, so do not repeat them as fact — [SocialDay (makes the claim)](https://socialday.live/features/instagrams-dm-share-signal-now-drives-3-to-5-times-more-reach-than-likes); [WebSearch synthesis of Buffer / PostEverywhere](https://posteverywhere.ai/blog/how-the-instagram-algorithm-works)
- [INDUSTRY, Apr 2026] Instagram reportedly added "share rate" to Insights in April 2026. This is the closest built-in measure of sends per reach — [Keywords Everywhere update tracker](https://keywordseverywhere.com/news/instagram-algorithm-updates/) (secondary; not verified against an Instagram post)
- [OFFICIAL, 30 Apr 2024] Reels recommendations moved to a new system. Earlier ranking leaned on follower engagement, which favoured large accounts. Now "content can reach a small audience, including non-followers, and expands to larger audiences if it performs well" (paraphrased from the page) — [Instagram Creators: Recommendations & Originality](https://creators.instagram.com/recommendations-and-originality)
- [OFFICIAL, early 2025, as reported] Mosseri: "The first three seconds of a reel are super important… we call this the hook." Reports also say Instagram's models predict how likely a viewer is to watch less than three seconds — [Inman, 7 Mar 2025](https://www.inman.com/2025/03/07/head-of-instagram-reveals-secrets-to-social-media-success/)
- [OFFICIAL, as reported] Mosseri's checklist says a Reel should include sound, whether a popular song, a voiceover or original audio — [Inman](https://www.inman.com/2025/03/07/head-of-instagram-reveals-secrets-to-social-media-success/)
- [OFFICIAL via secondary, 2025] Instagram allows Reels up to 20 minutes. Secondary sources quote Help Center guidance that "Reels over 3 minutes won't be recommended to new audiences" — [Exemplary/aggregated in search](https://exemplary.ai/blog/instagram-trial-reels); [Dataslayer](https://www.dataslayer.ai/blog/instagram-algorithm-2025-complete-guide-for-marketers) (not verified on help.instagram.com directly)
- [Posting frequency] I found no official Mosseri number. Secondary summaries say he advised a frequency you can sustain and gave no figure — [Bazzaal summary](https://www.bazzaal.com/blog/instagram-algorithm-2026-mosseri)

### Inferences
- Our Reels run 60–90 s, well under the 3-minute limit. The first chalk stroke or line of narration has to work as a hook in under 3 s.
- Sends per reach (DM shares) is the key metric for non-follower reach. Mythology "did you know" endings that people want to send to family fit this. That is an inference, not a measured result.

### Gaps
- I could not fetch the original Jan 2025 Mosseri video or the Social Media Today write-up. The quotes above come from secondary outlets.
- I found no official statement on posting frequency or on how often a new account should post.

## 2. Trial Reels: what they are, who can use them, and API support

### Takeaway
Trial Reels are shown only to non-followers at first. They can then be "graduated" (shared to followers) by hand or automatically if they perform well. The Content Publishing API supports them through `trial_params.graduation_strategy` = `MANUAL` | `SS_PERFORMANCE`, added in late 2025. Eligibility needs a public professional account. The follower threshold is disputed (200 vs 1,000), so a brand-new account will probably not qualify on day one.

### Cited Findings
- [OFFICIAL, Meta dev docs] `trial_params`: "An optional parameter for publishing trial reels. The `media_type` must be `REELS` if this parameter is included." Its only field is `graduation_strategy` (required), set to `MANUAL` ("can be manually graduated in the native app") or `SS_PERFORMANCE` ("automatically graduated if the trial reel performs well"). It is listed for standard `video_url` uploads, not for resumable uploads — [Meta: IG User Media reference](https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media)
- [OFFICIAL, changelog] The changelog entry "Supporting Trial Reels in the Content Publishing API" is dated 10 Nov 2025 on Meta's changelog. One secondary source says 3 Dec 2025 — [Meta changelog](https://developers.facebook.com/docs/instagram-platform/changelog); [AdaptlyPost](https://adaptlypost.com/blog/instagram-trial-reels)
- [INDUSTRY] The API cannot graduate a trial later and has no field showing trial status. Graduation happens in the app — [Ayrshare docs](https://www.ayrshare.com/docs/apis/post/social-networks/instagram); [AdaptlyPost](https://adaptlypost.com/blog/instagram-trial-reels)
- [INDUSTRY] Eligibility conflicts. One source says the Help Center now lists 200 followers for professional accounts and 1,000 for personal accounts, both public. Others say 1,000+ for a public professional account. One scheduler says 1,000+ is an API requirement — [Superprofile guide](https://superprofile.bio/guides/instagram-trial-reels); [CreatorFlow](https://creatorflow.so/blog/instagram-trial-reels/); [SocialCal help](https://www.socialcal.app/help/posting-scheduling/instagram-trial-reels)
- [INDUSTRY] If an account is not eligible for recommendations, its trial reels are removed until it is eligible again. Followers can still meet a trial reel through DMs or audio/location pages — [Superprofile guide](https://superprofile.bio/guides/instagram-trial-reels)
- [INDUSTRY, unverified] Reports say there is a cap of about 20 trial reels a day and no collaborator tags on trials — [PostProxy guide](https://postproxy.dev/blog/instagram-reels-api-publishing-guide/)

### Inferences
- Plan for trial reels to be unavailable until the account passes the follower threshold. Have `publish.py` treat `trial_params` as optional and fall back to a normal Reel if the API rejects it.
- A trial reel posted with `SS_PERFORMANCE` needs no follow-up app step. That suits our automated pipeline, but G3 still applies.

### Gaps
- I could not fetch the Help Center article that gives the exact current follower threshold. Check it in the app (the Trial toggle appears in the share sheet if eligible).

## 3. Originality, cross-posting from YouTube, and watermarks

### Takeaway
Since April 2024, Instagram recommends only the original when it finds near-identical content. It stops recommending accounts that repeatedly repost other people's work, and recommended content must have "no visible watermark". In April 2026 the policy was reportedly extended from Reels to photos and carousels. Posting our own self-made videos is original, as long as the file Instagram receives has no YouTube or TikTok branding.

### Cited Findings
- [OFFICIAL, 30 Apr 2024] When Instagram finds two or more near-identical pieces, only the original is recommended. Matching uses audio and visual signals. Content with meaningful changes, such as a new voiceover, reactions or parody, is not replaced — [Instagram Creators](https://creators.instagram.com/recommendations-and-originality)
- [OFFICIAL, 30 Apr 2024] To be recommended, content must be original, follow the Community Guidelines, have **no visible watermark**, and meet the Recommendation Guidelines — [Instagram Creators](https://creators.instagram.com/recommendations-and-originality)
- [OFFICIAL, 30 Apr 2024] Accounts that repeatedly post others' content without meaningful change stop being recommended. They can become eligible again after a significant period without non-original posts, and can check status and appeal in Account Status — [Instagram Creators](https://creators.instagram.com/recommendations-and-originality)
- [OFFICIAL via press, 2024] The 2024 version reportedly cut off Reels recommendations for accounts posting unoriginal content 10+ times in 30 days — [Nasdaq/RTTNews](https://www.nasdaq.com/articles/instagram-updates-its-reels-algorithm-to-prioritize-original-content); [Engadget](https://www.engadget.com/instagrams-algorithm-overhaul-will-reward-original-content-and-penalize-aggregators-130018977.html)
- [OFFICIAL via secondary, 30 Apr 2026] The rule now reportedly covers photos and carousels too. Accounts that "primarily post unoriginal content in photos or carousel posts, in addition to reels" will not be recommended. Reposts are demoted for non-followers, not removed — [ALM Corp](https://almcorp.com/blog/instagram-restricts-reach-content-aggregators/); [Status 200 Uploads](https://status200uploads.com/blog/instagram-originality-rules-reposts) (PetaPixel's coverage returned 403, so I could not verify the exact wording)
- [INDUSTRY] Watermarks, crops or a caption credit do not make a re-upload original — [Status 200 Uploads](https://status200uploads.com/blog/instagram-originality-rules-reposts); [ALM Corp](https://almcorp.com/blog/meta-original-content-rules-2026-facebook-instagram-creators/)
- [OFFICIAL via press] Mosseri has warned against content carrying other platforms' watermarks, especially TikTok's — [Inman, Mar 2025](https://www.inman.com/2025/03/07/head-of-instagram-reveals-secrets-to-social-media-success/)
- [INDUSTRY, Nov 2025] Instagram reportedly launched content-protection tools that scan for similar Reels across platforms and alert creators — [WebSearch result citing launchvibes](https://www.launchvibes.tech/articles/instagram-original-content-algorithm) (secondary)

### Inferences
- Posting the same self-made video on YouTube first does not make it unoriginal under the stated rules. Those rules target content the poster did not create or did not meaningfully change. Upload the clean master render, never a file downloaded from YouTube, since Shorts downloads can carry YouTube branding.
- No end card should say "Subscribe on YouTube" with a YouTube logo. A visible third-party logo may count as a watermark.

### Gaps
- I found no official statement that names YouTube or own-channel cross-posting. Our reading that it is "fine" comes from the general rule, not a specific ruling.
- I found no official detail on whether cross-platform content matching ties a YouTube upload to the Instagram copy.

## 4. Recommendation eligibility, Account Status, and religious or violent content

### Takeaway
The Recommendation Guidelines set a higher bar than the Community Guidelines. Content that stays on the platform can still be kept out of Explore, Reels and suggestions if it involves violence or self-harm, sexual suggestiveness, regulated products, health claims, political or social topics, engagement bait, low-quality or unoriginal material, or false claims flagged by fact-checkers. Professional accounts can see flagged posts in Account Status and appeal. I found no official rule that singles out religious or mythological content. A stylised chalk scene of a demon being slain falls under the general "violence" item, so keep it non-graphic.

### Cited Findings
- [OFFICIAL, Apr 2024] Categories that are allowed on Instagram but may not be recommended: self-harm, violence or sexually suggestive content; tobacco, vapes and regulated products; cosmetic procedures, miracle health claims, payday loans; political or social topics; clickbait and engagement bait; low-quality unoriginal content; content rated false by fact-checkers — [Instagram Creators](https://creators.instagram.com/recommendations-and-originality)
- [OFFICIAL, Apr 2024] Accounts that repeatedly post guideline-violating content may be temporarily blocked from recommendations. While blocked, none of their content is recommended, though followers still see it — [Instagram Creators](https://creators.instagram.com/recommendations-and-originality); [Instagram Help: recommendations](https://help.instagram.com/313829416281232)
- [OFFICIAL, Dec 2022, PRE-2024] Account Status shows professional accounts whether their content can be recommended. It shows samples of ineligible posts and the guideline each one broke, and lets the creator edit, delete or request a review — [TechCrunch, 7 Dec 2022](https://techcrunch.com/2022/12/07/instagrams-new-transparency-tools-will-tell-you-if-your-content-is-ineligible-to-be-recommended/)
- [OFFICIAL, Aug 2020, PRE-2024] Meta first published the Recommendation Guidelines in five categories, covering borderline, spammy, low-quality and debunked content — [Engadget, 31 Aug 2020](https://www.engadget.com/facebook-and-instagram-reveal-content-recommendation-guidelines-130011327.html)

### Inferences
- A non-graphic illustrated battle with no gore, blood spray or lingering on injury should be fine for recommendation. This is an inference, since the exact "violence" sub-criteria were not retrieved.
- Avoid comparisons to modern politics or communal framing in captions. "Social topics" content is excluded from recommendations by default.
- Endings like "Comment ॐ if…" or "Share to 5 people" can be read as engagement bait. Ask open questions instead.
- Check Account Status weekly in the first month.

### Gaps
- The full current Recommendation Guidelines text failed to load (the transparency.meta.com URL returned 404 and the Help Center page rendered empty). I have no official wording on fictional, illustrated or mythological violence, or on religious content.

## 5. AI labelling ("AI info")

### Takeaway
Meta has required disclosure since Feb 2024 for organic content with "photorealistic video or realistic-sounding audio that was digitally created or altered", and "may apply penalties" if creators don't disclose. The label has been called "AI info" since 2024. Stylised chalk illustrations are not photorealistic, but synthetic TTS narration is arguably "realistic-sounding audio", so disclosure is the safe choice. The API has an `is_ai_generated` self-disclosure parameter. In the app, use "Label as made with AI" when creating the Reel.

### Cited Findings
- [OFFICIAL, Meta Newsroom 6 Feb 2024, updated 1 Apr 2025] "We'll require people to use this disclosure and label tool when they post organic content with a photorealistic video or realistic-sounding audio that was digitally created or altered… we may apply penalties if they fail to do so." — [Meta Newsroom](https://about.fb.com/news/2024/02/labeling-ai-generated-images-on-facebook-instagram-and-threads/)
- [OFFICIAL, Transparency Center, last updated 19 Feb 2025] "AI info" labels began in May 2024 on a wider range of video, audio and images. They are applied when Meta detects "industry standard AI image indicators" or when the uploader discloses AI use. Meta says its method may miss some AI-edited content — [Meta Transparency: Labeling AI content](https://transparency.meta.com/governance/tracking-impact/labeling-ai-content)
- [OFFICIAL via press, 2024] The label was renamed from "Made with AI" to "AI info" after photographers complained of false flags. Fully AI-generated images still show the label on the post — [PhoneArena](https://www.phonearena.com/news/meta-changes-ai-generated-content-label_id160026); [MediaPost](https://www.mediapost.com/publications/article/399304/)
- [OFFICIAL, Help Center] Reels created or modified with AI should be labelled before sharing: create the Reel, then use the toggle next to "Label as made with AI". Viewers can tap "AI info" then "View AI info" to see whether the creator or Instagram added the label — [Instagram Help](https://help.instagram.com/761121959519495); [Meta Help: identify AI content](https://www.meta.com/en-gb/help/artificial-intelligence/1783222608822690/)
- [OFFICIAL, Meta dev docs] `is_ai_generated`: "An optional parameter to provide a self-disclosure of AI usage in the post. Not available for carousel children." The reference does not show it in a REELS example, so support for Reels is implied but not stated — [Meta: IG User Media reference](https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media)
- [INDUSTRY, Aug 2026] Instagram reportedly renamed its account-level "AI creator" label to "AI-generated profile" and limits unlabelled AI-generated profiles (aimed at fake-human influencers) — [Unite.AI](https://www.unite.ai/instagram-renames-ai-creator-label-and-restricts-unlabeled-ai-generated-profiles/); [MediaPost](https://www.mediapost.com/publications/article/414862/instagram-unveils-new-ai-creator-account-label.html)
- [INDUSTRY] Meta has set no general reach penalty for content that is correctly labelled. Blog claims of a "15–80% reach drop" are unsupported — [WebSearch synthesis; Magic Hour checklist](https://magichour.ai/blog/instagram-ai-generated-content-labels)

### Inferences
- Send `is_ai_generated=true` on every Reel container. Test it on one dry-run container first, since Reels support is not explicit, and confirm the label shows on the published Reel. If the API rejects it, label manually in the app before scheduling. That breaks full automation for those posts.
- Images from a local model usually lack C2PA/IPTC metadata, so Meta will probably not auto-detect them. Self-disclosure is therefore the only route to a label and the main protection against penalties.
- A faceless, illustrated, clearly non-human channel is unlikely to count as an "AI-generated profile" (fake persona). Stating "AI-assisted art and narration" in the bio is cheap insurance.

### Gaps
- I found no official statement on whether stylised, non-photorealistic AI images on their own require disclosure. The rule text covers photorealistic video and realistic audio.
- The concrete penalties for not disclosing are not specified.

## 6. Music: original audio vs licensed music

### Takeaway
I found no official claim that original audio gets a ranking boost. Mosseri only says a Reel should have sound. Our own music and voice bed becomes the Reel's "original audio". The API lets us name it once via `audio_name`, which helps attribution when others reuse the sound. Using our own audio avoids the music-library limits on Business accounts entirely.

### Cited Findings
- [OFFICIAL, Meta dev docs] `audio_name`: "For Reels only. Name of the audio of your Reels media. You can only rename once." — [Meta: IG User Media reference](https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media)
- [OFFICIAL via press, 2025] Mosseri: make sure a Reel includes sound, whether a popular song, a voiceover or original audio — [Inman](https://www.inman.com/2025/03/07/head-of-instagram-reveals-secrets-to-social-media-success/)

### Inferences
- Set `audio_name` to something searchable and branded, for example "Ramayana Ep05 Tataka · mr.aks.tale", so every reuse links back to us.
- A Creator account (not Business) keeps the full music library for any manual posts. Our self-generated bed makes this moot.

### Gaps
- I did not retrieve an official source on the current Business vs Creator music library limits in 2025–26.
- I found no official evidence that original audio is ranked higher.

## 7. Hashtags and keyword captions

### Takeaway
Since December 2025 Instagram caps hashtags at **5 per post or Reel**, down from 30, and the Help Center confirms it. Mosseri has repeatedly said hashtags do not increase reach and only help explain what a post is about. Caption keywords matter more for Instagram search.

### Cited Findings
- [OFFICIAL, Help Center] "You can use up to 5 tags on a post. If you include more than 5 tags on a single photo/video, your comment won't post." Announced about 18 Dec 2025 by @creators / Mosseri, with a gradual rollout — [Business Today, 19 Dec 2025](https://www.businesstoday.in/technology/news/story/no-more-hashtag-stuffing-instagram-limits-hashtag-usage-to-just-5-per-reel-and-post-507444-2025-12-19); [Social Media Today](https://www.socialmediatoday.com/news/instagrams-implementing-new-limits-on-hashtag-use/808309/)
- [OFFICIAL via press, 2025] Mosseri says hashtags don't improve visibility but are "a great way to let people know what a post is about" — [LatestLY](https://www.latestly.com/technology/instagram-caps-hashtags-at-five-per-post-in-new-policy-shift-amidst-head-of-instagram-mosseris-myth-claims-7245760.html)
- [INDUSTRY] It is unclear whether hashtags in the caption and in the first comment count toward the same five — [CreatorFlow](https://creatorflow.so/blog/how-many-hashtags-instagram/)

### Inferences
- Use at most 3–5 specific tags per language, such as #ramayana #ramayan #valmikiramayana plus one language tag. Put natural keywords in the caption's first line, in the native script and in transliteration (e.g. "Tataka", "ताड़का", "તાડકા", "తాటక").
- `publish.py` should enforce a limit of 5 hashtags or fewer.

### Gaps
- I found no 2025–26 official statement detailing how caption keywords are indexed for Instagram search.

## 8. Posting cadence and time of day for India

### Takeaway
I found no official Instagram guidance on the best posting time for India. Industry sources mostly point to early evening IST (about 6–9 PM), but they conflict and are vendor blogs. Use Insights "Most active times" once the account has followers.

### Cited Findings
- [INDUSTRY, 2025] SocialPilot's 2025 study lists Monday 7:30 am, 3 pm and 7:30 pm IST as the best India Reels slots — [SocialPilot](https://www.socialpilot.co/insights/best-time-to-post-reels-on-instagram)
- [INDUSTRY] Other India guides suggest 6–9 PM IST, weekdays at 7:30 PM, or Sunday 7–9 PM. Some admit their figures are "editorial baselines", not measured data — [WsCubeTech](https://www.wscubetech.com/blog/instagram-post-time/); [Boss Wallah](https://bosswallah.com/blog/creator-hub/best-instagram-reels-posting-time-in-india-boost-views-engagement/); [timetopost.co](https://timetopost.co/best-time-to-post/instagram/india/)
- [Frequency] There is no official number. Mosseri reportedly advises a sustainable frequency — [Bazzaal summary](https://www.bazzaal.com/blog/instagram-algorithm-2026-mosseri)

### Inferences
- Our existing YouTube slots (HI 20:30, EN 21:30 IST) fit the industry evening window. Keep them as a starting hypothesis and test against Insights. These are industry guesses, not evidence.

### Gaps
- I found no primary dataset on India posting times or on GU/TE audiences specifically.

## 9. Language handling and Meta AI translations

### Takeaway
Since 9 Oct 2025, Meta AI can translate and dub Reels between English, Spanish, Hindi and Portuguese, with optional lip-sync. It is free for all public Instagram accounts in countries where Meta AI is available, and each dubbed Reel is labelled "Translated with Meta AI". Gujarati and Telugu were not on the announced list. Because we already publish native-language versions, separate per-language posts remain the main approach.

### Cited Findings
- [OFFICIAL, Meta Newsroom 9 Oct 2025] Translations work between English, Spanish, Hindi and Portuguese, "with more languages on the way". The feature is free and open to all public Instagram accounts where Meta AI is available (Facebook requires 1,000+ followers). Translated Reels are labelled "Translated with Meta AI". Viewers can turn translations off ("Don't translate") in the three-dot audio and language menu — [Meta Newsroom](https://about.fb.com/news/2025/10/translate-dub-and-lip-sync-your-reels-between-hindi-and-english-now-on-instagram-and-facebook/)
- [OFFICIAL via press, Oct 2025] The tool clones the creator's voice tone. Multi-speaker translation and on-screen text/caption translation were described as coming soon — [Business Today](https://www.businesstoday.in/technology/news/story/meta-adds-hindi-ai-translation-for-reels-on-instagram-and-facebook-497661-2025-10-10); [Social Samosa](https://www.socialsamosa.com/news-2/meta-ai-reels-translations-10547482)

### Inferences
- If we enable Meta AI translation on English Reels, they would also be dubbed into Hindi, competing with our own Hindi upload. This would also stack a second AI layer on top of synthetic TTS. Recommendation: leave auto-translation off and keep the four native-language versions.
- One account carrying four languages could confuse audience signals. That is an inference only, since Instagram has not documented language targeting for organic Reels.

### Gaps
- I found no official documentation on how Instagram matches organic Reels to viewers by language, and no update on whether Gujarati or Telugu were added to translations after Oct 2025.
- The announcement does not say whether faceless or voiceover-only Reels qualify for dubbing.
