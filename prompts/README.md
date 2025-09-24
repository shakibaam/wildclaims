# Prompt Library

This folder contains prompts used to create and label the WildClaims dataset. Each file contains the prompt used in the corresponding scripts in `generation/`. Below is a description of each prompt and its provenance.

**Factual Claim Extraction Prompts:**

-   `F_Huo.txt`: This prompt is used in `f_huo_method.py` to run the **FHuo** claim extractor. The methodology is adapted from the work by [[Huo et al., 2023](https://dl.acm.org/doi/10.1145/3624918.3625336)].
-   `F_Song.txt`: This prompt is used in `f_song.py` and is based on the **VeriScore** method (**FSong**) from [[Song et al., 2024](https://aclanthology.org/2024.findings-emnlp.552/)].

**Check-Worthiness Classification Prompts:**

-   `Hassan.txt`: This prompt is used in `cw.py --prompt_mode Hassan` for check-worthiness classification. The prompt is based on the crowdsourcing task description from the early work on check-worthiness by [[Hassan et al., 2015](https://dl.acm.org/doi/10.1145/2806416.2806652)].
-   `Majer.txt`: This prompt is used in `cw.py --prompt_mode Majer` for check-worthiness classification. The prompt is adapted from the optimized prompt design for check-worthiness detection by [[Majer et al., 2024](https://aclanthology.org/2024.fever-1.27/)].

**Task Classification Prompt:**

- `Task_Classification.txt`: This prompt is used in `task_classification.py` to classify user tasks before claim extraction. The task categories and their definitions are adapted from the WildBench benchmark by [[Lin et al., 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/771155abaae744e08576f1f3b4b7ac0d-Paper-Conference.pdf)].
