import json
import time
import logging
import os

from decision_engine import get_precedent_signal, calculate_inferred_deadline
from models import LegalGenome

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# API KEYS
# ─────────────────────────────────────────────
GEMINI_API_KEY    = os.environ.get("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MISTRAL_API_KEY   = os.environ.get("MISTRAL_API_KEY")

# ─────────────────────────────────────────────
# MODEL CASCADE (tried in order)
# ─────────────────────────────────────────────
# Each entry: (provider, model_name)
MODEL_CASCADE = [
    ("gemini",    "gemini-2.5-flash"),
    ("gemini",    "gemini-2.0-flash"),
    ("gemini",    "gemini-1.5-flash"),
    ("anthropic", "claude-sonnet-4-5"),
    ("mistral",   "mistral-large-latest"),
]

MAX_RETRIES        = 3
INITIAL_RETRY_WAIT = 5   # seconds; doubles each attempt


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _is_transient(err: str) -> bool:
    markers = ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED",
               "overloaded", "high demand", "too many requests", "rate limit"]
    el = err.lower()
    return any(m.lower() in el for m in markers)


def _build_prompts(zoned_blocks):
    """Shared prompt content for all providers."""
    critical_text = "\n".join([
        f"[{b['zone']}] (Chars {b['start_char']}-{b['end_char']}): {b['text']}"
        for b in zoned_blocks
    ])
    sample_text       = critical_text[:1000]
    precedent_signal  = get_precedent_signal(sample_text)
    timeline_signal   = calculate_inferred_deadline(sample_text)

    system_prompt = f"""You are a highly advanced legal extraction AI for the Centre for e-Governance.
You evaluate judgments using extracted text and external systemic signals.

EXTERNAL SYSTEM SIGNALS FOR THIS CASE:
- Precedent Memory: {precedent_signal}
- Statutory Timeline Engine: {timeline_signal}

TASKS:
1. Extract explicitly ordered directives into LegalDNAUnits.
   * Pay primary attention to [Direction Zone], [Operative Zone], [Timeline Zone].
   * If a binding directive is misclassified inside [Background Zone] or [Observation Zone], extract it anyway.
2. Determine Strategy (APPEAL vs COMPLY). Factor in the Precedent Memory signal in your reasoning.
3. Calculate the 3-axis confidence scores (integers 1-100).
4. For timeline_inferred, use the Statutory Timeline Engine signal if no explicit date exists.
5. For source_span, copy exact_text, start_char, and end_char from the brackets preceding the text.

Respond with ONLY valid JSON — no markdown fences, no explanation — matching this schema exactly:
{{
  "case_metadata": {{
    "case_title": "string",
    "date": "string",
    "parties_involved": "string"
  }},
  "directions": [
    {{
      "action_verb": "string",
      "action_subject": "string",
      "action_object": "string",
      "timeline_explicit": "string or null",
      "timeline_inferred": "string or null",
      "compliance_vs_appeal": "COMPLY or APPEAL",
      "reasoning": "string",
      "source_span": {{
        "start_char": 0,
        "end_char": 0,
        "exact_text": "string"
      }},
      "confidence": {{
        "extraction_confidence": 85,
        "timeline_confidence": 70,
        "action_confidence": 90
      }},
      "is_verified": false
    }}
  ]
}}"""
    return system_prompt, critical_text


def _strip_fences(text: str) -> str:
    """Remove ```json ... ``` wrappers if the model adds them."""
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


def _parse(raw: str) -> LegalGenome:
    return LegalGenome(**json.loads(_strip_fences(raw)))


# ─────────────────────────────────────────────
# PROVIDER CALLERS
# ─────────────────────────────────────────────
def _call_gemini(model: str, system_prompt: str, critical_text: str) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set — skipping Gemini models.")
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=model,
        contents=[system_prompt, critical_text],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LegalGenome,
            temperature=0.1,
        ),
    )
    return response.text


def _call_anthropic(model: str, system_prompt: str, critical_text: str) -> str:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY not set — skipping Claude.")
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=model,
        max_tokens=8000,
        temperature=0,
        system=system_prompt,
        messages=[{"role": "user", "content": critical_text}],
    )
    return response.content[0].text


def _call_mistral(model: str, system_prompt: str, critical_text: str) -> str:
    if not MISTRAL_API_KEY:
        raise RuntimeError("MISTRAL_API_KEY not set — skipping Mistral.")
    from mistralai import Mistral
    client = Mistral(api_key=MISTRAL_API_KEY)
    response = client.chat.complete(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": critical_text},
        ],
    )
    return response.choices[0].message.content


CALLERS = {
    "gemini":    _call_gemini,
    "anthropic": _call_anthropic,
    "mistral":   _call_mistral,
}


# ─────────────────────────────────────────────
# CORE: retry + cascade logic
# ─────────────────────────────────────────────
def _call_with_retry(provider: str, model: str, system_prompt: str, critical_text: str) -> str:
    caller = CALLERS[provider]
    delay  = INITIAL_RETRY_WAIT
    last_err = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"🔁 [{provider.upper()}] Attempt {attempt}/{MAX_RETRIES} — {model}")
            return caller(model, system_prompt, critical_text)
        except Exception as e:
            last_err = e
            if _is_transient(str(e)) and attempt < MAX_RETRIES:
                logger.warning(f"⚠️  Transient error on {model}. Retrying in {delay}s... ({attempt}/{MAX_RETRIES})")
                time.sleep(delay)
                delay *= 2
            else:
                raise   # non-transient OR final attempt → let cascade move on

    raise last_err  # shouldn't reach here, but satisfies type checkers


# ─────────────────────────────────────────────
# PUBLIC ENTRY POINT
# ─────────────────────────────────────────────
def generate_legal_dna(zoned_blocks) -> LegalGenome:
    system_prompt, critical_text = _build_prompts(zoned_blocks)
    last_error = None

    for provider, model in MODEL_CASCADE:
        try:
            raw = _call_with_retry(provider, model, system_prompt, critical_text)
            result = _parse(raw)
            logger.info(f"✅ Success — [{provider.upper()}] {model}")
            return result

        except Exception as e:
            err_str = str(e)
            # Skip-worthy conditions: transient failure OR missing API key for this provider
            if _is_transient(err_str) or "not set" in err_str:
                logger.warning(f"❌ [{provider.upper()}] {model} failed — moving to next. Reason: {err_str[:120]}")
                last_error = e
                continue
            # Hard error (schema mismatch, bad key content, etc.) — still cascade, but log loudly
            logger.error(f"💥 [{provider.upper()}] {model} hard error — {err_str[:200]}")
            last_error = e
            continue

    raise RuntimeError(
        f"🚨 All models in the cascade failed. Last error: {last_error}"
    )