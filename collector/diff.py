from __future__ import annotations


def diff_listings(previous: dict[str, dict], current: dict[str, dict], target: dict, margin: float = 0.05) -> list[dict]:
    events: list[dict] = []
    max_price = int(target["max_price"])

    for article_no, item in current.items():
        price = int(item.get("price", 0) or 0)
        old = previous.get(article_no)
        parsed = item.get("parsed", {})

        if old is None and price and price <= max_price:
            events.append({"kind": "new_under_cap", "article_no": article_no, "item": item})
        if old is None and str(parsed.get("tenant_until") or "").startswith(("2027-03", "2027-04")):
            events.append({"kind": "tenant_window", "article_no": article_no, "item": item})
        if old and price < int(old.get("price", price) or price) and price <= int(max_price * (1 + margin)):
            events.append({"kind": "price_drop_near_cap", "article_no": article_no, "item": item})

    for article_no, item in previous.items():
        if article_no not in current:
            events.append({"kind": "gone", "article_no": article_no, "item": item})
    return events
