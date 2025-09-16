#!/usr/bin/env python3
"""
Script to analyze the 3k_Results.csv file and compute various statistics.
"""

import csv
from collections import defaultdict, Counter

def count_words(text):
    """Count words in a text string, handling empty/None values."""
    if not text or text == '' or text == 'nan':
        return 0
    return len(str(text).split())

def main():
    # Read the CSV file
    print("Loading data from run_analysis.csv...")
    
    # Initialize data structures
    conversation_data = defaultdict(list)
    task_classification_counts = Counter()
    user_question_word_counts = []
    agent_utterance_word_counts = []
    total_rows = 0
    
    # Read the CSV file
    with open('../Annotations/run_analysis.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            total_rows += 1
            
            # Extract data
            conversation_hash = row['conversation_hash']
            turn_num = row['turn_num']
            user_question = row['Corresponding_User_Question']
            agent_utterance = row['Selected_Agent_Utterance']
            task_classification = row['task_classification']
            
            # Convert turn_num to int, handling any non-numeric values
            try:
                turn_num = int(turn_num)
            except (ValueError, TypeError):
                continue  # Skip rows with invalid turn_num
            
            # Store data
            conversation_data[conversation_hash].append(turn_num)
            task_classification_counts[task_classification] += 1
            
            # Count words
            user_question_word_counts.append(count_words(user_question))
            agent_utterance_word_counts.append(count_words(agent_utterance))
    
    print(f"#Utterances: {total_rows}")
    print()
    
    # 1. Number of unique conversation_hash values
    unique_conversations = len(conversation_data)
    print(f"1. Number of unique conversation_hash values: {unique_conversations}")
    print()
    
    # 2. Percentage of single-turn vs multi-turn conversations
    single_turn_conversations = 0
    multi_turn_conversations = 0
    
    for conversation_hash, turns in conversation_data.items():
        if len(turns) == 1:
            single_turn_conversations += 1
        else:
            multi_turn_conversations += 1
    
    total_conversations = len(conversation_data)
    
    pct_single_turn = (single_turn_conversations / total_conversations) * 100 if total_conversations > 0 else 0
    pct_multi_turn = (multi_turn_conversations / total_conversations) * 100 if total_conversations > 0 else 0
    
    print(f"2. Turn number distribution:")
    print(f"   - Single-turn conversations: {single_turn_conversations} ({pct_single_turn:.2f}%)")
    print(f"   - Multi-turn conversations: {multi_turn_conversations} ({pct_multi_turn:.2f}%)")
    print()
    
    # 3. Group by conversation_hash and compute average turn_num
    avg_turns_per_conversation = []
    for conversation_hash, turns in conversation_data.items():
        if turns:
            avg_turns_per_conversation.append(sum(turns) / len(turns))
    
    overall_avg_turn = sum(avg_turns_per_conversation) / len(avg_turns_per_conversation) if avg_turns_per_conversation else 0
    
    print(f"3. Average turn_num by conversation:")
    print(f"   - Overall average turn_num: {overall_avg_turn:.2f}")
    print()
    
    # 4. Compute average words in Corresponding_User_Question
    avg_words_user_question = sum(user_question_word_counts) / len(user_question_word_counts) if user_question_word_counts else 0
    
    print(f"4. Average words in Corresponding_User_Question:")
    print(f"   - Average words: {avg_words_user_question:.2f}")
    print()
    
    # 5. Compute average words in Selected_Agent_Utterance
    avg_words_agent_utterance = sum(agent_utterance_word_counts) / len(agent_utterance_word_counts) if agent_utterance_word_counts else 0
    
    print(f"5. Average words in Selected_Agent_Utterance:")
    print(f"   - Average words: {avg_words_agent_utterance:.2f}")
    print()
    
    # 6. Task classification distribution
    total_classifications = len(task_classification_counts)
    
    print(f"6. Task classification distribution:")
    print(f"   - Total classifications: {sum(task_classification_counts.values())}")
    print(f"   - Unique task types: {total_classifications}")
    print()
    
    print("   Task classification breakdown:")
    for task_type, count in task_classification_counts.most_common():
        percentage = (count / sum(task_classification_counts.values())) * 100
        print(f"   - {task_type}: {count} ({percentage:.2f}%)")
    print()
    


if __name__ == "__main__":
    main()
