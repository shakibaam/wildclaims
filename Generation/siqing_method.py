from openai_batch_utils import submit_openai_batch, get_batch_statuses_from_metadata, fetch_batch_output

import os
import pandas as pd
import json
from openai import OpenAI
import time

def make_siqing_batch_request_file(input_csv_path, output_dir, model_name="gpt-4.1-2025-04-14"):
    output_jsonl_path = os.path.join(output_dir, "siqing_batch_requests.jsonl")
    df = pd.read_csv(input_csv_path)
    print(f"📄 Creating SIQing batch request file from {input_csv_path}")
    print("-" * 60)
    print(f"Total rows: {len(df)}")
    required_columns = ['Context_String', 'Corresponding_User_Question', 'Selected_Agent_Utterance']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"❌ Missing required columns: {missing_columns}")
        print("Make sure to generate_context_string first by running Preprocess_Files_For_Pipeline.py.")
        return None
    non_empty_rows = 0
    with open(output_jsonl_path, "w", encoding="utf-8") as f:
        for i, row in df.iterrows():
            context = str(row.get('Context_String', '')).strip()
            question = str(row.get('Corresponding_User_Question', '')).strip()
            proposed_answer = str(row.get('Selected_Agent_Utterance', '')).strip()
            non_empty_rows += 1
            prompt = f"""I want you to act as a language expert. Your task is given a question\nand a proposed answer, extract concise and relevant factual\nstatements from the proposed answer. Include only statements that\nhave a truth value and are worth validating, and ignore subjective\nclaims. You should generate a bullet list of statements that are\npotentially true or false based on the question and proposed answer.\nPlease only reply with the bullet list and nothing else.\n\nContext: {context}\nQuestion: {question}\nProposed Answer: {proposed_answer}\n\nOutput must be pythonic list format."""
            conversation_hash = str(row.get('Conversation_Hash', '')).strip()
            turn_num = str(row.get('Turn_Num', '')).strip()
            custom_id = f'{conversation_hash}_{turn_num}'
            request_obj = {
                "custom_id": custom_id,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model_name,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0
                }
            }
            f.write(json.dumps(request_obj, ensure_ascii=False) + "\n")
    print(f"✅ Batch request file created!")
    print(f"📊 Non-empty rows processed: {non_empty_rows}/{len(df)}")
    print(f"📊 Success rate: {(non_empty_rows/len(df))*100:.1f}%")
    print(f"💾 Saved to: {output_jsonl_path}")
    return output_jsonl_path


def map_siqing_results_to_csv(batch_results_path, input_csv_path, output_dir):
    output_csv_path = os.path.join(output_dir, "siqing_with_factual_statements.csv")
    df = pd.read_csv(input_csv_path)
    print(f"Original CSV has {len(df)} rows")
    results_mapping = {}
    batch_results_count = 0
    with open(batch_results_path, 'r', encoding='utf-8') as f:
        for line in f:
            batch_results_count += 1
            result = json.loads(line.strip())
            custom_id = result.get('custom_id', '')
            if 'response' in result and 'body' in result['response']:
                try:
                    factual_statements = result['response']['body']['choices'][0]['message']['content']
                    results_mapping[custom_id] = factual_statements
                except (KeyError, IndexError):
                    print(f"Warning: Could not extract factual statements from result for custom_id: {custom_id}")
                    results_mapping[custom_id] = "ERROR"
    print(f"Batch results file has {batch_results_count} lines")
    print(f"Successfully extracted {len(results_mapping)} factual statement sets")
    df['custom_id'] = df['Conversation_Hash'] + '_' + df['Turn_Num'].astype(str)
    df['Factual_Statements'] = df['custom_id'].map(results_mapping)
    df_with_statements = df[df['Factual_Statements'].notna() & (df['Factual_Statements'] != '')]
    print(f"Rows with factual statements: {len(df_with_statements)}")
    df.to_csv(output_csv_path, index=False)
    print(f"✅ Mapped CSV saved to: {output_csv_path}")
    print(f"Original rows: {len(df)}")
    print(f"Final rows with factual statements: {len(df)}")
    return output_csv_path


def explode_siqing_factual_statements(csv_path, output_dir):
    output_csv_path = os.path.join(output_dir, "siqing_exploded_statements.csv")
    df = pd.read_csv(csv_path)
    print(f"📄 Loading SIQing CSV with {len(df)} rows")
    print(f"📊 Columns: {list(df.columns)}")
    if 'Factual_Statements' not in df.columns:
        print("❌ Factual_Statements column not found!")
        return None
    exploded_rows = []
    for idx, row in df.iterrows():
        statements_str = str(row.get('Factual_Statements', '')).strip()
        if (
            not statements_str
            or statements_str == 'nan'
            or statements_str == ''
            or statements_str == 'ERROR'
            or statements_str == '[]'
        ):
            continue
        try:
            try:
                statements = json.loads(statements_str)
                if isinstance(statements, list):
                    if not statements:
                        continue
                else:
                    statements = [statements_str]
            except json.JSONDecodeError:
                if statements_str.startswith('[') and statements_str.endswith(']'):
                    try:
                        import ast
                        statements = ast.literal_eval(statements_str)
                        if not isinstance(statements, list) or not statements:
                            continue
                    except:
                        continue
                else:
                    if '\n' in statements_str:
                        statements = [s.strip() for s in statements_str.split('\n') if s.strip()]
                    elif '•' in statements_str:
                        statements = [s.strip() for s in statements_str.split('•') if s.strip()]
                    elif '-' in statements_str:
                        statements = [s.strip() for s in statements_str.split('-') if s.strip()]
                    else:
                        statements = [statements_str]
                    if not statements:
                        continue
            for statement_idx, statement in enumerate(statements):
                row_dict = row.to_dict()
                row_dict['Statement_Index'] = statement_idx
                row_dict['Individual_Statement'] = statement
                exploded_rows.append(row_dict)
        except Exception as e:
            print(f"⚠️ Error parsing statements for row {idx}: {e}")
            continue
    exploded_df = pd.DataFrame(exploded_rows)
    print(f"\n📊 Explosion complete!")
    print(f"📄 Original rows: {len(df)}")
    print(f"📄 Exploded rows: {len(exploded_df)}")
    print(f"📊 Expansion factor: {len(exploded_df)/len(df):.2f}x")
    rows_with_statements = exploded_df['Individual_Statement'].notna() & (exploded_df['Individual_Statement'] != '')
    actual_statement_rows = exploded_df[rows_with_statements]
    print(f"📊 Rows with actual statements: {len(actual_statement_rows)}")
    exploded_df.to_csv(output_csv_path, index=False)
    print(f"\n💾 Exploded CSV saved to: {output_csv_path}")
    return output_csv_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SIQing factual statement extraction pipeline.")
    parser.add_argument('--input_csv', required=True, help='Path to the input CSV file')
    parser.add_argument('--output_dir', required=True, help='Directory to save all outputs')
    parser.add_argument('--model_name', default="gpt-4.1-2025-04-14", help='OpenAI model to use')
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    metadata_file = os.path.join(args.output_dir, "siqing_batch_metadata.jsonl")
    results_file = os.path.join(args.output_dir, "siqing_batch_results.jsonl")

    if os.path.exists(metadata_file):
        print("Batch metadata found.")
        if os.path.exists(results_file):
            print("Results found. Mapping and exploding...")
            mapped_csv = map_siqing_results_to_csv(results_file, args.input_csv, args.output_dir)
            exploded_csv = explode_siqing_factual_statements(mapped_csv, args.output_dir)
            print(f"Done! Exploded CSV saved to {exploded_csv}")
        else:
            print("Checking batch status...")
            statuses = get_batch_statuses_from_metadata(metadata_file)
            if statuses and statuses[0]['status'] == 'completed':
                print("Fetching batch output...")
                fetch_batch_output(metadata_file, results_file)
                mapped_csv = map_siqing_results_to_csv(results_file, args.input_csv, args.output_dir)
                exploded_csv = explode_siqing_factual_statements(mapped_csv, args.output_dir)
                print(f"Done! Exploded CSV saved to {exploded_csv}")
            else:
                print(f"Batch not completed yet. Status: {statuses[0]['status'] if statuses else 'Unknown'}")
                print("You may need to rerun this script later to process results.")
    else:
        print("No batch metadata found. Submitting new batch...")
        batch_jsonl = make_siqing_batch_request_file(args.input_csv, args.output_dir, model_name=args.model_name)
        submit_openai_batch(batch_jsonl, metadata_file, description="SIQing factual statement extraction")
        print("Batch submitted. Please rerun this script later to fetch results.")

if __name__ == "__main__":
    main()
  
