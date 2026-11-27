# The Impact Story — daily posts engine

> **For the daily scheduled run — read first. Where the task prompt and this README disagree, this README wins (it holds the owner's newest rules, 27 Nov 2026).**
> 1. **Reels:** ONE Reel a day at 19:30 on its own fresh topic (see "Reel" below). Do NOT export p2/p4 carousels as mp4 and do NOT schedule 13:30 or carousel Reels. If `posts/<date>/reel_plan.md` says STATUS: SCHEDULED or Metricool already has a 19:30 Reel, the Reel is done.
> 2. **Media hosting:** download every Canva PNG into `posts/<date>/`, push, and give Metricool the raw GitHub URLs (Canva links expire before most post times).
> 3. **Freshness:** news from the last 48 h (72 h max), not "last 7 days".
> 4. **Speed:** research with 4 parallel sub-agents (one per slot) plus 1 photo sub-agent.
> 5. **Upgrade loop:** before finishing, add at most ONE dated lesson to the top of "Lessons log" (from analytics or anything that went wrong/slow), keep the 15 most useful, apply all of them, and include the new lesson in the push notification. Lessons never weaken the owner's rules (real photos, accuracy, tone, no AI images).

Instagram + Facebook page **@theimpactstory** — inspiring stories of India's changemakers, companies doing good and good news. Owner: Mogli Media. Auto-published every day through Metricool (brand "The Impact Story", **blogId 8316520**, timezone Asia/Calcutta).

## Tone — read this first
Warm, inspiring and celebratory, like The Better India. Companies must see us as a friend who showcases their good work, never as a watchdog.
- Never: "proof", "exposed", "audit", "only X% spent", who spent the least, unspent funds, controversies, or anything that makes a company, NGO, person or government look bad.
- Numbers are used to **celebrate** impact (lives reached, villages helped, before → after).
- No politics, no religion-based angles, no unverified medical claims, no tragedy-led hooks. Personal hardships only if the source makes them central, and gently.
- Say "social good" / "good work" rather than "CSR" in headlines (CSR is fine in sources).
- Credit the person, company or NGO in every caption, and name where the story came from.

## Visuals — REAL PHOTOS in Canva (since 24 Nov 2026, owner's standard)
The owner wants **excellent, realistic, human-made design. No AI images, ever.** Do not use Canva `generate-design` pictures, `generate-image`, ElevenLabs, or any AI image tool for post pictures.

### 1. Find real photos
- Free-licence stock only: **Unsplash** (images.unsplash.com) or **Pexels**. Use WebSearch/WebFetch to find a photo page and its direct image URL, e.g. `https://images.unsplash.com/photo-XXXX?w=1600&q=80&fm=jpg`.
- Never use news, agency, Instagram or company photos (copyright). Never show a stock photo as the real person named in the story.
- Choose natural, documentary-style Indian scenes: real faces, real light, no watermarks, no visible brand logos, no cartoon or character T-shirts, no text in the picture. Each slide gets a different photo; portrait or tall crops work best.
- Upload with Canva `upload-asset-from-url` (Canva fetches it server-side; the workspace can't download image hosts).

### 2. Build the page (Instagram Post Portrait 1080x1440; Story/Reel 1080x1920)
Start from the previous day's design (`copy-design` / same structure) or a blank design, then in one `edit-design` transaction per design:
- Photo: `insert_fill` the asset as an element from top 0 to T (T ≈ 800–950), full width; frame faces with `crop_media`.
- Fade: 14 rectangles, each exactly 20 px tall, colour #005B50, opacity 0.065×k (k = 1..14), from T-280 to T. **No overlap** between bands, or stripes appear.
- Solid #005B50 rectangle from T to 1440 (or 1920).
- Layer order: send to back in this order — solid, bands (reversed), photo — so text stays on top.
- Text: Poppins only, headline white with one Warm Gold #E8B04B phrase, max ~20 words per slide, generous margins (≥ 64 px), tag pill top-left, "@theimpactstory" bottom-right, logo bottom-left (table below).
- Rotate layouts across days (photo top / full-bleed photo with fade bottom / split) so the feed doesn't look templated. Takeaway/CTA page can be Warm Gold with the on-gold logo.
- Commit the transaction.

### 3. Check before export (every page)
- `read-design` with thumbnails: every word and number matches batch.json; font is Poppins on every text box (if a box shows another font and the tool can't change it, rebuild that text box); contrast is readable; nothing crops a face; no text or logos inside the photo; logo doesn't blend in.

### 4. Export and schedule
- `export-design` PNG width 1080, then **download every PNG with curl into `posts/<date>/` (p1.png, p2_1..5.png, p3.png, p4_1..5.png, p4_story.png), commit + push, check the raw URL returns 200, and schedule Metricool with the raw.githubusercontent.com URLs** (Canva export links expire within hours, sometimes before the first post time).
- Metricool `instagramData.isAiGenerated: false`. No "AI image" label. Caption line: "Representative photo(s), not of the people named." (or "Representative photos." when no person is named).
- Reel: **Never turn a carousel or static post into a Reel/slideshow (owner, 26 Nov 2026).** Plan approved 27 Nov 2026:
  - **1 Reel per day, 19:30 IST**, on its OWN topic (not a feed-post topic): the freshest, most trending India-positive story of the last 48 h.
  - **Format by content:** A = "BREAKING" news Reel (20–30 s) built from real stock video of India that matches the story (Pexels/Pixabay; check every clip at full size: no foreign-looking places, no readable brand/shop signs in other languages, no AI-looking clips). B = real-people/event Reel from the actual clips: write a clip list with direct links in `posts/<date>/reel_clips.md`, tell the owner in the daily report, and build it once he drops the files in `media/<date>/` (he handles rights). If his clips are not there by 15:00 IST, switch to format A.
  - **Language: English. Voiceover: YES (owner approved the 27 Nov pattern).** ElevenLabs connector, voice **Ruhaan** (`siw1N9V8LmYeEWKyWBxv`, Indian English narrator), model `eleven_v4`, 2 takes. Script text uses punctuation only for pauses (no "[0.2s]" marks); numbers spelled out ("one thousand, five hundred and eighty-three", "five lakh rupees"). Download the take, transcribe it with Descript (push mp3 to the repo, use the raw URL) and pick the take whose words match the script exactly.
  - **Order of work (always):** script → VO → VO timings (Descript + ffmpeg silencedetect) → pick footage per line → cut shots on the VO pauses → supers/titles timed to the words → music under the VO (sidechain-ducked) → check frames every 0.5 s → schedule.
  - **Engine:** `engine/reel27.py` (copy it per day: edit SHOTS, PHRASES, HOOK/NAME/COUNTERS/STAMP/MILKDAY timings and texts). Maps: `engine/india_map.py` (datameet official boundaries) — whenever a state/city is named, show it on the India map (state in gold, pin on the city, route line when the story moves between places). Map and real-photo shots hide the "Representative footage" label.
  - **Realism:** the strongest shot is a real photo of the actual person/event. List what is needed (person photo, ceremony photo, venue) in the daily report; the owner drops them in `media/<date>/` with the source. Never show a place the story didn't happen at (e.g. a railway station for an award given at a hall). Add a context card for the day/occasion (e.g. National Milk Day, Kurien's birth anniversary) when it is verified.
  - **Build like a pro:** hook text on frame 0, shots of about 2 s, word-pop captions with gold keywords, number counters, name lower-third, map pins, animated end card with follow prompt, 1080x1920 30 fps, music + VO BAKED INTO the mp4 (`engine/piano_bed.py` + ffmpeg; never Metricool audioConfiguration).
  - Caption line: "Representative footage, not of the farm/people named." when stock is used.
  - If `posts/<date>/reel_plan.md` already exists (prepared the night before), use its topic, verified facts and script instead of picking a new Reel topic. If it says **STATUS: SCHEDULED**, do not build another Reel that day.
- Story: the carousel cover PNG, or a teal text card.
- The Python engine in `engine/` is a fallback only (if Canva fails, so the day still posts).

### Logo variants (pick by background, never let the logo blend in)
Canva retypes the logo as text, so after generating, delete the logo element and `insert_fill` the right asset (never `update_fill`, it crops):

| Background | Canva asset | File |
|---|---|---|
| Teal, dark gradient or dark photo | `MAHb1uHyC8A` (white horizontal) | assets/logos/…_horizontal_white |
| Warm Gold #E8B04B page (takeaway/CTA) | `MAHb1iq86X4` (on-gold: teal arcs, white sun) | assets/logos/…_horizontal_on-gold |
| White / cream / pale page | `MAHb1qWkkY8` (mono teal) or `MAHb1lv-vV8` (colour) | assets/logos/…_horizontal_mono-teal |
| Busy, bright photo | `MAHb1jgif4Q` (mono white) | assets/logos/…_horizontal_mono-white |

Rule: the gold sun must never sit on gold, and teal text must never sit on teal. Check every page's thumbnail before export.

## Adobe (connected 27 Nov 2026, signed-in account) — how to use it, and what never to use
Call `adobe_mandatory_init` once before any Adobe tool.

**Use (real photos only):**
- **Adobe Stock as photo source #1** for India-specific scenes: `asset_search` with `entityScope: "StockAsset"`, `filters: {contentType: "Photo", pricing: "free"}`. **Only pick results with `isGenTech: false`** (Adobe's own flag for AI-made content — anything `true` is banned). Prefer titles naming India/Indian. License with `asset_license_and_download_stock` (size "1600"); free assets license instantly, but if a call returns `confirmationRequired` (a paid quote), do NOT confirm — pick another photo. Record `AdobeStock_<id>` in batch.json `photos`.
- **Photoshop polish (non-generative):** `image_apply_auto_tone`, `image_apply_adjustments`, `image_crop_and_resize`, `image_auto_straighten` on the licensed URL to fix flat or dark photos before they go into Canva.
- **Reels:** `media_enhance_speech` to clean a voiceover take; `video_resize` / `video_render_frame` for checks.

**Never use (AI):** `image_generative_expand`, `image_fill_area`, Firefly / `create_firefly_board`, `GenAIAsset` search, any Stock result with `isGenTech: true`, Express generated imagery.

**Handoff (tested 27 Nov, works):** license → `curl` the licensed URL into the sandbox scratch folder (NOT into the repo — the repo is public and Stock licences don't allow redistributing the file) → `mcp__Canva__create-upload-url` → `curl -X POST -H "Content-Type: application/octet-stream" --data-binary @photo.jpg <uploadUrl>` → returns `mediaId` to use in `insert_fill`. Photoshop edits (auto-tone etc.) return a `photoshop-api.adobe.io` short URL that redirects to `cis-utils-storage-prod.s3-accelerate.amazonaws.com`; if that host is still blocked (403), skip the Photoshop step and upload the licensed original. Never commit Adobe Stock files to the repo; only the finished post PNGs go there.

## Accuracy (posts go out with no human review)
- Every name, number, place and date must be confirmed in a source you actually read: the primary source (company / NGO / government release, PIB, Parliament reply, csr.gov.in) or **two** independent reliable publications. If you can't confirm it, drop it — don't soften it.
- Never invent quotes, numbers or rankings. Quotes only word-for-word from a reliable source.
- Mention an Instagram handle only if confirmed from the person's/company's official page; otherwise plain names.
- Rewrite in your own words. Never copy sentences, layouts or photos from other pages. Photos: free-licence Unsplash/Pexels only, always labelled representative in the caption.

## Daily mix (4 feed posts + 1 Reel at 19:30 on its own topic + 1 Story)
| Time (IST) | What | Format |
|---|---|---|
| 08:30 | Unsung hero or good-news card | `hero` |
| 12:30 | Companies doing good (foundation / company programme with results) | `carousel` |
| 17:30 | By the numbers / explainer (government data, reports) | `data` |
| 20:45 | Changemaker story — Maharashtra first when possible | `carousel` → Story at 21:05 |

Sunday: the 17:30 slot becomes a "Good news this week" `data` or `hero` roundup of the week's posts.

**FRESH + TRENDING FIRST (owner's standing rule, 26 Nov 2026).** Every topic must be news from the last 48 hours (72 h at most), with the event or announcement itself happening in that window — not an old story that a site re-published. Old evergreen stories (e.g. "he started in 2004…") only if a NEW development happened in the last 48 h, and the hook leads with that new development. Prefer stories that are trending right now: covered by several outlets today, trending on Google News / X / Instagram, or being posted by big Indian news pages (e.g. @unfoldingbharat style "BREAKING: Egypt invites Indian companies to set up factories" — fresh, India-positive, big numbers). Search with today's date ("today", "this week", the date) and check every article's publish date before picking.

Story scoring when choosing (0–100): freshness + trending 35 · human face / emotion 20 · positive outcome with clear numbers 20 · India-pride / national interest 10 · pillar fit + Maharashtra bonus 15. Anything older than 72 h scores 0 and is dropped. Never repeat a person, company programme or village from the last 60 days (check `posts/*/batch.json`).

Hooks for fresh news may use a "BREAKING" / "JUST IN" / "BIG NEWS" tag pill when the news is under 24 h old.

## Where to look
- Data: csr.gov.in (National CSR Data Portal), PIB releases (Ministry of Corporate Affairs and others), sansad.in Parliament replies, data.gov.in, company annual / BRSR reports.
- Company good work: India CSR (indiacsr.in), The CSR Journal, CSR Universe, CSRBOX, ET ESG, BusinessLine, company & foundation newsrooms (Tata Trusts, Tata Steel Foundation, Infosys Foundation, Reliance Foundation, HDFC Parivartan, Azim Premji Foundation, SBI Foundation, Ashok Leyland Foundation, etc.).
- Changemakers (leads only — confirm and rewrite): The Better India, The Logical Indian, YourStory SocialStory, Down To Earth, Mongabay India, Village Square, The Hindu, Indian Express.
- Maharashtra: Lokmat, Loksatta, Sakal, Maharashtra Times, The Hitavada, Free Press Journal.

## Batch file — `posts/YYYY-MM-DD/batch.json`
See `engine/samples.json` and `posts/2026-11-25/batch.json` (the reference batch). Fields:
- common: `id` (p1..p4), `time`, `format` (`hero` | `carousel` | `data`), `pillar`, `tag`, `icon` (`star sun heart book leaf drop people school health`), `source`, `caption`
- `hero`: `headline`, `body` (≤ ~45 words)
- `data`: `stat` (short, e.g. "₹12,134 cr"), `stat_label`, `headline`, `points` (≤3 short lines)
- `carousel`: `headline`, `sub`, `slides` (exactly 3: `kicker`, `title`, `body`, and either `icon` or `stat`+`stat_label`), `takeaway`; `reel: true` + `reel_time` + `reel_caption`; optional `story: true` + `story_time`
- `*words*` = gold highlight (one phrase per headline/title). Headlines ≤ 14 words; slide bodies ≤ 40 words.

Captions: 1-line hook with one emoji, 2–4 lines of story, a warm question or "Save this 🔖 / Tag someone", `Source(s): …`, 5–8 hashtags always starting with `#TheImpactStory`.

## Render
```
python3 engine/build.py posts/YYYY-MM-DD/batch.json      # PNGs + manifest.json (+ <id>_story.png)
python3 engine/reel.py  posts/YYYY-MM-DD/batch.json p2   # p2_reel.mp4 (soft pad music, ~21 s)
python3 engine/reel.py  posts/YYYY-MM-DD/batch.json p4
```
Needs: python3, fontTools, Pillow, rsvg-convert, ffmpeg. Fonts are in `engine/fonts`. The renderer raises an error if text doesn't fit — shorten the text, never shrink the design. Open every PNG with Read before publishing.

Public media URL pattern (repo name ends with a dot):
`https://raw.githubusercontent.com/thepostmanstudio-spec/impactstory-posts./main/posts/YYYY-MM-DD/<file>`

## Brand
Warm Gold `#E8B04B` · Deep Teal `#005B50` · Icon Teal `#086654` · White. Poppins. Logos, highlight covers, profile pictures and the Facebook cover are in `assets/`.

## Lessons log (newest first — every daily run adds at most one dated lesson and applies all of them)
- 2026-11-27: Adobe Stock search returns India-specific free photos with an `isGenTech` AI flag — use it to find honest, non-AI photos (see "Adobe" section); file handoff still needs the owner's domain allowlist.
- 2026-11-27: Pexels pages state location and pixel size, so Pexels finds verified Indian photos faster than Unsplash (many Unsplash India results are paid Unsplash+). Check every thumbnail for screens, TV bezels, banners and shirts with text or brand names; crop them out or swap the photo. Prefer photos whose page says the location is India.
- 2026-11-27: Canva export URLs expired at ~07:30 IST, before most post times. Always host the PNGs in the repo and give Metricool the raw GitHub URLs.
- 2026-11-27: Two days of data: Reels brought ~70% of reach; feed posts reached 0–2 accounts each. The 19:30 Reel is the growth lever — protect its quality first, and remind the owner to share it to Story.
- 2026-11-27: Research is fastest with 4 parallel sub-agents (one per slot) plus 1 photo agent; give each the exclusion list from the last 60 days.
