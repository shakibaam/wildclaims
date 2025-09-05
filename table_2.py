#!/usr/bin/env python3
"""
Script to analyze the 3k_Results.csv file and compute various statistics.
"""

import pandas as pd
import numpy as np

def count_words(text):
    """Count words in a text string, handling NaN values."""
    if pd.isna(text) or text == '':
        return 0
    return len(str(text).split())

def main():
    # Read the CSV file
    print("Loading data from 3k_Results.csv...")
    df = pd.read_csv('Annotations/3k_Results.csv')
    
    print(f"#Utterances: {len(df)}")
    # print(f"Columns: {list(df.columns)}")
    print()
    
    # 1. Number of unique conversation_hash values
    unique_conversations = df['conversation_hash'].nunique()
    print(f"1. Number of unique conversation_hash values: {unique_conversations}")
    print()
    
    # 2. Percentage of turn_num = 1 vs >1
    total_rows = len(df)
    turn_num_1 = len(df[df['turn_num'] == 1])
    turn_num_gt_1 = len(df[df['turn_num'] > 1])
    
    pct_turn_1 = (turn_num_1 / total_rows) * 100
    pct_turn_gt_1 = (turn_num_gt_1 / total_rows) * 100
    
    print(f"2. Turn number distribution:")
    print(f"   - turn_num = 1: {turn_num_1} rows ({pct_turn_1:.2f}%)")
    print(f"   - turn_num > 1: {turn_num_gt_1} rows ({pct_turn_gt_1:.2f}%)")
    print()
    
    # 3. Group by conversation_hash and compute average turn_num
    avg_turn_by_conversation = df.groupby('conversation_hash')['turn_num'].mean()
    overall_avg_turn = avg_turn_by_conversation.mean()
    
    print(f"3. Average turn_num by conversation:")
    print(f"   - Overall average turn_num: {overall_avg_turn:.2f}")
    print()
    
    # 4. Compute average words in Corresponding_User_Question
    df['user_question_word_count'] = df['Corresponding_User_Question'].apply(count_words)
    avg_words_user_question = df['user_question_word_count'].mean()
    
    print(f"4. Average words in Corresponding_User_Question:")
    print(f"   - Average words: {avg_words_user_question:.2f}")
    print()
    
    # 5. Compute average words in Selected_Agent_Utterance
    df['agent_utterance_word_count'] = df['Selected_Agent_Utterance'].apply(count_words)
    avg_words_agent_utterance = df['agent_utterance_word_count'].mean()
    
    print(f"5. Average words in Selected_Agent_Utterance:")
    print(f"   - Average words: {avg_words_agent_utterance:.2f}")
    print()
    
    # 6. Task classification distribution
    task_classification_counts = df['task_classification'].value_counts()
    total_classifications = len(df)
    
    print(f"6. Task classification distribution:")
    print(f"   - Total classifications: {total_classifications}")
    print(f"   - Unique task types: {len(task_classification_counts)}")
    print()
    
    print("   Task classification breakdown:")
    for task_type, count in task_classification_counts.items():
        percentage = (count / total_classifications) * 100
        print(f"   - {task_type}: {count} ({percentage:.2f}%)")
    print()
    


if __name__ == "__main__":
    main()
