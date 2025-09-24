import os
import sys
os.environ['PYTHONPATH'] = os.getcwd()

import re
import json
from typing import List
import pandas as pd
import openai
import os
from openai import OpenAI
import numpy as np
import argparse

from openai_batch_utils import submit_openai_batch, get_batch_statuses_from_metadata, fetch_batch_output, split_jsonl_file


def make_claim_batch_request_file(
    input_csv_path, output_jsonl_path, prompt_mode='Majer', model_name="gpt-4.1-2025-04-14"
):
    """
    Creates a batch request file for SIQing claims for OpenAI batch API.
    Each request uses Individual_Statement as the claim and Context_String as the context.
    custom_id is set to the conversation_hash column.
    """
    df = pd.read_csv(input_csv_path)
    required_columns = ["Individual_Statement", "Context_String", "Conversation_Hash", "Statement_Index"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    with open(output_jsonl_path, "w", encoding="utf-8") as f:
        for i, row in df.iterrows():
            claim = str(row["Individual_Statement"]).strip()
            context_str = str(row["Context_String"]).strip()
            conversation_hash = str(row["Conversation_Hash"]).strip()
            turn_num = str(row["Turn_Num"]).strip()
            statement_index = str(row["Statement_Index"]).strip() if "Statement_Index" in row else ""
            if not claim or not context_str or not conversation_hash or not statement_index:
                continue
            if prompt_mode == "Majer":
                prompt = (
                    "Classify the extracted claim from the conversation between a human and a language model into one of the following categories:\n"
                    "- NFS: Non-Factual Sentence\n"
                    "- UFS: Unimportant Factual Sentence\n"
                    "- CFS: Check-worthy Factual Sentence\n\n"
                    "Respond with only one label: NFS, UFS, or CFS. Do not provide any explanation.\n"
                    f"Claim:\n{claim}\n"
                    f"Context:{context_str}"
                )
            elif prompt_mode == "Hassan":
                prompt = (
                    "\nQuestion: Will the user be interested in knowing whether (part of) this sentence is true or false?\n"
                    "- NFS: There is no factual claim in this sentence.\n"
                    "- UFS: There is a factual claim but it is unimportant.\n"
                    "- CFS: There is an important factual claim.\n\n"
                    "Respond with only one label: NFS, UFS, or CFS. Do not provide any explanation.\n"
                    "Sentence:\n"
                    f"{claim}\n\n"
                    "Context: \n"
                    f"{context_str}\n"
                )
            else:
                raise ValueError(f"Unknown prompt_mode: {prompt_mode}")
            request_obj = {
                "custom_id": f"{conversation_hash}_{turn_num}_{statement_index}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0,
                    "max_tokens": 1000
                }
            }
            f.write(json.dumps(request_obj, ensure_ascii=False) + "\n")
    print(f"✅ CW batch request file saved to: {output_jsonl_path}")


def add_CW_predictions_to_csv(
    original_csv_path: str,
    batch_results_jsonl_path: str,
    output_csv_path: str,
    new_column_name: str = "Majer"
):
    """
    Maps OpenAI batch results from a JSONL file to the original CSV using conversation_hash and Statement_Index,
    and adds a new column with the prediction.
    """
    df = pd.read_csv(original_csv_path)
    df['Statement_Index'] = df['Statement_Index'].astype(str)
    df['Conversation_Hash'] = df['Conversation_Hash'].astype(str)
    df['Turn_Num'] =  df['Turn_Num'].astype(str)
    predictions = {}
    with open(batch_results_jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            custom_id = item.get("custom_id")
            if not custom_id or "response" not in item:
                continue
            parts = custom_id.split("_")
            if len(parts) < 3:
                continue
            statement_index = parts[-1]
            turn_num = parts[-2]
            conversation_hash = "_".join(parts[:-2])
            answer = (
                item["response"]["body"]["choices"][0]["message"]["content"].strip()
                if "body" in item["response"] and "choices" in item["response"]["body"]
                else ""
            )
            predictions[(conversation_hash, turn_num, statement_index)] = answer
    df[new_column_name] = [
        predictions.get((str(row['Conversation_Hash']), str(row['Turn_Num']), str(row['Statement_Index'])), "")
        for _, row in df.iterrows()
    ]
    num_predicted = (df[new_column_name] != "").sum()
    num_empty = (df[new_column_name] == "").sum()
    print(f"Number of rows with a prediction in '{new_column_name}': {num_predicted}")
    print(f"Number of rows with EMPTY value in '{new_column_name}': {num_empty}")
    df.to_csv(output_csv_path, index=False, encoding='utf-8')
    print(f"✅ Updated CSV with '{new_column_name}' saved to: {output_csv_path}")


def main():
    parser = argparse.ArgumentParser(description="SIQing Claim Checkworthiness Pipeline")
    parser.add_argument('--input_csv', type=str, required=True, help='Input CSV file (exploded claims)')
    parser.add_argument('--output_dir', type=str, required=False, help='Output directory for all results (defaults to input CSV directory)')
    parser.add_argument('--model_name', type=str, default='gpt-4.1-2025-04-14', help='OpenAI model name (default: gpt-4.1-2025-04-14)')
    parser.add_argument('--prompt_mode', type=str, default='Majer', choices=['Majer', 'Hassan'], help='Prompt mode (default: Majer)')
    parser.add_argument('--column_name', type=str, default='Majer', help='Column name for predictions in output CSV (default: Majer)')
    args = parser.parse_args()

    # Use input CSV directory as default output directory if not specified
    output_dir = args.output_dir if args.output_dir else os.path.dirname(args.input_csv)
    print(f"📁 Using output directory: {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    batch_requests_path = os.path.join(output_dir, f'batch_requests_CW_{args.column_name}.jsonl')
    batch_metadata_path = os.path.join(output_dir, f'batch_metadata_CW_{args.column_name}.jsonl')
    batch_results_path = os.path.join(output_dir, f'batch_results_CW_{args.column_name}.jsonl')

    if os.path.exists(batch_metadata_path):
        print("Batch metadata found.")
        if os.path.exists(batch_results_path):
            print("Results found. Mapping predictions to original CSV...")
            add_CW_predictions_to_csv(
                original_csv_path=args.input_csv,
                batch_results_jsonl_path=batch_results_path,
                output_csv_path=args.input_csv,
                new_column_name=args.column_name
            )
            print(f"\n🎉 Mapping complete! All outputs saved in: {output_dir}")
        else:
            print("Checking batch status...")
            statuses = get_batch_statuses_from_metadata(batch_metadata_path)
            if statuses and statuses[0]['status'] == 'completed':
                print("Fetching batch results from OpenAI...")
                fetch_batch_output(
                    metadata_path=batch_metadata_path,
                    save_path=batch_results_path
                )
                print("Results fetched. Mapping predictions to original CSV...")
                add_CW_predictions_to_csv(
                    original_csv_path=args.input_csv,
                    batch_results_jsonl_path=batch_results_path,
                    output_csv_path=args.input_csv,
                    new_column_name=args.column_name
                )
                print(f"\n🎉 Mapping complete! All outputs saved in: {output_dir}")
            else:
                print(f"Batch not completed yet. Status: {statuses[0]['status'] if statuses else 'Unknown'}")
                print("You may need to rerun this script later to process results.")
    else:
        print("No batch metadata found. Creating and submitting new batch...")
        print(f"\n[1/4] Creating batch request JSONL...")
        make_claim_batch_request_file(
            input_csv_path=args.input_csv,
            output_jsonl_path=batch_requests_path,
            prompt_mode=args.prompt_mode,
            model_name=args.model_name
        )
        print(f"\n[2/4] Submitting batch to OpenAI...")
        submit_openai_batch(
            batch_requests_path,
            metadata_path=batch_metadata_path
        )
        print("Batch submitted. Please rerun this script later to fetch results.")


if __name__ == "__main__":
    main()




