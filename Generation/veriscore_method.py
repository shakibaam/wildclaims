import csv
import json
import re
import os
import subprocess
import random
import pandas as pd
import shutil
import argparse
from tqdm import tqdm
from typing import Optional


def create_single_json_obj_from_new_format(row, model_name, prompt_source):
    """Create one JSON object from the new CSV format with Context_String, Corresponding_User_Question, and Selected_Agent_Utterance."""
    
    context_string = str(row.get('Context_String', '')).strip()
    user_question = str(row.get('Corresponding_User_Question', '')).strip()
    agent_response = str(row.get('Selected_Agent_Utterance', '')).strip()
    
    question_text = f"User: {user_question}\nContext: {context_string}"
    
    return {
        "question": question_text,
        "response": agent_response,
        "model": model_name,
        "prompt_source": prompt_source
    }



def batch_generate_jsonl_from_new_format(
    csv_path: str,
    output_dir: str,
    model_name: str = "gpt-4",
    prompt_source: str = "WildChat"
):
    """Generate JSONL files from the new CSV format."""
    random.seed(42)  # For reproducibility
    os.makedirs(output_dir, exist_ok=True)

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        for row_index, row in enumerate(reader):
            conv_hash = row['Conversation_Hash']
            turn_num = row['Turn_Num']
            row_folder = os.path.join(output_dir, f"{conv_hash}")
            os.makedirs(row_folder, exist_ok=True)
            # You must implement this function or import it from your utils
            json_obj = create_single_json_obj_from_new_format(
                row, model_name=model_name, prompt_source=prompt_source
            )
            if json_obj:
                filename = f"{conv_hash}_{turn_num}.jsonl"
                out_path = os.path.join(row_folder, filename)
                with open(out_path, "w", encoding="utf-8") as out_f:
                    out_f.write(json.dumps(json_obj, ensure_ascii=False) + "\n")
                print(f"✅ Processed row {row_index}")
            else:
                print(f"⚠️ Skipping row {row_index}: Could not create JSON object")
    print(f"🎉 All JSONL files saved in: {os.path.abspath(output_dir)}")


def run_veriscore(requests_dir: str, model_name: str = 'gpt-4.1-2025-04-14', veriscore_dir: Optional[str] = None):
    """
    Run VeriScore extraction for all JSONL files in the requests_dir.
    """
    if veriscore_dir is None:
        veriscore_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../VeriScore'))
    # Gather all folders to process
    row_folders = [f for f in os.listdir(requests_dir) if os.path.isdir(os.path.join(requests_dir, f))]
    total_files = 0
    file_paths = []

    # First, collect all jsonl files to get total count for progress bar
    for row_folder in row_folders:
        folder_path = os.path.join(requests_dir, row_folder)
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".jsonl"):
                file_paths.append((folder_path, file_name))
                total_files += 1
    print(total_files)
    # Now process with progress bar
    for folder_path, file_name in tqdm(file_paths, desc="Processing files"):
        folder_path = os.path.abspath(folder_path)
        cmd = [
            "python3", "-m", "veriscore.extract_claims",
            "--data_dir", folder_path,
            "--input_file", file_name,
            "--model_name", model_name
        ]
        print("🚀 Running:", " ".join(cmd))
        subprocess.run(cmd, cwd=veriscore_dir)


def map_veriscore_claims_to_csv(veriscore_dir, original_csv_path, output_csv_path):
    """
    Maps VeriScore claims from JSONL files back to the original CSV rows.
    """
    df = pd.read_csv(original_csv_path)
    print(f"📄 Original CSV has {len(df)} rows")
    claims_mapping = {}
    for root, dirs, files in os.walk(veriscore_dir):
        for file in files:
            if file.endswith('.jsonl'):
                file_path = os.path.join(root, file)
                claim_match = re.search(r'claims_([a-f0-9]+)_(\d+)\.jsonl', file)
                if not claim_match:
                    print(f"⚠️ Could not extract conv_hash and turn_num from filename: {file}")
                    continue
                conv_hash = claim_match.group(1)
                turn_num = int(claim_match.group(2))
                matching_rows = df[(df['conversation_hash'] == conv_hash) & (df['turn_num'] == turn_num)]
                if len(matching_rows) == 0:
                    print(f"⚠️ No matching row found for conv_hash: {conv_hash}, turn_num: {turn_num}")
                    continue
                row_index = matching_rows.index[0]
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            data = json.loads(line.strip())
                            if 'all_claims' in data:
                                claims = data['all_claims']
                                claims_mapping[row_index] = claims
                                print(f"✅ Row {row_index} (conv_hash: {conv_hash}, turn: {turn_num}): Found {len(claims)} claims")
                            else:
                                print(f"⚠️ Row {row_index} (conv_hash: {conv_hash}, turn: {turn_num}): No 'all_claims' key found")
                except Exception as e:
                    print(f"❌ Error reading {file}: {e}")
    print(f"\n📊 Found claims for {len(claims_mapping)} rows")
    df['Factual_Statements'] = df.index.map(claims_mapping)
    rows_with_claims = df['Factual_Statements'].notna().sum()
    print(f"📊 Rows with claims: {rows_with_claims}/{len(df)}")
    na_claims_rows = df[df['Factual_Statements'].isna()]
    if not na_claims_rows.empty:
        print(f"\n📋 Rows with NA claims:")
        for idx, row in na_claims_rows.iterrows():
            print(f"  Row {idx}: conversation_hash={row['Conversation_Hash']}, turn_num={row['Turn_Num']}")
    else:
        print("\n✅ No rows with NA claims.")

    
    def format_claims(claims):
        if claims is None:
            return ""
        if isinstance(claims, list):
            return json.dumps(claims, ensure_ascii=False)
        return str(claims)
    
    df['Factual_Statements'] = df['Factual_Statements'].apply(format_claims)
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False)
    print(f"💾 Mapped CSV saved to: {output_csv_path}")
    return df


def explode_veriscore_claims(csv_path, output_csv_path):
    """
    Explodes the Factual_Statements column into separate rows, one for each claim.
    """
    df = pd.read_csv(csv_path)
    print(f"📄 Loading CSV with {len(df)} rows")
    print(f"📊 Columns: {list(df.columns)}")
    if 'Factual_Statements' not in df.columns:
        print("❌ Factual_Statements column not found!")
        return None
    exploded_rows = []
    for idx, row in df.iterrows():
        claims_str = str(row.get('Factual_Statements', '')).strip()
        if (
            not claims_str
            or claims_str == 'nan'
            or claims_str == ''
            or claims_str == '[]'
        ):
            continue
        try:
            claims = json.loads(claims_str)
            if not claims or len(claims) == 0:
                continue
            for claim_idx, claim in enumerate(claims):
                row_dict = row.to_dict()
                row_dict['Statement_Index'] = claim_idx
                row_dict['Individual_Statement'] = claim
                exploded_rows.append(row_dict)
        except json.JSONDecodeError as e:
            print(f"⚠️ Error parsing claims for row {idx}: {e}")
            continue
    exploded_df = pd.DataFrame(exploded_rows)
    print(f"\n📊 Explosion complete!")
    print(f"📄 Original rows: {len(df)}")
    print(f"📄 Exploded rows: {len(exploded_df)}")
    print(f"📊 Expansion factor: {len(exploded_df)/len(df):.2f}x")
    rows_with_claims = exploded_df['Individual_Statement'].notna() & (exploded_df['Individual_Statement'] != '')
    actual_claim_rows = exploded_df[rows_with_claims]
    print(f"📊 Rows with actual claims: {len(actual_claim_rows)}")
    exploded_df.to_csv(output_csv_path, index=False)
    print(f"\n💾 Exploded CSV saved to: {output_csv_path}")
    return exploded_df


def copy_jsonl_files(src_dir, dst_dir):
    import os
    import shutil
    os.makedirs(dst_dir, exist_ok=True)
    copied = 0
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.jsonl'):
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dst_dir, file)
                print(f"Copying {src_file} -> {dst_file}")
                shutil.copy2(src_file, dst_file)
                os.remove(src_file)  # Delete the source file after copying
                copied += 1
    print(f"Copied and deleted {copied} .jsonl files from {src_dir} to {dst_dir}")


def main():
    parser = argparse.ArgumentParser(description="VeriScore Method Pipeline")
    parser.add_argument('--input_csv', type=str, required=True, help='Input CSV file path')
    parser.add_argument('--output_dir', type=str, required=True, help='Output directory for all results')
    parser.add_argument('--model_name', type=str, default='gpt-4', help='Model name for batch requests (default: gpt-4)')
    parser.add_argument('--veriscore_model', type=str, default='gpt-4.1-2025-04-14', help='Model name for VeriScore extraction (default: gpt-4.1-2025-04-14)')
    parser.add_argument('--veriscore_dir', type=str, default='VeriScore', help='Path to VeriScore directory (default: VeriScore')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    requests_dir = os.path.join(args.output_dir, 'batch_requests')
    mapped_csv = os.path.join(args.output_dir, 'veriscore_with_factual_statements.csv')
    exploded_csv = os.path.join(args.output_dir, 'veriscore_exploded_statements.csv')

    print(f"\n[1/4] Generating batch requests JSONL files...")
    batch_generate_jsonl_from_new_format(
        csv_path=args.input_csv,
        output_dir=requests_dir,
        model_name=args.model_name
    )

    print(f"\n[2/4] Running VeriScore extraction...")
    run_veriscore(requests_dir, model_name=args.veriscore_model, veriscore_dir=args.veriscore_dir)

    print(f"\n[2.5/4] Copying VeriScore output files to output directory...")
    copy_jsonl_files(args.veriscore_dir if args.veriscore_dir else requests_dir, args.output_dir)

    print(f"\n[3/4] Mapping VeriScore claims to CSV...")
    map_veriscore_claims_to_csv(
        veriscore_dir=args.output_dir,
        original_csv_path=args.input_csv,
        output_csv_path=mapped_csv
    )

    print(f"\n[4/4] Exploding claims to rows...")
    explode_veriscore_claims(
        csv_path=mapped_csv,
        output_csv_path=exploded_csv
    )
    print(f"\n🎉 Pipeline complete! All outputs saved in: {args.output_dir}")


if __name__ == "__main__":
    main()