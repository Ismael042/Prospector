from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

MODEL = "claude-opus-5"

PROMPT_TEMPLATE = """You are a copywriter helping a freelance web developer pitch
a custom website to a real local business. The business below has no website of
its own — only a Google Maps listing.

Business: {name}
Category: {category}
Address: {address}
Google rating: {rating} ({review_count} reviews)

Write, in English:

1. A short, professional cold email pitching a custom website. Reference at
   least one real detail above (rating or review count) as a hook — no generic
   filler. Under 150 words, plain text body.

2. Copy for a one-page website mockup of this business, as if it already
   existed:
   - headline: a short, specific headline (not a generic tagline)
   - subheadline: one supporting sentence
   - about_paragraph: 2-3 sentences about the business, in a warm but
     professional tone appropriate to its category
   - highlights: exactly 3 short phrases (3-6 words each) naming concrete
     services or features specific to this type of business — not generic
     ("Quality service") filler
   - cta_label: 2-4 words for a call-to-action button, appropriate to the
     category (e.g. "Book a Table", "Get a Free Quote")
"""


class LeadCopy(BaseModel):
    email_subject: str
    email_body: str
    headline: str
    subheadline: str
    about_paragraph: str
    highlights: list[str]
    cta_label: str


def generate_pitch(lead: dict, category: str) -> tuple[LeadCopy, dict]:
    prompt = PROMPT_TEMPLATE.format(
        name=lead["name"],
        category=category,
        address=lead.get("address") or "address not listed",
        rating=lead.get("rating") or "no rating yet",
        review_count=lead.get("review_count") or 0,
    )

    response = Anthropic().messages.parse(
        model=MODEL,
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
        output_format=LeadCopy,
    )
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return response.parsed_output, usage
