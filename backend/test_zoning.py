from zoning_engine import classify_paragraph

# Let's test it with brand new sentences it has never seen before!
test_sentences = [
    "The respondent authorities are hereby ordered to immediately reinstate the petitioner.",
    "It is the case of the plaintiff that no prior hearing was provided before the termination.",
    "IN THE SUPREME COURT OF INDIA CIVIL APPELLATE JURISDICTION"
]

print("🔍 Testing ML Zoning Engine...\n")
for sentence in test_sentences:
    prediction = classify_paragraph(sentence)
    print(f"Text: '{sentence}'")
    print(f"🧠 Zone: {prediction}\n")
    print("-" * 40)