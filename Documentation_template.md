# ML Challenge 2026: Business Entity Resolution Solution Template

**Team Name:** NITDominars  
**Team Members:** NITDominars  
**Submission Date:** 2026-09-27

---

## 1. Executive Summary
This solution uses local normalization, multi-pass indexed blocking, candidate filtering, and a precision-oriented logistic regression classifier. It supports zero, one, or many matches for each Source 1 entity and treats country labels as open-set values.

---

## 2. Methodology

### 2.1 Problem Analysis
The supplied training data contains 2,206,821 Source 1 records, 5,034,616 Source 2 records, and 5,285,603 Source 3 records. Ground truth contains singleton Source 1 entities as well as links to both source types, with up to 11 linked records for one Source 1 entity. Names contain legal suffixes, punctuation, abbreviations, transliteration, and duplicates; Source 2/3 addresses can be missing. Test data additionally contains France, so country handling is open-set.

### 2.2 Solution Strategy
Records are normalized into compact strings, token lists, numeric address components, and country fields. Indexed candidate generation is followed by inexpensive evidence filtering and learned pair scoring. Matches are selected independently, so valid multi-match relationships are preserved.

**Approach Type:** Blocking + Classifier  
**Core Innovation:** Unioning exact and rare-token blocks while bounding common blocks, then applying a precision-oriented second-stage filter before classification.

---

## 3. Candidate Generation (Blocking)
Source 2 and Source 3 rows are stored in a SQLite index. Blocking passes use exact compact business name, exact compact address, and normalized tokens from both fields. Common keys are capped; a bounded name-prefix fallback handles records without usable rare keys. The union is filtered by name/address evidence before model scoring.

- **Blocking keys used:** compact name, compact address, rare name tokens, rare address tokens, and bounded name-prefix fallback.
- **Candidate pairs generated:** Recorded in `output/metrics.json` after the complete run.
- **How you ensured true matches were not lost:** Multiple independent keys are unioned; exact name and address passes preserve high-confidence links while token passes cover noisy variants.

---

## 4. Matching Model

**Features used:**
- Name features: compact and normalized sequence similarity, token Jaccard, exact normalized name flag, token overlap.
- Address features: normalized sequence similarity, token Jaccard, numeric component equality/overlap, exact normalized address flag.
- Other: country equality and name/address interaction features.

**Model type:** scikit-learn LogisticRegression, balanced class weights, fixed random seed. BSD-3-Clause licensed; no pretrained parameters.  
**Threshold selection method:** Entity-level macro F0.5 on held-out training Source 1 records, with a conservative threshold and independent multi-match decisions.

---

## 5. Results & Error Analysis

- **F_0.5 Score (macro):** [your best validation score]
- **Common false positives (wrong merges):** [brief description]
- **Common false negatives (missed matches):** [brief description]

---

## 6. Conclusion
*Summarize your approach, key achievements, and lessons learned in 2-3 sentences.*

---

## Appendix

### A. Code Artefacts
*Your complete, runnable code ships in the submission zip under
`code/business_entity_resolution/` (all source in `src/`, with a `README.md` and
`requirements.txt`). Summarise its structure and the entry point(s) to reproduce
`output/matching_results.tsv` and `output/candidate_pairs.tsv` here.*

### B. Additional Results
*Include any additional charts, graphs, or detailed results.*

---

**Note:** Teams can modify sections according to their approach while maintaining clarity and technical depth.
