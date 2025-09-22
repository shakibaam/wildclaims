 
### `labeling_math_and_code.py`

**Purpose**  
This script identifies and labels conversations in the WildChat dataset that are primarily about **mathematics** or **coding**, so they can be filtered out before claim extraction and check-worthiness analysis.  

**Pipeline**  
1. **Explode User Utterances**  
   - Reads the input conversation CSV.  
   - Creates a new row for every **user utterance**, preserving context, preceding system/agent utterances, and original metadata.  
   - Saves the result as `exploded.csv` in the output directory.  

2. **Batch Request Creation**  
   - Generates a JSONL file (`batch_requests.jsonl`) for the OpenAI Batch API.  
   - Each request contains the first user utterance and system response, with a classification prompt.  
   - Categories:  
     - **Math** – if the conversation involves mathematical problems or reasoning.  
     - **Coding** – if the conversation involves actual programming/code.  
     - **Others** – all remaining conversations.  

3. **Submit to OpenAI**  
   - You manually submit the `batch_requests.jsonl` file to the OpenAI Batch API.  
   - Once the job completes, place the results file as `batch_results.jsonl` in the same output directory.  

4. **Mapping Results Back**  
   - The script maps the predictions from `batch_results.jsonl` back to the exploded CSV rows using `Conversation_Hash`.  
   - Adds a `Label` column with the assigned category.  
   - Deduplicates rows by conversation.  
   - Saves the final labeled file as `labeled_output.csv`.  

**Output Files**  
- `exploded.csv` – exploded user utterances with context.  
- `batch_requests.jsonl` – batch request payload for OpenAI API.  
- `batch_results.jsonl` – batch API results (must be manually downloaded and placed).  
- `labeled_output.csv` – final labeled dataset with one row per conversation and a `Label` column (`Math`, `Coding`, or `Others`).  

**How to Run**
```bash
python labeling_math_and_code.py \
    --input_csv path/to/input.csv \
    --output_dir outputs/labeling_math_and_code \
    --model_name gpt-4.1-mini-2025-04-14


`Preprocess_Files_For_Pipeline.py`

**Purpose**  
This script runs the **preprocessing pipeline** to prepare system utterances (Agent/System) for downstream **claim extraction**.  
It takes in raw conversation CSV files, explodes them into utterance-level rows, generates conversation contexts, and merges everything into a single unified dataset.

**Pipeline**  
1. **Explode System Utterances** (`explode_all_system_utterances_with_all_columns`)  
   - Iterates over each conversation.  
   - Creates a new row for every system utterance (columns like `Utterance-1 (Agent)` or `Utterance-2 (System)`).  
   - Adds metadata columns:  
     - `Turn_Num` – index of the utterance within the conversation  
     - `Selected_Agent_Utterance` – the system’s utterance text  
     - `Corresponding_User_Question` – the preceding user input, if available  
     - `Selected_Agent_Column` – the column name where the utterance was located  
   - Saves the exploded dataset as `exploded_system.csv`.

2. **Generate Context Strings** (`generate_context_string`)  
   - For each system utterance, builds a **context window** containing all user–agent exchanges leading up to that utterance.  
   - Contexts are formatted as Python-style lists of strings, e.g.:
     ```text
     [
     User: What is photosynthesis?
     System: Photosynthesis is the process by which plants make food...
     ]
     ```
   - Saves results as `context_system.csv`.

3. **Merge Contexts** (`preprocess`)  
   - Merges the context strings back into the exploded DataFrame.  
   - Produces the final preprocessed file `preprocessed_unified.csv`.

**Output Files**  
- `exploded_system.csv` – one row per system utterance with metadata  
- `context_system.csv` – system utterances with generated conversation contexts  
- `preprocessed_unified.csv` – unified dataset containing both utterances and contexts (used as input for claim extraction methods such as SIQing or VeriScore)

**How to Run**
```bash
python Preprocess_Files_For_Pipeline.py \
  --input_csv path/to/input.csv \
  --output_dir outputs/preprocessing
 
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

This classification enables downstream analyses such as **distribution of tasks**, filtering, or comparison across model types.

---

**Pipeline**  
1. **Explode User Utterances** (`explode_all_user_utterances_with_all_columns`)  
   - Converts each conversation row into multiple rows, one per user utterance.  
   - Adds metadata:  
     - `Turn_Num` (utterance position)  
     - `Context_String` (prior conversation history)  
     - `Selected_User_Utterance` (the utterance being classified)  
     - `Selected_User_Column` (original column name).  
   - Output: `exploded_user_utterances.csv`

2. **Batch Request File Generation** (`make_task_classification_batch_request_file`)  
   - Creates a JSONL file of requests for the OpenAI Batch API.  
   - Each request includes the utterance and its surrounding context.  
   - Output: `batch_requests.jsonl`

3. **Submit and Fetch Batch Results**  
   - Submits classification requests to the OpenAI Batch API.  
   - Once results are available, fetches them and stores as `batch_results.jsonl`.

4. **Map Results Back to CSV** (`map_task_classification_results_to_csv`)  
   - Matches batch results with utterances using `(Conversation_Hash, Turn_Num)`.  
   - Adds a new column `Task_Classification` with the predicted category.  
   - Output: `task_classified.csv`

---

**Output Files**  
- `exploded_user_utterances.csv` — per-utterance dataset with context.  
- `batch_requests.jsonl` — request payload for OpenAI Batch API.  
- `batch_results.jsonl` — raw classification outputs from OpenAI.  
- `task_classified.csv` — final dataset with task category labels.

---

**How to Run**
```bash
python task_classification.py \
  --input_csv path/to/input.csv \
  --output_dir outputs/task_classification \
  --model_name gpt-4.1-2025-04-14


### `siqing_method.py`

**Purpose**  
Extracts factual statements from agent utterances using the **SIQing method**.  
This step generates candidate claims (concise factual assertions) that can be validated for check-worthiness.

**Input**  
- `preprocessed_unified.csv` (from the preprocessing pipeline)  
  Required columns: `Conversation_Hash`, `Turn_Num`, `Context_String`, `Corresponding_User_Question`, `Selected_Agent_Utterance`

**Pipeline**  
1. **Batch Request Creation** (`make_siqing_batch_request_file`)  
   - Creates a JSONL batch file (`siqing_batch_requests.jsonl`) for the OpenAI Batch API.  
   - Each request asks the model to extract concise factual statements from an agent utterance.  
   - Identified by `custom_id = Conversation_Hash_TurnNum`.

2. **Mapping Results** (`map_siqing_results_to_csv`)  
   - Maps OpenAI batch results back to the CSV.  
   - Adds a `Factual_Statements` column containing the extracted claims.  
   - Output: `siqing_with_factual_statements.csv`.

3. **Exploding Claims** (`explode_siqing_factual_statements`)  
   - Splits the `Factual_Statements` list into separate rows.  
   - Each claim is stored under `Individual_Statement` with its index (`Statement_Index`).  
   - Output: `siqing_exploded_statements.csv`.

**Output Files**  
- `siqing_batch_requests.jsonl` – batch request payloads  
- `siqing_batch_metadata.jsonl` – metadata for submitted jobs  
- `siqing_batch_results.jsonl` – raw model outputs  
- `siqing_with_factual_statements.csv` – aligned claims in CSV format  
- `siqing_exploded_statements.csv` – one claim per row, ready for downstream classification


### `veriscore_method.py`

**Purpose**  
Runs the **VeriScore claim extraction pipeline** (Song et al.) as an alternative to SIQing.  
Generates factual claims from agent/system utterances using the official VeriScore extractor.

**Setup**  
Clone the VeriScore repository:  
```bash
git clone https://github.com/Yixiao-Song/VeriScore



### `CW.py`

**Purpose**  
Classifies extracted factual statements into **check-worthiness categories** using OpenAI batch inference.  
Two prompt variants are supported:  

- **Major**: Classifies into `NFS` (Non-Factual Sentence), `UFS` (Unimportant Factual Sentence), or `CFS` (Check-worthy Factual Sentence).  
- **Hassan**: A question-driven formulation asking whether the user would care if the claim were true or false, producing the same three labels.

**Input**  
- CSV with exploded claims (e.g., from `siqing_exploded_statements.csv` or `veriscore_exploded_statements.csv`)  
  Required columns: `Individual_Statement`, `Context_String`, `Conversation_Hash`, `Turn_Num`, `Statement_Index`

**Pipeline**  
1. **Batch Request Creation** (`make_claim_batch_request_file`)  
   - Generates JSONL requests for each claim + context pair.  
   - `custom_id` encodes `(Conversation_Hash, Turn_Num, Statement_Index)`.

2. **Batch Submission & Retrieval**  
   - Submits jobs via the OpenAI Batch API.  
   - Fetches results once jobs are complete.

3. **Mapping Predictions** (`add_CW_predictions_to_csv`)  
   - Aligns results back into the CSV.  
   - Adds a new column with classifier predictions (default: `Major`, or user-specified).

**Output**  
- Updated CSV with one additional column (e.g., `Major` or `Hassan`) containing `NFS`, `UFS`, or `CFS` labels for each claim.  
- Batch request/metadata/results JSONL files saved in the same output directory.
