import pandas as pd
import re
import argparse
import os

def explode_all_system_utterances_with_all_columns(input_csv, output_dir):
    """
    For each row in the input CSV, create a new row for every system utterance (Agent/System),
    with context, preceding user question, and all original columns, ready for claim extraction.
    Context_String will be a Python-style list of utterance strings.
    Saves the exploded CSV as 'exploded_system.csv' in output_dir.
    """
    output_csv = os.path.join(output_dir, "exploded_system.csv")
    df = pd.read_csv(input_csv)
    system_pattern = re.compile(r'Utterance-(\d+) \((Agent|System)\)')

    all_columns = list(df.columns) + [
        'Turn_Num', 'Context_String', 'Corresponding_User_Question',
        'Selected_Agent_Utterance', 'Selected_Agent_Column'
    ]

    exploded_rows = []

    for idx, row in df.iterrows():
        # Find all system utterance columns for this row
        system_cols = [col for col in df.columns if system_pattern.match(col) and pd.notna(row[col]) and str(row[col]).strip() != '']
        for sys_col in system_cols:
            turn_num = int(system_pattern.match(sys_col).group(1))
            # Gather context: all utterances up to and including this turn
            context = []
            for t in range(turn_num + 1):
                for role in ['User', 'Agent', 'System']:
                    col = f'Utterance-{t} ({role})'
                    if col in df.columns and pd.notna(row[col]) and str(row[col]).strip() != '':
                        context.append(f"{role}: {row[col]}")
            # Format as a Python list of strings
            context_str = '[\n' + ',\n'.join(context) + '\n]'
            # Find preceding user utterance
            user_col = f'Utterance-{turn_num-1} (User)'
            question = row[user_col] if user_col in df.columns and pd.notna(row[user_col]) and str(row[user_col]).strip() != '' else ""
            # The system utterance itself
            answer = row[sys_col]
            # Build new row with all original columns
            new_row = row.to_dict()
            new_row.update({
                'Turn_Num': turn_num,
                'Context_String': context_str,
                'Corresponding_User_Question': question,
                'Selected_Agent_Utterance': answer,
                'Selected_Agent_Column': sys_col,
            })
            exploded_rows.append(new_row)

    exploded_df = pd.DataFrame(exploded_rows)
    # Ensure all columns are present and in the same order
    for col in all_columns:
        if col not in exploded_df.columns:
            exploded_df[col] = ''
    exploded_df = exploded_df[all_columns]

    exploded_df.to_csv(output_csv, index=False)
    print(f"✅ Saved exploded system utterances and original rows (with all columns) to {output_csv}")
    return output_csv


def generate_context_string(exploded_csv, output_dir, seed=42):
    """
    Generates a context string containing conversation history before the selected agent utterance.
    The context includes all user-system exchanges up to but not including the selected utterance.
    Saves the file as 'context_system.csv' in output_dir.
    """
    output_csv_path = os.path.join(output_dir, "context_system.csv")
    df = pd.read_csv(exploded_csv)
    print(f"🔍 Generating context strings from {exploded_csv}")
    print("-" * 60)
    print(f"Original rows: {len(df)}")
    if 'Selected_Agent_Column' not in df.columns:
        print("❌ Selected_Agent_Column not found! Run select_random_agent_utterance first.")
        return None
    context_strings = []
    for idx, row in df.iterrows():
        selected_column = row.get('Selected_Agent_Column', '')
        if not selected_column:
            context_strings.append("")
            continue
        turn_match = re.search(r'Utterance-(\d+)', selected_column)
        if not turn_match:
            context_strings.append("")
            continue
        selected_turn = int(turn_match.group(1))
        context_parts = []
        for turn in range(0, selected_turn - 1, 2):
            user_col = f'Utterance-{turn} (User)'
            agent_col = f'Utterance-{turn + 1} (Agent)'
            if user_col in df.columns and agent_col in df.columns:
                user_utterance = str(row.get(user_col, '')).strip()
                agent_utterance = str(row.get(agent_col, '')).strip()
                if user_utterance and user_utterance != 'nan' and user_utterance != '':
                    if agent_utterance and agent_utterance != 'nan' and agent_utterance != '':
                        context_parts.append(f"User: {user_utterance}")
                        context_parts.append(f"System: {agent_utterance}")
        context_string = "\n\n".join(context_parts)
        if context_string:
            context_string = f"[\n{context_string}\n]"
        else:
            context_string = "[]"
        context_strings.append(context_string)
    df['Context_String'] = context_strings
    df.to_csv(output_csv_path, index=False)
    print(f"💾 CSV with context strings saved to: {output_csv_path}")
    sample_contexts = [ctx for ctx in context_strings if ctx and ctx != "Context: [\n]"]
    if sample_contexts:
        print(f"\n📋 Sample context string (first 200 chars):")
        sample = sample_contexts[0][:200] + "..." if len(sample_contexts[0]) > 200 else sample_contexts[0]
        print(sample)
    return output_csv_path


def preprocess(input_csv, output_dir):
    """
    Runs the full preprocessing pipeline:
    1. Explodes all system utterances with all columns.
    2. Generates context strings for each system utterance.
    3. Merges context strings into the exploded DataFrame and saves a unified CSV.
    """
    print("Exploding all system utterances...")
    exploded_csv_path = explode_all_system_utterances_with_all_columns(input_csv, output_dir)
    print("Generating context strings...")
    context_csv_path = generate_context_string(exploded_csv_path, output_dir)

    # Load both DataFrames
    exploded_df = pd.read_csv(exploded_csv_path)
    context_df = pd.read_csv(context_csv_path)

    # Merge context string column into exploded_df (assume row alignment)
    if 'Context_String' in context_df.columns:
        exploded_df['Context_String'] = context_df['Context_String']

    unified_csv_path = os.path.join(output_dir, 'preprocessed_unified.csv')
    exploded_df.to_csv(unified_csv_path, index=False)
    print(f"Done! Unified CSV saved to {unified_csv_path}")
    return unified_csv_path


def main():
    parser = argparse.ArgumentParser(description="Explode system utterances and generate context strings.")
    parser.add_argument('--input_csv', required=True, help='Path to the input CSV file')
    parser.add_argument('--output_dir', required=True, help='Directory to save all outputs')
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    preprocess(args.input_csv, args.output_dir)

if __name__ == "__main__":
    main()

