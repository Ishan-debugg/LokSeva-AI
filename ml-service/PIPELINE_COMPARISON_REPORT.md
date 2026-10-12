# Previous vs Narrowed Complaint-Routing Rules

## Summary

The narrowed rules restore Solid Waste recall while keeping high-confidence
drainage patterns such as blocked/overflowing drains and foul drain smells
routed to Sewage & Drainage. Generic drain-cleaning and drain-plus-garbage
complaints are no longer forced to either department by keyword rules; they
fall through to the trained classifier.

On the same 544-record grouped holdout, the narrowed pipeline scored 86.95%
end-to-end accuracy, compared with 82.72% for the previous broad rule set.
The gain is diagnostic, not an unbiased estimate, because the rules were
refined after reviewing errors from this holdout.

## Evaluation method

- Dataset: `dataset/kdmc_data.xlsx`; 2,724 real complaints across five labeled
  departments.
- Holdout: the same grouped split for both versions: 448 primary
  non-Marathi-marker rows and 96 Marathi-marker rows (544 records total).
  Duplicate records remain part of the record-weighted score.
- Model: Logistic Regression (`C=5`), selected by grouped cross-validation.
  The selected configuration and classifier-only holdout metrics remained
  the same. The final run also retrained with the standalone "काढा" expansion
  removed, so the comparison reflects the complete final pipeline, not only
  rule changes.
- Marathi identification: the existing grammatical-marker heuristic, not
  human-verified language labels.
- The previous broad-rule results were recorded in the prior comparison;
  narrowed-rule results were recomputed on the same holdout after removing
  broad cleaning and septic-tank overrides.

## End-to-end results

| Evaluation set | Previous broad rules | Narrowed rules | Change |
|---|---:|---:|---:|
| Combined accuracy (544) | 82.72% | 86.95% | +4.23 pp |
| Combined macro F1 | 83.77% | 86.95% | +3.18 pp |
| Primary accuracy (448) | 85.27% | 90.63% | +5.36 pp |
| Primary macro F1 | 86.33% | 90.82% | +4.49 pp |
| Marathi-marker accuracy (96) | 70.83% | 69.79% | -1.04 pp |
| Marathi-marker macro F1 | 68.44% | 66.17% | -2.27 pp |

For context, the classifier without keyword overrides scored 90.63% on the
primary holdout and 81.25% on the Marathi-marker holdout. The full pipeline
must be reported separately because deterministic keyword rules can replace
the model's result.

## Sewage vs Solid Waste tradeoff

Combined end-to-end class metrics:

| Department | Previous broad rules (precision / recall / F1) | Narrowed rules (precision / recall / F1) |
|---|---|---|
| Sewage & Drainage | 59.74% / 90.20% / 71.88% | 84% / 69% / 76% |
| Solid Waste | 94.51% / 58.11% / 71.97% | 84% / 88% / 86% |

In the primary holdout, Sewage-to-Solid-Waste errors changed from 2 to 21,
while Solid-Waste-to-Sewage errors changed from 48 to 6. The narrowed rules
reduce the false routing of waste complaints into Sewage, but the classifier
still misses 21 primary Sewage complaints as Solid Waste. Overall combined
holdout errors were 22 Sewage-to-Solid-Waste and 7 Solid-Waste-to-Sewage.

The narrower behavior is deliberate: blocked/overflowing drains and foul
drain smells are high-confidence Sewage signals, while generic cleaning,
garbage-in-a-drain, and septic-tank-cleaning requests have conflicting
department labels in the workbook. Those ambiguous cases now defer to the
model instead of being forced by a rule.

## Data and interpretation caveats

- This holdout was used to inspect errors and shape the rules, so the
  improvement must not be presented as an independent estimate of future
  performance. Validate against newly collected, human-reviewed complaints.
- The dataset contains conflicting labels for drainage-related requests,
  including septic-tank cleaning and garbage in drains. Confirm the intended
  municipal ownership before relabeling or adding deterministic routing.
- The Marathi subset is heuristic and small. Its score decreased slightly;
  collect human-verified Marathi complaints and evaluate them separately.
- Encroachment has no real labeled examples in the workbook, so real-world
  performance for that department remains unknown.
- A complaint with little information may still receive a class from the
  classifier fallback; removing a hard-coded rule does not make the API
  abstain or request clarification.

## Recommendation

Keep the narrowed rules rather than restoring broad drain-cleaning or
septic-tank overrides. Review the remaining Sewage-to-Solid-Waste examples
with department owners, then evaluate the chosen policy on a new untouched
holdout. Do not claim 95% accuracy from these results.
