# Information Access Conversations in the Wild(Chat) — Scripts & Annotations

This repository provides the **annotations, prompts, and analysis scripts** used in the paper *“Information Access Conversations in the Wild(Chat)”*.  
It is intended as a companion resource to help researchers **reproduce the reported results**, explore the annotated datasets, and extend the analyses.  

Each script corresponds to a section of the paper and generates specific statistics or evaluation metrics directly from the released annotations.



## Annotation Files

### `Annotations/run_analysis.csv`

This file contains the **utterance-level results** used for check-worthiness analysis.  
Each row corresponds to a single agent utterance within a conversation.

**Columns:**

- `conversation_hash`: Unique identifier for each conversation  
- `turn_num`: Turn number within the conversation (1, 2, 3, …)  
- `Corresponding_User_Question`: The user’s question/input for this turn  
- `Selected_Agent_Utterance`: The agent’s response/utterance for this turn  
- `Selected_Agent_Column`: Column identifier (e.g., *Utterance-1 (Agent)*)  
- `task_classification`: Task type (e.g., *Information seeking*, *Creative Writing*, …)  
- `use`: Usage flag (TRUE/FALSE)  

**Check-worthiness outputs:** (arrays of booleans, one per extracted claim)  
- `FHou_hassan`: Using **FHou** claim extraction + *Hassan* check-worthiness classifier  
- `FSong_hassan`: Using **FSong** claim extraction + *Hassan* check-worthiness classifier  
- `FHou_major`: Using **FHou** extraction + *Major* check-worthiness classifier   
- `FSong_major`: Using **FSong** extraction + *Major* check-worthiness classifier   
- `FHou_intersection`: Intersection of *Hassan* and *Major* results (FHou extraction)  
- `FSong_intersection`: Intersection of *Hassan* and *Majority* results (FSong extraction)  
- `FHou_union`: Union of *Hassan* and *Majority* results (FHou extraction)  
- `FSong_union`: Union of *Hassan* and *Majority* results (FSong extraction)  

**Counts:**  
- `*_fact_num`: Number of check-worthy facts identified by each method  
- `*_fact_total`: Total number of facts extracted by each method


### `Annotations/Human_Annotation.csv`

This file contains **200 human-annotated claims** used for inter-annotator agreement analysis and evaluation of automatic check-worthiness classifiers.

**Basic Information**
- `claim_extr_method`: Claim extraction method used (*FHou* or *FSong*)  
- `ver`: Version identifier  
- `conversation_hash`: Unique identifier for the conversation  
- `Individual_Statement`: The specific claim being annotated  
- `Task_Classification`: Task type of the conversation turn  

**Human Annotations**
- `Human1_Annotation`, `Human2_Annotation`: Full-label classifications by each annotator (*NFS, UFS, CFS*)  
- `Human1_CW`, `Human2_CW`: Binary check-worthiness decisions (TRUE/FALSE)  
- `Human1_Human2_Agree`: Agreement flag (TRUE if both annotators agree)  
- `check worthy? (tie-breaking)`: Tie-breaking annotation label (applied when Human1 and Human2 disagree)  
- `CW_Tie`: Tie-breaking binary decision (TRUE/FALSE)  

**Automatic Classifier Outputs**
- `major`: Major classifier output label (*NFS, UFS, CFS*)    
- `hassan`: Hassan classifier output label (*NFS, UFS, CFS*)  
- `major_binary`: Major classifier binary output (TRUE/FALSE)  
- `hassan_binary`: Hassan classifier binary output (TRUE/FALSE)  
- `Gold`: Final gold standard binary label (TRUE/FALSE), integrating tie-breaks  
- `Intersection`: TRUE if both Hassan and Major classifiers predict CW  
- `Union`: TRUE if either Hassan or Major classifier predicts CW



### `Annotations/run_factual_claim_extraction.csv`

This file contains the **full set of extracted factual claims** from the 3k sampled conversations.  
Each row corresponds to a **single claim** linked to its originating agent utterance.

**Columns**
- `Selected_Agent_Utterance`: The agent’s utterance from which the claim was extracted  
- `conversation_hash`: Unique identifier for the conversation  
- `claim_extr_method`: Claim extraction method used (*FHou* or *FSong*)  
- `Individual_Statement`: The extracted claim text  
- `hassan`: Hassan check-worthiness classifier output (True/False)  
- `major`: Major check-worthiness classifier output (True/False) 

**Notes**
- This file operates at the **claim level** (one row per claim), unlike `run_analysis.csv`, which is **utterance-level**.  
- Totals:  
    - **FHou** extraction: **~31,108** claims  
    - **FSong** extraction: **~90,797** claims   
- These counts align with the paper’s reported results and can be used to replicate extraction statistics.


## Scripts Overview

### `Statistics_3k_Conversation.py`

**Purpose**  
Generates descriptive statistics for the 3,000 sampled conversations from the WildChat dataset.  
This provides a high-level overview of conversation structure and task distribution.

**Input**  
- `Annotations/run_analysis.csv` (utterance-level annotations)

**Output (printed to console)**  
- **#Utterances**: Total number of rows in the dataset  
- **Unique conversations**: Number of distinct `conversation_hash` values  
- **Turn distribution**: Counts and percentages of single-turn vs. multi-turn conversations  
- **Average turn index per conversation**: Mean of number of turns within each conversation  
- **Average words per user question** (`Corresponding_User_Question`)  
- **Average words per agent utterance** (`Selected_Agent_Utterance`)  
- **Task classification distribution**: Count and percentage of utterances per `task_classification` label  




### `Statistics_Fact_Claim_Extraction_3k.py`

**Purpose**  
Computes statistics about factual claim extraction on the 3,000 sampled conversations, comparing the **FHou** and **FSong** extraction methods.  
Focuses on claim counts, averages, and coverage at both utterance and conversation levels.

**Input**  
- `Annotations/run_analysis.csv` (utterance-level annotations with claim arrays)

**Output (printed to console)**  
- **Total number of extracted claims**  
  - Total elements in `FHou_hassan` arrays  
  - Total elements in `FSong_hassan` arrays  
- **Average claims per utterance**  
  - Average number of claims in `FHou_hassan` per utterance  
  - Average number of claims in `FSong_hassan` per utterance  
- **Average claims per conversation**  
  - Average number of claims in `FHou_hassan` per conversation  
  - Average number of claims in `FSong_hassan` per conversation  
- **Coverage statistics**  
  - % of utterances with ≥1 extracted claim (FHou vs. FSong)  
  - % of conversations with ≥1 extracted claim (FHou vs. FSong)  



### `Statistics_Human_Annotations.py`

**Purpose**  
Analyzes the **200 human-annotated claims** to measure inter-annotator agreement and compare human labels against automatic classifiers.  
Provides per-method statistics for **FHou** and **FSong** claim extraction.

**Input**  
- `Annotations/Human_Annotation.csv` (200 annotated claims)

**Output (printed to console)**  
- **Row counts per method**: Number of annotated claims for FHou and FSong  
- **Percentage of TRUE labels**  
  - For `Human1_CW`  
  - For `Human2_CW`  
  - For `Gold` (final aggregated label)  
- **Cohen’s κ scores**  
  - Agreement between Human1 and Human2 (binary check-worthiness decisions)  


### `Effectiveness_Automatic_Check_Worthiness.py`

**Purpose**  
Evaluates the effectiveness of **automatic check-worthiness (CW) classifiers** against the human-annotated gold standard.  
Reports standard evaluation metrics to benchmark the Hassan, Major, Intersection, and Union of these methods.

**Input**  
- `Annotations/Human_Annotation.csv` (200 annotated claims)

**Output (printed to console)**  
For each claim extraction method (*FHou* and *FSong*):  
- **Precision**, **Recall**, **F1-score** (binary classification vs. Gold)  
- **Cohen’s κ** (agreement between automatic method and Gold)  
- Separate analyses for:  
  - `hassan_binary`  
  - `major_binary`  
  - `Intersection` (Hassan ∩ Major)  
  - `Union` (Hassan ∪ Major) 



### `Prevalence_Check_Worthy_3k.py`

**Purpose**  
Estimates the prevalence of **check-worthy (CW) claims** across the 3,000 sampled conversations, using different CW classifiers (Hassan, Major, Intersection, Union) applied to both FHou and FSong claim extraction methods.

**Input**  
- `Annotations/run_analysis.csv` (utterance-level annotations with claim arrays)

**Output (printed to console)**  
For each method combination  
(*FHou_hassan, FHou_major, FHou_intersection, FHou_union, FSong_hassan, FSong_major, FSong_intersection, FSong_union*):  
- **% of CW claims among all extracted claims**  
  - e.g., number of TRUE values across all arrays ÷ total number of elements  
- **% of utterances with ≥1 CW claim**  
  - proportion of rows where at least one claim is marked TRUE  
- **% of conversations with ≥1 CW claim**  
  - proportion of conversations where at least one utterance contains a CW claim 

## Usage

Each script can be run independently to reproduce the analyses reported in the paper.  
Run them from the repository root as follows:

```bash
python3 Scripts/Effectiveness_Automatic_Check_Worthiness.py
python3 Scripts/Prevalence_Check_Worthy_3k.py
python3 Scripts/Statistics_3k_Conversation.py
python3 Scripts/Statistics_Fact_Claim_Extraction_3k.py
python3 Scripts/Statistics_Human_Annotations.py


