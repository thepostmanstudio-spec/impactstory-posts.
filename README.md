# The Impact Story — daily posts engine

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
- `export-design` PNG width 1080, then schedule in Metricool **right away** (Canva links expire in a few hours).
- Metricool `instagramData.isAiGenerated: false`. No "AI image" label. Caption line: "Representative photo(s), not of the people named." (or "Representative photos." when no person is named).
- Reel: export the checked carousel as mp4 (`export-design` type mp4, quality "vertical_1080p"). Canva's mp4 is silent, so schedule as REEL with `instagramData.audioConfiguration: {"audioId": "2477944699150252", "audioVolume": 60}` ("Peaceful Piano", Dr. Pheel; another calm instrumental is fine, never a beat). Never post a silent Reel.
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

## Accuracy (posts go out with no human review)
- Every name, number, place and date must be confirmed in a source you actually read: the primary source (company / NGO / government release, PIB, Parliament reply, csr.gov.in) or **two** independent reliable publications. If you can't confirm it, drop it — don't soften it.
- Never invent quotes, numbers or rankings. Quotes only word-for-word from a reliable source.
- Mention an Instagram handle only if confirmed from the person's/company's official page; otherwise plain names.
- Rewrite in your own words. Never copy sentences, layouts or photos from other pages. Photos: free-licence Unsplash/Pexels only, always labelled representative in the caption.

## Daily mix (4 feed posts + 2 Reels + 1 Story)
| Time (IST) | What | Format |
|---|---|---|
| 08:30 | Unsung hero or good-news card | `hero` |
| 12:30 | Companies doing good (foundation / company programme with results) | `carousel` → also Reel at 13:30 |
| 17:30 | By the numbers / explainer (government data, reports) | `data` |
| 20:45 | Changemaker story — Maharashtra first when possible | `carousel` → Reel at 19:30, Story at 21:05 |

Sunday: the 17:30 slot becomes a "Good news this week" `data` or `hero` roundup of the week's posts.

Story scoring when choosing (0–100): human face / emotion 30 · positive outcome with numbers 20 · freshness 20 · not already viral on big pages 15 · pillar fit + Maharashtra bonus 15. Never repeat a person, company programme or village from the last 60 days (check `posts/*/batch.json`).

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
