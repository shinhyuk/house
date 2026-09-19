"""Naver Land adapter.

This module intentionally does not try to bypass authentication, anti-bot
controls, or access restrictions. Keep requests low-frequency and replace
this adapter if the service no longer permits the access pattern.
"""
from __future__ import annotations

import time
from typing import Any

import requests

BASE_URL = "https://new.land.naver.com/api"


class NaverLandClient:
    def __init__(self, timeout: int = 15, sleep_seconds: float = 1.5) -> None:
        self.timeout = timeout
        self.sleep_seconds = sleep_seconds
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "apt-watch/0.1 (personal monitoring)",
            "Referer": "https://new.land.naver.com/",
        })

    def fetch_articles(self, complex_no: str) -> list[dict[str, Any]]:
        if not complex_no or complex_no == "TODO":
            return []
        url = f"{BASE_URL}/articles/complex/{complex_no}"
        params = {"realEstateType": "APT", "tradeType": "A1", "page": 1}
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        time.sleep(self.sleep_seconds)
        return payload.get("articleList", [])
