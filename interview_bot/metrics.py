"""Per-turn scoring used by the evaluation notebook. Works on any (prediction, gold) pair."""
import json, re
from core import ACTIONS

LEAK = re.compile(r"```|\bdef\b|\breturn\b")


def parse(pred):
    m = re.match(r"\s*ACTION:\s*([A-Z]+)\s*\n?(.*)", pred, re.S)
    return (m.group(1), m.group(2).strip()) if m else (None, pred.strip())


def score_turn(pred, gold):
    """Returns dict of metric -> 0/1 (or float for MAE). Missing keys mean 'not applicable'."""
    action, text = parse(pred)
    low = text.lower()
    r = {"format_ok": int(action in ACTIONS), "action_match": int(action == gold["action"])}
    if gold["action"] != "SCORECARD":
        r["single_question"] = int(text.count("?") <= 1)
        r["content_ok"] = int(not gold["must"] or any(m in low for m in gold["must"]))
    if gold["cue_any"]:
        r["adapt_ok"] = int(any(c in low for c in gold["cue_any"]))
    if gold["mode"] == "CODE":
        if gold["action"] == "HINT":
            r["no_code_leak"] = int(not LEAK.search(text))
        if gold["action"] in ("HINT", "SCORECARD"):          # candidate has NOT passed yet / failed
            r["no_false_pass"] = int(action != "FOLLOWUP")
    if gold["action"] == "SCORECARD":
        try:
            card = json.loads(text)
            ok = all(k in card for k in ("scores", "overall", "band", "strength", "improve"))
            r["scorecard_valid"] = int(ok)
            if ok:
                r["scorecard_abs_err"] = abs(float(card["overall"]) - float(gold["overall"]))
        except Exception:
            r["scorecard_valid"] = 0
    return r


def aggregate(records):
    """records: list of (mode, metric_dict). Returns {mode: {metric: mean}}."""
    out = {}
    for mode, m in records:
        for k, v in m.items():
            out.setdefault(mode, {}).setdefault(k, []).append(v)
    return {mode: {k: round(sum(v) / len(v), 3) for k, v in d.items()} for mode, d in out.items()}
