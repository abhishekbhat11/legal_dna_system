import joblib
import os

# Load the trained ML model into memory when the server starts
MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml_models/zoning_classifier.joblib")

try:
    zoning_classifier = joblib.load(MODEL_PATH)
except FileNotFoundError:
    print("⚠️ ML Model not found! Did you run train_zoning_model.py?")
    zoning_classifier = None

def classify_paragraph(text: str) -> str:
    """Predicts the semantic zone of a given paragraph."""
    if not text.strip() or not zoning_classifier:
        return "Unknown Zone"
    
    # The ML model predicts the label instantly
    prediction = zoning_classifier.predict([text])[0]
    return prediction

def zone_document(pdf_blocks):
    """Takes blocks of text from PyMuPDF and tags them with ML."""
    zoned_blocks = []
    
    for block in pdf_blocks:
        zone_label = classify_paragraph(block["text"])
        zoned_blocks.append({
            "text": block["text"],
            "start_char": block["start_char"],
            "end_char": block["end_char"],
            "zone": zone_label
        })
        
    return zoned_blocks