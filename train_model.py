import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# ✅ Step 1: Connect to SQLite Database
conn = sqlite3.connect("career_guidance.db")

# ✅ Step 2: Fetch Data from Tables
query = """
SELECT p.job_id, p.title, p.description, 
       COALESCE(sal.max_salary, 0) AS max_salary, 
       COALESCE(sal.min_salary, 0) AS min_salary
FROM postings p
LEFT JOIN salaries sal ON p.job_id = sal.job_id
"""

try:
    df = pd.read_sql(query, conn)
    print("✅ Data Loaded Successfully!")
except Exception as e:
    print(f"❌ Error Fetching Data: {e}")
    conn.close()
    exit()

# ✅ Step 3: Close Database Connection
conn.close()

# ✅ Step 4: Data Preprocessing
df.fillna("", inplace=True)  # Fill NaN values
y = df["title"]  # Target variable (Job Titles)

# ✅ Step 5: Convert Text to Numerical Features
vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
X_vectorized = vectorizer.fit_transform(df["description"])  # Using only description for features

# ✅ Step 6: Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized, y, test_size=0.2, stratify=y, random_state=42
)

# ✅ Step 7: Train Random Forest Classifier
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# ✅ Step 8: Save Model & Vectorizer
joblib.dump(model, "career_recommendation_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("✅ Career Recommendation Model Trained & Saved Successfully!")
