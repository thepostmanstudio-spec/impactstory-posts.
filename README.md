# The Impact Story — daily posts engine

Instagram + Facebook page **@theimpactstory** — inspiring stories of India's changemakers, companies doing good and good news. Owner: Mogli Media. Auto-published every day through Metricool (brand "The Impact Story", **blogId 8316520**, timezone Asia/Calcutta).

## Tone — read this first
Warm, inspiring and celebratory, like The Better India. Companies must see us as a friend who showcases their good work, never as a watchdog.
- Never: "proof", "exposed", "audit", "only X% spent", who spent the least, unspent funds, controversies, or anything that makes a company, NGO, person or government look bad.
- Numbers are used to **celebrate** impact (lives reached, villages helped, before → after).
- No politics, no religion-based angles, no unverified medical claims, no tragedy-led hooks. Personal hardships only if the source makes them central, and gently.
- Say "social good" / "good work" rather than "CSR" in headlines (CSR is fine in sources).
- Credit the person, company or NGO in every caption, and name where the story came from.

## Accuracy (posts go out with no human review)
- Every name, number, place and date must be confirmed in a source you actually read: the primary source (company / NGO / government release, PIB, Parliament reply, csr.gov.in) or **two** independent reliable publications. If you can't confirm it, drop it — don't soften it.
- Never invent quotes, numbers or rankings. Quotes only word-for-word from a reliable source.
- Mention an Instagram handle only if confirmed from the person's/company's official page; otherwise plain names.
- Rewrite in your own words. Never copy sentences, layouts or photos from other pages. Graphic visuals only (the engine draws them) — no photos.

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
