from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from typing import Any

import requests

URL = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"


def fetch_trades(lawd_cd: str, deal_ymd: str) -> list[dict[str, Any]]:
    key = os.getenv("MOLIT_API_KEY")
    if not key:
        return []
    response = requests.get(
        URL,
        params={
            "serviceKey": key,
            "LAWD_CD": lawd_cd,
            "DEAL_YMD": deal_ymd,
            "numOfRows": 999,
            "pageNo": 1,
        },
        timeout=20,
    )
    response.raise_for_status()
    root = ET.fromstring(response.text)
    rows: list[dict[str, Any]] = []
    for item in root.findall(".//item"):
        rows.append({child.tag: (child.text or "").strip() for child in item})
    return rows
