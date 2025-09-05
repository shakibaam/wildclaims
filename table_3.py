#!/usr/bin/env python3
"""
Script to analyze array columns in CSV files and human annotation data.
"""

import csv
import ast
from collections import defaultdict
import math

def parse_array_string(array_str):
    """Parse array string representation to actual list."""
    if not array_str or array_str.strip() == '' or array_str == 'nan':
        return []
    try:
        # Remove any extra whitespace and parse as Python literal
        return ast.literal_eval(array_str.strip())
    except (ValueError, SyntaxError):
        # If parsing fails, return empty list
        return []

def calculate_kappa(observed_agreement, expected_agreement):
    """Calculate Cohen's kappa coefficient."""
    if expected_agreement == 1:
        return 1.0  # Perfect agreement
    return (observed_agreement - expected_agreement) / (1 - expected_agreement)

def main():
    csv_file_path = 'Annotations/3k_Results.csv'
    
    print("Loading data from 3k_Results.csv...")
    
    # Initialize data structures
    siqing_hassan_arrays = []
    veriscore_hassan_arrays = []
    conversation_data = defaultdict(lambda: {'siqing_hassan': [], 'veriscore_hassan': []})
    total_rows = 0
    
    # Read the CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            total_rows += 1
            
            # Extract data
            conversation_hash = row['conversation_hash']
            siqing_hassan_str = row['siqing_hassan']
            veriscore_hassan_str = row['veriscore_hassan']
            
            # Parse arrays
            siqing_hassan_array = parse_array_string(siqing_hassan_str)
            veriscore_hassan_array = parse_array_string(veriscore_hassan_str)
            
            # Store arrays
            siqing_hassan_arrays.append(siqing_hassan_array)
            veriscore_hassan_arrays.append(veriscore_hassan_array)
            
            # Store by conversation
            conversation_data[conversation_hash]['siqing_hassan'].append(siqing_hassan_array)
            conversation_data[conversation_hash]['veriscore_hassan'].append(veriscore_hassan_array)
    
    print(f"Total rows in dataset: {total_rows}")
    print()
    
    # 1. Total number of elements in siqing_hassan arrays
    total_siqing_hassan_elements = sum(len(arr) for arr in siqing_hassan_arrays)
    print(f"1. Total number of elements in siqing_hassan arrays: {total_siqing_hassan_elements}")
    
    # 2. Total number of elements in veriscore_hassan arrays
    total_veriscore_hassan_elements = sum(len(arr) for arr in veriscore_hassan_arrays)
    print(f"2. Total number of elements in veriscore_hassan arrays: {total_veriscore_hassan_elements}")
    print()
    
    # 3. Average number of elements in siqing_hassan arrays
    avg_siqing_hassan_elements = total_siqing_hassan_elements / total_rows if total_rows > 0 else 0
    print(f"3. Average number of elements in siqing_hassan arrays: {avg_siqing_hassan_elements:.2f}")
    
    # 4. Average number of elements in veriscore_hassan arrays
    avg_veriscore_hassan_elements = total_veriscore_hassan_elements / total_rows if total_rows > 0 else 0
    print(f"4. Average number of elements in veriscore_hassan arrays: {avg_veriscore_hassan_elements:.2f}")
    print()
    
    # 5. Average number of elements in siqing_hassan arrays per conversation
    siqing_elements_per_conversation = []
    for conv_hash, data in conversation_data.items():
        total_elements = sum(len(arr) for arr in data['siqing_hassan'])
        siqing_elements_per_conversation.append(total_elements)
    
    avg_siqing_elements_per_conversation = sum(siqing_elements_per_conversation) / len(siqing_elements_per_conversation) if siqing_elements_per_conversation else 0
    print(f"5. Average number of elements in siqing_hassan arrays per conversation: {avg_siqing_elements_per_conversation:.2f}")
    
    # 6. Average number of elements in veriscore_hassan arrays per conversation
    veriscore_elements_per_conversation = []
    for conv_hash, data in conversation_data.items():
        total_elements = sum(len(arr) for arr in data['veriscore_hassan'])
        veriscore_elements_per_conversation.append(total_elements)
    
    avg_veriscore_elements_per_conversation = sum(veriscore_elements_per_conversation) / len(veriscore_elements_per_conversation) if veriscore_elements_per_conversation else 0
    print(f"6. Average number of elements in veriscore_hassan arrays per conversation: {avg_veriscore_elements_per_conversation:.2f}")
    print()
    
    # 7. Percentage of rows with non-empty siqing_hassan arrays
    non_empty_siqing_hassan = sum(1 for arr in siqing_hassan_arrays if len(arr) > 0)
    pct_non_empty_siqing_hassan = (non_empty_siqing_hassan / total_rows) * 100 if total_rows > 0 else 0
    print(f"7. Percentage of rows with non-empty siqing_hassan arrays: {pct_non_empty_siqing_hassan:.2f}%")
    print(f"   - Non-empty rows: {non_empty_siqing_hassan} out of {total_rows}")
    
    # 8. Percentage of rows with non-empty veriscore_hassan arrays
    non_empty_veriscore_hassan = sum(1 for arr in veriscore_hassan_arrays if len(arr) > 0)
    pct_non_empty_veriscore_hassan = (non_empty_veriscore_hassan / total_rows) * 100 if total_rows > 0 else 0
    print(f"8. Percentage of rows with non-empty veriscore_hassan arrays: {pct_non_empty_veriscore_hassan:.2f}%")
    print(f"   - Non-empty rows: {non_empty_veriscore_hassan} out of {total_rows}")
    print()
    
    # 9. Group by conversation_hash: Percentage of conversations with non-empty siqing_hassan
    conversations_with_siqing_hassan = 0
    total_conversations = len(conversation_data)
    
    for conv_hash, data in conversation_data.items():
        # Check if any turn in this conversation has non-empty siqing_hassan array
        has_non_empty_siqing = any(len(arr) > 0 for arr in data['siqing_hassan'])
        if has_non_empty_siqing:
            conversations_with_siqing_hassan += 1
    
    pct_conversations_siqing_hassan = (conversations_with_siqing_hassan / total_conversations) * 100 if total_conversations > 0 else 0
    print(f"9. Percentage of conversations with non-empty siqing_hassan arrays: {pct_conversations_siqing_hassan:.2f}%")
    print(f"   - Conversations with non-empty siqing_hassan: {conversations_with_siqing_hassan} out of {total_conversations}")
    
    # 10. Group by conversation_hash: Percentage of conversations with non-empty veriscore_hassan
    conversations_with_veriscore_hassan = 0
    
    for conv_hash, data in conversation_data.items():
        # Check if any turn in this conversation has non-empty veriscore_hassan array
        has_non_empty_veriscore = any(len(arr) > 0 for arr in data['veriscore_hassan'])
        if has_non_empty_veriscore:
            conversations_with_veriscore_hassan += 1
    
    pct_conversations_veriscore_hassan = (conversations_with_veriscore_hassan / total_conversations) * 100 if total_conversations > 0 else 0
    print(f"10. Percentage of conversations with non-empty veriscore_hassan arrays: {pct_conversations_veriscore_hassan:.2f}%")
    print(f"   - Conversations with non-empty veriscore_hassan: {conversations_with_veriscore_hassan} out of {total_conversations}")
    print()
    

if __name__ == "__main__":
    main()
