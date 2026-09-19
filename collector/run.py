from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from dotenv import load_dotenv

from .diff import diff_listings
from .naver import NaverLandClient
from .notify import send_telegram
from .parse import parse_description

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "data" / "snapshots"


def load_config() -> dict:
    path = ROOT / "config" / "targets.yaml"
    if not path.exists():
        path = ROOT / "config" / "targets.example.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def normalize_article(raw: dict) -> dict:
    article_no = str(raw.get("articleNo") or raw.get("article_no") or "")
    description = raw.get("articleFeatureDesc") or raw.get("description") or ""
    price = raw.get("dealOrWarrantPrc") or raw.get("price") or 0
    if isinstance(price, str):
        # Naver may return display prices; preserve raw value until a verified
        # normalization rule is available rather than guessing units.
        numeric_price = 0
    else:
        numeric_price = int(price or 0)
    return {
        "article_no": article_no,
        "price": numeric_price,
        "price_raw": price,
        "description": description,
        "floor": raw.get("floorInfo"),
        "exclusive_area": raw.get("area2"),
        "direction": raw.get("direction"),
        "realtor": raw.get("realtorName"),
        "parsed": parse_description(description),
        "raw": raw,
    }


def run_once() -> None:
    load_dotenv(ROOT / ".env")
    config = load_config()
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    client = NaverLandClient()
    margin = float(config.get("global", {}).get("alert_margin", 0.05))

    for target in config.get("targets", []):
        raw_articles = client.fetch_articles(str(target.get("naver_complex_no", "TODO")))
        current = {}
        for raw in raw_articles:
            item = normalize_article(raw)
            if item["article_no"]:
                current[item["article_no"]] = item

        snapshot = SNAPSHOT_DIR / f'{target["name"]}.json'
        previous = json.loads(snapshot.read_text(encoding="utf-8")) if snapshot.exists() else {}
        events = diff_listings(previous, current, target, margin)
        for event in events:
            if event["kind"] == "gone":
                continue
            item = event["item"]
            send_telegram(f'[{target["name"]}] {event["kind"]}\n{item.get("price_raw")}\n{item.get("description", "")}')
        snapshot.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.parse_args()
    run_once()
