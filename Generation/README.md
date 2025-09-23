# Data Generation Pipeline

This directory contains the pipeline for preprocessing WildChat conversations, filtering out math/coding content, extracting factual claims using `FHuo` and `FSong` methods, and classifying claims for check-worthiness. The scripts process raw conversation data through multiple stages to generate the WildClaims dataset.

The summary of each script is as follows:
- `labeling_math_and_code.py`: Labels conversations as Math, Coding, or Others to filter non-relevant domains before claim extraction.
- `Preprocess_Files_For_Pipeline.py`: Expands conversations into utterance-level rows and generates context windows for downstream claim extraction.
- `task_classification.py`: Classifies user utterances into high-level task categories like information seeking, creative writing, reasoning, etc.
- `FHuo_method.py`: Extracts factual statements from agent utterances using the FHuo method via OpenAI Batch API.
- `FSong.py`: End-to-end pipeline running FSong claim extraction, mapping results back to CSV, and expanding claims.
- `CW.py`: Classifies extracted factual statements into check-worthiness categories using the Majer or Hassan prompt variants.

⚠️ **WARNING**: Running these reproduction scripts may cost ~$1,000 in OpenAI API charges! ⚠️

**Table of Contents**

- [Claim Extraction and Check-Worthiness Methods Overview](#claim-extraction-and-check-worthiness-methods-overview)
- [Preprocessing](#preprocessing)
  - [`labeling_math_and_code.py`](#labeling_math_and_codepy)
  - [`Preprocess_Files_For_Pipeline.py`](#preprocess_files_for_pipelinepy)
  - [`task_classification.py`](#task_classificationpy)
- [Claim Extraction](#claim-extraction)
  - [`FHuo_method.py`](#fhuo_methodpy)
  - [`FSong.py`](#fsongpy)
- [Check-Worthiness Classification](#check-worthiness-classification)
  - [`CW.py`](#cwpy)

## Setting OpenAI API Key
Before running any pipeline scripts, set your OpenAI API key in your environment. For example, in a Unix-like shell, you can run:
```bash
export OPENAI_API_KEY="sk-..."
```

## Claim Extraction and Check-Worthiness Methods Overview

This resource builds on prior work in **claim extraction** and **check-worthiness detection**.  
We use the following methods, as described in the paper:

- **FHuo (Huo et al. 2023)** — Extracts factual statements from system utterances by prompting an LLM directly. 
  [[Paper link]](https://dl.acm.org/doi/fullHtml/10.1145/3624918.3625336/)  

- **FSong (Song et al. 2024)** — Extracts only *verifiable* factual claims. Produces broader coverage, yielding nearly 3× more claims than FHuo.  
  [[Paper link]](https://aclanthology.org/2024.findings-emnlp.552/)  

- **Hassan (Hassan et al. 2015)** — one of the earliest check-worthiness detection approaches, originally based on crowd annotation guidelines. In our work, we adapted it into an LLM prompt to classify claims as check-worthy or not.  
  [[Paper link]](https://dl.acm.org/doi/10.1145/2806416.2806652)  

- **Majer (Majer & Šnajder 2024)** — A recent check-worthiness detection method, using an effective LLM prompt designed to identify both factual and check-worthy factual claims.  
  [[Paper link]](https://aclanthology.org/2024.fever-1.27/)  

These methods are combined in different ways (e.g., intersection, union) to estimate the prevalence of check-worthy claims and to evaluate classifier effectiveness (See Section 4.1 of the paper).

## Preprocessing

### `labeling_math_and_code.py`

**Purpose**  
This script identifies and labels conversations in the WildChat dataset that are primarily about **mathematics** or **coding**, so they can be filtered out before claim extraction and check-worthiness analysis.  


**Pipeline**  
1. **Expand User Utterances**  
   - Reads the input conversation CSV.  
   - Creates a new row for every **user utterance**, preserving context, preceding system/agent utterances, and original metadata.  

2. **Batch Request Creation**  
   - Generates a JSONL file (`batch_requests.jsonl`) for the OpenAI Batch API.  
   - Each request contains the first user utterance and system response, with a classification prompt.  
   - Categories:  
     - **Math** – if the conversation involves mathematical problems or reasoning.  
     - **Coding** – if the conversation involves actual programming/code.  
     - **Others** – all remaining conversations.  

3. **Submit to OpenAI**  
   - Submit the `batch_requests.jsonl` file to the OpenAI Batch API.  

4. **Mapping Results Back**  
   - The script maps the predictions back to the exploded CSV rows using `Conversation_Hash`.  
   - Adds a `Label` column with the assigned category.  
   - Deduplicates rows by conversation.  
   - Saves the final labeled file  


**How to Run**  
```bash
python labeling_math_and_code.py \
  --input_csv path/to/input.csv \
  --output_dir outputs/labeling_math_and_code \
  --model_name gpt-4.1-mini-2025-04-14
```


### `Preprocess_Files_For_Pipeline.py`

**Purpose**  
This script runs the **preprocessing pipeline** to prepare system utterances (Agent/System) for downstream **claim extraction**.  
It takes in raw conversation CSV files, expands them into utterance-level rows, generates conversation contexts, and merges everything into a single unified dataset.

**Pipeline**  
1. **Expand System Utterances** (`explode_all_system_utterances_with_all_columns`)  
   - Iterates over each conversation.  
   - Creates a new row for every system utterance (columns like `Utterance-1 (Agent)` or `Utterance-2 (System)`).  
   - Adds metadata columns:  
     - `Turn_Num` – index of the utterance within the conversation  
     - `Selected_Agent_Utterance` – the system's utterance text  
     - `Corresponding_User_Question` – the preceding user input, if available  
     - `Selected_Agent_Column` – the column name where the utterance was located  

2. **Generate Context Strings** 
   - For each system utterance, builds a **context window** containing all user–agent exchanges leading up to that utterance.  
   - Contexts are formatted as Python-style lists of strings, e.g.:
     ```text
     [
     User: What is photosynthesis?
     System: Photosynthesis is the process by which plants make food...
     ]
     ```

**How to Run**
```bash
python Preprocess_Files_For_Pipeline.py \
  --input_csv path/to/input.csv \
  --output_dir outputs/preprocessing
```
 
### `task_classification.py`

**Purpose**  
Classifies **user utterances** into high-level **task categories** to better understand user intent in WildChat conversations.  
Categories include:  
- *Information seeking*  
- *Creative Writing*  
- *Editing*  
- *Reasoning*  
- *Brainstorming*  
- *Planning*  
- *Role playing*  
- *Others*  

**How to Run**
```bash
python task_classification.py \
  --input_csv path/to/input.csv \
  --output_dir outputs/task_classification \
  --model_name gpt-4.1-2025-04-14
```

## Claim Extraction

### `FHuo_method.py`

2. **Mapping Results** 
   - Maps OpenAI batch results back to the CSV.  
   - Adds a `Factual_Statements` column containing the extracted claims.  

3. **Expanding Claims**   
   - Splits the `Factual_Statements` list into separate rows.  
   - Each claim is stored under `Individual_Statement` with its index (`Statement_Index`). 

**How to Run**
```bash
python FHuo_method.py \
  --input_csv path/to/input.csv \
  --output_dir outputs/FHuo \
  --model_name gpt-4.1-2025-04-14
``` 


### `FSong.py`

**Purpose**  
End-to-end pipeline to (1) generate per-row JSONL requests from a CSV, (2) run **FSong** claim extraction on each request, (3) map extracted claims back to the CSV, and (4) expand the list of claims into one-row-per-claim.

**Setup**  
Before running this pipeline, you need to clone the FSong repository and set up the environment. Clone the FSong repository to your local machine and ensure it's properly configured for claim extraction:
`https://github.com/Yixiao-Song/VeriScore`



**Pipeline**  
1. **Batch Request Creation**  
   - Builds one JSONL file per row under `output_dir/batch_requests/{Conversation_Hash}/{Conversation_Hash}_{Turn_Num}.jsonl`.  
   - Each JSON contains `question` (User + Context), `response` (agent), and metadata.

2. **Run FSong** (`run_FSong`)  
   - Calls `python -m FSong.extract_claims` for every JSONL.  
   - Produces `claims_{hash}_{turn}.jsonl` files inside the FSong output folder.

3. **Map Claims to CSV** (`map_FSong_claims_to_csv`)  
   - Reads all `claims_{hash}_{turn}.jsonl`, matches them to CSV rows, and writes a new file:  
     `FSong_with_factual_statements.csv` with a `Factual_Statements` JSON list column.

4. **Expand Claims** (`explode_FSong_claims`)  
   - Turns each list of claims into multiple rows.  
   - Adds `Statement_Index` and `Individual_Statement`.  


**How to Run**
```bash
python FSong.py \
  --input_csv path/to/preprocessed_unified.csv \
  --output_dir outputs/FSong \
  --model_name gpt-4 \
  --FSong_model gpt-4.1-2025-04-14 \
  --FSong_dir path/to/FSongRepo
```


## Check-Worthiness Classification

### `CW.py`

**Purpose**  
Classifies extracted factual statements into **check-worthiness categories** using OpenAI batch inference.  
Two prompt variants are supported:  

- **Majer**: Classifies into `NFS` (Non-Factual Sentence), `UFS` (Unimportant Factual Sentence), or `CFS` (Check-worthy Factual Sentence).  
- **Hassan**: A question-driven formulation asking whether the user would care if the claim were true or false, producing the same three labels.

Note that while the original paper uses three labels, for our analysis we binarize them into **Check-Worthy** (`CFS`) vs. **Not Check-Worthy** (`NFS` + `UFS`).

**Pipeline**  
1. **Batch Request Creation** 
   - Generates JSONL requests for each claim + context pair.  
   - `custom_id` encodes `(Conversation_Hash, Turn_Num, Statement_Index)`.

2. **Batch Submission & Retrieval**  
   - Submits jobs via the OpenAI Batch API.  
   - Fetches results once jobs are complete.

3. **Mapping Predictions**  
   - Aligns results back into the CSV.  
   - Adds a new column with classifier predictions (default: `Majer`, or user-specified).

**How to Run**
```bash
python CW.py \
  --input_csv path/to/input.csv \
  --output_dir outputs/CW \
  --model_name gpt-4.1-2025-04-14 \
  --prompt_variant Majer
```
