# Analysis Scripts

This directory contains Python scripts to reproduce the analyses reported in the paper *"Information Access Conversations in the Wild(Chat)"*. Each script processes the annotation files and generates specific statistics or evaluation metrics.

## Prerequisites

Before running the scripts, make sure you have Python 3.x installed and install the required dependencies:

```bash
pip install -r requirements.txt
```

## Scripts Overview

### `Statistics_3k_Conversation.py`

**Purpose**: Generates descriptive statistics for the 3,000 sampled conversations from the WildChat dataset.

**Input**: `Annotations/run_analysis.csv` (utterance-level annotations)

**Output**: Console output with conversation statistics including:
- Total utterances and unique conversations
- Turn distribution (single-turn vs. multi-turn)
- Average turn index per conversation
- Average words per user question and agent utterance
- Task classification distribution

### `Statistics_Fact_Claim_Extraction_3k.py`

**Purpose**: Computes statistics about factual claim extraction comparing FHuo and FSong extraction methods.

**Input**: `Annotations/run_analysis.csv` (utterance-level annotations with claim arrays)

**Output**: Console output with extraction statistics including:
- Total number of extracted claims by method
- Average claims per utterance and conversation
- Coverage statistics (% of utterances/conversations with ≥1 claim)

### `Statistics_Human_Annotations.py`

**Purpose**: Analyzes the 200 human-annotated claims for inter-annotator agreement.

**Input**: `Annotations/Human_Annotation.csv` (200 annotated claims)

**Output**: Console output with annotation statistics including:
- Row counts per extraction method
- Percentage of TRUE labels for each annotator and gold standard
- Cohen's κ scores for inter-annotator agreement

### `Effectiveness_Automatic_Check_Worthiness.py`

**Purpose**: Evaluates automatic check-worthiness classifiers against human-annotated gold standard.

**Input**: `Annotations/Human_Annotation.csv` (200 annotated claims)

**Output**: Console output with effectiveness metrics including:
- Precision, Recall, F1-score for each classifier (Hassan, Majer, Intersection, Union)
- Cohen's κ agreement scores between automatic methods and gold standard
- Separate analyses for FHuo and FSong extraction methods

### `Prevalence_Check_Worthy_3k.py`

**Purpose**: Estimates prevalence of check-worthy claims across the 3,000 sampled conversations.

**Input**: `Annotations/run_analysis.csv` (utterance-level annotations with claim arrays)

**Output**: Console output with prevalence statistics including:
- Percentage of check-worthy claims among all extracted claims
- Percentage of utterances with ≥1 check-worthy claim
- Percentage of conversations with ≥1 check-worthy claim
- Results for all method combinations (FHuo/FSong × Hassan/Majer/Intersection/Union)

## Usage

Run each script independently from the repository root directory:

```bash
# Navigate to repository root
cd /path/to/Wildchat_Paper_Github

# Run individual scripts
python3 Scripts/Statistics_3k_Conversation.py
python3 Scripts/Statistics_Fact_Claim_Extraction_3k.py
python3 Scripts/Statistics_Human_Annotations.py
python3 Scripts/Effectiveness_Automatic_Check_Worthiness.py
python3 Scripts/Prevalence_Check_Worthy_3k.py
```

## Notes

- All scripts expect to be run from the repository root directory
- Input files should be placed in the `Annotations/` directory
- Some scripts reference files with slightly different names (e.g., `3k_Results.csv`, `Human_Annotation_200.csv`) - ensure your annotation files match the expected filenames or update the file paths in the scripts accordingly
