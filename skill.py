import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# Load Data
df = pd.read_csv("skill_data.csv")

# Check available columns
print("Columns in dataset:", df.columns)

# Ensure required columns exist
if "skill" not in df.columns or "demand" not in df.columns:
    raise ValueError("❌ Required columns 'skill' and 'demand' not found in dataset!")

# Rename column for consistency
df.rename(columns={"skill": "skills_required"}, inplace=True)

# Fill missing values in skills column (if any)
df["skills_required"] = df["skills_required"].fillna("")

# Convert demand to categorical values if it's not numeric
if df["demand"].dtype == 'object':
    df["demand"] = df["demand"].astype('category').cat.codes

# Feature Extraction using TF-IDF
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df["skills_required"])
y = df["demand"]

# Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save Model & Vectorizer
joblib.dump(model, "career_recommendation_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("✅ Model Training Completed and Saved.")
