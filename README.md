# <div align="center"><img src="images/icon.png" alt="WildClaims icon" width="30" /> WildClaims: Conversational Information Access<br>in the Wild(Chat)<div>

<div align="center">
    <a href="https://arxiv.org/abs/2509.17442" target="_blank"><img src=https://img.shields.io/badge/arXiv-b5212f.svg?logo=arxiv></a>
    <a href="https://opendatacommons.org/licenses/by/1-0/">
        <img alt="License" src="https://img.shields.io/badge/License-ODC--BY--1.0-blue?style=flat">
    </a>
</div>


This is the repo for our paper: **[WildClaims: Conversational Information Access in the Wild(Chat)](https://arxiv.org/abs/2509.17442)**.
The repository contains:  
- The [**`WildClaims dataset`**](annotations/) with extracted factual claims and human annotations.  
- The [**`data generation pipeline`**](generation/) for preprocessing, filtering, claim extraction, and check-worthiness classification.  
- The [**`analysis scripts`**](analysis/) used to reproduce the statistics and evaluation results reported in the paper.
- The [**`prompts`**](prompts/) used to generate the dataset via LLM-based claim extraction and check-worthiness classification. 


## What is WildClaims?
- **WildClaims** is a dataset designed to study **implicit information access** in real-world human-system conversations. It focuses on the phenomenon that we found, where users' access to the information often occurs implicitly in the form of check-worthy factual claims made by the system, even when the user's task is not explicitly informational (e.g., during creative writing).
- Derived from the existing WildChat corpus, the dataset contains **121,905 factual claims** extracted from 7,587 system utterances across 3,000 conversations. Each claim is annotated for check-worthiness, indicating whether it merits fact-checking.
- This resource aims to help the community move beyond traditional explicit information access to better understand and address the **implicit information access** that arises in real-world user-system conversations. 

## Data Release  

The directory [`annotations/`](annotations/) contains utterance-level results, human annotations, and full claim extractions used in our check-worthiness analysis.

This resource builds on prior work in **claim extraction** and **check-worthiness detection**.
Specifically, we use [Huo et al., 2023](https://dl.acm.org/doi/fullHtml/10.1145/3624918.3625336/) and [Song et al., 2024](https://aclanthology.org/2024.findings-emnlp.552/) for claim extraction, and [Hassan et al., 2015](https://dl.acm.org/doi/10.1145/2806416.2806652) and [Majer et al., 2024](https://aclanthology.org/2024.fever-1.27/) for check-worthiness classification. See [**`generation/README.md`**](generation/README.md) for more details.

- [**`claims.csv`**](annotations/claims.csv)  
  Full set of extracted factual claims (~31K with `FHuo`, ~91K with `FSong`). Each row corresponds to a claim linked to its source utterance (`Selected_Agent_Utterance`, `Conversation_Hash`, `Claim_Extr_Method`, `Individual_Statement`) with classifier outputs (`Hassan`, `Majer`). 


- [**`human_annotations.csv`**](annotations/human_annotations.csv)  
  200 human-annotated claims for inter-annotator agreement and classifier evaluation. Includes annotator labels (`Human1_Annotation`, `Human2_Annotation`, `Check_Worthy`), binary CW flags (`Human1_CW`, `Human2_CW`, `CW_Tie`), agreement flags (`Human1_Human2_Agree`), and automatic classifier outputs (`Majer`, `Hassan`, `Intersection`, `Union`).  

- [**`analysis.csv`**](annotations/analysis.csv)  
  Utterance-level results for ~3k sampled conversations. Each row corresponds to an agent utterance, with metadata (`Conversation_Hash`, `Turn_Num`, `Corresponding_User_Question`, `Selected_Agent_Utterance`, `Task_Classification`, `Use`) and multiple check-worthiness outputs (`Hassan`, `Majer`, `Intersection`, `Union`) plus fact counts (`*_Fact_Num`, `*_Fact_Total`).  

Together, these files enable replication of utterance-level and claim-level statistics, as well as evaluation of human vs. automatic check-worthiness classification.  

👉 For detailed schema and column descriptions, see [`annotations/README.md`](annotations/README.md).

## WildClaims Statistics

**Table: General statistics of the WILDCLAIMS dataset.**
| Statistic | Value |
| :--- | :--- |
| # Conversations | 3,000 |
| Single/multi-turn ratio | 57% : 43% |
| # Utterances | 15,174 |
| # System utterances | 7,587 |
| Avg. utterances per conversation | 2.52 |
| Avg. words per user utterance | 95.70 |
| Avg. words per system utterance | 219.24 |
| # Total extracted factual claims | 121,905 |
| # Automatic check-worthiness annotations | 243,810 |
| # Manual check-worthiness annotations | 200 |

## Data Generation Pipeline

The [`generation/`](./generation/) directory contains scripts for preparing, labeling, and extracting claims from WildChat conversations before running check-worthiness analysis.  

**Workflow Summary:**
1. **Preprocessing** [**`preprocess_files_for_pipeline.py`**](generation/preprocess_files_for_pipeline.py)  
   - Explodes conversations into utterance-level rows.  
   - Generates context windows for each system utterance.  

2. **Filtering Math & Code** [**`labeling_math_and_code.py`**](generation/labeling_math_and_code.py)   
   - Labels conversations as *Math*, *Coding*, or *Others* to filter out non-relevant domains.  

3. **Task Classification** [**`task_classification.py`**](generation/task_classification.py)   
   - Categorizes user utterances into high-level task types (information seeking, creative writing, reasoning, etc.).  

4. **Claim Extraction**  
   - **FHuo Method** [**`f_huo_method.py`**](generation/f_huo_method.py): Extracts factual statements from system responses via OpenAI Batch.  
   - **FSong Method** [**`f_song.py`**](generation/f_song.py): Generates JSONLs, runs FSong extraction, maps claims back, and explodes them into one-row-per-claim.  

5. **Check-Worthiness Classification** [**`cw.py`**](generation/cw.py)  
   - Classifies factual statements; supports both *Majer* and *Hassan* prompt variants.  

📂 **Details:** See the [generation/README.md](./generation/README.md) for complete pipeline descriptions, usage examples, and command-line arguments.



## Analysis  

The directory [`analysis/`](analysis/) contains Python scripts used to analyze the annotations and reproduce results reported in the paper.  

- [**`statistics_3k_conversation.py`**](analysis/statistics_3k_conversation.py)  
  Generates descriptive statistics for the 3,000 sampled conversations. Outputs counts of utterances, unique conversations, turn distributions, average lengths of user questions and agent utterances, and task classification distributions.  

- [**`statistics_fact_claim_extraction_3k.py`**](analysis/statistics_fact_claim_extraction_3k.py)  
  Computes statistics on factual claim extraction across the 3k conversations, comparing **FHuo** and **FSong** methods. Reports total claims, average claims per utterance/conversation, and coverage statistics.  

- [**`statistics_human_annotations.py`**](analysis/statistics_human_annotations.py)  
  Analyzes the 200 human-annotated claims. Provides row counts per extraction method, percentages of TRUE labels (`Human1_CW`, `Human2_CW`, `Gold`), and inter-annotator agreement using Cohen’s κ.  

- [**`effectiveness_automatic_check_worthiness.py`**](analysis/effectiveness_automatic_check_worthiness.py)  
  Evaluates automatic CW classifiers (`Hassan`, `Majer`, `Intersection`, `Union`) against the human-annotated gold labels. Reports Precision, Recall, F1-score, and Cohen’s κ for each extraction method.  

- [**`prevalence_check_worthy_3k.py`**](analysis/prevalence_check_worthy_3k.py)  
  Estimates the prevalence of CW claims across the 3,000 sampled conversations. Reports percentages of CW claims, utterances with ≥1 CW claim, and conversations with ≥1 CW claim for all classifier–extraction combinations. 

  For detailed instructions on running the analysis scripts, see the [analysis README](analysis/README.md). 




## License

WildClaims is currently released under the [ODC-By 1.0](https://opendatacommons.org/licenses/by/1-0/) license, following WildChat, and by using WildClaims you are agreeing to its usage terms.


## Citation

```
@misc{Joko:2025:WildClaims,
      title={WildClaims: Conversational Information Access in the Wild(Chat)}, 
      author={Hideaki Joko and Shakiba Amirshahi and Charles L. A. Clarke and Faegheh Hasibi},
      year={2025},
      eprint={2509.17442},
      archivePrefix={arXiv},
      primaryClass={cs.IR},
      url={https://arxiv.org/abs/2509.17442}, 
}
```

## Contact

If you have any questions, please contact Shakiba Amirshahi or Hideaki Joko hideaki.joko@ru.nl
