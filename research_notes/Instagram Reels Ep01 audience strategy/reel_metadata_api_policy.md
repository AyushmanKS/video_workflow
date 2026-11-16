# Instagram Reel publishing metadata and policy via the Graph API (v27.0, 2025–2026)

Research date: 2026-11-16. Context: the repo's `instagram.py` currently uses `API_VERSION = "v27.0"`, both `graph.instagram.com` and `graph.facebook.com`, and sends only `media_type=REELS`, `video_url`, `caption`, `share_to_feed=true`, plus `cover_url` or `thumb_offset` (local repo inspection, not a web source).

## 1. POST /{ig-user-id}/media with media_type=REELS: parameters, constraints, login compatibility

### Takeaway
For Reels the documented settable fields are `video_url`, `caption`, `cover_url`, `thumb_offset`, `share_to_feed`, `collaborators` (max 3), `location_id`, `audio_name` (one rename only), `user_tags` (usernames, no x/y), `trial_params` and `is_ai_generated`. `alt_text` is image-only and does not apply to Reels. Most fields work with both Facebook Login (graph.facebook.com) and Instagram Login (graph.instagram.com). The exceptions are the Facebook-Login-only features: partnership labels, resumable uploads and the 2026 Audio API.

### Cited Findings
- `video_url` is required for Reels. Instagram fetches it, so the file must be on a public server. Reels can be 3 s to 15 min long and up to 300 MB. Containers expire after 24 h, and an account can create at most 400 containers per rolling 24 h. — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)
- `caption`: "Maximum 2200 characters, 30 hashtags, and 20 @ tags". @-mentioned users are notified when the container is published. — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)
- `cover_url` is for Reels only and sets the Reels-tab cover. It must be JPEG, at most 8 MB and sRGB, with 9:16 recommended. If both `cover_url` and `thumb_offset` are sent, `cover_url` wins. — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)
- `thumb_offset` is a frame position in milliseconds and defaults to 0 (the first frame). It is ignored when `cover_url` is set. — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)
- `share_to_feed` is for Reels only. `true` shows the Reel in both Feed and the Reels tab, and `false` shows it in the Reels tab only. The docs add: "Neither value determines whether the reel actually appears in the Reels tab", because eligibility still applies. — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)
- `collaborators` is "For Feed image, Reels and Carousels only" and takes "A list of up to 3 instagram usernames". — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)
- Collaborator management was added in 2025–2026. An account can accept or decline invites via `media_id` (2025-12-03) and retrieve media where it is an accepted collaborator through `/<IG_USER_ID>/collaborative_media` (2026-04-22). — [Instagram Platform changelog](https://developers.facebook.com/docs/instagram-platform/changelog)
- `location_id` is a Facebook Page ID that has location data. Using a Page with no location data fails with `INSTAGRAM_PLATFORM_API__INVALID_LOCATION_ID`. — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)
- `audio_name` is for Reels only and names the Reel's original audio: "You can only rename once, either while creating a reel or after from the audio page." — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)
- `user_tags` takes usernames. The `x`/`y` coordinates "Applies only to images and stories", so a Reel tag is a username without a position. Support for image and video stories was added on 2025-07-09. — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)
- `alt_text` was added on 2025-03-24 "For image posts only". "Reels and stories are not supported." — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media); [Changelog](https://developers.facebook.com/docs/instagram-platform/changelog)
- `is_ai_generated` is an optional self-disclosure of AI use. It is "Not available for carousel children". The 2026-06-22 changelog says: "Set the new `is_ai_generated` parameter to `true` when creating a media container". This applies the AI info label at publish time, and the field can also be read back on IG Media. — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media); [Changelog](https://developers.facebook.com/docs/instagram-platform/changelog)
- The Content Publishing guide says `is_ai_generated` "is available for both Facebook Login and Instagram Login". — [Content Publishing guide](https://developers.facebook.com/docs/instagram-platform/content-publishing)
- Login setups:
  - Unified Login: Facebook Login for Business with a Business Integration System User token, on graph.facebook.com.
  - Facebook Login: Facebook Login for Business with a Page token, on graph.facebook.com.
  - Instagram Login: Business Login for Instagram with an Instagram User token, on graph.instagram.com.
  - Resumable uploads through rupload.facebook.com are available only to Facebook Login for Business apps.
  — [Content Publishing guide](https://developers.facebook.com/docs/instagram-platform/content-publishing)
- Partnership label fields `branded_content_sponsor_ids` (max 2) and `is_paid_partnership` work with Facebook Login only. — [Content Publishing guide](https://developers.facebook.com/docs/instagram-platform/content-publishing); [Changelog 2026-04-22](https://developers.facebook.com/docs/instagram-platform/changelog)
- Rate limit: 100 API-published posts per 24-hour moving window, checked at `content_publishing_limit`. The carousel section of the same guide says 50, which conflicts. — [Content Publishing guide](https://developers.facebook.com/docs/instagram-platform/content-publishing)
- Documented limitations: no shopping tags and no filters, and the media must be publicly accessible when publishing is attempted. — [Content Publishing guide](https://developers.facebook.com/docs/instagram-platform/content-publishing)
- The latest version listed in the reference is v27.0. The reference lists `share_to_feed` twice in the Reels syntax, which is probably a documentation error. — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)
- From 2026-07-30, `media_url` should be treated as optional. It may be omitted for copyrighted videos and for Reels whose owners disabled downloads. — [Changelog](https://developers.facebook.com/docs/instagram-platform/changelog)

### Inferences
- For four language versions, the fields worth setting are:
  - a language-specific `caption`
  - a custom `cover_url`
  - `share_to_feed=true`
  - `audio_name`, set once at creation to a clear, language-specific title
  - `is_ai_generated=true` if the narration is a realistic synthetic voice (see section 3)
- Leave out the fields that do not help a new solo account: `location_id`, `collaborators` and `user_tags`.
- Because `audio_name` can be renamed only once, it should be set deliberately at creation rather than left as the default "Original audio".
- The repo's current publisher sends none of `audio_name`, `is_ai_generated` or `trial_params`.
- The repo mixes graph.instagram.com and graph.facebook.com. All the Reel fields above, including `is_ai_generated`, work on either host. Partnership labels, resumable upload and the Audio API need Facebook Login.

### Gaps
- No official per-field login-compatibility matrix was found for `audio_name`, `collaborators`, `location_id` and `trial_params`. The reference does not mark them as Facebook-Login-only, but this was not confirmed by testing.
- `location_id` needs a Facebook Page with location data. It is unclear whether arbitrary public place Pages work with an Instagram Login token.
- The changelog does not list release dates for v23–v27.

## 2. Trial Reels via the API (trial_params)

### Takeaway
Trial Reels are officially supported in the API (changelog dated 2025-12-03). `graduation_strategy` takes `MANUAL` or `SS_PERFORMANCE`, and a trial Reel is shown only to non-followers until it graduates. Trial Reels require a public professional account that is eligible for recommendations. The follower minimum is disputed (200 vs 1,000), so a brand-new account may not qualify, and with no followers a trial has little purpose.

### Cited Findings
- `trial_params` is optional, and "The `media_type` must be `REELS` if this parameter is included". Its required `graduation_strategy` takes one of two values:
  - `MANUAL`: graduate manually in the native app.
  - `SS_PERFORMANCE`: graduate automatically if the Reel performs well.
  — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)
- "Supporting Trial Reels in the Content Publishing API", dated 2025-12-03. One search snippet showed 2025-11-10, which conflicts. — [Changelog](https://developers.facebook.com/docs/instagram-platform/changelog)
- Trial Reels are shared only with non-followers until they graduate. — [Content Publishing guide](https://developers.facebook.com/docs/instagram-platform/content-publishing)
- Third-party reports say graduation cannot be triggered by the API, and that no IG Media field reports whether a Reel is still a trial. — [Ayrshare docs](https://www.ayrshare.com/docs/apis/post/social-networks/instagram); [AdaptlyPost](https://adaptlypost.com/blog/instagram-trial-reels)
- Eligibility is a public professional account. Accounts that are ineligible for recommendations lose Trial Reels until they become eligible again. — [superprofile.bio guide](https://superprofile.bio/guides/instagram-trial-reels); [Planoly](https://www.planoly.com/blog/how-to-post-a-trial-reel-on-instagram)
- The follower minimum is disputed. Some guides cite the Help Center as 200 for professional accounts and 1,000 for personal ones. Others say 1,000, with expansion in early 2026. One analysis says Meta's announcements state no threshold. — [superprofile.bio](https://superprofile.bio/guides/instagram-trial-reels); [Postfa.st](https://postfa.st/blog/instagram-trial-reels); [AdaptlyPost](https://adaptlypost.com/blog/instagram-trial-reels)
- One third-party guide reports a cap of roughly 20 trial Reels per day through the API. This is unverified. — [AdaptlyPost](https://adaptlypost.com/blog/instagram-trial-reels)
- Trial Reels launched in December 2024 as a way to test content with non-followers. — [Social Media Today](https://socialmediatoday.com/news/instagram-trial-reels-increase-reach-tests/750121/)

### Inferences
- For a brand-new account with few followers:
  - The main benefit of a trial (protecting followers from a weak post) barely applies, because nearly all reach is already non-follower reach.
  - The account may also be below the follower threshold.
  - The API call may fail, or the trial may never graduate onto the profile unless it is graduated manually in the app.
- If the API rejects `trial_params`, publish normally, without `trial_params`.
- Possible later use: once the account passes the threshold, publish the secondary language versions as `SS_PERFORMANCE` trials. Their reach to non-followers can be tested without four near-identical posts landing in followers' feeds on the same day.

### Gaps
- The official Help Center follower threshold could not be confirmed because the page was not retrievable.
- What the API returns for an ineligible account is undocumented.

## 3. Meta AI labelling policy (AI info) for AI images and AI voice narration

### Takeaway
Meta's self-disclosure requirement covers photorealistic video and realistic-sounding audio that were digitally generated or altered. It does not cover non-photorealistic, cartoon or illustrated visuals, or images. Chalkboard-style AI visuals therefore probably do not need a label on their own. A realistic AI voiceover is the trigger: Instagram's help page explicitly lists "a reel narrated with a realistic AI-generated voiceover" as needing a label. For API uploads, disclosure is `is_ai_generated=true` on the container.

### Cited Findings
- Instagram's help page "requires a label on content you share that has photorealistic video or realistic-sounding audio that has been digitally generated or altered, including with AI". Its examples are:
  - Needs a label: "A reel narrated with a realistic AI-generated voiceover", and songs with AI vocals.
  - Does not need one: "Video of an outdoor landscape, created in a style resembling a cartoon".
  - The page warns there may be penalties for not labelling.
  Source note: these quotes come from a search-result extract. A direct fetch returned only the page shell. — [Instagram Help Center 761121959519495](https://help.instagram.com/761121959519495)
- A secondary guide says Meta's help page states the requirement does not apply to images, and that AI-written captions or scripts do not need a label. — [Magic Hour checklist](https://magichour.ai/blog/instagram-ai-generated-content-labels); [Kompozy guide](https://kompozy.io/guides/instagram-ai-disclosure-policy)
- Meta's April 2024 policy post:
  - "We will begin adding 'AI info' labels to a wider range of video, audio and image content".
  - Update of 2024-07-01: "Made with AI" was renamed "AI info".
  - Update of 2024-09-12: for content "only modified or edited by AI tools", the label moves to the post menu. Fully generated content keeps the visible label.
  — [Meta newsroom, April 2024](https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/)
- Meta's transparency page (updated 2025-02-19) says labels come from detected industry-standard AI indicators or from user self-disclosure. It gives no detailed disclosure thresholds. — [Meta Transparency Center: Labeling AI content](https://transparency.meta.com/governance/tracking-impact/labeling-ai-content)
- API mechanism: `is_ai_generated=true` applies the AI info label at publish time. It works with both login types (changelog of 2026-06-22). — [Changelog](https://developers.facebook.com/docs/instagram-platform/changelog); [Content Publishing guide](https://developers.facebook.com/docs/instagram-platform/content-publishing)

### Inferences
- In this project the visuals are chalkboard illustrations, so they are non-photorealistic. The narration is TTS: Veena or Maya2 voices that are intended to sound natural and human.
- Under the help-page wording, a realistic synthetic narrator falls within "realistic-sounding audio … digitally generated". The conservative, policy-compliant choice is `is_ai_generated=true` on all four language versions.
- The cost of disclosing is a visible "AI info" label. No source found says the label reduces distribution.
- The risk of not disclosing is possible penalties under the help page's wording.

### Gaps
- No official statement was found on whether the AI info label affects recommendation reach.
- The Meta help page on identifying AI content could not be fetched directly (only its title came back), so the exact current wording is second-hand apart from the search extract.

## 4. Originality and recommendation rules: cross-posting to YouTube Shorts, watermarks, and four near-identical language versions

### Takeaway
Instagram's originality system targets accounts that repost content they did not create, plus visible watermarks. Your own work first posted on YouTube is original, as long as the upload carries no YouTube or other app watermark. Instagram's duplicate detection matches "audio and visual signals" and recommends only the original of identical or near-identical content. New voiceovers are explicitly listed as a material change. Four language versions with identical visuals but different narration are therefore probably not treated as duplicates of each other, but no official source addresses an account duplicating its own visuals, so some risk remains.

### Cited Findings
- April 30, 2024 creators post (fetched in Hindi locale):
  - To be eligible, content must be original, follow the Community Guidelines, have no visible watermark ("उसमें कोई वॉटरमार्क न दिख रहा हो") and follow the recommendation guidelines.
  - Accounts that repeatedly post others' content "without creating it or substantially changing it" will no longer be recommended.
  - When duplicate or near-identical content is found, "only the original content will be recommended". Matching is based on "audio and visual signals".
  - Substantially altered content such as memes, parodies, reaction videos or new voiceovers is not swapped out.
  - The Account Status tool shows ineligible content and allows appeals.
  — [Instagram for Creators: Recommendations and Originality](https://creators.instagram.com/recommendations-and-originality)
- Engadget, 2024-04-30, on the same change:
  - Aggregators that post others' content 10 or more times in 30 days stop being recommended for Reels.
  - When two identical pieces are detected, the original replaces the repost in suggestions.
  - Reposts get a label crediting the original creator.
  — [Engadget](https://www.engadget.com/instagrams-algorithm-overhaul-will-reward-original-content-and-penalize-aggregators-130018977.html)
- Recommendation eligibility can return after 30 days with no unoriginal posts, according to search-result coverage of the creators page. The fetched Hindi version did not state "30 days" explicitly, so this is unconfirmed. — [creators.instagram.com](https://creators.instagram.com/recommendations-and-originality); [RouteNote](https://routenote.com/blog/instagram-tightens-rules-reposted-content/)
- 2026-04-30 expansion:
  - The originality standards were extended from Reels to photos and carousels.
  - Accounts that mainly share content they did not create or meaningfully transform will not be recommended to non-followers.
  - Follower feeds are unchanged.
  — [PetaPixel](https://petapixel.com/2026-04-30/new-instagram-policies-target-reposted-content/) (fetch blocked, cited from search summary); [MobileSyrup](https://mobilesyrup.com/2026/05/01/instagram-tweaks-algorithm-to-reduce-reach-of-content-aggregators/); [MediaPost](https://www.mediapost.com/publications/article/414773/instagram-algorithm-update-deprioritizes-unorigina.html); [Digital Music News](https://www.digitalmusicnews.com/2026/05/01/instagram-debuts-more-original-content-protections-for-creators/)
- Watermarks, crops and credits are not transformation: "adding a watermark, cropping slightly, or simply crediting the original creator" does not count as meaningful transformation. — [Planoly](https://planoly.com/blog/instagram-updates-its-original-content-policy)
- Agency guidance: remove other platforms' watermarks, and "if you made the video it counts as original, even if it ran on TikTok first". — [Vamp](https://vamp.com/insights/how-brands-can-create-more-original-content-to-beat-instagrams-new-algorithm-update/)
- Unverified claim: one site says accounts with more than 50% reposts in 30 days are classed as aggregators. No official source was found. — [search summary; sociallyin](https://sociallyin.com/blog/instagram-algorithm-update-repost/)

### Inferences
- Cross-posting the same self-made videos to YouTube Shorts is fine if the file uploaded to Instagram is the clean render with no YouTube Shorts UI or watermark. The pipeline renders its own MP4s, so this should hold.
- Four language versions on one account:
  - They share visuals but differ in voiceover audio. Since matching uses both audio and visual signals, and new voiceovers are named as a material change, they are unlikely to be treated as reposts of someone else's work.
  - They are all the account's own originals, so the aggregator penalty does not obviously apply.
  - However, near-identical visuals posted back-to-back could be read as low-effort or spammy, and the system could still choose just one as the "original" to recommend. No source addresses this exact case.
- Mitigations: stagger the versions in time, give each its own cover text and caption in its own script, and consider separate language accounts or trial Reels for secondary languages once eligible.
- Watch Account Status for an "ineligible for recommendations" flag after the first batch.

### Gaps
- No official guidance was found on translated or dubbed versions of one's own video posted on the same account.
- Instagram's recommendation-guidelines Help Center page (help.instagram.com/313829416281232) returned only a shell, so its exact wording on watermarks and low-quality content was not verified.
- The watermark-suppression claims are mostly from agency blogs. The creators page itself lists "no visible watermark" as an eligibility condition.

## 5. Covers: size, aspect ratio, grid crop

### Takeaway
Upload a 9:16 (1080×1920) JPEG cover through `cover_url`. Since early 2025 the profile grid shows posts as a centre-cropped 3:4 rectangle rather than a 1:1 square, so keep title text and focal art inside the central 3:4 area (about 1080×1440 centred on the 1920 height).

### Cited Findings
- Reels cover specs in the API: JPEG, at most 8 MB, sRGB, 9:16 recommended. — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)
- Grid history:
  - Mosseri flagged the coming grid change and said most uploads are vertical (4:3 photos or 9:16 videos). — [Social Media Today](https://www.socialmediatoday.com/news/instagram-chief-flags-coming-changes-to-profile-grid-displays/724532/)
  - Instagram tested a vertical grid in August 2024. — [Mezha](https://mezha.ua/en/2024/08/19/instagram-tests-vertical-profile-grid-among-a-limited-number-of-users/)
  - The profile grid moved from 1:1 to 3:4 for all accounts in January 2025. — [Planoly Jan 2025](https://planoly.com/blog/instagram-updates-jan-2025); [Social Samosa](https://www.socialsamosa.com/news-2/instagram-updates-profile-grid-vertical-thumbnail-display-8636556)
- Grid thumbnails are centre-cropped to 3:4. Recommended pixel sizes conflict:
  - 1080×1440 per Kapwing.
  - 1013×1350 display size per Planoly.
  — [Kapwing](https://www.kapwing.com/resources/instagrams-new-grid-layout-size-and-dimensions-2025/); [Planoly vertical grid guide](https://www.planoly.com/blog/guide-to-instagrams-new-vertical-grid.md)

### Inferences
- The central 1080×1440 band of a 1080×1920 cover is what shows on the profile grid. The full 9:16 shows in the Reels tab.
- Keep large titles in the native script of each language, with high contrast (chalk white on dark board), inside that band. Avoid the top and bottom roughly 240 px.

### Gaps
- Instagram's own documentation gives no pixel-exact grid safe zone. The figures above are vendor estimates.
- Whether the API can set a separate grid crop for a cover is undocumented. The in-app crop tool has no API equivalent found.

## 6. Music and original audio; renaming audio

### Takeaway
API-published Reels carry their own embedded track as original audio. The 2026 Instagram Audio API lets Facebook Login apps attach licensed audio at creation, which is not available over Instagram Login. Renaming the original audio is possible once via `audio_name`. No primary source quantifies a reach effect of original audio versus trending audio.

### Cited Findings
- `audio_name` renames the Reel's audio, but only once. The reference notes "Music tagging is only available for original audio". — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)
- Changelog of 2026-06-01:
  - A new `media_audio_type` field returns `MUSIC` or `ORIGINAL_SOUND`.
  - The new Instagram Audio API lets Facebook Login apps search for audio and attach it to Reels at creation time.
  — [Changelog](https://developers.facebook.com/docs/instagram-platform/changelog)
- The originality page treats new voiceovers as material transformation (see section 4). — [creators.instagram.com](https://creators.instagram.com/recommendations-and-originality)

### Inferences
- The narration plus chalk SFX is genuinely original audio. A clear `audio_name`, for example "Ramayana Ep01 – Hindi narration", makes the sound page identifiable if others reuse it.
- Adding licensed music would need the Facebook Login Audio API path and is not required.

### Gaps
- No official evidence was found that original audio gets more or less reach than library music.
- The parameters of the Audio API endpoint were not retrieved.

## 7. Location tags and collaborators: reach evidence

### Takeaway
There is no primary evidence that location tags increase Reel reach. For collabs, Mosseri has reportedly advised that the larger account should create the post. That advice comes through third-party write-ups and is irrelevant without a partner account.

### Cited Findings
- Collab posts reportedly "tend to reach more people when the Instagram account with a larger following kicks off the collaboration", attributed to Mosseri. — [Buffer](https://buffer.com/resources/instagram-collab-post/); [OnlineMarketing.de](https://onlinemarketing.de/social-media-marketing/instagram-collabs-nach-posting-algorithmus-insights)
- Mosseri reportedly said "Posting a Reel to your stories will help a bit with reach". — [Buffer](https://buffer.com/resources/instagram-collab-post/)
- A vendor claims collab posts get 2× the average reach, attributed to Sprout Social. This is unverified. — [search summary; trymypost](https://www.trymypost.com/blog/instagram-collab-posts-strategy-guide-2026)
- API constraint: at most 3 collaborators. `location_id` must be a Page with location data. — [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)

### Inferences
- Location tags are optional and low priority. A mythological story has no natural real-world location, and a mismatched tag would be a relevance signal of unknown value.
- Collaborators only make sense with a real partner account that accepts the invite. Inviting one's own secondary language accounts as collaborators would merge audiences, but that is speculative.

### Gaps
- No Meta-published data on the reach effect of location tags or collaborators was found.
- Mosseri's original statements on collabs were not located. The citations are secondary.
