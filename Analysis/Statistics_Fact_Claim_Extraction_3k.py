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
    csv_file_path = '../Annotations/analysis.csv'
    
    print("Loading data from analysis.csv...")
    
    # Initialize data structures
    FHuo_hassan_arrays = []
    FSong_hassan_arrays = []
    conversation_data = defaultdict(lambda: {'FHuo_Hassan': [], 'FSong_Hassan': []})
    total_rows = 0
    
    # Read the CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            total_rows += 1
            
            # Extract data
            conversation_hash = row['Conversation_Hash']
            FHuo_hassan_str = row['FHuo_Hassan']
            FSong_hassan_str = row['FSong_Hassan']
            
            # Parse arrays
            FHuo_hassan_array = parse_array_string(FHuo_hassan_str)
            FSong_hassan_array = parse_array_string(FSong_hassan_str)
            
            # Store arrays
            FHuo_hassan_arrays.append(FHuo_hassan_array)
            FSong_hassan_arrays.append(FSong_hassan_array)
            
            # Store by conversation
            conversation_data[conversation_hash]['FHuo_Hassan'].append(FHuo_hassan_array)
            conversation_data[conversation_hash]['FSong_Hassan'].append(FSong_hassan_array)
    
    print(f"Total rows in dataset: {total_rows}")
    print()
    
    # 1. Total number of elements in FHou_hassan arrays
    total_FHuo_hassan_elements = sum(len(arr) for arr in FHuo_hassan_arrays)
    print(f"1. Total number of elements in FHuo_hassan arrays: {total_FHuo_hassan_elements}")
    
    # 2. Total number of elements in FSong_hassan arrays
    total_FSong_hassan_elements = sum(len(arr) for arr in FSong_hassan_arrays)
    print(f"2. Total number of elements in FSong_hassan arrays: {total_FSong_hassan_elements}")
    print()
    
    # 3. Average number of elements in FHou_hassan arrays
    avg_FHuo_hassan_elements = total_FHuo_hassan_elements / total_rows if total_rows > 0 else 0
    print(f"3. Average number of elements in FHuo_hassan arrays: {avg_FHuo_hassan_elements:.2f}")
    
    # 4. Average number of elements in FSong_hassan arrays
    avg_FSong_hassan_elements = total_FSong_hassan_elements / total_rows if total_rows > 0 else 0
    print(f"4. Average number of elements in FSong_hassan arrays: {avg_FSong_hassan_elements:.2f}")
    print()
    
    # 5. Average number of elements in FHou_hassan arrays per conversation
    FHuo_elements_per_conversation = []
    for conv_hash, data in conversation_data.items():
        total_elements = sum(len(arr) for arr in data['FHuo_Hassan'])
        FHuo_elements_per_conversation.append(total_elements)
    
    avg_FHuo_elements_per_conversation = sum(FHuo_elements_per_conversation) / len(FHuo_elements_per_conversation) if FHuo_elements_per_conversation else 0
    print(f"5. Average number of elements in FHuo_hassan arrays per conversation: {avg_FHuo_elements_per_conversation:.2f}")
    
    # 6. Average number of elements in FSong_hassan arrays per conversation
    FSong_elements_per_conversation = []
    for conv_hash, data in conversation_data.items():
        total_elements = sum(len(arr) for arr in data['FSong_Hassan'])
        FSong_elements_per_conversation.append(total_elements)
    
    avg_FSong_elements_per_conversation = sum(FSong_elements_per_conversation) / len(FSong_elements_per_conversation) if FSong_elements_per_conversation else 0
    print(f"6. Average number of elements in FSong_hassan arrays per conversation: {avg_FSong_elements_per_conversation:.2f}")
    print()
    
    # 7. Percentage of rows with non-empty FHuo_hassan arrays
    non_empty_FHuo_hassan = sum(1 for arr in FHuo_hassan_arrays if len(arr) > 0)
    pct_non_empty_FHuo_hassan = (non_empty_FHuo_hassan / total_rows) * 100 if total_rows > 0 else 0
    print(f"7. Percentage of rows with non-empty FHuo_hassan arrays: {pct_non_empty_FHuo_hassan:.2f}%")
    print(f"   - Non-empty rows: {non_empty_FHuo_hassan} out of {total_rows}")
    
    # 8. Percentage of rows with non-empty FSong_hassan arrays
    non_empty_FSong_hassan = sum(1 for arr in FSong_hassan_arrays if len(arr) > 0)
    pct_non_empty_FSong_hassan = (non_empty_FSong_hassan / total_rows) * 100 if total_rows > 0 else 0
    print(f"8. Percentage of rows with non-empty FSong_hassan arrays: {pct_non_empty_FSong_hassan:.2f}%")
    print(f"   - Non-empty rows: {non_empty_FSong_hassan} out of {total_rows}")
    print()
    
    # 9. Group by conversation_hash: Percentage of conversations with non-empty FHuo_hassan
    conversations_with_FHuo_hassan = 0
    total_conversations = len(conversation_data)
    
    for conv_hash, data in conversation_data.items():
        # Check if any turn in this conversation has non-empty FHou_hassan array
        has_non_empty_FHuo = any(len(arr) > 0 for arr in data['FHuo_Hassan'])
        if has_non_empty_FHuo:
            conversations_with_FHuo_hassan += 1
    
    pct_conversations_FHuo_hassan = (conversations_with_FHuo_hassan / total_conversations) * 100 if total_conversations > 0 else 0
    print(f"9. Percentage of conversations with non-empty FHuo_hassan arrays: {pct_conversations_FHuo_hassan:.2f}%")
    print(f"   - Conversations with non-empty FHuo_hassan: {conversations_with_FHuo_hassan} out of {total_conversations}")
    
    # 10. Group by conversation_hash: Percentage of conversations with non-empty FSong_hassan
    conversations_with_FSong_hassan = 0
    
    for conv_hash, data in conversation_data.items():
        # Check if any turn in this conversation has non-empty FSong_hassan array
        has_non_empty_FSong = any(len(arr) > 0 for arr in data['FSong_Hassan'])
        if has_non_empty_FSong:
            conversations_with_FSong_hassan += 1
    
    pct_conversations_FSong_hassan = (conversations_with_FSong_hassan / total_conversations) * 100 if total_conversations > 0 else 0
    print(f"10. Percentage of conversations with non-empty FSong_hassan arrays: {pct_conversations_FSong_hassan:.2f}%")
    print(f"   - Conversations with non-empty FSong_hassan: {conversations_with_FSong_hassan} out of {total_conversations}")
    print()
    

if __name__ == "__main__":
    main()
