# Complaint Classification: Evaluation and Roadmap to 95%

## Current evaluation

`train.py` now reserves independent grouped holdouts for the primary
non-Marathi evaluation and a Marathi-marker benchmark. It tunes model settings
using grouped cross-validation on the primary training partition, adds
synthetic examples only to training, and keeps normalized duplicate complaints
together. Holdouts are selected using label counts only—not model scores.

Latest run against `dataset/kdmc_data.xlsx`:

| Measure | Result |
|---|---:|
| Usable real complaints | 2,724 |
| Real labeled departments | 5 |
| Primary (non-Marathi marker) holdout | 448 complaints / 341 normalized text groups |
| Marathi-marker benchmark | 96 complaints / 91 normalized text groups |
| Selected model | Logistic Regression, `C=5` |
| Primary grouped 4-fold CV accuracy | 91.29% |
| Primary grouped 4-fold CV macro F1 | 90.57% |
| Primary holdout accuracy | 90.62% |
| Primary holdout macro F1 | 90.55% |
| Marathi-marker holdout accuracy | 81.25% |
| Marathi-marker holdout macro F1 | 79.74% |

Primary holdout F1 by department:

| Department | F1 |
|---|---:|
| Electric | 0.98 |
| Road & Traffic | 0.93 |
| Sewage & Drainage | 0.77 |
| Solid Waste | 0.88 |
| Water Supply | 0.97 |

The 92.05% primary score excludes rows identified by the Marathi-marker
heuristic and is not directly comparable with the earlier 86.62% mixed holdout.
The separate Marathi-marker result is 83.16% on 95 complaints. These are
evaluation scores, not a guarantee of live-site accuracy. Encroachment is not
represented in either real-data holdout.

The workbook does not label complaint language. The Marathi subset is
provisionally identified by explicit Marathi grammatical markers because Hindi
and Marathi share Devanagari script. Marathi complaints without these markers
(including Romanized Marathi) can remain in the primary set. Review or add
human-verified language labels before using these language-specific scores as
formal benchmarks.

The latest Marathi phrase-rule regression check passed 14/14 hand-written
cases. This checks only those specific deterministic rules; it is not the
Marathi model accuracy result.

After reviewing the Sewage-to-Solid-Waste confusions, phrase-first Marathi
routing, drain-anchor co-occurrence checks, and targeted compound patterns
were added. All seven content-bearing drainage misclassification examples
now route to Sewage & Drainage in direct prediction checks; the low-information
"Hi / Please assist" complaint is not treated as a drainage rule and needs
label/data review. These routing checks do not change the classifier-only
holdout accuracy above; evaluate the full live pipeline separately before
claiming an updated overall system accuracy.

The workbook has no real Encroachment Department examples; that class is
currently represented by synthetic training examples, so its production
accuracy and recall are unknown. There are also 637 repeated normalized rows,
eight normalized text groups with conflicting department labels, and only 36
Devanagari complaints labeled Water Supply. These are data-quality and
coverage limits, not problems that can be solved by increasing a model
hyperparameter.

## Work completed in this iteration

- Added separate deterministic, grouped 20% holdouts for primary complaints
  and complaints matching Marathi grammatical markers. Duplicate normalized
  complaints cannot cross between training and either holdout.
- Added grouped 4-fold cross-validation over Logistic Regression and Linear
  SVM configurations. Model selection uses primary-set mean macro F1, then
  accuracy, so the Marathi test set does not influence tuning or primary
  accuracy.
- Kept the existing word unigram/bigram plus character 3–5-gram TF-IDF
  features.
- Prevented augmented examples matching validation or holdout text groups
  from entering training for those partitions.
- Added longest-first explicit Marathi phrase rules and explicit inflection
  mappings; no suffix stripping is used. Standalone "काढा" is not a routing
  rule.
- Added drain-anchor and targeted compound rules to separate drainage
  complaints from generic garbage complaints, with sewage checked before
  water in single-keyword fallback.
- Added a separate Marathi metrics chart, confusion matrix, and
  `evaluation_metrics.json`; Marathi metrics do not contribute to the primary
  accuracy score.
- Added `marathi_test_cases.py` as a focused phrase-rule regression check.
- Kept final production retraining on all real and synthetic training data
  after evaluation.

## Practical roadmap

### 1. Repair and protect the labels

- Review the eight normalized complaint groups that have conflicting
  department labels; correct them from the original complaint or exclude
  genuinely ambiguous records from supervised training.
- Deduplicate repeated complaints or assign them lower weight. Keep every
  duplicate and near-duplicate family in a single split.
- Check that each complaint's label is the intended routing department,
  especially road versus drainage and streetlight versus electricity.

### 2. Fill the real-data gaps

- Collect genuine, human-labeled examples for every department, beginning
  with Encroachment, which currently has no real labeled examples.
- Prioritize Marathi coverage in Water Supply and Sewage & Drainage, and
  capture natural spelling variants, Romanized Marathi, code-switching, and
  short/noisy complaints.
- As an initial collection target, add at least 200 distinct Marathi
  complaints per existing department and 300 or more real Encroachment
  complaints. These are data-collection targets, not a promise of 95%.
- Save source and date information so future evaluation can include a
  chronological test set and detect changes in complaint patterns.

### 3. Re-evaluate after each labeled-data batch

- Keep both grouped language-specific holdouts for comparable experiments,
  and also run repeated grouped cross-validation with fixed seeds.
- Report accuracy, macro precision/recall/F1, per-department support, and the
  confusion matrix; do not optimize or publish accuracy alone.
- Tune the feature settings and classifier only on training folds. Preserve a
  final untouched, preferably newer, real-complaint test set.
- Compare the candidate model's class-level errors with the rules layer;
  manually review errors before adding new rules or synthetic examples.

### 4. Gate a 95% claim on independent evidence

Use a new, deduplicated, human-reviewed holdout collected after the training
data. Aim for at least 1,000 unique complaints overall and at least 100
examples per department, including Encroachment, before making a broad
accuracy claim. Require the held-out accuracy and macro F1 to meet the target,
with no department's recall collapsing. Continue collecting data if the
holdout remains below target.

No model or preprocessing change can guarantee 95% on future complaints from
the current workbook alone. More representative, correctly labeled real
complaints—and independent validation—are the main remaining requirements.
