"""Import official DataForSEO exports without credentials or a host-specific transport."""
import json
import math
from pathlib import Path


def results(path, endpoint):
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if payload.get("status_code") != 20000 or not payload.get("tasks"):
        raise ValueError("Research export has no successful tasks")
    output = []
    for task in payload["tasks"]:
        if task.get("status_code") != 20000 or "/".join(task.get("path", [])) != "v3/" + endpoint:
            raise ValueError("Research export contains a failed task or unexpected endpoint")
        output.extend(task.get("result") or [])
    if not output:
        raise ValueError("Research export contains no results")
    return output, payload.get("cost")


def metric(value):
    if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
        raise ValueError("Research metrics must be nonnegative numbers or null")
    return value


def import_research(keyword_data, primary_keyword, serp_data=()):
    if not primary_keyword:
        raise ValueError("--keyword-data requires --primary-keyword chosen for product fit")
    demand, cost = results(keyword_data, "dataforseo_labs/google/keyword_overview/live")
    locales = {(r.get("location_code"), r.get("language_code")) for r in demand}
    if len(locales) != 1 or any(None in locale for locale in locales):
        raise ValueError("Research must have one explicit location and language")
    keywords = []
    for result in demand:
        for item in result.get("items") or []:
            info = item.get("keyword_info") or {}
            keywords.append({"keyword": item["keyword"], "volume": metric(info.get("search_volume")),
                "difficulty": metric((item.get("keyword_properties") or {}).get("keyword_difficulty")),
                "intent": (item.get("search_intent_info") or {}).get("main_intent") or "unknown",
                "source": "dataforseo-keyword-overview", "updated_at": info.get("last_updated_time"),
                "category": "Provider estimate"})
    primary = next((k for k in keywords if k["keyword"].casefold() == primary_keyword.casefold()), None)
    if primary is None:
        raise ValueError("Selected primary keyword was not returned by the provider")
    serps, costs = [], [cost]
    for path in serp_data:
        collected, call_cost = results(path, "serp/google/organic/live/advanced")
        costs.append(call_cost)
        for result in collected:
            if (result.get("location_code"), result.get("language_code")) not in locales:
                raise ValueError("SERP and keyword research locales differ")
            serps.append({"keyword": result.get("keyword"), "checked_at": result.get("datetime"),
                "depth": result.get("items_count"), "results": [
                    {"rank": i.get("rank_group"), "title": i.get("title"), "url": i.get("url")}
                    for i in result.get("items") or [] if i.get("type") == "organic"]})
    location, language = next(iter(locales))
    return {"primary_keyword": primary, "keyword_research": keywords,
        "research_locale": {"location_code": location, "language_code": language},
        "serp_observations": serps, "analysis_mode": "imported-dataforseo-evidence",
        "cost_receipt": {"currency": "USD", "reported_total": sum(costs) if all(isinstance(c, (float, int)) for c in costs) else None,
                         "note": "Historical export costs; importing incurs no API charges."}}
