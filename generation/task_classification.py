import os
import sys
os.environ['PYTHONPATH'] = os.getcwd()

import re
import json
from typing import List
import pandas as pd
import openai
from openai import OpenAI
import numpy as np
import argparse

from openai_batch_utils import submit_openai_batch, get_batch_statuses_from_metadata, fetch_batch_output, split_jsonl_file


def explode_all_user_utterances_with_all_columns(input_csv, output_dir):
    """
    For each row in the input CSV, create a new row for every user utterance,
    with context, preceding system/agent utterance, and all original columns, ready for task classification.
    Context_String will be a Python-style list of utterance strings.
    Saves the exploded CSV as 'exploded_user_utterances.csv' in output_dir.
    """
    output_csv = os.path.join(output_dir, "exploded_user_utterances.csv")
    df = pd.read_csv(input_csv)
    user_pattern = re.compile(r'Utterance-(\d+) \(User\)')

    all_columns = list(df.columns) + [
        'Turn_Num', 'Context_String',
        'Selected_User_Utterance', 'Selected_User_Column',
    ]

    exploded_rows = []
    for idx, row in df.iterrows():
        conversation_hash = row['Conversation_Hash']
        
        # Find all user utterances in this conversation
        user_utterances = []
        for col in df.columns:
            if col.startswith('Utterance-') and '(User)' in col:
                match = user_pattern.match(col)
                if match:
                    turn_num = int(match.group(1))
                    utterance_text = str(row[col]).strip()
                    if utterance_text and utterance_text != 'nan':
                        user_utterances.append((turn_num, col, utterance_text))
        
        # Sort by turn number
        user_utterances.sort(key=lambda x: x[0])
        
        # Create a row for each user utterance
        for turn_num, col_name, utterance_text in user_utterances:
            # Build context string (all utterances up to this point)
            context_utterances = []
            for context_col in df.columns:
                if context_col.startswith('Utterance-'):
                    context_match = re.match(r'Utterance-(\d+)', context_col)
                    if context_match:
                        context_turn = int(context_match.group(1))
                        if context_turn < turn_num:
                            context_text = str(row[context_col]).strip()
                            if context_text and context_text != 'nan':
                                context_utterances.append(f"{context_col}: {context_text}")
            
            context_string = str(context_utterances) if context_utterances else "[]"
            
            # Create new row with all original columns plus new ones
            new_row = row.copy()
            new_row['Turn_Num'] = turn_num
            new_row['Context_String'] = context_string
            new_row['Selected_User_Utterance'] = utterance_text
            new_row['Selected_User_Column'] = col_name
            
            exploded_rows.append(new_row)

    # Create DataFrame and save
    exploded_df = pd.DataFrame(exploded_rows)
    exploded_df.to_csv(output_csv, index=False)
    print(f"✅ Exploded user utterances saved to: {output_csv}")
    print(f"📊 Original rows: {len(df)}, Exploded rows: {len(exploded_df)}")
    return output_csv


def make_task_classification_batch_request_file(
    input_csv_path, output_jsonl_path, model_name="gpt-4.1-2025-04-14"
):
    """
    Creates a batch request file for task classification using OpenAI batch API.
    Each request uses Selected_User_Utterance as the input and Context_String as context.
    custom_id is set to conversation_hash + turn_num.
    """
    df = pd.read_csv(input_csv_path)
    required_columns = ["Selected_User_Utterance", "Context_String", "Conversation_Hash", "Turn_Num"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    with open(output_jsonl_path, "w", encoding="utf-8") as f:
        for i, row in df.iterrows():
            user_utterance = str(row["Selected_User_Utterance"]).strip()
            context_str = str(row["Context_String"]).strip()
            conversation_hash = str(row["Conversation_Hash"]).strip()
            turn_num = str(row["Turn_Num"]).strip()
            
            if not user_utterance or not conversation_hash or not turn_num:
                continue
            
            prompt = (
                "Classify the following user utterance from a conversation with an AI assistant into one of these categories:\n\n"
                "- Information seeking: User is asking for factual information, explanations, or help with understanding something\n"
                "- Creative Writing: User is asking for creative content like stories, poems, scripts, or creative ideas\n"
                "- Editing: User is asking for help with editing, revising, or improving existing text\n"
                "- Reasoning: User is asking for logical analysis, problem-solving, or step-by-step thinking\n"
                "- Brainstorming: User is asking for ideas, suggestions, or exploring possibilities\n"
                "- Planning: User is asking for help with planning, organizing, or structuring something\n"
                "- Role playing: User is engaging in role-play, simulation, or acting as someone else\n"
                "- Others: Any other type of interaction that doesn't fit the above categories\n\n"
                "Respond with only the category name. Do not provide any explanation.\n\n"
                f"User utterance: {user_utterance}\n\n"
                f"Conversation context: {context_str}"
            )
            
            request_obj = {
                "custom_id": f"{conversation_hash}_{turn_num}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that classifies user utterances into task categories."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0,
                    "max_tokens": 1000
                }
            }
            f.write(json.dumps(request_obj, ensure_ascii=False) + "\n")
    
    print(f"✅ Task classification batch request file saved to: {output_jsonl_path}")


def map_task_classification_results_to_csv(
    original_csv_path: str,
    batch_results_jsonl_path: str,
    output_csv_path: str
):
    """
    Maps OpenAI batch results from a JSONL file to the original CSV using conversation_hash and turn_num,
    and adds a new column with the classification.
    """
    df = pd.read_csv(original_csv_path)
    df['Turn_Num'] = df['Turn_Num'].astype(str)
    df['Conversation_Hash'] = df['Conversation_Hash'].astype(str)
    
    classifications = {}
    with open(batch_results_jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            custom_id = item.get("custom_id")
            if not custom_id or "response" not in item:
                continue
            
            parts = custom_id.split("_")
            if len(parts) < 2:
                continue
            
            turn_num = parts[-1]
            conversation_hash = "_".join(parts[:-1])
            
            answer = (
                item["response"]["body"]["choices"][0]["message"]["content"].strip()
                if "body" in item["response"] and "choices" in item["response"]["body"]
                else ""
            )
            classifications[(conversation_hash, turn_num)] = answer
    
    df['Task_Classification'] = [
        classifications.get((str(row['Conversation_Hash']), str(row['Turn_Num'])), "")
        for _, row in df.iterrows()
    ]
    
    num_classified = (df['Task_Classification'] != "").sum()
    num_empty = (df['Task_Classification'] == "").sum()
    print(f"Number of rows with classification: {num_classified}")
    print(f"Number of rows with EMPTY classification: {num_empty}")
    
    df.to_csv(output_csv_path, index=False, encoding='utf-8')
    print(f"✅ Updated CSV with classifications saved to: {output_csv_path}")
    
    # Print classification distribution
    if num_classified > 0:
        print("\n📊 Classification distribution:")
        print(df['Task_Classification'].value_counts())
    
    return output_csv_path


def main():
    parser = argparse.ArgumentParser(description="Task Classification Pipeline")
    parser.add_argument('--input_csv', type=str, required=True, help='Input CSV file with conversations')
    parser.add_argument('--output_dir', type=str, required=False, default='output_task_classification', help='Output directory for all results')
    parser.add_argument('--model_name', type=str, default='gpt-4.1-2025-04-14', help='OpenAI model name')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    
    # File paths
    exploded_csv = os.path.join(args.output_dir, 'exploded_user_utterances.csv')
    batch_requests_path = os.path.join(args.output_dir, 'batch_requests.jsonl')
    batch_metadata_path = os.path.join(args.output_dir, 'batch_metadata.jsonl')
    batch_results_path = os.path.join(args.output_dir, 'batch_results.jsonl')
    classified_csv = os.path.join(args.output_dir, 'task_classified.csv')

    if os.path.exists(batch_metadata_path):
        print("Batch metadata found.")
        if os.path.exists(batch_results_path):
            print("Results found. Mapping classifications to CSV...")
            map_task_classification_results_to_csv(
                original_csv_path=exploded_csv,
                batch_results_jsonl_path=batch_results_path,
                output_csv_path=classified_csv
            )
            print(f"\n🎉 Task classification complete! Results saved in: {args.output_dir}")
        else:
            print("Checking batch status...")
            statuses = get_batch_statuses_from_metadata(batch_metadata_path)
            if statuses and statuses[0]['status'] == 'completed':
                print("Fetching batch results from OpenAI...")
                fetch_batch_output(
                    metadata_path=batch_metadata_path,
                    save_path=batch_results_path
                )
                print("Results fetched. Mapping classifications to CSV...")
                map_task_classification_results_to_csv(
                    original_csv_path=exploded_csv,
                    batch_results_jsonl_path=batch_results_path,
                    output_csv_path=classified_csv
                )
                print(f"\n🎉 Task classification complete! Results saved in: {args.output_dir}")
            else:
                print(f"Batch not completed yet. Status: {statuses[0]['status'] if statuses else 'Unknown'}")
                print("You may need to rerun this script later to process results.")
    else:
        print("No batch metadata found. Creating and submitting new batch...")
        
        # Step 1: Explode user utterances
        print(f"\n[1/4] Exploding user utterances...")
        explode_all_user_utterances_with_all_columns(args.input_csv, args.output_dir)
        
        # Step 2: Create batch request file
        print(f"\n[2/4] Creating batch request JSONL...")
        make_task_classification_batch_request_file(
            input_csv_path=exploded_csv,
            output_jsonl_path=batch_requests_path,
            model_name=args.model_name
        )
        
        # Step 3: Submit batch to OpenAI
        print(f"\n[3/4] Submitting batch to OpenAI...")
        submit_openai_batch(
            batch_requests_path,
            metadata_path=batch_metadata_path
        )
        print("Batch submitted. Please rerun this script later to fetch results.")


if __name__ == "__main__":
    main() 