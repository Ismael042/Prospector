import base64
import hashlib
import html
from string import Template

ACCENT_PALETTE = [
    ("#B5502E", "#F4E4DB"),  # terracota
    ("#2F6B4F", "#DFEAE3"),  # verde-floresta
    ("#2C4A7C", "#DEE6F0"),  # azul-tinta
    ("#6B3F5C", "#EBE0E7"),  # ameixa
    ("#A8792E", "#F1E7D3"),  # ocre
]

GOOGLE_FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;'
    '0,9..144,600;1,9..144,500&family=Public+Sans:wght@400;500;600;700&display=swap" '
    'rel="stylesheet">'
)

# Usa string.Template ($var) em vez de .format()/f-string porque CSS esta cheio
# de chaves literais ({ }) que colidiriam com a sintaxe de formatacao.
CSS_TEMPLATE = Template(
    """
:root {
  --bg: #FBFAF7;
  --ink: #1C2230;
  --ink-soft: #565C68;
  --border: #E7E4DD;
  --accent: $accent;
  --accent-soft: $accent_soft;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--ink);
  font-family: "Public Sans", -apple-system, "Segoe UI", sans-serif;
  -webkit-font-smoothing: antialiased;
  line-height: 1.5;
}
h1, h2, h3 {
  font-family: "Fraunces", Georgia, serif;
  font-weight: 600;
  line-height: 1.08;
  letter-spacing: -0.01em;
  text-wrap: balance;
  margin: 0;
}
a { color: inherit; }
.wrap { max-width: 1120px; margin: 0 auto; padding: 0 32px; }

header.site { padding: 28px 0; border-bottom: 1px solid var(--border); }
header.site .wrap { display: flex; align-items: center; justify-content: space-between; gap: 24px; }
.brand { font-family: "Fraunces", serif; font-weight: 600; font-size: 1.1rem; }
nav.site a {
  text-decoration: none; color: var(--ink-soft); font-size: 0.92rem;
  font-weight: 500; margin-left: 28px;
}

.hero { padding: 76px 0 88px; }
.hero .wrap { display: grid; gap: 56px; align-items: center; }
.hero.hero--with-photo .wrap { grid-template-columns: 1.05fr 1fr; }
.hero.hero--no-photo .wrap { grid-template-columns: 1fr; max-width: 680px; }

.eyebrow {
  display: inline-block; font-size: 0.76rem; font-weight: 600; letter-spacing: 0.09em;
  text-transform: uppercase; color: var(--accent); margin-bottom: 16px;
}
.hero h1 { font-size: clamp(2.1rem, 3.6vw, 3.15rem); margin-bottom: 18px; }
.hero .lede { font-size: 1.12rem; color: var(--ink-soft); max-width: 46ch; margin: 0 0 26px; }

.rating-line {
  display: flex; align-items: baseline; gap: 6px; font-size: 0.94rem; color: var(--ink-soft);
  font-variant-numeric: tabular-nums; margin: 0 0 30px;
}
.rating-line strong { color: var(--ink); font-weight: 700; }

.cta {
  display: inline-block; padding: 14px 30px; background: var(--ink); color: #FBFAF7;
  text-decoration: none; font-weight: 600; font-size: 0.95rem; border-radius: 3px;
  transition: background 0.15s ease;
}
.cta:hover { background: var(--accent); }

.hero-photo img { width: 100%; height: 100%; aspect-ratio: 4 / 5; object-fit: cover; border-radius: 4px; display: block; }

section.about { padding: 68px 0 76px; border-top: 1px solid var(--border); }
.about .wrap { max-width: 880px; }
.about h2 { font-size: 1.7rem; margin-bottom: 18px; }
.about p { font-size: 1.04rem; color: var(--ink-soft); max-width: 64ch; margin: 0 0 44px; }

.highlights { display: grid; grid-template-columns: repeat(3, 1fr); gap: 36px; }
.highlight { border-top: 2px solid var(--accent); padding-top: 16px; }
.highlight h3 { font-size: 1.02rem; font-weight: 600; font-family: "Public Sans", sans-serif; }

footer.contact { background: var(--ink); color: #F1EFEA; padding: 56px 0; }
footer.contact .wrap { display: flex; flex-wrap: wrap; gap: 32px; justify-content: space-between; align-items: flex-end; }
footer.contact h2 { color: #fff; font-size: 1.4rem; margin-bottom: 10px; }
footer.contact .details { font-size: 0.95rem; color: #C7C4BC; line-height: 1.7; }
footer.contact .cta { background: var(--accent); }
footer.contact .cta:hover { background: #fff; color: var(--ink); }

@media (max-width: 760px) {
  .hero.hero--with-photo .wrap { grid-template-columns: 1fr; }
  .hero-photo { order: -1; }
  .highlights { grid-template-columns: 1fr; gap: 28px; }
  nav.site { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .cta { transition: none; }
}
"""
)


def _pick_accent(place_id: str) -> tuple[str, str]:
    digest = hashlib.md5((place_id or "").encode()).hexdigest()
    return ACCENT_PALETTE[int(digest, 16) % len(ACCENT_PALETTE)]


def _rating_line_html(lead: dict) -> str:
    rating = lead.get("rating")
    if not rating:
        return ""
    review_count = lead.get("review_count")
    reviews = f" · {html.escape(str(review_count))} reviews" if review_count else ""
    return f'<p class="rating-line">★ <strong>{html.escape(str(rating))}</strong>{reviews}</p>'


def render_landing_page(
    lead: dict,
    copy,
    photo_bytes: bytes | None,
    photo_content_type: str | None,
    category: str,
) -> str:
    esc = html.escape
    accent, accent_soft = _pick_accent(lead.get("place_id", ""))
    css = CSS_TEMPLATE.substitute(accent=accent, accent_soft=accent_soft)

    name = esc(lead.get("name") or "")

    if photo_bytes:
        b64 = base64.b64encode(photo_bytes).decode("ascii")
        photo_html = (
            f'<div class="hero-photo"><img src="data:{photo_content_type};base64,{b64}" '
            f'alt="{name}" loading="lazy"></div>'
        )
        hero_class = "hero hero--with-photo"
    else:
        photo_html = ""
        hero_class = "hero hero--no-photo"

    highlights_html = "".join(
        f"<div class=\"highlight\"><h3>{esc(item)}</h3></div>" for item in copy.highlights
    )

    address = lead.get("address") or ""
    phone = lead.get("phone") or ""
    address_line = f"<div>{esc(address)}</div>" if address else ""
    phone_line = f"<div>{esc(phone)}</div>" if phone else ""
    cta_label = esc(copy.cta_label)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name}</title>
{GOOGLE_FONTS_LINK}
<style>{css}</style>
</head>
<body>
  <header class="site">
    <div class="wrap">
      <div class="brand">{name}</div>
      <nav class="site">
        <a href="#about">About</a>
        <a href="#contact">Contact</a>
      </nav>
    </div>
  </header>

  <section class="{hero_class}">
    <div class="wrap">
      <div class="hero-copy">
        <span class="eyebrow">{esc(category)}</span>
        <h1>{esc(copy.headline)}</h1>
        <p class="lede">{esc(copy.subheadline)}</p>
        {_rating_line_html(lead)}
        <a class="cta" href="#contact">{cta_label}</a>
      </div>
      {photo_html}
    </div>
  </section>

  <section class="about" id="about">
    <div class="wrap">
      <h2>About</h2>
      <p>{esc(copy.about_paragraph)}</p>
      <div class="highlights">
        {highlights_html}
      </div>
    </div>
  </section>

  <footer class="contact" id="contact">
    <div class="wrap">
      <div>
        <h2>Visit or get in touch</h2>
        <div class="details">
          {address_line}
          {phone_line}
        </div>
      </div>
      <a class="cta" href="#contact">{cta_label}</a>
    </div>
  </footer>
</body>
</html>
"""
