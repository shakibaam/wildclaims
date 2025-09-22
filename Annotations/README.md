### `Annotations/run_analysis.csv`

This file contains the **utterance-level results** used for check-worthiness analysis.  
Each row corresponds to a single agent utterance within a conversation.

**Columns:**

- `Conversation_Hash`: Unique identifier for each conversation  
- `Turn_Num`: Turn number within the conversation (1, 2, 3, …)  
- `Corresponding_User_Question`: The user’s question/input for this turn  
- `Selected_Agent_Utterance`: The agent’s response/utterance for this turn  
- `Selected_Agent_Column`: Column identifier (e.g., *Utterance-1 (Agent)*)  
- `Task_Classification`: Task type (e.g., *Information seeking*, *Creative Writing*, …)  
- `Use`: Usage flag (TRUE/FALSE)  

**Check-worthiness outputs:** (arrays of booleans, one per extracted claim)  
- `FHuo_Hassan`: Using **FHuo** claim extraction + *Hassan* check-worthiness classifier  
- `FSong_Hassan`: Using **FSong** claim extraction + *Hassan* check-worthiness classifier  
- `FHuo_Majer`: Using **FHuo** extraction + *Majer* check-worthiness classifier   
- `FSong_Majer`: Using **FSong** extraction + *Majer* check-worthiness classifier   
- `FHuo_Intersection`: Intersection of *Hassan* and *Majer* results (FHuo extraction)  
- `FSong_Intersection`: Intersection of *Hassan* and *Majer* results (FSong extraction)  
- `FHuo_Union`: Union of *Hassan* and *Majer* results (FHuo extraction)  
- `FSong_Union`: Union of *Hassan* and *Majer* results (FSong extraction)  

**Counts:**  
- `*_Fact_Num`: Number of check-worthy facts identified by each method  
- `*_Fact_Total`: Total number of facts extracted by each method


### `Annotations/Human_Annotation.csv`

This file contains **200 human-annotated claims** used for inter-annotator agreement analysis and evaluation of automatic check-worthiness classifiers.

**Basic Information**
- `Claim_Extr_Method`: Claim extraction method used (*FHuo* or *FSong*)  
- `Ver`: Version identifier  
- `Conversation_Hash`: Unique identifier for the conversation  
- `Individual_Statement`: The specific claim being annotated  
- `Task_Classification`: Task type of the conversation turn  

**Human Annotations**
- `Human1_Annotation`, `Human2_Annotation`: Full-label classifications by each annotator (*NFS, UFS, CFS*)  
- `Human1_CW`, `Human2_CW`: Binary check-worthiness decisions (TRUE/FALSE)  
- `Human1_Human2_Agree`: Agreement flag (TRUE if both annotators agree)  
- `Check_Worthy`: Tie-breaking annotation label (applied when Human1 and Human2 disagree)  
- `CW_Tie`: Tie-breaking binary decision (TRUE/FALSE)  

**Automatic Classifier Outputs**
- `Majer`: Majer classifier output label (*NFS, UFS, CFS*)    
- `Hassan`: Hassan classifier output label (*NFS, UFS, CFS*)  
- `Majer_Binary`: Majer classifier binary output (TRUE/FALSE)  
- `Hassan_Binary`: Hassan classifier binary output (TRUE/FALSE)  
- `Gold`: Final gold standard binary label (TRUE/FALSE), integrating tie-breaks  
- `Intersection`: TRUE if both Hassan and Majer classifiers predict CW  
- `Union`: TRUE if either Hassan or Majer classifier predicts CW



### `Annotations/run_factual_claim_extraction.csv`

This file contains the **full set of extracted factual claims** from the 3k sampled conversations.  
Each row corresponds to a **single claim** linked to its originating agent utterance.

**Columns**
- `Selected_Agent_Utterance`: The agent’s utterance from which the claim was extracted  
- `Conversation_Hash`: Unique identifier for the conversation  
- `Claim_Extr_Method`: Claim extraction method used (*FHuo* or *FSong*)  
- `Individual_Statement`: The extracted claim text  
- `Hassan`: Hassan check-worthiness classifier output (True/False)  
- `Majer`: Majer check-worthiness classifier output (True/False) 

**Notes**
- This file operates at the **claim level** (one row per claim), unlike `run_analysis.csv`, which is **utterance-level**.  
- Totals:  
    - **FHuo** extraction: **~31,108** claims  
    - **FSong** extraction: **~90,797** claims   
- These counts align with the paper’s reported results and can be used to replicate extraction statistics.