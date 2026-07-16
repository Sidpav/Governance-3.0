# utils/helpers.py
# Shared utility functions — API key detection, model selection, AI calls, parsers

import re
import json
import os
import streamlit as st
import hashlib
import uuid
from datetime import datetime, timezone

from config.constants import REQUIRED_FIELDS, FIELD_KEYS
from config.prompts import M1_SYSTEM_PROMPT


# ══════════════════════════════════════════════════════════════════════════════
# API KEY & MODEL AUTO-DETECTION
# ══════════════════════════════════════════════════════════════════════════════

# Priority-ordered preferred models per provider
PREFERRED_MODELS = {
    "gemini": [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ],
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ],
    "anthropic": [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
    ],
    "groq": [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama3-70b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ],
}


SECRET_KEY_NAMES = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY",
                     "ANTHROPIC_API_KEY", "GROQ_API_KEY")


def get_backend_api_key() -> tuple[str, str]:
    """
    Check ONLY the automatic, no-user-input sources: st.secrets, env vars,
    and config/app_config.json. Returns (key, source_label) — source_label
    is "" if nothing was found.
    """
    for k in SECRET_KEY_NAMES:
        try:
            v = st.secrets[k]
            if v:
                return v, "Streamlit secrets"
        except Exception:
            pass
    for k in SECRET_KEY_NAMES:
        v = os.environ.get(k, "")
        if v:
            return v, "environment variable"
    try:
        from config.app_config import load_app_config
        cfg = load_app_config()
        if cfg.get("api_key"):
            return cfg["api_key"], "config/app_config.json"
    except Exception:
        pass
    return "", ""


def get_configured_provider_model() -> tuple[str, str]:
    """
    Returns (provider, model) EXPLICITLY set in config/app_config.json,
    e.g. ("groq", "llama-3.3-70b-versatile"). Empty strings if not set.
    This takes priority over format-based auto-detection — if you've told
    the config file which provider/model to use, that's authoritative.
    """
    try:
        from config.app_config import load_app_config
        cfg = load_app_config()
        return cfg.get("provider", ""), cfg.get("model", "")
    except Exception:
        return "", ""


def get_api_key() -> str:
    """Check secrets → env vars → config/app_config.json → session state."""
    backend_key, _source = get_backend_api_key()
    if backend_key:
        return backend_key
    return st.session_state.get("api_key_input", "")


def detect_provider(api_key: str) -> str:
    """
    Detect LLM provider from API key format.
    Returns: 'gemini' | 'openai' | 'anthropic' | 'unknown'
    """
    if not api_key:
        return "unknown"
    key = api_key.strip()
    if key.startswith("AIza"):
        return "gemini"
    if key.startswith("sk-ant-"):
        return "anthropic"
    if key.startswith("gsk_"):
        return "groq"
    if key.startswith("sk-") and not key.startswith("sk-ant-"):
        return "openai"
    return "unknown"


def resolve_model(api_key: str) -> tuple[str, str]:
    """
    Given an API key, resolve the (provider, model) to use.

    Priority:
      1. Explicit provider/model set in config/app_config.json — e.g.
         {"provider": "groq", "model": "llama-3.3-70b-versatile"}. This is
         authoritative: if you've told the config file which provider and
         model to use, that's what gets used, no auto-detection involved.
      2. Otherwise, detect provider from the key's format (AIza.../sk-.../
         sk-ant-.../gsk_...) and auto-pick the best available model for it.

    Caches result in session state to avoid repeated API calls.
    """
    cache_key = f"_model_cache_{api_key[:8]}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    cfg_provider, cfg_model = get_configured_provider_model()
    if cfg_provider and cfg_model:
        result = (cfg_provider, cfg_model)
        st.session_state[cache_key] = result
        return result

    provider = detect_provider(api_key)

    if provider == "gemini":
        result = _resolve_gemini(api_key)
    elif provider == "openai":
        result = _resolve_openai(api_key)
    elif provider == "anthropic":
        result = _resolve_anthropic(api_key)
    elif provider == "groq":
        result = _resolve_groq(api_key)
    else:
        result = ("unknown", "")

    st.session_state[cache_key] = result
    return result


def _resolve_gemini(api_key: str) -> tuple[str, str]:
    """List available Gemini models and pick the best preferred one."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        available = [m.name.replace("models/", "") for m in genai.list_models()
                     if "generateContent" in m.supported_generation_methods]
        for preferred in PREFERRED_MODELS["gemini"]:
            if preferred in available:
                return ("gemini", preferred)
        # Fallback: pick first flash or pro available
        for m in available:
            if "flash" in m or "pro" in m:
                return ("gemini", m)
        return ("gemini", available[0] if available else "gemini-1.5-flash")
    except Exception:
        return ("gemini", "gemini-1.5-flash")


def _resolve_openai(api_key: str) -> tuple[str, str]:
    """List available OpenAI models and pick the best preferred one."""
    try:
        from openai import OpenAI
        client  = OpenAI(api_key=api_key)
        models  = [m.id for m in client.models.list().data]
        for preferred in PREFERRED_MODELS["openai"]:
            if preferred in models:
                return ("openai", preferred)
        for m in models:
            if "gpt-4" in m or "gpt-3.5" in m:
                return ("openai", m)
        return ("openai", "gpt-4o-mini")
    except Exception:
        return ("openai", "gpt-4o-mini")


def _resolve_anthropic(api_key: str) -> tuple[str, str]:
    """Anthropic has no list-models endpoint — use priority order directly."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        # Try each preferred model with a tiny test call
        for model in PREFERRED_MODELS["anthropic"]:
            try:
                client.messages.create(
                    model=model, max_tokens=1,
                    messages=[{"role": "user", "content": "hi"}]
                )
                return ("anthropic", model)
            except Exception:
                continue
        return ("anthropic", PREFERRED_MODELS["anthropic"][0])
    except Exception:
        return ("anthropic", PREFERRED_MODELS["anthropic"][0])


# ══════════════════════════════════════════════════════════════════════════════
# UNIFIED AI CALL
# ══════════════════════════════════════════════════════════════════════════════

def _resolve_groq(api_key: str) -> tuple[str, str]:
    """List available Groq models and pick best preferred one."""
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        available = [m.id for m in client.models.list().data]
        for preferred in PREFERRED_MODELS["groq"]:
            if preferred in available:
                return ("groq", preferred)
        return ("groq", available[0] if available else PREFERRED_MODELS["groq"][0])
    except Exception:
        return ("groq", PREFERRED_MODELS["groq"][0])


def call_ai(prompt: str, system: str = "", api_key: str = None) -> str:
    """
    Single unified AI call — uses LLM provider and model selected in the sidebar.
    """
    if api_key is None:
        api_key = get_api_key()
    if not api_key:
        st.error("No API key found. Enter your key in the sidebar.")
        st.stop()

    # Prefer explicit selection from sidebar
    prov = st.session_state.get("llm_provider", "").strip()
    model = st.session_state.get("llm_model", "").strip()
    if not prov or not model:
        st.error("Select LLM provider and model in the sidebar (and provide API key).")
        st.stop()

    provider = prov.lower()

    if provider == "gemini":
        return _call_gemini(api_key, model, system, prompt)
    elif provider == "openai":
        return _call_openai(api_key, model, system, prompt)
    elif provider == "anthropic":
        return _call_anthropic(api_key, model, system, prompt)
    elif provider == "groq":
        return _call_groq(api_key, model, system, prompt)
    else:
        st.error("Unsupported provider selected. Choose Gemini, OpenAI, Anthropic or Groq.")
        st.stop()


def _call_gemini(api_key, model, system, prompt) -> str:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    m = genai.GenerativeModel(model_name=model,
                              system_instruction=system if system else None)
    return m.generate_content(prompt).text


def _call_openai(api_key, model, system, prompt) -> str:
    from openai import OpenAI
    client   = OpenAI(api_key=api_key)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(model=model, messages=messages)
    return resp.choices[0].message.content


def _call_anthropic(api_key, model, system, prompt) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    kwargs = {"model": model, "max_tokens": 4096,
              "messages": [{"role": "user", "content": prompt}]}
    if system:
        kwargs["system"] = system
    return client.messages.create(**kwargs).content[0].text


def _call_groq(api_key, model, system, prompt) -> str:
    from groq import Groq
    client   = Groq(api_key=api_key)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(model=model, messages=messages)
    return resp.choices[0].message.content


def call_ai_chat(messages: list, system: str, api_key: str = None) -> str:
    """
    Multi-turn chat call — used by Module 1 conversation.
    Uses provider/model selected in sidebar.
    """
    if api_key is None:
        api_key = get_api_key()
    if not api_key:
        st.error("No API key found. Enter your key in the sidebar.")
        st.stop()

    prov = st.session_state.get("llm_provider", "").strip()
    model = st.session_state.get("llm_model", "").strip()
    if not prov or not model:
        st.error("Select LLM provider and model in the sidebar (and provide API key).")
        st.stop()

    provider = prov.lower()

    if provider == "gemini":
        return _chat_gemini(api_key, model, system, messages)
    elif provider == "openai":
        return _chat_openai(api_key, model, system, messages)
    elif provider == "anthropic":
        return _chat_anthropic(api_key, model, system, messages)
    elif provider == "groq":
        return _chat_groq(api_key, model, system, messages)
    else:
        st.error("Unsupported provider selected. Choose Gemini, OpenAI, Anthropic or Groq.")
        st.stop()


def _chat_gemini(api_key, model, system, messages) -> str:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    m       = genai.GenerativeModel(model_name=model, system_instruction=system)
    history = [{"role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["content"]]} for msg in messages[:-1]]
    chat    = m.start_chat(history=history)
    return chat.send_message(messages[-1]["content"]).text


def _chat_openai(api_key, model, system, messages) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    msgs   = [{"role": "system", "content": system}] if system else []
    for msg in messages:
        msgs.append({"role": msg["role"], "content": msg["content"]})
    resp = client.chat.completions.create(model=model, messages=msgs)
    return resp.choices[0].message.content


def _chat_anthropic(api_key, model, system, messages) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    msgs   = [{"role": m["role"], "content": m["content"]} for m in messages]
    kwargs = {"model": model, "max_tokens": 2048, "messages": msgs}
    if system:
        kwargs["system"] = system
    return client.messages.create(**kwargs).content[0].text


def _chat_groq(api_key, model, system, messages) -> str:
    from groq import Groq
    client = Groq(api_key=api_key)
    msgs   = [{"role": "system", "content": system}] if system else []
    for msg in messages:
        msgs.append({"role": msg["role"], "content": msg["content"]})
    resp = client.chat.completions.create(model=model, messages=msgs)
    return resp.choices[0].message.content


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 1 — CONVERSATION
# ══════════════════════════════════════════════════════════════════════════════

def get_missing_fields() -> list:
    ext = st.session_state.get("extracted", {})
    return [label for key, label in REQUIRED_FIELDS
            if not ext.get(key) or ext.get(key) in ("null", "unknown", "TBD", "")]


def call_m1_ai(messages: list) -> str:
    missing = get_missing_fields()
    last    = messages[-1]["content"]
    if missing:
        injected = ("[MISSING FIELDS — ask about the FIRST one only]:\n"
                    + "\n".join(f"- {m}" for m in missing)
                    + f"\n\n[USER MESSAGE]:\n{last}")
    else:
        injected = f"[ALL FIELDS COLLECTED — confirm summary now]\n\n[USER MESSAGE]:\n{last}"

    msgs = messages[:-1] + [{"role": "user", "content": injected}]
    return call_ai_chat(msgs, system=M1_SYSTEM_PROMPT)


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 2 — ASSESSMENT
# ══════════════════════════════════════════════════════════════════════════════

def call_m2_assessment(problem: dict) -> dict | None:
    from config.prompts import M2_ASSESSMENT_PROMPT
    prompt = f"""{M2_ASSESSMENT_PROMPT}

PROBLEM STATEMENT TO ASSESS:
- Business problem: {problem.get('problem_statement', '')}
- Business objective: {problem.get('business_objective', '')}
- Proposed solution: {problem.get('solution_approach', '')}
- Workflow / department: {problem.get('workflow_location', '')}
- Decision support needed: {problem.get('decision_support', '')}
- Timeline: {problem.get('timeline', '')}
- Action owner: {problem.get('action_owner', '')}
- Quantified business value: {problem.get('business_value', '')}
- ISO 42001 Risk Category: {problem.get('iso_risk_category', 'Not specified')}
- Affected stakeholders: {problem.get('affected_stakeholders', '')}
- Human override mechanism: {problem.get('human_override', '')}
- Data sources & PII: {problem.get('data_sources', '')}
- Success criteria: {problem.get('success_criteria', '')}

Apply hard gate rules and ISO risk penalty as defined. Return ONLY the JSON object."""

    try:
        raw  = call_ai(prompt)
        text = clean_llm_json(raw)
        parsed = json.loads(text)
        from governance.rules import validate_feasibility_result
        validated = validate_feasibility_result(parsed, problem)
        _record_llm_run(problem.get("id"), "feasibility", raw, "succeeded")
        return validated
    except json.JSONDecodeError as e:
        st.error(f"AI returned malformed JSON: {e}")
        st.code(raw[:800], language="json")
        return None
    except Exception as e:
        _record_llm_run(problem.get("id"), "feasibility", "", "failed", str(e))
        st.error(f"AI assessment failed: {e}")
        return None


def _record_llm_run(problem_id, task_type, response, status, error=""):
    """Store reproducibility metadata without persisting confidential prompt text."""
    try:
        from database.db import get_conn
        provider = st.session_state.get("llm_provider", "")
        model = st.session_state.get("llm_model", "")
        conn = get_conn()
        conn.execute("""INSERT INTO llm_runs
            (id, problem_id, task_type, provider, model, prompt_hash, response_hash, status, error, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), problem_id, task_type, provider, model, "",
             hashlib.sha256((response or "").encode()).hexdigest(), status, error[:500],
             datetime.now(timezone.utc).isoformat(timespec="seconds")))
        conn.commit(); conn.close()
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# SHARED UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

def get_completeness_color(pct: int) -> str:
    if pct < 40:  return "#E24B4A"
    if pct < 75:  return "#EF9F27"
    return "#1D9E75"


def sanitize_ai_text(text: str) -> str:
    """
    Strip any HTML tags the LLM may have echoed into a free-text field
    (e.g. hard_gate_reason, overall_summary). AI-generated strings are
    plain text by contract, but models occasionally mirror markup from
    the prompt back into their output. Rendering that raw — whether via
    st.error()/st.markdown() in plain mode, or interpolated into an
    unsafe_allow_html block — can break the surrounding layout or print
    stray tags like "</div>" as visible text. This neutralises tags
    without altering normal punctuation (e.g. "x < y" stays intact).
    """
    if not text:
        return text
    import re as _re
    # Remove anything that looks like an actual tag: <word ...> or </word>
    cleaned = _re.sub(r"</?[a-zA-Z][^<>]{0,200}>", "", text)
    # Escape any remaining bare angle brackets so they can't be
    # misinterpreted if this string is later placed in an HTML context
    cleaned = cleaned.replace("<", "&lt;").replace(">", "&gt;")
    return cleaned.strip()


def is_field_done(key: str) -> bool:
    v = st.session_state.extracted.get(key)
    return bool(v and v not in ("null", "unknown", "TBD", ""))


def parse_extracted(text: str) -> dict | None:
    m = re.search(r"```json\s*([\s\S]*?)```", text)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def strip_json(text: str) -> str:
    return re.sub(r"```json[\s\S]*?```", "", text).strip()

def clean_llm_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return text
