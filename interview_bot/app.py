"""Mock interviewer app.  Run:  python app.py --adapter adapter --share      (add --dry to test without the model)

Architecture: a rule-based controller (core.py) checks answers, runs unit tests, tracks state and computes scores.
The fine-tuned LLM writes the interviewer's turn. The controller's action decides the flow; we also show what the
model chose, so you can see where the two agree (that agreement is the 'action_match' metric in the evaluation).
Safety: CODE mode executes the candidate's code locally. Only use it on Colab / your own machine, never on a public server.
"""
import argparse
import json
from core import SESSIONS
from metrics import parse


class Interviewer:
    def __init__(self, generate=None):
        self.gen = generate        # function(messages) -> str, or None for dry mode
        self.s = None

    def start(self, mode):
        self.s = SESSIONS[mode]()
        self.msgs = [{"role": "system", "content": self.s.system}]
        self.log, self.debug, self.final = [], "", None
        self._turn(self.s.observe("(ready)"), shown=None)
        return self.render()

    def respond(self, text):
        if self.s is None:
            return "Click 'Start new interview' first.", ""
        if self.s.done:
            return self.render()[0] + "\n\n*Interview finished - start a new one.*", self.debug
        if not text.strip():
            return self.render()
        self._turn(self.s.observe(text), shown=text)
        return self.render()

    def _turn(self, user_content, shown):
        g = self.s.gold()                       # rule engine's decision (verified)
        self.msgs.append({"role": "user", "content": user_content})
        reply = self.gen(self.msgs) if self.gen else None
        if reply is None:
            reply = g["full"]
        m_action, m_text = parse(reply)
        self.msgs.append({"role": "assistant", "content": reply})
        if shown is not None:
            self.log.append(("You", shown))
        self.log.append(("Interviewer", m_text))
        state_line = user_content.split("\n")[0]
        agree = "agrees" if m_action == g["action"] else "DIFFERS"
        self.debug = (f"**Rule engine action:** `{g['action']}`  |  **Model action:** `{m_action}` ({agree})\n\n"
                      f"`{state_line}`")
        self.last_action = g["action"]
        self.s.apply(g["action"])
        if self.s.done:
            self.final = g["text"]

    def render(self):
        parts = []
        for who, txt in self.log:
            if who == "You" and "def " in txt:
                parts.append(f"**You:**\n```python\n{txt}\n```")
            else:
                parts.append(f"**{who}:** {txt}")
        if self.final:
            parts.append("**Verified scorecard (computed by code, not by the model):**\n```json\n"
                         + json.dumps(json.loads(self.final), indent=2) + "\n```")
            parts.append("*Practice feedback only - not a hiring decision.*")
        return "\n\n".join(parts), self.debug


def load_model(adapter, base_name):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel
    tok = AutoTokenizer.from_pretrained(adapter)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
    base = AutoModelForCausalLM.from_pretrained(base_name, quantization_config=bnb, device_map={"": 0})
    model = PeftModel.from_pretrained(base, adapter)
    model.eval()

    def generate(messages):
        text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_tensors="pt", add_special_tokens=False).to(model.device)
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=160, do_sample=False, pad_token_id=tok.pad_token_id)
        return tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)
    return generate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", default="adapter")
    ap.add_argument("--base", default="Qwen/Qwen2.5-1.5B-Instruct")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--share", action="store_true")
    a = ap.parse_args()
    import gradio as gr
    bot = Interviewer(None if a.dry else load_model(a.adapter, a.base))

    with gr.Blocks(title="Mock Interviewer") as demo:
        gr.Markdown("# Mock job interviewer\nPick a mode, start, and answer. In CODE mode paste Python code. "
                    "Practice tool only.")
        mode = gr.Dropdown(["HR", "TECH", "CODE"], value="HR", label="Interview mode")
        start_btn = gr.Button("Start new interview")
        transcript = gr.Markdown()
        box = gr.Textbox(label="Your answer (in CODE mode paste your Python code)", lines=8)
        send = gr.Button("Send")
        debug = gr.Markdown()
        start_btn.click(lambda m: bot.start(m), [mode], [transcript, debug])
        send.click(lambda t: (*bot.respond(t), ""), [box], [transcript, debug, box])
    demo.launch(share=a.share)


if __name__ == "__main__":
    main()
