import json
from google import genai
from google.genai import types
from models import LegalGenome
import os

# 1. Securely load your Gemini Key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("🚨 GEMINI_API_KEY is missing! Did you export it in the terminal?")

# 2. Initialize the modern Google GenAI Client
client = genai.Client(api_key=api_key)

def generate_legal_dna(zoned_blocks):
    # Filter out noise (Background Zone) so the LLM stays laser-focused
    critical_text = "\n".join([
        f"[{b['zone']}] (Chars {b['start_char']}-{b['end_char']}): {b['text']}" 
        for b in zoned_blocks if b['zone'] in ["Direction Zone", "Observation Zone", "Preamble Zone"]
    ])[:30000]
    
    system_prompt = """
    You are a legal extraction AI for the Centre for e-Governance.
    1. Extract explicitly ordered directives into LegalDNAUnits.
    2. Determine Strategy (APPEAL vs COMPLY) based on the 'Observation Zone' tone. Provide reasoning.
    3. Calculate the 3-axis confidence scores.
    4. For 'source_span', copy the exact_text, start_char, and end_char exactly as provided in the brackets preceding the text.
    """
    
    # 3. Fire the request using Google's native Structured Outputs!
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[system_prompt, critical_text],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LegalGenome,
            temperature=0.1, # Keep temperature low for strict, analytical extraction
        ),
    )
    
    # 4. Convert the AI's JSON response directly into our Python model
    genome_dict = json.loads(response.text)
    return LegalGenome(**genome_dict)