# Analysis Scripts

### `statistics_3k_conversation.py`

**Purpose**  
Generates descriptive statistics for the 3,000 sampled conversations from the WildChat dataset.  
This provides a high-level overview of conversation structure and task distribution.

**Input**  
- `annotations/analysis.csv` (utterance-level annotations)

**Output (printed to console)**  
- **#Utterances**: Total number of rows in the dataset  
- **Unique conversations**: Number of distinct `Conversation_Hash` values  
- **Turn distribution**: Counts and percentages of single-turn vs. multi-turn conversations  
- **Average turn index per conversation**: Mean of number of turns within each conversation  
- **Average words per user question** (`Corresponding_User_Question`)  
- **Average words per agent utterance** (`Selected_Agent_Utterance`)  
- **Task classification distribution**: Count and percentage of utterances per `Task_Classification` label  




### `statistics_fact_claim_extraction_3k.py`

**Purpose**  
Computes statistics about factual claim extraction on the 3,000 sampled conversations, comparing the **FHuo** and **FSong** extraction methods.  
Focuses on claim counts, averages, and coverage at both utterance and conversation levels.

**Input**  
- `annotations/analysis.csv` (utterance-level annotations with claim arrays)

**Output (printed to console)**  
- **Total number of extracted claims**  
  - Total elements in `FHuo_Hassan` arrays  
  - Total elements in `FSong_Hassan` arrays  
- **Average claims per utterance**  
  - Average number of claims in `FHuo_Hassan` per utterance  
  - Average number of claims in `FSong_Hassan` per utterance  
- **Average claims per conversation**  
  - Average number of claims in `FHuo_Hassan` per conversation  
  - Average number of claims in `FSong_Hassan` per conversation  
- **Coverage statistics**  
  - % of utterances with ≥1 extracted claim (FHuo vs. FSong)  
  - % of conversations with ≥1 extracted claim (FHuo vs. FSong)  



### `statistics_human_annotations.py`

**Purpose**  
Analyzes the **200 human-annotated claims** to measure inter-annotator agreement and compare human labels against automatic classifiers.  
Provides per-method statistics for **FHuo** and **FSong** claim extraction.

**Input**  
- `annotations/human_annotations.csv` (200 annotated claims)

**Output (printed to console)**  
- **Row counts per method**: Number of annotated claims for FHuo and FSong  
- **Percentage of TRUE labels**  
  - For `Human1_CW`  
  - For `Human2_CW`  
  - For `Gold` (final aggregated label)  
- **Cohen’s κ scores**  
  - Agreement between Human1 and Human2 (binary check-worthiness decisions)  


### `effectiveness_automatic_check_worthiness.py`

**Purpose**  
Evaluates the effectiveness of **automatic check-worthiness (CW) classifiers** against the human-annotated gold standard.  
Reports standard evaluation metrics to benchmark the Hassan, Majer, Intersection, and Union of these methods.

**Input**  
- `annotations/human_annotations.csv` (200 annotated claims)

**Output (printed to console)**  
For each claim extraction method (*FHuo* and *FSong*):  
- **Precision**, **Recall**, **F1-score** (binary classification vs. Gold)  
- **Cohen’s κ** (agreement between automatic method and Gold)  
- Separate analyses for:  
  - `Hassan_Binary`  
  - `Majer_Binary`  
  - `Intersection` (Hassan ∩ Majer)  
  - `Union` (Hassan ∪ Majer) 



### `prevalence_check_worthy_3k.py`

**Purpose**  
Estimates the prevalence of **check-worthy (CW) claims** across the 3,000 sampled conversations, using different CW classifiers (Hassan, Majer, Intersection, Union) applied to both FHuo and FSong claim extraction methods.

**Input**  
- `annotations/analysis.csv` (utterance-level annotations with claim arrays)

**Output (printed to console)**  
For each method combination  
(*FHuo_Hassan, FHuo_Majer, FHuo_Intersection, FHuo_Union, FSong_Hassan, FSong_Majer, FSong_Intersection, FSong_Union*):  
- **% of CW claims among all extracted claims**  
  - e.g., number of TRUE values across all arrays ÷ total number of elements  
- **% of utterances with ≥1 CW claim**  
  - proportion of rows where at least one claim is marked TRUE  
- **% of conversations with ≥1 CW claim**  
  - proportion of conversations where at least one utterance contains a CW claim 

## Usage

For detailed instructions on running the analysis scripts, please see the [root README](../README.md).

Each script can be run independently to reproduce the analyzes reported in the paper. Make sure to install any required dependencies by running:

```bash
pip install -r requirements.txt
```
