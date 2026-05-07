import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline
import joblib

print("🚀 Loading training data...")
# 1. Load the dataset
df = pd.read_csv("ml_models/training_data.csv")

# 2. Create an ML Pipeline (TF-IDF + LinearSVC)
# TF-IDF turns words into mathematical vectors.
# LinearSVC draws the mathematical boundary between the zones.
model = make_pipeline(
    TfidfVectorizer(ngram_range=(1, 2), stop_words="english"),
    LinearSVC(dual=False, class_weight="balanced")
)

print("🧠 Training the zoning classifier...")
# 3. Train the model
model.fit(df["text"], df["label"])

# 4. Save the trained model to disk
joblib.dump(model, "ml_models/zoning_classifier.joblib")
print("✅ Model saved to ml_models/zoning_classifier.joblib!")