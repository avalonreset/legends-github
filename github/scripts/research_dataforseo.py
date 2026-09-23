"""Bounded keyword/SERP acquisition through the shared Legends DataForSEO Kit."""
from datetime import datetime, timezone
from decimal import Decimal
import json
import math
from uuid import uuid4

from github_runtime import offline_mode
from runtime_paths import repo_output_dir


def collect_research(repo_root, *, keywords, serp_keywords=(), location_code=2840,
                     language="en", execute=False, ceiling=0, no_cost_ceiling=False):
    keywords = list(dict.fromkeys(k.strip() for k in keywords if k.strip()))
    serp_keywords = list(dict.fromkeys(k.strip() for k in serp_keywords if k.strip()))
    if not 1 <= len(keywords) <= 30 or len(serp_keywords) > 3:
        raise ValueError("Use 1-30 keywords and at most three SERP queries per research run")
    if location_code <= 0 or not language.strip() or any(len(k) > 200 for k in keywords + serp_keywords):
        raise ValueError("Supply an explicit valid locale and keywords of at most 200 characters")
    if no_cost_ceiling and ceiling != 0:
        raise ValueError("Choose a cost ceiling or no cost ceiling, not both")
    if not math.isfinite(ceiling) or ceiling < 0:
        raise ValueError("Cost ceiling must be finite and nonnegative")
    demand_cost = Decimal("0.012") + Decimal("0.00012") * len(keywords)
    estimate = demand_cost + Decimal("0.002") * len(serp_keywords)
    plan = {"operation": "research", "status": "estimate", "provider": "legends-dataforseo-kit",
            "keywords": keywords, "serp_keywords": serp_keywords, "location_code": location_code,
            "language_code": language, "cost_ceiling_usd": None if no_cost_ceiling else ceiling, "estimated_cost_usd": float(estimate),
            "cost_note": "Modeled base rates; not provider-enforced billing limits. No optional clickstream or SERP enrichments."}
    if not execute:
        return plan
    if offline_mode():
        raise ValueError("Paid research cannot execute in offline mode")
    if not no_cost_ceiling and Decimal(str(ceiling)) < estimate:
        raise ValueError("Research estimate exceeds --confirm-cost-usd; no request made")
    try:
        from legends_dataforseo import api_request
    except ImportError as exc:
        raise RuntimeError("Install requirements-dataforseo.txt before collecting live research") from exc
    output = repo_output_dir(repo_root) / ("research-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-") + uuid4().hex[:8])
    output.mkdir(parents=True, exist_ok=False)
    calls = [("demand.json", "/dataforseo_labs/google/keyword_overview/live",
              [{"keywords": keywords, "location_code": location_code, "language_code": language,
                "include_serp_info": False, "include_clickstream_data": False}], demand_cost)]
    calls.extend((f"serp-{i}.json", "/serp/google/organic/live/advanced",
                  [{"keyword": keyword, "location_code": location_code, "language_code": language,
                    "device": "desktop", "depth": 10}], Decimal("0.002"))
                 for i, keyword in enumerate(serp_keywords, 1))
    spent = Decimal("0")
    receipts = []
    completed = False
    cost_complete = True
    try:
        for name, endpoint, body, cost in calls:
            if not no_cost_ceiling and spent + cost > Decimal(str(ceiling)):
                raise ValueError("Reported costs leave insufficient budget for the next request")
            try:
                response = api_request(endpoint, body, confirm=True, consumer="legends-github",
                                       estimated_cost_usd=float(cost), max_cost_usd=None if no_cost_ceiling else float(Decimal(str(ceiling)) - spent))
            except Exception as exc:
                rejected = getattr(exc, "response", None)
                if isinstance(rejected, dict):
                    (output / name).write_text(json.dumps(rejected, indent=2) + "\n", encoding="utf-8")
                cost_complete = False
                raise
            (output / name).write_text(json.dumps(response, indent=2) + "\n", encoding="utf-8")
            value = response.get("cost")
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                cost_complete = False
                raise ValueError("Provider cost unknown; retained response and stopped before further requests")
            spent += Decimal(str(value))
            receipts.append({"file": name, "endpoint": endpoint, "reported_cost_usd": value})
            if response.get("status_code") != 20000 or not response.get("tasks") or any(t.get("status_code") != 20000 for t in response["tasks"]):
                raise ValueError("Research task failed; retained response and stopped before further requests")
            if not no_cost_ceiling and spent > Decimal(str(ceiling)):
                raise ValueError("Provider reported cost exceeded advisory ceiling; stopped")
        completed = True
    finally:
        (output / "receipt.json").write_text(json.dumps({**plan, "status": "collected" if completed else "partial",
            "collected_at": datetime.now(timezone.utc).isoformat(), "calls": receipts,
            "reported_cost_usd": float(spent) if cost_complete else None,
            "known_reported_cost_usd": float(spent)}, indent=2) + "\n", encoding="utf-8")
    return {**plan, "status": "collected", "reported_cost_usd": float(spent), "output_dir": str(output),
            "keyword_data": str(output / "demand.json"),
            "serp_data": [str(output / f"serp-{i}.json") for i in range(1, len(serp_keywords) + 1)]}
