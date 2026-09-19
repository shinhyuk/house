from __future__ import annotations

import re
from datetime import date

KEYWORDS = ("잔금 협의", "공실", "주인 거주", "즉시 입주")
TENANT_PATTERNS = [
    re.compile(r"(?:세입자|임차인)?\s*(?:만기|계약만료)\s*[:：]?\s*(20\d{2})[.년/-]\s*(\d{1,2})[.월/-]\s*(\d{1,2})?"),
]


def parse_description(text: str) -> dict:
    text = text or ""
    tenant_until = None
    for pattern in TENANT_PATTERNS:
        match = pattern.search(text)
        if match:
            year, month, day = match.groups()
            tenant_until = date(int(year), int(month), int(day or 1)).isoformat()
            break

    renewal_used = None
    if re.search(r"갱신(?:청구권)?\s*(?:사용|행사)(?:함|완료)?", text):
        renewal_used = True
    elif re.search(r"갱신(?:청구권)?\s*(?:미사용|미행사)", text):
        renewal_used = False

    return {
        "tenant_until": tenant_until,
        "renewal_used": renewal_used,
        "keywords": [keyword for keyword in KEYWORDS if keyword in text],
    }
