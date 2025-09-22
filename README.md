This is the repo for our paper: WildClaims: Information Access Conversations in the Wild(Chat). The repo contains:
-XXX
-XXX
-XXX


## What is WildClaims?
- **WildClaims** is a dataset designed to study **implicit information access** in real-world human-system conversations. It focuses on the phenomenon that we found, where users' access to the information often occurs implicitly through the form of check-worthy factual claims made by the system, even when the user's task is not explicitly informational (e.g., during creative writing).
- Derived from the existing WildChat corpus, the dataset contains 121,905 factual claims extracted from 7,587 system utterances across 3,000 conversations. Each claim is annotated for check-worthiness, indicating whether it merits fact-checking.
- This resource aims to help the community to move beyond traditional explicit information access to better understand and address the **implicit information access** that arises in real-world user-system conversations. 

## Methods Overview

This repository builds on prior work in **claim extraction** and **check-worthiness detection**.  
We use the following methods, as described in the paper:

- **FHuo (Huo et al. 2023)** — Extracts factual statements from system utterances by prompting an LLM directly. 
  [[Paper link]](https://dl.acm.org/doi/fullHtml/10.1145/3624918.3625336/)  

- **FSong (Song et al. 2024)** — Extracts only *verifiable* factual claims. Produces broader coverage, yielding nearly 3× more claims than FHuo.  
  [[Paper link]](https://aclanthology.org/2024.findings-emnlp.552//)  

- **Hassan (Hassan et al. 2015)** — one of the earliest check-worthiness detection approaches, originally based on crowd annotation guidelines. In our work, we adapted it into an LLM prompt to classify claims as check-worthy or not.  
  [[Paper link]](https://dl.acm.org/doi/10.1145/2806416.2806652)  

- **Majer (Majer & Šnajder 2024)** — A recent check-worthiness detection method, using an effective LLM prompt designed to identify both factual and check-worthy factual claims.  
  [[Paper link]](https://aclanthology.org/2024.fever-1.27//)  

These methods are combined in different ways (e.g., intersection, union) to estimate the prevalence of check-worthy claims and to evaluate classifier effectiveness (See Section 4.1 of the paper).

## Statistics
![Statistics](https://github.com/shakibaam/wildclaims/blob/main/Statistics.png?raw=true)


## Data Release  

The directory **`Annotations/`** contains utterance-level results, human annotations, and full claim extractions used in our check-worthiness analysis.  

- **`run_analysis.csv`**  
  Utterance-level results for ~3k sampled conversations. Each row corresponds to an agent utterance, with metadata (`Conversation_Hash`, `Turn_Num`, `Corresponding_User_Question`, `Selected_Agent_Utterance`, `Task_Classification`, `Use`) and multiple check-worthiness outputs (`Hassan`, `Majer`, `Intersection`, `Union`) plus fact counts (`*_Fact_Num`, `*_Fact_Total`).  

- **`Human_Annotation.csv`**  
  200 human-annotated claims for inter-annotator agreement and classifier evaluation. Includes annotator labels (`Human1_Annotation`, `Human2_Annotation`, `Check_Worthy`), binary CW flags (`Human1_CW`, `Human2_CW`, `CW_Tie`), agreement flags (`Human1_Human2_Agree`), and automatic classifier outputs (`Majer`, `Hassan`, `Intersection`, `Union`).  

- **`run_factual_claim_extraction.csv`**  
  Full set of extracted factual claims (~31K with `FHuo`, ~91K with `FSong`). Each row corresponds to a claim linked to its source utterance (`Selected_Agent_Utterance`, `Conversation_Hash`, `Claim_Extr_Method`, `Individual_Statement`) with classifier outputs (`Hassan`, `Majer`).  

Together, these files enable replication of utterance-level and claim-level statistics, as well as evaluation of human vs. automatic check-worthiness classification.  

👉 For detailed schema and column descriptions, see [`Annotations/README.md`](Annotations/README.md).



## Scripts Overview

### `Statistics_3k_Conversation.py`

**Purpose**  
Generates descriptive statistics for the 3,000 sampled conversations from the WildChat dataset.  
This provides a high-level overview of conversation structure and task distribution.

**Input**  
- `Annotations/run_analysis.csv` (utterance-level annotations)

**Output (printed to console)**  
- **#Utterances**: Total number of rows in the dataset  
- **Unique conversations**: Number of distinct `Conversation_Hash` values  
- **Turn distribution**: Counts and percentages of single-turn vs. multi-turn conversations  
- **Average turn index per conversation**: Mean of number of turns within each conversation  
- **Average words per user question** (`Corresponding_User_Question`)  
- **Average words per agent utterance** (`Selected_Agent_Utterance`)  
- **Task classification distribution**: Count and percentage of utterances per `Task_Classification` label  




### `Statistics_Fact_Claim_Extraction_3k.py`

**Purpose**  
Computes statistics about factual claim extraction on the 3,000 sampled conversations, comparing the **FHuo** and **FSong** extraction methods.  
Focuses on claim counts, averages, and coverage at both utterance and conversation levels.

**Input**  
- `Annotations/run_analysis.csv` (utterance-level annotations with claim arrays)

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



### `Statistics_Human_Annotations.py`

**Purpose**  
Analyzes the **200 human-annotated claims** to measure inter-annotator agreement and compare human labels against automatic classifiers.  
Provides per-method statistics for **FHuo** and **FSong** claim extraction.

**Input**  
- `Annotations/Human_Annotation.csv` (200 annotated claims)

**Output (printed to console)**  
- **Row counts per method**: Number of annotated claims for FHuo and FSong  
- **Percentage of TRUE labels**  
  - For `Human1_CW`  
  - For `Human2_CW`  
  - For `Gold` (final aggregated label)  
- **Cohen’s κ scores**  
  - Agreement between Human1 and Human2 (binary check-worthiness decisions)  


### `Effectiveness_Automatic_Check_Worthiness.py`

**Purpose**  
Evaluates the effectiveness of **automatic check-worthiness (CW) classifiers** against the human-annotated gold standard.  
Reports standard evaluation metrics to benchmark the Hassan, Majer, Intersection, and Union of these methods.

**Input**  
- `Annotations/Human_Annotation.csv` (200 annotated claims)

**Output (printed to console)**  
For each claim extraction method (*FHuo* and *FSong*):  
- **Precision**, **Recall**, **F1-score** (binary classification vs. Gold)  
- **Cohen’s κ** (agreement between automatic method and Gold)  
- Separate analyses for:  
  - `Hassan_Binary`  
  - `Majer_Binary`  
  - `Intersection` (Hassan ∩ Majer)  
  - `Union` (Hassan ∪ Majer) 



### `Prevalence_Check_Worthy_3k.py`

**Purpose**  
Estimates the prevalence of **check-worthy (CW) claims** across the 3,000 sampled conversations, using different CW classifiers (Hassan, Majer, Intersection, Union) applied to both FHuo and FSong claim extraction methods.

**Input**  
- `Annotations/run_analysis.csv` (utterance-level annotations with claim arrays)

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

For detailed instructions on running the analysis scripts, please see the [Scripts README](Scripts/README.md).

Each script can be run independently to reproduce the analyses reported in the paper. Make sure to install any required dependencies by running:

```bash
pip install -r requirements.txt
```

