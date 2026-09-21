"""Human-readable reports for the evidence contract and legacy score migration."""

from __future__ import annotations

from typing import Any


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def _actions(audit: dict[str, Any]) -> str:
    actions = audit["prioritized_actions"]
    if not actions:
        return "No recommendations from evaluated checks. Review unavailable evidence before drawing a broader conclusion."
    lines = []
    for action in actions:
        lines.extend([
            f"### {action['id']} ({action['priority']})", "", action["recommendation"], "",
            f"Impact: {action['impact']}; effort: {action['effort']}; confidence: {action['confidence']:.0%}; basis: {action['recommendation_basis']}.", "",
            "Evidence: " + "; ".join(f"`{_cell(e['source'])}` — {_cell(e['detail'])}" for e in action["evidence"]), "",
            "Verify: " + action["verification"]["method"], "",
        ])
    return "\n".join(lines).rstrip()


def build_evidence_report(context: dict[str, Any], audit: dict[str, Any]) -> str:
    profile = audit["repository_profile"]
    coverage = audit["evidence_coverage"]
    counts = coverage["counts"]
    lines = ["# GitHub Audit Report", "", f"- **Repository:** {_cell(context['repo'])}",
             f"- **Generated at:** {audit['timestamp']}",
             f"- **Evidence schema:** {audit['evidence_schema_version']}",
             f"- **Profile:** {profile['primary']}; audience: {profile['audience']}; scope: {profile['scope']}", "",
             "## Evidence summary", "",
             f"Observed: {counts['observed']}; missing: {counts['missing']}; unavailable: {counts['unavailable']}; not applicable: {counts['not_applicable']}.", "",
             "Unavailable evidence is not a failed check. Inapplicable and unavailable checks do not enter the evaluated denominator. "
             "Observed means the named static signal was found, not that the software works. Profile inference can require correction.", "",
             "## Prioritized findings", "", _actions(audit), "",
             "## All checks", "", "| Check | Status | Applicability | Evidence |",
             "| --- | --- | --- | --- |"]
    for finding in audit["findings"]:
        evidence = "; ".join(f"{e['source']}: {e.get('reason') or e['detail']}" for e in finding["evidence"])
        lines.append("| " + " | ".join(_cell(v) for v in (finding["id"], finding["status"],
                     finding["applicability"]["reason"], evidence)) + " |")
    lines.extend(["", "## Collection availability", "", "| Source | Availability | Reason |", "| --- | --- | --- |"])
    for group in ("github", "git"):
        for name, obs in audit["collection"][group].items():
            lines.append(f"| {group}.{name} | {obs['availability']} | {obs['reason'] or 'Collected this run'} |")
    lines.extend(["", "## Legacy checklist (compatibility only)", "",
                  f"**Legacy score: {audit['overall_score']}/100. Scoring version: {audit['scoring_version']}.**", "",
                  "The preserved checklist can penalize unavailable metadata, inapplicable policies, and decoration. "
                  "It is not a quality, compliance, discoverability, or business-impact rating. Priorities above use individual findings, not category scores.", "",
                  "| Category | Legacy score | Weight |", "| --- | ---: | ---: |"])
    for category, score in audit["scores"].items():
        lines.append(f"| {category} | {score} | {audit['weights'][category]:.0%} |")
    lines.extend(["", "## Limits and verification", ""] + ["- " + text for text in audit["limitations"]])
    return "\n".join(lines) + "\n"


def build_evidence_action_plan(context: dict[str, Any], audit: dict[str, Any]) -> str:
    return (f"# Action Plan\n\n- **Repository:** {_cell(context['repo'])}\n"
            f"- **Evidence schema:** {audit['evidence_schema_version']}\n\n"
            "Actions are ordered by the impact of the individual finding, with confidence as a tie-breaker. "
            "Nothing in this plan authorizes a publish, deployment, or remote mutation.\n\n" + _actions(audit) + "\n\n"
            "Re-audit after changes and complete each finding's verification step. "
            "A checklist score increase is not proof of a successful installation, release, or user outcome.\n")
