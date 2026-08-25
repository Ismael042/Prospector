from urllib.parse import urlparse

# Domínios que aparecem no campo "site" mas não são um site próprio do negócio
# (página de rede social, link-in-bio, ou o placeholder gerado pelo Google Business
# Profile) - contam como lead sem site pra fins de prospecção.
WEAK_DOMAINS = {
    "facebook.com",
    "instagram.com",
    "linktr.ee",
    "linktree.com",
    "wa.me",
    "whatsapp.com",
    "business.site",
    "yelp.com",
}


def _domain(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def _is_weak_domain(domain: str) -> bool:
    return any(domain == weak or domain.endswith(f".{weak}") for weak in WEAK_DOMAINS)


def has_real_website(place: dict) -> bool:
    website = place.get("website")
    if not website:
        return False
    return not _is_weak_domain(_domain(website))
