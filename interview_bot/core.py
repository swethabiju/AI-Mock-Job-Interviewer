"""Core logic shared by the data generator, the evaluation and the app.
Code does the checking (STAR markers, key points, unit tests, scores); the LLM is the conversational policy.
"""
import json, os, random, re, subprocess, sys, tempfile
from seeds import *

ACTIONS = ["ASK", "PROBE", "HINT", "FOLLOWUP", "SCORECARD"]
PROTOCOL = (
    "You are a mock job interviewer. Reply format: the first line is 'ACTION: X' where X is one of "
    "ASK, PROBE, HINT, FOLLOWUP, SCORECARD; the rest is your message. Rules: ask only one question per turn, "
    "never write code or reveal full solutions, never answer for the candidate, follow the STATE line in each "
    "user message, and when the interview ends reply with a SCORECARD as JSON.")


def system_prompt(mode, role, project):
    return (f"{PROTOCOL}\nMODE: {mode}. ROLE: {role['role']}. JD SKILLS: {', '.join(role['skills'])}. "
            f"CANDIDATE: final-year CS student; project: {project}.")


# ------------------------------------------------------------------ marker checks
def has_marker(text, marker):
    t = text.lower()
    if marker.endswith("*"):
        pat = r"(?<!\w)" + re.escape(marker[:-1])
    else:
        pat = r"(?<!\w)" + re.escape(marker) + r"(?!\w)"
    return re.search(pat, t) is not None


def star_missing(text):
    return [c for c in STAR_ORDER if not any(has_marker(text, m) for m in STAR_MARKERS[c])]


def tech_check(text, q):
    missing = [k["label"] for k in q["kps"] if not any(has_marker(text, m) for m in k["markers"])]
    cov = round((len(q["kps"]) - len(missing)) / len(q["kps"]), 2)
    return cov, missing


def complexity_ok(text, p):
    norm = re.sub(r"\s+", "", text.lower())
    return int(any(re.sub(r"\s+", "", m) in norm for m in p["cx"]))


# ------------------------------------------------------------------ code runner
_HARNESS = r'''
import json, sys, copy
cfg = json.load(open(sys.argv[1]))
ns = {}
try:
    exec(compile(cfg["code"], "<candidate>", "exec"), ns)
    f = ns[cfg["fn"]]
except Exception as e:
    print(json.dumps({"error": "load: " + str(e)[:80]})); sys.exit()
res = []
for args, exp, cat in cfg["tests"]:
    try:
        out = f(*copy.deepcopy(args))
        ok = (out == exp)
    except Exception:
        ok = False
    res.append([ok, cat])
print(json.dumps({"res": res}))
'''
_CACHE = {}


def expected_tests(p):
    ns = {}
    exec(p["ref"], ns)
    f = ns[p["fn"]]
    return [[list(a), f(*a), cat] for a, cat in p["tests"]]


def run_submission(code, p, timeout=6):
    """Run candidate code against the problem's tests in a subprocess. Returns (passed, total, first_failed_category)."""
    key = (p["id"], code)
    if key in _CACHE:
        return _CACHE[key]
    tests = expected_tests(p)
    total = len(tests)
    with tempfile.TemporaryDirectory() as d:
        cfg_path, h_path = os.path.join(d, "cfg.json"), os.path.join(d, "h.py")
        json.dump({"code": code, "fn": p["fn"], "tests": tests}, open(cfg_path, "w"))
        open(h_path, "w").write(_HARNESS)
        try:
            r = subprocess.run([sys.executable, h_path, cfg_path], capture_output=True, text=True, timeout=timeout, cwd=d)
            data = json.loads(r.stdout.strip().splitlines()[-1])
        except subprocess.TimeoutExpired:
            data = {"timeout": True}
        except Exception:
            data = {"error": "crash"}
    if "res" in data:
        passed = sum(1 for ok, _ in data["res"] if ok)
        failed = [c for ok, c in data["res"] if not ok]
        out = (passed, total, failed[0] if failed else "")
    elif data.get("timeout"):
        out = (0, total, "timeout")
    else:
        out = (0, total, "code does not load")
    _CACHE[key] = out
    return out


def extract_code(text):
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip()


# ------------------------------------------------------------------ scorecards
SI = {
    "HR": {"strong": ("Your answers were well structured and complete.", "Keep tailoring examples to the role."),
           "developing": ("You gave relevant examples.", "Make sure every answer covers situation, task, action and result."),
           "needs work": ("You were willing to engage with each question.", "Practise structuring answers with the STAR method.")},
    "TECH": {"strong": ("You covered the key points clearly.", "Practise explaining trade-offs in more depth."),
             "developing": ("You know the basics.", "Review the key points you missed and practise explaining them aloud."),
             "needs work": ("You attempted every question.", "Revise the fundamentals of each topic before the next round.")},
    "CODE": {"strong": ("You solved the problem efficiently.", "Practise explaining complexity and edge cases."),
             "developing": ("You reached a working direction.", "Test edge cases before submitting."),
             "needs work": ("You kept trying after feedback.", "Practise the core pattern and write small tests first.")},
}


def band(x):
    return "strong" if x >= 4 else "developing" if x >= 2.8 else "needs work"


def fmt_scores(parts):
    return ",".join(f"{p:.2f}" for p in parts)


def scorecard(mode, parts):
    parts = [round(p, 2) for p in parts]
    overall = round(5 * sum(parts) / len(parts), 2)
    b = band(overall)
    return {"mode": mode, "scores": [round(5 * p, 2) for p in parts], "overall": overall, "band": b,
            "strength": SI[mode][b][0], "improve": SI[mode][b][1]}


def _g(action, text, must=None, cue=None, card=None):
    return {"action": action, "text": text, "full": f"ACTION: {action}\n{text}", "must": must or [],
            "cue_any": cue or [], "overall": card["overall"] if card else None}


# ------------------------------------------------------------------ sessions
class HRSession:
    mode = "HR"
    NQ = 3

    def __init__(self, rng=None, test=False):
        self.rng = rng or random.Random()
        self.role = self.rng.choice(ROLES)
        self.project = self.rng.choice(PROJECTS)
        train = [q for q in HR_QS if not q.get("test_only")]
        if test:
            held = [q for q in HR_QS if q.get("test_only")]
            first = self.rng.choice(held)
            self.qs = [first] + self.rng.sample([q for q in HR_QS if q is not first], 2)
            self.rng.shuffle(self.qs)
        else:
            self.qs = self.rng.sample(train, 3)
        self.qi, self.probes, self.cum, self.done_scores, self.turn = 0, 0, "", [], 0
        self.missing, self.cov, self.done = [], 0.0, False

    @property
    def system(self):
        return system_prompt("HR", self.role, self.project)

    def observe(self, text):
        if self.turn == 0:
            return f"STATE: mode=HR turn=0 q=1/3 next_q={self.qs[0]['q']}\nCANDIDATE: (ready)"
        self.cum += " " + text
        self.missing = star_missing(self.cum)
        self.cov = round((4 - len(self.missing)) / 4, 2)
        nxt = self.qs[self.qi + 1]["q"] if self.qi + 1 < self.NQ else "END"
        scores = self.done_scores + [self.cov]
        return (f"STATE: mode=HR turn={self.turn} q={self.qi + 1}/3 star_missing={'|'.join(self.missing) or 'none'} "
                f"probes={self.probes} scores={fmt_scores(scores)} next_q={nxt}\nCANDIDATE: {text}")

    def gold(self):
        r = self.rng
        if self.turn == 0:
            s = self.role["skills"]
            t = r.choice(GREETS).format(role=self.role["role"], s1=s[0], s2=s[1], q=self.qs[0]["q"])
            return _g("ASK", t, must=[self.role["role"].lower()])
        if self.missing and self.probes == 0:
            c = self.missing[0]
            return _g("PROBE", r.choice(ACKS) + " " + r.choice(HR_PROBES[c]), must=HR_PROBE_KEYS[c])
        if self.qi + 1 < self.NQ:
            nq = self.qs[self.qi + 1]["q"]
            return _g("ASK", f"{r.choice(ACKS)} Next question: {nq}", must=[nq.lower()[:30]])
        card = scorecard("HR", self.done_scores + [self.cov])
        return _g("SCORECARD", json.dumps(card), card=card)

    def apply(self, action):
        if self.turn == 0:
            self.turn = 1
            return
        self.turn += 1
        if action == "PROBE":
            self.probes += 1
        elif action == "ASK":
            self.done_scores.append(self.cov)
            self.qi += 1
            self.probes, self.cum = 0, ""
        elif action == "SCORECARD":
            self.done = True


class TechSession:
    mode = "TECH"
    NQ = 4

    def __init__(self, rng=None, test=False):
        self.rng = rng or random.Random()
        self.role = self.rng.choice(ROLES)
        self.project = self.rng.choice(PROJECTS)
        self.pool = [q for q in TECH_QS if test or not q.get("test_only")]
        self.pref = {SKILL_TOPIC[s] for s in self.role["skills"] if s in SKILL_TOPIC}
        self.asked, self.diff, self.qi, self.probes, self.cum, self.done_scores = [], 2, 0, 0, "", []
        self.turn, self.done, self.cov, self.missing = 0, False, 0.0, []
        self.move, self.nxt, self.nxt_diff = "same", None, 2
        self.cur = self._pick(2, [])

    def _pick(self, diff, exclude):
        left = [q for q in self.pool if q["id"] not in exclude]
        c = [q for q in left if q["diff"] == diff] or [q for q in left if abs(q["diff"] - diff) == 1] or left
        pref = [q for q in c if q["topic"] in self.pref] or c
        return self.rng.choice(pref)

    @property
    def system(self):
        return system_prompt("TECH", self.role, self.project)

    def observe(self, text):
        if self.turn == 0:
            return f"STATE: mode=TECH turn=0 q=1/4 next_q={self.cur['q']}\nCANDIDATE: (ready)"
        self.cum += " " + text
        self.cov, self.missing = tech_check(self.cum, self.cur)
        self.move = "up" if self.cov >= 0.75 else "down" if self.cov < 0.4 else "same"
        self.nxt_diff = min(3, self.diff + 1) if self.move == "up" else max(1, self.diff - 1) if self.move == "down" else self.diff
        if self.qi + 1 < self.NQ:
            self.nxt = self._pick(self.nxt_diff, self.asked + [self.cur["id"]])
            nq = self.nxt["q"]
        else:
            self.nxt, nq = None, "END"
        scores = self.done_scores + [self.cov]
        return (f"STATE: mode=TECH turn={self.turn} q={self.qi + 1}/4 cov={self.cov:.2f} "
                f"missing={'|'.join(self.missing) or 'none'} probes={self.probes} diff_move={self.move} "
                f"scores={fmt_scores(scores)} next_q={nq}\nCANDIDATE: {text}")

    def gold(self):
        r = self.rng
        if self.turn == 0:
            s = self.role["skills"]
            t = r.choice(GREETS).format(role=self.role["role"], s1=s[0], s2=s[1], q=self.cur["q"])
            return _g("ASK", t, must=[self.role["role"].lower()])
        if self.missing and self.probes == 0 and len(self.missing) < len(self.cur["kps"]):
            lab = self.missing[0]
            return _g("PROBE", f"{r.choice(ACKS)} " + r.choice(["Can you also explain {l}?", "What can you say about {l}?"]).format(l=lab),
                      must=[lab.lower()])
        if self.qi + 1 < self.NQ:
            cues = {"up": (["Let's step it up a bit.", "Let's try something more challenging."], ["step it up", "challeng", "harder"]),
                    "down": (["Let's try something simpler.", "Let's go back to the basics."], ["simpler", "basic"]),
                    "same": (["Moving on."], [])}
            phr, cue = cues[self.move]
            nq = self.nxt["q"]
            return _g("ASK", f"{r.choice(ACKS)} {r.choice(phr)} {nq}", must=[nq.lower()[:30]], cue=cue)
        card = scorecard("TECH", self.done_scores + [self.cov])
        return _g("SCORECARD", json.dumps(card), card=card)

    def apply(self, action):
        if self.turn == 0:
            self.turn = 1
            return
        self.turn += 1
        if action == "PROBE":
            self.probes += 1
        elif action == "ASK":
            self.done_scores.append(self.cov)
            self.asked.append(self.cur["id"])
            self.cur, self.diff = self.nxt, self.nxt_diff
            self.qi += 1
            self.probes, self.cum = 0, ""
        elif action == "SCORECARD":
            self.done = True


ATT_SCORE = {1: 1.0, 2: 0.75, 3: 0.5, 4: 0.25}


class CodeSession:
    mode = "CODE"
    MAXATT = 4

    def __init__(self, rng=None, test=False):
        self.rng = rng or random.Random()
        self.role = self.rng.choice(ROLES)
        self.project = self.rng.choice(PROJECTS)
        pool = [p for p in CODE_PROBLEMS if test or not p.get("test_only")]
        self.p = self.rng.choice(pool)
        self.turn, self.attempt, self.phase, self.done = 0, 0, "code", False
        self.passed = self.total = 0
        self.cat, self.solved, self.cx = "", False, 0

    @property
    def system(self):
        return system_prompt("CODE", self.role, self.project)

    def _parts(self):
        return [self.passed / self.total if self.total else 0.0,
                ATT_SCORE.get(self.attempt, 0.25) if self.solved else 0.0, float(self.cx)]

    def hint_text(self):
        if self.attempt == 1:
            return f"Your function fails on the '{self.cat}' case - re-read the problem statement for that situation."
        return self.p["hint2"] if self.attempt == 2 else self.p["hint3"]

    def observe(self, text):
        if self.turn == 0:
            return f"STATE: mode=CODE turn=0 next_q={self.p['statement']}\nCANDIDATE: (ready)"
        if self.phase == "followup":
            self.cx = complexity_ok(text, self.p)
            return (f"STATE: mode=CODE turn={self.turn} phase=followup complexity_ok={self.cx} "
                    f"scores={fmt_scores(self._parts())}\nCANDIDATE: {text}")
        code = extract_code(text)
        self.passed, self.total, self.cat = run_submission(code, self.p)
        self.attempt += 1
        self.solved = self.passed == self.total
        base = f"STATE: mode=CODE turn={self.turn} attempt={self.attempt} passed={self.passed}/{self.total}"
        if self.solved:
            return f"{base} phase=code\nCANDIDATE: {text}"
        if self.attempt < self.MAXATT:
            return f"{base} level={self.attempt} failed={self.cat} hint={self.hint_text()}\nCANDIDATE: {text}"
        return f"{base} final=failed scores={fmt_scores(self._parts())}\nCANDIDATE: {text}"

    def gold(self):
        r = self.rng
        if self.turn == 0:
            t = (f"Hello, and welcome to the coding round for the {self.role['role']} position. "
                 f"Here is your problem: {self.p['statement']} Please submit your solution as Python code.")
            return _g("ASK", t, must=[self.p["fn"]])
        if self.phase == "followup":
            card = scorecard("CODE", self._parts())
            return _g("SCORECARD", json.dumps(card), card=card)
        if self.solved:
            return _g("FOLLOWUP", f"All {self.total} tests pass - nice work. What is the time complexity of your solution, and could it be improved?",
                      must=["complexity"])
        if self.attempt < self.MAXATT:
            ht = self.hint_text()
            return _g("HINT", f"{r.choice(ACKS)} {self.passed} of {self.total} tests pass so far. Hint (level {self.attempt}): {ht}",
                      must=[ht.lower()[:25]])
        card = scorecard("CODE", self._parts())
        return _g("SCORECARD", json.dumps(card), card=card)

    def apply(self, action):
        if self.turn == 0:
            self.turn = 1
            return
        self.turn += 1
        if action == "FOLLOWUP":
            self.phase = "followup"
        elif action == "SCORECARD":
            self.done = True


SESSIONS = {"HR": HRSession, "TECH": TechSession, "CODE": CodeSession}
