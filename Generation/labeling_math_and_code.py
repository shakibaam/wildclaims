import os
import pandas as pd
import json
from openai import OpenAI
import re
from typing import List, Dict, Any
import pandas as pd
import numpy as np

from openai_batch_utils import (
    split_jsonl_file, 
    submit_openai_batch, 
    get_batch_statuses_from_metadata, 
    fetch_batch_output
)

import argparse


def explode_all_user_utterances_with_all_columns(input_csv, output_dir):
    """
    For each row in the input CSV, create a new row for every user utterance,
    with context, preceding system/agent utterance, and all original columns, ready for claim extraction.
    Context_String will be a Python-style list of utterance strings.
    Saves the exploded CSV as 'exploded.csv' in output_dir.
    """
    output_csv = os.path.join(output_dir, "exploded.csv")
    df = pd.read_csv(input_csv)
    user_pattern = re.compile(r'Utterance-(\d+) \(User\)')

    all_columns = list(df.columns) + [
        'Turn_Num', 'Context_String',
        'Selected_User_Utterance', 'Selected_User_Column',
    ]

    exploded_rows = []

    for idx, row in df.iterrows():
        # Find all user utterance columns for this row
        user_cols = [col for col in df.columns if user_pattern.match(col) and pd.notna(row[col]) and str(row[col]).strip() != '']
        for user_col in user_cols:
            turn_num = int(user_pattern.match(user_col).group(1))
            # Gather context: all utterances up to and including this turn
            context = []
            for t in range(turn_num + 1):
                for role in ['User', 'Agent', 'System']:
                    col = f'Utterance-{t} ({role})'
                    if col in df.columns and pd.notna(row[col]) and str(row[col]).strip() != '':
                        context.append(f"{role}: {row[col]}")
            # Format as a Python list of strings
            context_str = '[\n' + ',\n'.join(context) + '\n]'
   
            user_utt = row[user_col]
            # Build new row with all original columns
            new_row = row.to_dict()
            new_row.update({
                'Turn_Num': turn_num,
                'Context_String': context_str,
                'Selected_User_Utterance': user_utt,
                'Selected_User_Column': user_col
            })
            exploded_rows.append(new_row)

    exploded_df = pd.DataFrame(exploded_rows)
    # Ensure all columns are present and in the same order
    for col in all_columns:
        if col not in exploded_df.columns:
            exploded_df[col] = ''
    exploded_df = exploded_df[all_columns]

    exploded_df.to_csv(output_csv, index=False)
    print(f"✅ Saved exploded user utterances and original rows (with all columns) to {output_csv}")
    return output_csv


def make_openai_batch_request_file(exploded_csv, output_dir, model_name="gpt-4.1-mini-2025-04-14"):
    """
    Reads the exploded CSV, creates a batch request file for OpenAI batch API, and saves as JSONL in output_dir.
    custom_id is set to the conversation_hash column if available, otherwise falls back to row index.
    """
    output_jsonl_path = os.path.join(output_dir, "batch_requests.jsonl")
    df = pd.read_csv(exploded_csv)
    system_prompt = (
        "You are an annotation expert tasked with categorizing conversations between humans and AI. "
        "Review each conversation and assign it to one of these categories: 'Math', 'Coding', or 'Others'. "
        "Use the following guidelines: Math: Assign this category if the conversation focuses on mathematical problems or concepts. "
        "Coding: Choose this category for conversations that involve actual coding. Others: Use this category for conversations that do not clearly fit into 'Math' or 'Coding,' or are only slightly related to these topics. "
        "For generating output: Your response MUST contain the chosen category, formatted as: [[Category]]. "
    )
    with open(output_jsonl_path, "w", encoding="utf-8") as f:
        for i, row in df.iterrows():
            user_utterance = str(row.get('Utterance-0 (User)', '')).strip()
            system_utterance = str(row.get('Utterance-1 (Agent)', '')).strip()
            conversation_prompt = f"User: \n{user_utterance}\n\nSystem: \n{system_utterance}"
            conversation_hash = str(row.get('Conversation_Hash', '')).strip()
            custom_id = conversation_hash if conversation_hash else f"request-{i}"
            request_obj = {
                "custom_id": custom_id,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": conversation_prompt}
                    ],
                    "max_tokens": 20,
                    "temperature": 0
                }
            }
            f.write(json.dumps(request_obj, ensure_ascii=False) + "\n")
    print(f"✅ Batch request file saved to {output_jsonl_path}")
    return output_jsonl_path


def map_batch_results_to_csv(batch_results_path, exploded_csv, output_dir):
    """
    Maps batch results back to the exploded CSV using custom_id/conversation_hash.
    Extracts labels from batch results and adds them as the second column.
    Saves the labeled CSV as 'labeled_output.csv' in output_dir.
    """
    output_csv_path = os.path.join(output_dir, "labeled_output.csv")
    # Load exploded CSV
    df = pd.read_csv(exploded_csv)
    print(f"Original CSV has {len(df)} rows")
    
    # Load batch results and extract labels
    results_mapping = {}
    batch_results_count = 0
    with open(batch_results_path, 'r', encoding='utf-8') as f:
        for line in f:
            batch_results_count += 1
            result = json.loads(line.strip())
            custom_id = result.get('custom_id', '')
            if 'response' in result and 'body' in result['response']:
                try:
                    label_content = result['response']['body']['choices'][0]['message']['content']
                    # Extract label from [[Category]] format
                    label_match = re.search(r'\[\[(.*?)\]\]', label_content)
                    if label_match:
                        label = label_match.group(1).strip()
                    else:
                        label = label_content.strip()
                    results_mapping[custom_id] = label
                except (KeyError, IndexError):
                    print(f"Warning: Could not extract label from result for custom_id: {custom_id}")
                    results_mapping[custom_id] = "ERROR"
    print(f"Batch results file has {batch_results_count} lines")
    print(f"Successfully extracted {len(results_mapping)} labels")
    
    # Check if all custom_ids in results are in the exploded CSV
    missing_hashes = set(results_mapping.keys()) - set(df['conversation_hash'].unique())
    if missing_hashes:
        print(f"⚠️ Warning: {len(missing_hashes)} custom_ids from results not found in exploded CSV")
        print("First few missing hashes:", list(missing_hashes)[:5])
    
    # Add label column to dataframe
    df['Label'] = df['Conversation_Hash'].map(results_mapping)
    
    # Filter rows that have labels (i.e., were successfully processed)
    df_with_labels = df[df['Label'].notna() & (df['Label'] != '')]
    
    print(f"Rows with labels: {len(df_with_labels)}")
    
    # Remove duplicates based on conversation_hash to avoid repetitive rows
    df_with_labels = df_with_labels.drop_duplicates(subset=['Conversation_Hash'], keep='first')
    
    print(f"After removing duplicates: {len(df_with_labels)} rows")
    
    # Reorder columns to put Label as second column
    cols = list(df_with_labels.columns)
    if 'Label' in cols:
        cols.remove('Label')
        cols.insert(1, 'Label')  # Insert as second column (index 1)
        df_with_labels = df_with_labels[cols]
    
    # Save the filtered CSV
    df_with_labels.to_csv(output_csv_path, index=False)
    
    print(f"✅ Mapped CSV saved to: {output_csv_path}")
    print(f"Original rows: {len(df)}")
    print(f"Final rows with labels: {len(df_with_labels)}")
    print(f"Label distribution:")
    print(df_with_labels['Label'].value_counts())
    
    return output_csv_path


def main():
    parser = argparse.ArgumentParser(description="Label conversations as Math, Code, or Other.")
    parser.add_argument('--input_csv', required=True, help='Path to the input CSV file')
    parser.add_argument('--output_dir', required=True, help='Directory to save all outputs')
    parser.add_argument('--model_name', default="gpt-4.1-mini-2025-04-14", help='OpenAI model to use')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Step 1: Explode user utterances
    print("Exploding all user utterances...")
    exploded_csv = explode_all_user_utterances_with_all_columns(args.input_csv, args.output_dir)

    # Step 2: Create batch request file
    print("Creating OpenAI batch request file...")
    batch_jsonl = make_openai_batch_request_file(exploded_csv, args.output_dir, model_name=args.model_name)

    print("Submit your batch request file to OpenAI and wait for results.")
    print(f"Once you have the results JSONL, place it as 'batch_results.jsonl' in {args.output_dir} and rerun this script.")

    # Step 3: Map results to CSV
    batch_results = os.path.join(args.output_dir, "batch_results.jsonl")
    print("Mapping batch results to CSV...")
    labeled_csv = map_batch_results_to_csv(batch_results, exploded_csv, args.output_dir)
    print(f"Done! Labeled CSV saved to {labeled_csv}")

if __name__ == "__main__":
    main()

