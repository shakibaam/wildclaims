# WildClaims

This is the repo for our paper: **WildClaims: Information Access Conversations in the Wild(Chat)**.  
The repository contains:  
- The [**`WildClaims dataset`**](Annotations/)  with extracted factual claims and human annotations.  
- The [**`data generation pipeline`**](Generation/) for preprocessing, filtering, claim extraction, and check-worthiness classification.  
- The [**`Analysis Scripts`**](Analysis/) used to reproduce the statistics and evaluation results reported in the paper.
- The [**`Prompts`**](Prompts/) used to generate the dataset via LLM-based claim extraction and check-worthiness classification. 


## What is WildClaims?
- **WildClaims** is a dataset designed to study **implicit information access** in real-world human-system conversations. It focuses on the phenomenon that we found, where users' access to the information often occurs implicitly through the form of check-worthy factual claims made by the system, even when the user's task is not explicitly informational (e.g., during creative writing).
- Derived from the existing WildChat corpus, the dataset contains **121,905 factual claims** extracted from 7,587 system utterances across 3,000 conversations. Each claim is annotated for check-worthiness, indicating whether it merits fact-checking.
- This resource aims to help the community to move beyond traditional explicit information access to better understand and address the **implicit information access** that arises in real-world user-system conversations. 

## Data Release  

The directory [`Annotations`](Annotations/) contains utterance-level results, human annotations, and full claim extractions used in our check-worthiness analysis.

This resource builds on prior work in **claim extraction** and **check-worthiness detection**.
Specifically, we use [Huo et al., 2023](https://dl.acm.org/doi/fullHtml/10.1145/3624918.3625336/) and [Song et al., 2024](https://aclanthology.org/2024.findings-emnlp.552//) for claim extraction, and [Hassan et al., 2015](https://dl.acm.org/doi/10.1145/2806416.2806652) and [Majer et al., 2024](https://aclanthology.org/2024.fever-1.27//) for check-worthiness classification. See [**`Generation/README.md`**](Generation/) for more details.

- [**`run_factual_claim_extraction.csv`**](Annotations/run_factual_claim_extraction.csv)  
  Full set of extracted factual claims (~31K with `FHuo`, ~91K with `FSong`). Each row corresponds to a claim linked to its source utterance (`Selected_Agent_Utterance`, `Conversation_Hash`, `Claim_Extr_Method`, `Individual_Statement`) with classifier outputs (`Hassan`, `Majer`). 


- [**`Human_Annotation.csv`**](Annotations/Human_Annotation.csv)  
  200 human-annotated claims for inter-annotator agreement and classifier evaluation. Includes annotator labels (`Human1_Annotation`, `Human2_Annotation`, `Check_Worthy`), binary CW flags (`Human1_CW`, `Human2_CW`, `CW_Tie`), agreement flags (`Human1_Human2_Agree`), and automatic classifier outputs (`Majer`, `Hassan`, `Intersection`, `Union`).  

- [**`run_analysis.csv`**](Annotations/run_analysis.csv)  
  Utterance-level results for ~3k sampled conversations. Each row corresponds to an agent utterance, with metadata (`Conversation_Hash`, `Turn_Num`, `Corresponding_User_Question`, `Selected_Agent_Utterance`, `Task_Classification`, `Use`) and multiple check-worthiness outputs (`Hassan`, `Majer`, `Intersection`, `Union`) plus fact counts (`*_Fact_Num`, `*_Fact_Total`).  

Together, these files enable replication of utterance-level and claim-level statistics, as well as evaluation of human vs. automatic check-worthiness classification.  

👉 For detailed schema and column descriptions, see [`Annotations/README.md`](Annotations/README.md).

## WilClaims Statistics
![Statistics](https://github.com/shakibaam/wildclaims/blob/main/Statistics.png?raw=true)



## Data Generation Pipeline

The [`Generation/`](./Generation/) directory contains scripts for preparing, labeling, and extracting claims from WildChat conversations before running check-worthiness analysis.  

**Workflow Summary:**
1. **Preprocessing** [**`Preprocess_Files_For_Pipeline.py`**](Generation/Preprocess_Files_For_Pipeline.py)  
   - Explodes conversations into utterance-level rows.  
   - Generates context windows for each system utterance.  

2. **Filtering Math & Code** [**`labeling_math_and_code.py`**](Generation/labeling_math_and_code.py)   
   - Labels conversations as *Math*, *Coding*, or *Others* to filter out non-relevant domains.  

3. **Task Classification** [**`task_classification.py`**](Generation/task_classification.py)   
   - Categorizes user utterances into high-level task types (information seeking, creative writing, reasoning, etc.).  

4. **Claim Extraction**  
   - **FHuo Method** [**`FHuo_method.py`**](Generation/FHuo_method.py): Extracts factual statements from system responses via OpenAI Batch.  
   - **FSong Method** [**`FSong_method.py`**](Generation/FSong_method.py): Generates JSONLs, runs FSong extraction, maps claims back, and explodes them into one-row-per-claim.  

5. **Check-Worthiness Classification** [**`CW.py`**](Generation/CW.py)  
   - Classifies factual statements; supports both *Major* and *Hassan* prompt variants.  

📂 **Details:** See the [Generation/README.md](./Generation/README.md) for complete pipeline descriptions, usage examples, and command-line arguments.



## Analysis  

The directory [`Analysis`](Analaysis/) contains Python scripts used to analyze the annotations and reproduce results reported in the paper.  

- [**`Statistics_3k_Conversation.py`**](Analaysis/Statistics_3k_Conversation.py)  
  Generates descriptive statistics for the 3,000 sampled conversations. Outputs counts of utterances, unique conversations, turn distributions, average lengths of user questions and agent utterances, and task classification distributions.  

- [**`Statistics_Fact_Claim_Extraction_3k.py`**](Analaysis/Statistics_Fact_Claim_Extraction_3k.py)  
  Computes statistics on factual claim extraction across the 3k conversations, comparing **FHuo** and **FSong** methods. Reports total claims, average claims per utterance/conversation, and coverage statistics.  

- [**`Statistics_Human_Annotations.py`**](Analaysis/Statistics_Human_Annotations.py)  
  Analyzes the 200 human-annotated claims. Provides row counts per extraction method, percentages of TRUE labels (`Human1_CW`, `Human2_CW`, `Gold`), and inter-annotator agreement using Cohen’s κ.  

- [**`Effectiveness_Automatic_Check_Worthiness.py`**](Analaysis/Effectiveness_Automatic_Check_Worthiness.py)  
  Evaluates automatic CW classifiers (`Hassan`, `Majer`, `Intersection`, `Union`) against the human-annotated gold labels. Reports Precision, Recall, F1-score, and Cohen’s κ for each extraction method.  

- [**`Prevalence_Check_Worthy_3k.py`**](Analaysis/Prevalence_Check_Worthy_3k.py)  
  Estimates the prevalence of CW claims across the 3,000 sampled conversations. Reports percentages of CW claims, utterances with ≥1 CW claim, and conversations with ≥1 CW claim for all classifier–extraction combinations. 

  For detailed instructions on running the analysis scripts, see the [Analaysis README](Analaysis/README.md). 




## License

WildClaims, following WildChat, is currently released under the [ODC-By 1.0](https://opendatacommons.org/licenses/by/1-0/) license, and by using WildClaims, you are agreeing to its usage terms.


<!-- ## Citation

TBA -->

## Contact

If you have any questions, please contact Shakiba Amirshahi or Hideaki Joko hideaki.joko@ru.nl