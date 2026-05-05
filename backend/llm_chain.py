import json
from google import genai
from google.genai import types
from models import LegalGenome
import os

# NEW IMPORT: Bring in our custom Decision Engine signals
from decision_engine import get_precedent_signal, calculate_inferred_deadline

# 1. Securely load your Gemini Key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("🚨 GEMINI_API_KEY is missing! Did you export it in the terminal?")

# 2. Initialize the modern Google GenAI Client
client = genai.Client(api_key=api_key)

def generate_legal_dna(zoned_blocks):
    # SOFT FILTERING: We pass all blocks, but with their ML tags attached!
    # No slicing here, so Gemini reads the entire 60+ page document.
    critical_text = "\n".join([
        f"[{b['zone']}] (Chars {b['start_char']}-{b['end_char']}): {b['text']}" 
        for b in zoned_blocks 
    ])
    
    # ---------------------------------------------------------
    # NEW: LAYER 3 DECISION ENGINE INJECTION
    # ---------------------------------------------------------
    # Grab a small sample of the text to check our Vector DB and Rules Engine
    sample_text = critical_text[:1000] 
    
    # Fire the signals!
    precedent_signal = get_precedent_signal(sample_text)
    timeline_signal = calculate_inferred_deadline(sample_text)
    
    # Note the 'f' before the quotes below! This allows us to inject our signals.
    system_prompt = f"""
    You are a highly advanced legal extraction AI for the Centre for e-Governance.
    You evaluate judgments using extracted text and external systemic signals.
    
    EXTERNAL SYSTEM SIGNALS FOR THIS CASE:
    - Precedent Memory: {precedent_signal}
    - Statutory Timeline Engine: {timeline_signal}
    
    TASKS:
    1. Extract explicitly ordered directives into LegalDNAUnits. 
       * Pay primary attention to the [Direction Zone], [Operative Zone], and [Timeline Zone].
       * However, if you find a binding directive misclassified inside a [Background Zone] or [Observation Zone], extract it anyway.
    2. Determine Strategy (APPEAL vs COMPLY). You MUST factor in the 'Precedent Memory' signal provided above when writing your reasoning.
    3. Calculate the 3-axis confidence scores.
    4. For 'timeline_inferred', use the 'Statutory Timeline Engine' signal provided above if the text lacks an explicit date.
    5. For 'source_span', copy the exact_text, start_char, and end_char exactly as provided in the brackets preceding the text.
    """
    
    # 3. Fire the request using Google's native Structured Outputs
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[system_prompt, critical_text],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LegalGenome,
            temperature=0.1, 
        ),
    )
    
    # 4. Convert the AI's JSON response directly into our Python model
    genome_dict = json.loads(response.text)
    return LegalGenome(**genome_dict)