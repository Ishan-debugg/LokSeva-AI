# Previous vs Current Complaint-Routing Evaluation

## Summary

The current keyword-rule changes improve routing of Sewage & Drainage
complaints, but redirect some Solid Waste complaints to Sewage. On the same
544-record holdout, overall end-to-end accuracy rose by only 0.55 percentage
points, from 82.17% to 82.72%. Macro F1 rose by 0.89 points.

This is a diagnostic comparison, not a new unbiased estimate: the current
rules were written after reviewing errors from this holdout. Validate them on
a newly collected, untouched dataset before making an accuracy claim.

## Evaluation method

- Dataset: `dataset/kdmc_data.xlsx`; 2,724 real complaints across five
  labeled departments.
- Holdout: same grouped split for both versions, 448 primary
  non-Marathi-marker rows and 96 Marathi-marker rows (544 records total).
  Exact duplicate text was retained as scoring weight; there were 450 distinct
  raw test texts and 432 normalized text groups.
- Model: Logistic Regression selected as `C=5` by the same grouped training
  CV. Both versions use the same fitted model predictions; only the keyword
  override implementation differs.
- Previous rules: `HEAD^` (`cbbd942343fd52debf41519b6bb05bc09441d55e`).
- Current rules: `HEAD` (`acd013da20430cb0684a853659751e15b1d05747`).
- Metrics are record-weighted. The language split uses the existing Marathi
  marker heuristic, not human-verified language labels.

## End-to-end results

| Evaluation set | Previous accuracy | Current accuracy | Change | Previous macro F1 | Current macro F1 | Change |
|---|---:|---:|---:|---:|---:|---:|
| Combined (544 records) | 82.17% | 82.72% | +0.55 pp | 82.88% | 83.77% | +0.89 pp |
| Primary, non-Marathi-marker (448) | 85.27% | 85.27% | 0.00 pp | 86.24% | 86.33% | +0.09 pp |
| Marathi-marker subset (96) | 67.71% | 70.83% | +3.13 pp | 64.85% | 68.44% | +3.59 pp |

For context, with keyword overrides bypassed, the classifier alone scored
90.63% on the primary holdout and 81.25% on the Marathi-marker holdout
(88.97% combined). These are not directly comparable to end-to-end results:
the complete pipeline can override classifier predictions, and those rules
currently lower accuracy on this holdout.

## Sewage vs Solid Waste tradeoff

Combined end-to-end class metrics:

| Department | Previous precision / recall / F1 | Current precision / recall / F1 | Effect |
|---|---|---|---|
| Sewage & Drainage | 65.71% / 67.65% / 66.67% | 59.74% / 90.20% / 71.88% | Recall +22.55 pp; precision -5.97 pp |
| Solid Waste | 81.40% / 70.95% / 75.81% | 94.51% / 58.11% / 71.97% | Recall -12.84 pp; precision +13.11 pp |

In the primary non-Marathi-marker subset, actual Sewage complaints predicted
as Solid Waste decreased from 21 to 2. However, actual Solid Waste complaints
predicted as Sewage increased from 29 to 48. The rules made Sewage routing
more sensitive, but too broad for some complaints whose labels are Solid
Waste.

Across changed routing decisions, 24 distinct raw texts (49 records) changed:
23 previously incorrect records became correct, 20 previously correct records
became incorrect, and 6 remained incorrect. The net gain is only 3 correct
records across the combined 544-record holdout.

## Recommendation

Do not describe this change as a broad accuracy improvement. It is a
Sewage-recall tradeoff with almost no primary-set accuracy gain. Review the
Solid Waste-to-Sewage regressions and verify their source labels. In
particular, blanket rules such as assigning every septic-tank-cleaning
complaint to Sewage may conflict with the dataset's Solid Waste labels.

Keep the classifier-only metrics and end-to-end pipeline metrics separate in
future reporting. Before deployment claims, evaluate the revised routing
rules on new labeled complaints that were not used to identify or write the
rules.
