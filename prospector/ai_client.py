from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

MODEL = "claude-opus-5"

PROMPT_TEMPLATE = """You are writing outreach material to help a freelance web
developer land a new client. The lead below is a real local business found on
Google Maps that has no real website of its own.

Business: {name}
Category: {category}
Address: {address}
Google rating: {rating} ({review_count} reviews)

Write two things:

1. A short, professional cold email (in English) pitching a custom website for
   this business. Reference at least one real detail above (e.g. the rating or
   review count) as a hook — do not write generic filler. Keep it under 150
   words. No markdown, plain text body.

2. A complete, self-contained HTML mockup of a one-page landing site for this
   business, as if it already existed. Inline all CSS in a <style> tag, no
   external stylesheets, fonts, images, or scripts. Include: a hero section
   with the business name and category, a short services/about section
   appropriate for this type of business, and a contact section using the
   real address and, if useful, mentioning the Google rating as social proof.
   Modern, clean, mobile-friendly design.
"""


class LeadPitch(BaseModel):
    email_subject: str
    email_body: str
    landing_page_html: str


def generate_pitch(lead: dict, category: str) -> tuple[LeadPitch, dict]:
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
        output_format=LeadPitch,
    )
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return response.parsed_output, usage
