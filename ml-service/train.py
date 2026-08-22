"""
train.py
─────────────────────────────────────────────────────────────────────────────
Improvements over previous version:
  1. No Google Translate / langdetect API calls — replaced with offline
     multilingual preprocessing (keyword dictionary in preprocess.py).
  2. Synthetic data augmentation — common misclassified patterns added so
     the model learns "power cut" → electric, "paani nahi" → water, etc.
  3. Proper 80/20 train/test split with no data leakage.
  4. Evaluation: Precision, Recall, F1 per class + confusion matrix charts.
  5. Retrain on full data before saving to disk for production.
─────────────────────────────────────────────────────────────────────────────
"""

import pandas as pd
import pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

from preprocess import preprocess_text


# ── SYNTHETIC AUGMENTATION DATA ────────────────────────────────────────────
# These examples patch common misclassification gaps in the KDMC dataset.
# Each tuple is (complaint_text, category_label).
# Category labels must match those in the KDMC dataset exactly.

AUGMENTED_DATA = [
    # ── Electric Department ──────────────────────────────────────────────
    ("power cut in our area since morning",                  "Electric Department"),
    ("no electricity since last night",                      "Electric Department"),
    ("power outage in sector 4",                             "Electric Department"),
    ("light is not working on our street",                   "Electric Department"),
    ("streetlight not working near school",                  "Electric Department"),
    ("electricity has been cut for 3 days",                  "Electric Department"),
    ("transformer burnt near market",                        "Electric Department"),
    ("no current in our building",                           "Electric Department"),
    ("load shedding problem in our ward",                    "Electric Department"),
    ("electric pole damaged after rain",                     "Electric Department"),
    ("bijli nahi hai hamare area mein",                      "Electric Department"),
    ("batti gayi hai raat se",                               "Electric Department"),
    ("light nahi aa rahi",                                   "Electric Department"),
    ("veej nahi aahe amchya bhagat",                         "Electric Department"),
    ("andhera hai sarak par",                                "Electric Department"),
    ("हमारे क्षेत्र में बिजली नहीं है",                     "Electric Department"),
    ("बत्ती गई है रात से",                                  "Electric Department"),
    ("वीज नाही आमच्या भागात",                               "Electric Department"),
    ("power supply issue in colony",                         "Electric Department"),
    ("electric wire hanging dangerously",                    "Electric Department"),
    ("voltage fluctuation problem",                          "Electric Department"),
    ("electricity meter not working",                        "Electric Department"),
    ("street light pole broken",                             "Electric Department"),
    ("lamp post not working since week",                     "Electric Department"),

    # ── Water Supply Department ──────────────────────────────────────────
    ("no water supply in our area",                          "Water Supply Department"),
    ("water not coming from tap",                            "Water Supply Department"),
    ("dirty water coming from pipe",                         "Water Supply Department"),
    ("pipe burst near junction",                             "Water Supply Department"),
    ("drinking water problem in colony",                     "Water Supply Department"),
    ("water pressure very low",                              "Water Supply Department"),
    ("water supply cut for 2 days",                          "Water Supply Department"),
    ("paani nahi aa raha nal mein",                          "Water Supply Department"),
    ("pani band hai kal se",                                 "Water Supply Department"),
    ("ganda paani aa raha hai",                              "Water Supply Department"),
    ("पानी नहीं आ रहा है",                                  "Water Supply Department"),
    ("पाणी येत नाही",                                        "Water Supply Department"),
    ("nal band hai hafte se",                                "Water Supply Department"),
    ("water pipe leaking on road",                           "Water Supply Department"),
    ("water tank not filled",                                "Water Supply Department"),

    # ── Sewage & Drainage Department ─────────────────────────────────────
    ("drainage blocked in our lane",                         "Sewage & Drainage Department"),
    ("sewage overflow on road",                              "Sewage & Drainage Department"),
    ("manhole open and overflowing",                         "Sewage & Drainage Department"),
    ("nala blocked causing water logging",                   "Sewage & Drainage Department"),
    ("sewage smell coming from drain",                       "Sewage & Drainage Department"),
    ("gutter blocked near building",                         "Sewage & Drainage Department"),
    ("naali jam hai colony mein",                            "Sewage & Drainage Department"),
    ("नाला बंद है पानी भर गया",                             "Sewage & Drainage Department"),
    ("गटार तुंबले आहे",                                     "Sewage & Drainage Department"),
    ("drain overflowing during rain",                        "Sewage & Drainage Department"),
    ("sewer line choked",                                    "Sewage & Drainage Department"),
    ("waterlogging due to blocked drain",                    "Sewage & Drainage Department"),

    # ── Road & Traffic Department ─────────────────────────────────────────
    ("big pothole on main road",                             "Road & Traffic management Department"),
    ("road full of potholes near school",                    "Road & Traffic management Department"),
    ("road broken after monsoon",                            "Road & Traffic management Department"),
    ("traffic signal not working",                           "Road & Traffic management Department"),
    ("road repair needed urgently",                          "Road & Traffic management Department"),
    ("sadak kharab hai bahut",                               "Road & Traffic management Department"),
    ("rasta kharab hai khade hain bahut",                    "Road & Traffic management Department"),
    ("सड़क टूटी हुई है",                                    "Road & Traffic management Department"),
    ("रस्त्यावर खड्डे आहेत",                                "Road & Traffic management Department"),
    ("speed breaker missing on highway",                     "Road & Traffic management Department"),
    ("footpath encroached by vendors",                       "Road & Traffic management Department"),
    ("divider broken on road",                               "Road & Traffic management Department"),

    # ── Solid Waste Management ────────────────────────────────────────────
    ("garbage not collected for 3 days",                     "Solid Waste Management"),
    ("no sweeping done in our area",                         "Solid Waste Management"),
    ("dustbin overflowing near market",                      "Solid Waste Management"),
    ("waste dumped on road",                                 "Solid Waste Management"),
    ("rubbish not cleared",                                  "Solid Waste Management"),
    ("kachra nahi utha hai",                                 "Solid Waste Management"),
    ("gandagi bahut hai gali mein",                          "Solid Waste Management"),
    ("कचरा नहीं उठाया गया",                                 "Solid Waste Management"),
    ("कचरा उचलला नाही",                                     "Solid Waste Management"),
    ("waste collection vehicle not coming",                  "Solid Waste Management"),
    ("illegal garbage dumping",                              "Solid Waste Management"),
    ("safai nahi ho rahi hai",                               "Solid Waste Management"),

    # ── Encroachment Department ───────────────────────────────────────────
    ("illegal construction on footpath",                     "Encroachment Department"),
    ("encroachment on public road",                          "Encroachment Department"),
    ("illegal shop on footpath",                             "Encroachment Department"),
    ("unauthorized construction",                            "Encroachment Department"),
    ("atikraman ho raha hai",                                "Encroachment Department"),
    ("अतिक्रमण हटाओ",                                       "Encroachment Department"),
    ("अतिक्रमण काढा",                                       "Encroachment Department"),
    ("kabja kar liya public land par",                       "Encroachment Department"),
    ("illegal parking blocking road",                        "Encroachment Department"),
    ("unauthorized stall on footpath",                       "Encroachment Department"),
]


# ── LOAD AND PREPARE DATA ──────────────────────────────────────────────────
print("📂 Loading KDMC dataset...")
df = pd.read_excel("../dataset/kdmc_data.xlsx")

df.rename(columns={
    "Complaint Description": "complaint",
    "Complaint Type":        "category"
}, inplace=True)
# ── CLEAN CATEGORY LABELS ─────────────────────────────────────────────────
# This is the single most important fix — standardise all label variants
# into 6 clean consistent categories matching the departmentMap in backend.

CATEGORY_MAP = {
    # Water
    "Water Supply Department":   "Water Supply Department",
    "Water Supply Department ":  "Water Supply Department",   # trailing space

    # Solid Waste
    "Solid Waste Management":            "Solid Waste Management",
    "Solid Waste Management Department": "Solid Waste Management",

    # Road & Traffic
    "Road & Traffic Related":              "Road & Traffic management Department",
    "Road & Traffic management Department":"Road & Traffic management Department",

    # Electric / Street Light
    "Street Light":         "Electric Department",
    "Electric Department":  "Electric Department",

    # Sewage / Drainage — merge all drainage into one
    "Sewage & Drainage Department":                         "Sewage & Drainage Department",
    "Strom Water Drainage":                                  "Sewage & Drainage Department",
    "Underground Drainage(Chambers / manholes under road)": "Sewage & Drainage Department",

    # Encroachment
    "Encroachment Department": "Encroachment Department",
}

df['category'] = df['category'].str.strip()           # removes trailing spaces
df['category'] = df['category'].map(CATEGORY_MAP)     # standardises names
df = df.dropna(subset=['category'])                   # drop any unmapped rows
print(f"   After label cleaning: {sorted(df['category'].unique())}")

df = df[['complaint', 'category']].dropna()
print(f"   Original dataset: {len(df)} rows")

# Append synthetic augmentation
aug_df = pd.DataFrame(AUGMENTED_DATA, columns=['complaint', 'category'])
df = pd.concat([df, aug_df], ignore_index=True)
print(f"   After augmentation: {len(df)} rows (+{len(aug_df)} synthetic)")

# Preprocess — offline multilingual expansion (no API)
print("🔤 Preprocessing text (multilingual keyword expansion)...")
df['clean_text'] = df['complaint'].astype(str).apply(preprocess_text)

X = df['clean_text']
y = df['category']

print(f"   Categories: {sorted(y.unique())}")


# ── TRAIN / TEST SPLIT ─────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\n📊 Train: {len(X_train)} | Test: {len(X_test)}")


# ── VECTORIZATION — fit only on training data ──────────────────────────────
vectorizer = TfidfVectorizer(
    stop_words='english',
    ngram_range=(1, 2),      # unigrams + bigrams capture "power cut", "no water"
    min_df=1,                # keep even rare terms (important for augmented data)
    max_features=8000
)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec  = vectorizer.transform(X_test)     # no fit → no data leakage


# ── TRAIN MODEL ────────────────────────────────────────────────────────────
print("🤖 Training Logistic Regression...")
model = LogisticRegression(
    max_iter=500,
    C=5.0,           # slightly higher regularisation strength vs default
    solver='lbfgs',
    multi_class='auto'
)
model.fit(X_train_vec, y_train)


# ── EVALUATE ───────────────────────────────────────────────────────────────
y_pred = model.predict(X_test_vec)

print("\n📈 Classification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

# Chart 1 — Precision / Recall / F1 bar chart
report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
report_df = pd.DataFrame(report).transpose()
report_df = report_df.drop(index=['accuracy', 'macro avg', 'weighted avg'], errors='ignore')
report_df = report_df[['precision', 'recall', 'f1-score']]

report_df.plot(kind='bar', figsize=(14, 6), colormap='Set2', edgecolor='black')
plt.title('Precision, Recall & F1-Score per Department', fontsize=14, fontweight='bold')
plt.xlabel('Department Category', fontsize=11)
plt.ylabel('Score (0–1)', fontsize=11)
plt.xticks(rotation=30, ha='right')
plt.ylim(0, 1.1)
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig('metrics_bar_chart.png', dpi=150)
plt.close()
print("✅ Saved: metrics_bar_chart.png")

# Chart 2 — Confusion matrix heatmap
labels = sorted(y.unique())
cm = confusion_matrix(y_test, y_pred, labels=labels)
plt.figure(figsize=(12, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=labels, yticklabels=labels)
plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
plt.xlabel('Predicted Department', fontsize=11)
plt.ylabel('Actual Department', fontsize=11)
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig('confusion_matrix.png', dpi=150)
plt.close()
print("✅ Saved: confusion_matrix.png")


# ── RETRAIN ON FULL DATA BEFORE SAVING ────────────────────────────────────
# Evaluation was on 20% held-out data.
# For production, we retrain on 100% so the saved model has seen everything.
print("\n🔁 Retraining on full dataset for production...")
X_full_vec = vectorizer.fit_transform(X)
model.fit(X_full_vec, y)

pickle.dump(model,      open("model.pkl",      "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))
print("✅ model.pkl and vectorizer.pkl saved.")
print("\n✅ Training complete!")
