import asyncio
import os
from app.services.cms_service import (
    get_settings,
    get_services,
    get_main_services,
    get_service_packages,
    get_faqs,
    get_locations,
    get_blogs,
    get_car_makes,
    get_car_models,
    get_testimonials,
    get_team,
    get_cta,
    get_homepage,
)

_INTENTS: dict[str, list[str]] = {
    "services": [
        "service", "repair", "fix", "maintenance", "oil", "brake", "tire",
        "engine", "transmission", "suspension", "battery", "diagnostic",
        "inspection", "detailing", "alignment", "filter", "fluid",
        "offer", "provide", "what can", "available", "list", "do you do",
    ],
    "pricing": [
        "price", "cost", "how much", "package", "fee", "rate", "charge",
        "afford", "expensive", "cheap", "quote",
    ],
    "location": [
        "location", "address", "where", "branch", "shop", "near me",
        "directions", "find you",
    ],
    "hours": [
        "hour", "open", "close", "closing", "timing", "schedule",
        "weekend", "weekday", "sunday", "monday", "saturday",
    ],
    "booking": [
        "book", "appointment", "schedule", "reserve", "slot", "available",
        "when can", "drop off", "make an appointment", "set up",
    ],
    "faq": [
        "faq", "frequently", "question", "how do", "what is", "can i",
        "do you", "tell me", "explain", "wonder",
    ],
    "blog": [
        "blog", "article", "post", "read", "news", "tip", "guide",
        "learn", "advice", "latest", "recent",
    ],
    "appointment": [
        "book", "appointment", "schedule", "car make", "car model",
        "vehicle", "year", "plate", "vin", "date", "time", "slot",
        "reserve", "drop off",
    ],
    "contact": [
        "contact", "email", "phone", "call", "reach", "talk to",
        "speak", "number", "social", "instagram", "facebook",
    ],
    "testimonials": [
        "review", "testimonial", "rating", "feedback", "customer say",
        "experience", "recommend", "star", "opinion", "trust",
    ],
    "team": [
        "team", "staff", "who works", "mechanic", "technician", "person",
        "employee", "expert", "specialist", "founder",
    ],
    "about": [
        "about", "company", "who are you", "history", "mission",
        "vision", "background", "established",
    ],
}


def _detect_intents(message: str) -> set[str]:
    msg = message.lower()
    found: set[str] = set()
    for intent, keywords in _INTENTS.items():
        if any(kw in msg for kw in keywords):
            found.add(intent)
    found.add("contact")
    return found


def _fmt_services(services: list[dict], site_url: str = "") -> str:
    lines = ["--- Services ---"]
    for s in services[:12]:
        name = s.get("serviceName", "")
        slug = s.get("slug", "")
        desc = (s.get("serviceDescription") or s.get("description") or "").strip()
        included = ", ".join(
            i.get("text", "") for i in s.get("included", []) if i.get("text")
        )
        line = f"• {name}"
        if desc:
            line += f": {desc[:120]}"
        if included:
            line += f" | Includes: {included[:100]}"
        if site_url and slug:
            line += f" | Link: {site_url}/services/{slug}"
        lines.append(line)
    return "\n".join(lines)


def _fmt_main_services(main_services: list[dict]) -> str:
    lines = ["--- Main Service Categories ---"]
    for ms in main_services:
        title = ms.get("title", "")
        desc = ms.get("description", "")
        lines.append(f"• {title}: {desc[:100]}")
    return "\n".join(lines)


def _fmt_packages(packages: list[dict]) -> str:
    lines = ["--- Packages & Pricing ---"]
    for p in packages[:12]:
        name = p.get("packageName", "")
        price = p.get("price")
        desc = (p.get("description") or "").strip()
        props = ", ".join(
            i.get("prop", "") for i in p.get("included", []) if i.get("prop")
        )
        line = f"• {name}"
        if price is not None:
            line += f" — ${price}"
        if desc:
            line += f": {desc[:80]}"
        if props:
            line += f" | Includes: {props[:80]}"
        lines.append(line)
    return "\n".join(lines)


def _fmt_locations(locations: list[dict]) -> str:
    lines = ["--- Locations ---"]
    for loc in locations:
        lines.append(f"• {loc.get('name', '')}")
    return "\n".join(lines)


def _fmt_faqs(faqs: list[dict]) -> str:
    lines = ["--- FAQs ---"]
    for faq in faqs[:8]:
        q = faq.get("question", "")
        a = (faq.get("answer") or "").strip()
        if q and a:
            lines.append(f"Q: {q}\nA: {a[:200]}")
    return "\n".join(lines)


def _fmt_blogs(blogs: list[dict], site_url: str = "") -> str:
    lines = ["--- Blog Posts ---"]
    for b in blogs[:8]:
        title = b.get("title", "")
        slug = b.get("slug", "")
        line = f"• {title}"
        if site_url and slug:
            line += f" | Link: {site_url}/blog/{slug}"
        lines.append(line)
    return "\n".join(lines)


def _fmt_car_makes(car_makes: list[dict]) -> str:
    names = [c.get("name", "") for c in car_makes if c.get("name")]
    return "--- Supported Car Makes ---\n" + ", ".join(names)


def _fmt_testimonials(testimonials: list[dict]) -> str:
    lines = ["--- Customer Reviews ---"]
    for t in testimonials[:6]:
        name = t.get("name", "")
        review = (t.get("testimonial") or "").strip()
        rating = t.get("rating")
        line = f"• {name}"
        if rating:
            line += f" ({rating}/5 stars)"
        if review:
            line += f": {review[:150]}"
        lines.append(line)
    return "\n".join(lines)


def _fmt_team(team: list[dict]) -> str:
    lines = ["--- Our Team ---"]
    for p in team:
        name = p.get("name", "")
        profession = p.get("profession", "")
        quote = p.get("quote", "")
        line = f"• {name}"
        if profession:
            line += f" — {profession}"
        if quote:
            line += f': "{quote[:100]}"'
        lines.append(line)
    return "\n".join(lines)


def _fmt_car_models(car_models: list[dict]) -> str:
    lines = ["--- Supported Car Models ---"]
    by_make: dict[str, list[str]] = {}
    for cm in car_models:
        model_name = cm.get("name", "")
        make = cm.get("make")
        make_name = make.get("name", "Unknown") if isinstance(make, dict) else "Other"
        by_make.setdefault(make_name, []).append(model_name)
    for make, models in list(by_make.items())[:10]:
        lines.append(f"• {make}: {', '.join(models[:8])}")
    return "\n".join(lines)


def _fmt_appointment_info(company_name: str, locations: list[dict], car_makes: list[dict]) -> str:
    lines = [f"--- Booking an Appointment ---"]
    lines.append(f"To book an appointment with {company_name}, you need:")
    lines.append("• First name, last name, email, phone number")
    lines.append("• Car make, car model, car year, licence plate")
    lines.append("• Preferred date and time")
    lines.append("• Preferred location and services")
    if locations:
        loc_names = ", ".join(l.get("name", "") for l in locations)
        lines.append(f"• Available locations: {loc_names}")
    if car_makes:
        makes = ", ".join(c.get("name", "") for c in car_makes[:10])
        lines.append(f"• Supported car makes include: {makes}")
    return "\n".join(lines)


async def build_context(message: str) -> tuple[str, str]:
    """Returns (company_name, context_string) — both pulled from CMS."""
    intents = _detect_intents(message)

    coros: dict[str, object] = {"settings": get_settings()}

    needs_services = intents & {"services", "pricing", "booking", "appointment"}
    if needs_services:
        coros["services"] = get_services()
        coros["main_services"] = get_main_services()

    if "pricing" in intents:
        coros["packages"] = get_service_packages()

    if "location" in intents or "booking" in intents or "appointment" in intents:
        coros["locations"] = get_locations()

    if "faq" in intents:
        coros["faqs"] = get_faqs()

    if "blog" in intents:
        coros["blogs"] = get_blogs()

    if "appointment" in intents or "booking" in intents:
        coros["car_makes"] = get_car_makes()
        coros["car_models"] = get_car_models()

    if "testimonials" in intents:
        coros["testimonials"] = get_testimonials()

    if "team" in intents:
        coros["team"] = get_team()

    if "about" in intents:
        coros["homepage"] = get_homepage()

    keys = list(coros.keys())
    results = await asyncio.gather(*coros.values(), return_exceptions=True)
    data: dict = {
        k: (v if not isinstance(v, Exception) else None)
        for k, v in zip(keys, results)
    }

    settings = data.get("settings") or {}
    company_name = (
        settings.get("companyName")
        or os.getenv("COMPANY_NAME")
        or "FixinMoto"
    )
    site_url = os.getenv("SITE_URL", "").rstrip("/")

    parts: list[str] = [f"=== {company_name} Company Context ==="]

    # Always include key page links so AI can reference them
    if site_url:
        parts.append(
            f"--- Website Page Links ---\n"
            f"Home: {site_url}\n"
            f"All Services: {site_url}/services\n"
            f"Book Appointment: {site_url}/appointment\n"
            f"Blog: {site_url}/blog\n"
            f"Contact: {site_url}/contact\n"
            f"Locations: {site_url}/locations"
        )

    if settings:
        parts.append(f"Company: {company_name}")
        if settings.get("phone"):
            parts.append(f"Phone: {settings['phone']}")
        if settings.get("contactEmail"):
            parts.append(f"Email: {settings['contactEmail']}")
        if settings.get("address"):
            parts.append(f"Address: {settings['address']}")
        if settings.get("website"):
            parts.append(f"Website: {settings['website']}")
        hours = settings.get("serviceHours") or {}
        if hours.get("weekDays"):
            parts.append(f"Mon–Fri: {hours['weekDays']}")
        if hours.get("weekEnds"):
            parts.append(f"Sat–Sun: {hours['weekEnds']}")

    if data.get("main_services"):
        parts.append(_fmt_main_services(data["main_services"]))

    if data.get("services"):
        parts.append(_fmt_services(data["services"], site_url))

    if data.get("packages"):
        parts.append(_fmt_packages(data["packages"]))

    if data.get("locations"):
        parts.append(_fmt_locations(data["locations"]))

    if data.get("faqs"):
        parts.append(_fmt_faqs(data["faqs"]))

    if data.get("blogs"):
        parts.append(_fmt_blogs(data["blogs"], site_url))

    if "appointment" in intents or "booking" in intents:
        parts.append(_fmt_appointment_info(
            company_name,
            data.get("locations") or [],
            data.get("car_makes") or [],
        ))
        if data.get("car_models"):
            parts.append(_fmt_car_models(data["car_models"]))

    if data.get("testimonials"):
        parts.append(_fmt_testimonials(data["testimonials"]))

    if data.get("team"):
        parts.append(_fmt_team(data["team"]))

    homepage = data.get("homepage") or {}
    if homepage:
        hero_title = homepage.get("heroTitle", "")
        hero_tagline = homepage.get("heroTagline", "")
        if hero_title or hero_tagline:
            parts.append(f"--- About {company_name} ---\n{hero_title}\n{hero_tagline}")

    return company_name, "\n\n".join(parts)
