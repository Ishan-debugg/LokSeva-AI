"""
train.py
─────────────────────────────────────────────────────────────────────────────
Improvements over previous version:
  1. No Google Translate / langdetect API calls — replaced with offline
     multilingual preprocessing (keyword dictionary in preprocess.py).
  2. Synthetic data augmentation — common misclassified patterns added so
     the model learns "power cut" → electric, "paani nahi" → water, etc.
  3. Stratified grouped holdout; duplicate complaints and synthetic examples
     are kept out of the test set.
  4. Evaluation: Precision, Recall, F1 per class + confusion matrix charts.
  5. Retrain on full data before saving to disk for production.
─────────────────────────────────────────────────────────────────────────────
"""

import pandas as pd
import pickle
import re
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.pipeline import FeatureUnion
from sklearn.svm import LinearSVC

from preprocess import preprocess_text


MODEL_CONFIGS = [
    {"name": "logistic_C1", "kind": "logistic", "C": 1.0, "class_weight": None},
    {"name": "logistic_C5", "kind": "logistic", "C": 5.0, "class_weight": None},
    {"name": "logistic_C1_balanced", "kind": "logistic", "C": 1.0, "class_weight": "balanced"},
    {"name": "linear_svc_C0.5", "kind": "linear_svc", "C": 0.5, "class_weight": None},
    {"name": "linear_svc_C1", "kind": "linear_svc", "C": 1.0, "class_weight": None},
    {"name": "linear_svc_C1_balanced", "kind": "linear_svc", "C": 1.0, "class_weight": "balanced"},
]


def make_vectorizer():
    return FeatureUnion([
        ('word', TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_features=8000
        )),
        ('char', TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(3, 5),
            min_df=2,
            max_features=30000,
            sublinear_tf=True
        ))
    ])


def make_model(config):
    if config["kind"] == "linear_svc":
        return LinearSVC(
            C=config["C"],
            class_weight=config["class_weight"],
            max_iter=5000,
            random_state=42
        )
    return LogisticRegression(
        C=config["C"],
        class_weight=config["class_weight"],
        max_iter=1000,
        solver='lbfgs',
        random_state=42
    )


MARATHI_EVAL_MARKERS = {
    "आहे", "आहेत", "नाही", "नाहीत", "आमच्या", "आपल्या", "भागात",
    "येत", "काढा", "तुंबले", "तुंबलेला", "पाहिजे", "केली", "केले",
    "करून", "झाली", "झाले", "झालं", "होत", "मिळत", "त्यामुळे",
}


def has_marathi_markers(text):
    words = re.findall(r'[\u0900-\u097f]+', text)
    return bool(MARATHI_EVAL_MARKERS.intersection(words))


def choose_grouped_holdout(text, labels, random_states=range(42, 62)):
    target_test_fraction = 0.2
    class_counts = labels.value_counts()
    best_split = None
    for seed in random_states:
        splitter = StratifiedGroupKFold(
            n_splits=5, shuffle=True, random_state=seed
        )
        for fold_number, (candidate_train, candidate_test) in enumerate(
            splitter.split(text, labels, groups=text), start=1
        ):
            candidate_counts = labels.iloc[candidate_test].value_counts()
            class_fraction_error = (
                candidate_counts.reindex(class_counts.index, fill_value=0)
                / class_counts - target_test_fraction
            ).abs().mean()
            size_fraction_error = (
                abs(len(candidate_test) / len(labels) - target_test_fraction)
            )
            score = class_fraction_error + size_fraction_error
            if best_split is None or score < best_split[0]:
                best_split = (
                    score, candidate_train, candidate_test, seed, fold_number
                )

    if best_split is None:
        raise ValueError("Unable to create a grouped holdout split.")
    return best_split[1:]


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

# Preprocess — offline multilingual expansion (no API)
print("🔤 Preprocessing text (multilingual keyword expansion)...")
df['is_marathi'] = df['complaint'].astype(str).apply(has_marathi_markers)
df['clean_text'] = df['complaint'].astype(str).apply(preprocess_text)

X = df['clean_text'].reset_index(drop=True)
y = df['category'].reset_index(drop=True)
is_marathi = df['is_marathi'].reset_index(drop=True)

print(f"   Categories: {sorted(y.unique())}")


# ── SEPARATE GROUPED HOLDOUTS ─────────────────────────────────────────────
# Marathi is detected using explicit grammatical markers, not Devanagari
# script alone (Hindi and Marathi share that script). Keep mixed-language
# normalized groups in the primary evaluation rather than the Marathi set.
language_counts_by_group = pd.DataFrame({
    "clean_text": X,
    "is_marathi": is_marathi
}).groupby("clean_text")["is_marathi"].nunique()
mixed_language_groups = set(language_counts_by_group[language_counts_by_group > 1].index)
marathi_mask = is_marathi & ~X.isin(mixed_language_groups)
primary_mask = ~marathi_mask

primary_indices = X.index[primary_mask]
marathi_indices = X.index[marathi_mask]
X_primary = X.iloc[primary_indices].reset_index(drop=True)
y_primary = y.iloc[primary_indices].reset_index(drop=True)
X_marathi = X.iloc[marathi_indices].reset_index(drop=True)
y_marathi = y.iloc[marathi_indices].reset_index(drop=True)

primary_train_idx, primary_test_idx, primary_seed, primary_fold = (
    choose_grouped_holdout(X_primary, y_primary)
)
marathi_train_idx, marathi_test_idx, marathi_seed, marathi_fold = (
    choose_grouped_holdout(X_marathi, y_marathi)
)

X_train_primary = X_primary.iloc[primary_train_idx].reset_index(drop=True)
y_train_primary = y_primary.iloc[primary_train_idx].reset_index(drop=True)
X_test = X_primary.iloc[primary_test_idx].reset_index(drop=True)
y_test = y_primary.iloc[primary_test_idx].reset_index(drop=True)
X_train_marathi = X_marathi.iloc[marathi_train_idx].reset_index(drop=True)
y_train_marathi = y_marathi.iloc[marathi_train_idx].reset_index(drop=True)
X_marathi_test = X_marathi.iloc[marathi_test_idx].reset_index(drop=True)
y_marathi_test = y_marathi.iloc[marathi_test_idx].reset_index(drop=True)

X_train_real = pd.concat(
    [X_train_primary, X_train_marathi], ignore_index=True
)
y_train_real = pd.concat(
    [y_train_primary, y_train_marathi], ignore_index=True
)
test_groups = set(X_test) | set(X_marathi_test)
if set(X_train_real) & test_groups:
    raise ValueError("A normalized complaint group appears in training and holdout.")

aug_df = pd.DataFrame(AUGMENTED_DATA, columns=['complaint', 'category'])
aug_df['clean_text'] = aug_df['complaint'].astype(str).apply(preprocess_text)


def add_training_augmentation(train_text, train_labels, excluded_groups):
    eligible_aug = aug_df.loc[~aug_df['clean_text'].isin(excluded_groups)]
    augmented_text = pd.concat(
        [train_text, eligible_aug['clean_text']], ignore_index=True
    )
    augmented_labels = pd.concat(
        [train_labels, eligible_aug['category']], ignore_index=True
    )
    return augmented_text, augmented_labels


print(
    f"\n📊 Primary non-Marathi — Train: {len(X_train_primary)} | "
    f"Test: {len(X_test)}"
)
print(
    f"   Split seed/fold: {primary_seed}/{primary_fold}; "
    f"test groups: {X_test.nunique()}"
)
print(
    f"📊 Marathi marker benchmark — Train: {len(X_train_marathi)} | "
    f"Test: {len(X_marathi_test)}"
)
print(
    f"   Split seed/fold: {marathi_seed}/{marathi_fold}; "
    f"test groups: {X_marathi_test.nunique()} | "
    f"test classes: {sorted(y_marathi_test.unique())}"
)
print(
    f"   Marathi marker rows: {int(is_marathi.sum())}; "
    f"mixed-language groups held in primary set: {len(mixed_language_groups)}"
)

# Select hyperparameters against the primary non-Marathi evaluation only.
# Marathi training rows remain available during CV without scoring the Marathi
# holdout or exposing either holdout's normalized complaint groups.
cv_splitter = StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=43)
cv_splits = list(cv_splitter.split(
    X_train_primary, y_train_primary, groups=X_train_primary
))
cv_results = []
print("\n🔎 Tuning grouped 4-fold CV configurations...")

for config in MODEL_CONFIGS:
    fold_accuracy = []
    fold_macro_f1 = []
    for fold_train_idx, fold_valid_idx in cv_splits:
        fold_train_text = pd.concat([
            X_train_primary.iloc[fold_train_idx].reset_index(drop=True),
            X_train_marathi
        ], ignore_index=True)
        fold_train_labels = pd.concat([
            y_train_primary.iloc[fold_train_idx].reset_index(drop=True),
            y_train_marathi
        ], ignore_index=True)
        fold_valid_text = X_train_primary.iloc[fold_valid_idx].reset_index(drop=True)
        fold_valid_labels = y_train_primary.iloc[fold_valid_idx].reset_index(drop=True)
        valid_groups = set(fold_valid_text)

        fit_text, fit_labels = add_training_augmentation(
            fold_train_text, fold_train_labels, valid_groups | test_groups
        )
        fold_vectorizer = make_vectorizer()
        fit_vectors = fold_vectorizer.fit_transform(fit_text)
        valid_vectors = fold_vectorizer.transform(fold_valid_text)
        fold_model = make_model(config)
        fold_model.fit(fit_vectors, fit_labels)
        fold_predictions = fold_model.predict(valid_vectors)

        fold_accuracy.append(accuracy_score(fold_valid_labels, fold_predictions))
        fold_macro_f1.append(f1_score(
            fold_valid_labels, fold_predictions, average='macro', zero_division=0
        ))

    cv_results.append({
        **config,
        "mean_accuracy": sum(fold_accuracy) / len(fold_accuracy),
        "mean_macro_f1": sum(fold_macro_f1) / len(fold_macro_f1),
    })
    print(
        f"   {config['name']}: accuracy={cv_results[-1]['mean_accuracy']:.4f}, "
        f"macro_f1={cv_results[-1]['mean_macro_f1']:.4f}"
    )

# Prefer balanced per-class quality; use CV accuracy as the tie-breaker.
best_config = max(
    cv_results,
    key=lambda result: (result["mean_macro_f1"], result["mean_accuracy"])
)
print(f"\n✅ Selected by grouped CV: {best_config['name']}")

X_train, y_train = add_training_augmentation(
    X_train_real, y_train_real, test_groups
)
vectorizer = make_vectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)
X_marathi_test_vec = vectorizer.transform(X_marathi_test)
model = make_model(best_config)
model.fit(X_train_vec, y_train)


# ── EVALUATE ───────────────────────────────────────────────────────────────
y_pred = model.predict(X_test_vec)

print("\n📈 Classification Report:")
print(classification_report(y_test, y_pred, zero_division=0))
print(f"Primary non-Marathi holdout accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(
    "Primary non-Marathi holdout macro F1: "
    f"{f1_score(y_test, y_pred, average='macro', zero_division=0):.4f}"
)
marathi_pred = model.predict(X_marathi_test_vec)
print("\n📈 Separate Marathi Marker Benchmark:")
print(classification_report(
    y_marathi_test, marathi_pred, zero_division=0
))
print(
    f"Marathi marker holdout accuracy: "
    f"{accuracy_score(y_marathi_test, marathi_pred):.4f}"
)
print(
    f"Marathi marker holdout macro F1: "
    f"{f1_score(y_marathi_test, marathi_pred, average='macro', zero_division=0):.4f}"
)
print(
    "Note: Encroachment Department has synthetic training examples only and "
    "is not represented in either real-data holdout."
)

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
labels = sorted(set(y_test) | set(y_pred))
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

# Marathi-specific charts are reported separately and do not contribute to
# the primary non-Marathi accuracy.
marathi_report = classification_report(
    y_marathi_test, marathi_pred, output_dict=True, zero_division=0
)
marathi_report_df = pd.DataFrame(marathi_report).transpose()
marathi_report_df = marathi_report_df.drop(
    index=['accuracy', 'macro avg', 'weighted avg'], errors='ignore'
)
marathi_report_df = marathi_report_df[['precision', 'recall', 'f1-score']]
marathi_report_df.plot(
    kind='bar', figsize=(14, 6), colormap='Set2', edgecolor='black'
)
plt.title('Marathi Marker Benchmark: Precision, Recall & F1 by Department')
plt.xlabel('Department Category')
plt.ylabel('Score (0–1)')
plt.xticks(rotation=30, ha='right')
plt.ylim(0, 1.1)
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig('marathi_metrics_bar_chart.png', dpi=150)
plt.close()
print("✅ Saved: marathi_metrics_bar_chart.png")

marathi_labels = sorted(set(y_marathi_test) | set(marathi_pred))
marathi_cm = confusion_matrix(
    y_marathi_test, marathi_pred, labels=marathi_labels
)
plt.figure(figsize=(12, 8))
sns.heatmap(
    marathi_cm, annot=True, fmt='d', cmap='Greens',
    xticklabels=marathi_labels, yticklabels=marathi_labels
)
plt.title('Marathi Marker Benchmark Confusion Matrix')
plt.xlabel('Predicted Department')
plt.ylabel('Actual Department')
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig('marathi_confusion_matrix.png', dpi=150)
plt.close()
print("✅ Saved: marathi_confusion_matrix.png")

evaluation_metrics = {
    "marathi_language_identification": (
        "Heuristic based on explicit Marathi grammatical markers; "
        "not a manually verified language label."
    ),
    "primary_non_marathi": {
        "train_support": len(X_train_primary),
        "test_support": len(y_test),
        "accuracy": accuracy_score(y_test, y_pred),
        "macro_f1": f1_score(y_test, y_pred, average='macro', zero_division=0),
        "classification_report": classification_report(
            y_test, y_pred, output_dict=True, zero_division=0
        ),
    },
    "marathi_marker_benchmark": {
        "train_support": len(X_train_marathi),
        "test_support": len(y_marathi_test),
        "accuracy": accuracy_score(y_marathi_test, marathi_pred),
        "macro_f1": f1_score(
            y_marathi_test, marathi_pred, average='macro', zero_division=0
        ),
        "classification_report": marathi_report,
    },
    "selected_model": {
        "name": best_config["name"],
        "grouped_cv_accuracy": best_config["mean_accuracy"],
        "grouped_cv_macro_f1": best_config["mean_macro_f1"],
    },
}
with open("evaluation_metrics.json", "w", encoding="utf-8") as metrics_file:
    json.dump(evaluation_metrics, metrics_file, ensure_ascii=False, indent=2)
print("✅ Saved: evaluation_metrics.json")


# ── RETRAIN ON FULL DATA BEFORE SAVING ────────────────────────────────────
print("\n🔁 Retraining on full dataset for production...")
X_full = pd.concat([X, aug_df['clean_text']], ignore_index=True)
y_full = pd.concat([y, aug_df['category']], ignore_index=True)
vectorizer = make_vectorizer()
X_full_vec = vectorizer.fit_transform(X_full)
model = make_model(best_config)
model.fit(X_full_vec, y_full)

pickle.dump(model,      open("model.pkl",      "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))
print("✅ model.pkl and vectorizer.pkl saved.")
print("\n✅ Training complete!")
