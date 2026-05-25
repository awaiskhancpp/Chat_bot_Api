import asyncio
from app.services.cms_service import (
    get_settings,
    get_services,
    get_main_services,
    get_service_packages,
    get_faqs,
    get_locations,
)

# Maps intent → trigger keywords
_INTENTS: dict[str, list[str]] = {
    "services": [
        "service", "repair", "fix", "maintenance", "oil", "brake", "tire",
        "engine", "transmission", "suspension", "battery", "diagnostic",
        "inspection", "detailing", "alignment", "filter", "fluid",
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
        "when can", "drop off",
    ],
    "faq": [
        "faq", "question", "how do", "what is", "can i", "do you",
        "tell me", "explain",
    ],
    "contact": [
        "contact", "email", "phone", "call", "reach", "talk to",
        "speak", "number",
    ],
}


def _detect_intents(message: str) -> set[str]:
    msg = message.lower()
    found: set[str] = set()
    for intent, keywords in _INTENTS.items():
        if any(kw in msg for kw in keywords):
            found.add(intent)
    # settings (contact + hours) are always fetched
    found.add("contact")
    return found


def _fmt_services(services: list[dict]) -> str:
    lines = ["--- Services ---"]
    for s in services[:12]:
        name = s.get("serviceName", "")
        desc = (s.get("serviceDescription") or s.get("description") or "").strip()
        included = ", ".join(
            i.get("text", "") for i in s.get("included", []) if i.get("text")
        )
        line = f"• {name}"
        if desc:
            line += f": {desc[:120]}"
        if included:
            line += f" | Includes: {included[:100]}"
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


async def build_context(message: str) -> str:
    intents = _detect_intents(message)

    # Decide which CMS calls to make
    coros: dict[str, object] = {"settings": get_settings()}

    needs_services = intents & {"services", "pricing", "booking"}
    if needs_services:
        coros["services"] = get_services()
        coros["main_services"] = get_main_services()

    if "pricing" in intents:
        coros["packages"] = get_service_packages()

    if "location" in intents or "booking" in intents:
        coros["locations"] = get_locations()

    if "faq" in intents:
        coros["faqs"] = get_faqs()

    keys = list(coros.keys())
    results = await asyncio.gather(*coros.values(), return_exceptions=True)
    data: dict = {
        k: (v if not isinstance(v, Exception) else None)
        for k, v in zip(keys, results)
    }

    parts: list[str] = ["=== FixinMoto Company Context ==="]

    # Company info (always present)
    settings = data.get("settings") or {}
    if settings:
        parts.append(f"Company: FixinMoto")
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
        parts.append(_fmt_services(data["services"]))

    if data.get("packages"):
        parts.append(_fmt_packages(data["packages"]))

    if data.get("locations"):
        parts.append(_fmt_locations(data["locations"]))

    if data.get("faqs"):
        parts.append(_fmt_faqs(data["faqs"]))

    return "\n\n".join(parts)
