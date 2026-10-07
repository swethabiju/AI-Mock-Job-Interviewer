"""Generate train/val/test conversations. Labels come from core.py rules, never from an LLM.
Usage: python gen_data.py [--train 400 400 300] [--val 30] [--test 36] [--seed 7]
"""
import argparse, json, os, random
from core import *

FILL = ["um", "like", "you know", "actually", "basically"]
TYPO = {"the": "teh", "because": "becuase", "project": "proejct", "database": "databse", "between": "betwen", "memory": "memroy"}


def messify(t, rng):
    t = t.lower()
    out = []
    for w in t.split():
        if rng.random() < 0.04:
            out.append(rng.choice(FILL))
        out.append(TYPO.get(w, w) if rng.random() < 0.5 else w)
    return " ".join(out)


def lower_first(s):
    return s[0].lower() + s[1:] if len(s) > 1 and s[1].islower() else s


def hr_answer(q, rng, comps=None):
    if comps is None:
        k = rng.choices([4, 3, 2, 1, 0], weights=[30, 25, 25, 12, 8])[0]
        comps = rng.sample(STAR_ORDER, k)
    x = {"situation": q["ctx"], "task": q["goal"], "action": rng.choice(q["acts"]), "result": q["out"]}
    parts = [rng.choice(STAR_TEMPLATES[c]).format(x=x[c]) for c in STAR_ORDER if c in comps]
    if not parts or rng.random() < 0.3:
        parts.append(rng.choice(HR_FILLER))
    return " ".join(parts)


def tech_answer(q, rng, only=None):
    if only is not None:
        kps = [k for k in q["kps"] if k["label"] == only]
        if rng.random() < 0.3:
            return rng.choice(TECH_FILLER)
    else:
        level = rng.choices(["strong", "partial", "weak"], weights=[35, 40, 25])[0]
        n = {"strong": 3, "partial": rng.choice([1, 2]), "weak": 0}[level]
        kps = rng.sample(q["kps"], n)
        kps.sort(key=lambda k: q["kps"].index(k))
        if not kps:
            return rng.choice(TECH_FILLER)
    pre = rng.choice(["I think ", "Basically, ", "", "As far as I know, "])
    sents = [k["sent"] for k in kps]
    sents[0] = pre + lower_first(sents[0]) if pre else sents[0]
    return " ".join(sents)


def code_plan(p, rng):
    r = rng.random()
    b = p["bugs"]
    if r < 0.25:
        seq = ["ref"]
    elif r < 0.55:
        seq = [rng.choice([0, 1]), "ref"]
    elif r < 0.75:
        seq = [0, 1, "ref"]
    elif r < 0.85:
        seq = [rng.choice([0, 1]), rng.choice([0, 1]), rng.choice([0, 1]), "ref"]
    else:
        seq = [rng.choice([0, 1]) for _ in range(4)]
    return seq


def code_msg(p, v, rng):
    code = p["ref"] if v == "ref" else p["bugs"][v]
    return rng.choice(["Here is my solution.", "Trying this version.", "This is my attempt."]) + f"\n```python\n{code}\n```"


def complexity_answer(p, rng):
    r = rng.random()
    if r < 0.6:
        return f"I think the time complexity is {p['cx_text']} because I pass over the input only once."
    if r < 0.85:
        return "It should be O(n^2) because of the loops."
    return "I am not sure about the complexity."


def candidate(s, g, rng, test, plan):
    if s.mode == "HR":
        if g["action"] == "PROBE":
            c = s.missing[0]
            t = hr_answer(s.qs[s.qi], rng, [c]) if rng.random() < 0.7 else rng.choice(HR_FILLER)
        else:
            t = hr_answer(s.qs[s.qi], rng)
        return messify(t, rng) if test else t
    if s.mode == "TECH":
        if g["action"] == "PROBE":
            t = tech_answer(s.cur, rng, only=s.missing[0])
        else:
            t = tech_answer(s.cur, rng)
        return messify(t, rng) if test else t
    if g["action"] == "FOLLOWUP":
        return complexity_answer(s.p, rng)
    idx = min(s.attempt, len(plan) - 1)
    return code_msg(s.p, plan[idx], rng)


def simulate(mode, rng, test):
    s = SESSIONS[mode](rng=rng, test=test)
    plan = code_plan(s.p, rng) if mode == "CODE" else None
    msgs = [{"role": "system", "content": s.system}]
    gold = []
    user = s.observe("(ready)")
    while True:
        g = s.gold()
        msgs.append({"role": "user", "content": user})
        msgs.append({"role": "assistant", "content": g["full"]})
        gold.append({"idx": len(msgs) - 1, "mode": mode, "action": g["action"], "must": g["must"],
                     "cue_any": g["cue_any"], "overall": g["overall"]})
        s.apply(g["action"])
        if s.done:
            break
        user = s.observe(candidate(s, g, rng, test, plan))
    return {"mode": mode, "messages": msgs, "gold": gold}


def write(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", type=int, nargs=3, default=[400, 400, 300])
    ap.add_argument("--val", type=int, default=30)
    ap.add_argument("--test", type=int, default=36)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    os.makedirs("data", exist_ok=True)
    modes = ["HR", "TECH", "CODE"]
    train, val, test = [], [], []
    for i, m in enumerate(modes):
        rng = random.Random(a.seed * 100 + i)
        train += [simulate(m, rng, False) for _ in range(a.train[i])]
        val += [simulate(m, rng, False) for _ in range(a.val)]
        rng2 = random.Random(a.seed * 1000 + i)
        test += [simulate(m, rng2, True) for _ in range(a.test)]
    random.Random(a.seed).shuffle(train)
    write("data/train.jsonl", train)
    write("data/val.jsonl", val)
    write("data/test.jsonl", test)
    print(f"train={len(train)} val={len(val)} test={len(test)}")
