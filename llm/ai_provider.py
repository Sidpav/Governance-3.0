# llm/ai_provider.py
# ─────────────────────────────────────────────────────────────────────────
# Friend's Module 1 (extractor.py) was written against this exact function:
#     generate_response(prompt, provider) -> str
# That contract is preserved unchanged so extractor.py / missing_fields.py /
# question_generator.py needed ZERO edits ("Module 1 — no changes required").
#
# Internally, the call is now routed through utils/helpers.call_ai() — the
# multi-provider (Gemini / OpenAI / Anthropic / Groq) AI client preserved
# from My Project, because "AI Logic -> My Project" takes priority on any
# conflict, and because the merge spec calls for ONE unified sidebar rather
# than two separate "LLM Settings" panels (Friend's original Ollama/OpenAI/
# Groq picker + My Project's Gemini/OpenAI/Anthropic/Groq picker). The
# `provider` argument is accepted for backwards compatibility with the
# original call site but the active provider/model is whatever was chosen
# in the single unified sidebar (see ui/sidebar.py).
# ─────────────────────────────────────────────────────────────────────────

from utils.helpers import call_ai


def generate_response(prompt, provider=None):
    return call_ai(prompt)
