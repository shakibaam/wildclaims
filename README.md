# Information Access Conversations in the Wild(Chat) Scripts

This repository contains analysis scripts for the Information Access Conversations in the Wild(Chat) paper. Each script generates results for specific tables in the paper.

**Note**: In these scripts:
- `FHou` corresponds to 𝐹𝐻𝑢𝑜 in the paper
- `FSong` corresponds to 𝐹𝑆𝑜𝑛𝑔 in the paper

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
**Input**: `Annotations/3k_Results.csv`  
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
- Grouped analysis by claim extraction method (FHou and FSong)
- Percentage of True values for Human_1, Human_2, and Gold
- Kappa scores between Human_1 and Human_2


### `table_5.py`
**Purpose**: Effectiveness of automatic check-worthiness (CW) classification evaluated using human annotations  
**Input**: `Annotations/Human_Annotation_100.csv`  
**Output**: Table 5 results including:
- Precision, Recall, F1, and Kappa for automatic check-worthiness (CW)classification  vs Gold standard
- Analysis for: major, hassan, Intersection, Union
- Grouped by claim extraction method (FHou vs FSong)

### `table_6.py`
**Purpose**: Prevalence of check-worthy (CW) claims in 3,000 conversations, estimated with CW classifiers.   
**Input**: `Annotations/3k_Results.csv`  
**Output**: Table 6 results including:
- Percentage of CW (Claim-Worthy) facts in all elements
- Percentage of rows (utterances) with at least one CW fact
- Percentage of conversations with at least one CW fact
- Analysis for all array columns: FHou_hassan, FHou_major, FHou_intersection, FHou_union, FSong_hassan, FSong_major, FSong_intersection, FSong_union

## Usage

Each script can be run independently:

```bash
python3 Scripts/table_2.py    # Generate Table 2 results
python3 Scripts/table_3.py    # Generate Table 3 results
python3 Scripts/table_4.py    # Generate Table 4 results
python3 Scripts/table_5.py    # Generate Table 5 results
python3 Scripts/table_6.py    # Generate Table 6 results
```

## Data Files

### `Annotations/3k_Results.csv`
Main dataset with 7,587 rows across 3,000 conversations containing:

**Basic Information:**
- `conversation_hash`: Unique identifier for each conversation
- `turn_num`: Turn number within the conversation (1, 2, 3, etc.)
- `Corresponding_User_Question`: The user's question/input for this turn
- `Selected_Agent_Utterance`: The agent's response/utterance for this turn
- `Selected_Agent_Column`: Column identifier (e.g., "Utterance-1 (Agent)")
- `task_classification`: Type of task (e.g., "Information seeking", "Creative Writing", etc.)
- `use`: Usage flag (TRUE/FALSE)

**Claim Extraction Results (Boolean Arrays):**
- `FHou_hassan`: Boolean array indicating check-worthiness using FHou claim extraction method with hassan check worthiness method
- `FSong_hassan`: Boolean array indicating check-worthiness using FSong claim extraction method with hassan check worthiness method
- `FHou_major`: Boolean array indicating check-worthiness using FHou claim extraction method with major check worthiness method
- `FSong_major`: Boolean array indicating check-worthiness using FSong claim extraction method with major check worthiness method
- `FHou_intersection`: Boolean array for intersection of major and hassan for FHou method
- `FSong_intersection`: Boolean array for intersection of major and hassan for FSong method
- `FHou_union`: Boolean array for union of major and hassan for FHou method
- `FSong_union`: Boolean array for union of major and hassan for FSong method

**Fact Count Columns:**
- `**_fact_num`: Number of CW facts extracted through each method
- `**_fact_total`: Total number of fact extracted through each method

### `Annotations/Human_Annotation_100 .csv`
Human annotation data with 200 rows for inter-annotator agreement analysis containing:

**Basic Information:**
- `claim_extr_method`: Claim extraction method used (FHou or FSong)
- `ver`: Version identifier
- `conversation_hash`: Unique identifier for the conversation
- `Individual_Statement`: The specific statement being annotated
- `Task_Classification`: Type of task

**Human Annotations:**
- `Human1_Annotation`: First annotator's classification (NFS, UFS, CFS)
- `Human2_Annotation`: Second annotator's classification (NFS, UFS, CFS)
- `Human1_CW`: First annotator's check-worthiness decision (TRUE/FALSE)
- `Human2_CW`: Second annotator's check-worthiness decision (TRUE/FALSE)
- `Human1_Human2_Agree`: Whether both annotators agree (TRUE/FALSE)
- `check worthy? (tie-breaking) (Charlie)`: Tie-breaking annotation
- `CW_Tie`: Tie-breaking check-worthiness decision

**Automatic Classifications:**
- `major_24`: Major CW output (UFS, CFS, etc.)
- `hassan_15`: Hassan CW output (UFS, CFS, etc.)
- `major_24_binary`: Major classifier binary output (TRUE/FALSE)
- `hassan_15_binary`: Hassan classifier binary output (TRUE/FALSE)
- `Gold`: Gold standard annotation (TRUE/FALSE)
- `Intersection`: Intersection of Hassan and Major (TRUE/FALSE)
- `Union`: Union of Hassan and Major (TRUE/FALSE)


