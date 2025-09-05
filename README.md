# Information Access Conversations in the Wild(Chat) Scripts

This repository contains analysis scripts for the Information Access Conversations in the Wild(Chat) paper. Each script generates results for specific tables in the paper.

**Note**: In these scripts:
- `siqing` corresponds to 𝐹𝐻𝑢𝑜 in the paper
- `veriscore` corresponds to 𝐹𝑆𝑜𝑛𝑔 in the paper

## Scripts Overview

### `table_2.py`
**Purpose**: Statistics of selected 3,000 conversations from the WildChat dataset  
**Input**: `Annotations/3k_Results.csv`  
**Output**: Table 2 results including:
- Number of unique conversation_hash values
- Turn number distribution (turn_num = 1 vs >1)
- Average turn_num by conversation
- Average words in user questions and agent utterances
- Task classification distribution

### `table_3.py`
**Purpose**: Statistics of factual claim extraction methods applied to 3,000 conversations  
**Input**: `Annotations/Human_Annotation_100.csv`  
**Output**: 
- Total number of facts
- Average facts per utterance
- Average facts per conversation
- Percentage of utterances with facts
- Percentage of conversations with facts


### `table_4.py`
**Purpose**: Human annotation agreement analysis  
**Input**: `Annotations/Human_Annotation_100.csv`  
**Output**: Table 4 results including:
- Grouped analysis by claim extraction method (siqing and veriscore)
- Percentage of True values for Human_1, Human_2, and Gold
- Kappa scores between Human_1 and Human_2


### `table_5.py`
**Purpose**: Effectiveness of automatic check-worthiness (CW) classification evaluated using human annotations  
**Input**: `Annotations/Human_Annotation_100.csv`  
**Output**: Table 5 results including:
- Precision, Recall, F1, and Kappa for automatic check-worthiness (CW)classification  vs Gold standard
- Analysis for: major, hassan, Intersection, Union
- Grouped by claim extraction method (siqing vs veriscore)

### `table_6.py`
**Purpose**: Prevalence of check-worthy (CW) claims in 3,000 conversations, estimated with CW classifiers.   
**Input**: `Annotations/3k_Results.csv`  
**Output**: Table 6 results including:
- Percentage of CW (Claim-Worthy) facts in all elements
- Percentage of rows (utterances) with at least one CW fact
- Percentage of conversations with at least one CW fact
- Analysis for all array columns: siqing_hassan, siqing_major, siqing_intersection, siqing_union, veriscore_hassan, veriscore_major, veriscore_intersection, veriscore_union

## Usage

Each script can be run independently:

```bash
python3 table_2.py    # Generate Table 2 results
python3 table_3.py    # Generate Table 3 results
python3 table_4.py    # Generate Table 4 results
python3 table_5.py    # Generate Table 5 results
python3 table_6.py    # Generate Table 6 results
```

## Data Files

- `Annotations/3k_Results.csv`: Main dataset with 7,587 rows across 3,000 conversations
- `Annotations/Human_Annotation_100 .csv`: Human annotation data with 200 rows for inter-annotator agreement analysis


