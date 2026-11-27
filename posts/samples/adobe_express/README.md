# Adobe Express sample (27 Nov 2026)
- Cover for the 27 Nov Sindhudurg women farmers post, rebuilt with the Adobe connector.
- Photo: Adobe Stock 216554106, "Indian rural women farming paddy" (free tier, isGenTech false, licensed 27 Nov). The Stock file itself is NOT in the repo.
- Built as HTML (Poppins via Adobe Fonts kit jvk3nmj), then imported into Adobe Express as an editable design (v2): https://new.express.adobe.com/id/urn:aaid:sc:AP:493e1756-5d60-49e0-a7c8-c8d153813026
- Lessons from the test:
  - Express can't fetch images from raw.githubusercontent.com, so the logo must go in as an inline data: PNG (a 300x60, 16-colour PNG is about 3 KB).
  - `right:` positioning gets converted wrongly; use left + width + text-align:right.
  - The sandbox can't reach at.adobe.com (Adobe's upload host), so the HTML is sent inline with the photo as the licensed Stock URL.
