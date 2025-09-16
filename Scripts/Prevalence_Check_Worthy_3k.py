#!/usr/bin/env python3
"""
Script to analyze array columns and compute statistics for True values.
"""

import csv
import ast
from collections import defaultdict

def parse_array_string(array_str):
    """Parse array string representation to actual list."""
    if not array_str or array_str.strip() == '' or array_str == 'nan':
        return []
    
    # Handle case where array_str is already an integer or other non-string type
    if not isinstance(array_str, str):
        return []
    
    try:
        # Remove any extra whitespace and parse as Python literal
        parsed = ast.literal_eval(array_str.strip())
        # Ensure we return a list
        if isinstance(parsed, list):
            return parsed
        else:
            return []
    except (ValueError, SyntaxError):
        # If parsing fails, return empty list
        return []

def main():
    csv_file_path = '../Annotations/run_analysis.csv'
    
    print("Loading data from run_analysis.csv...")
    
    # Define columns to analyze in the requested order
    columns_to_analyze = [
        'FHuo_hassan',
        'FHuo_majer',
        'FHuo_intersection',
        'FHuo_union',
        'FSong_hassan',
        'FSong_majer',
        'FSong_intersection',
        'FSong_union'
    ]
    
    # Initialize data structures
    column_data = {col: [] for col in columns_to_analyze}
    conversation_data = defaultdict(lambda: {col: [] for col in columns_to_analyze})
    selected_agent_column_data = defaultdict(lambda: {col: [] for col in columns_to_analyze})
    
    total_rows = 0
    
    # Read the CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            total_rows += 1
            
            # Extract data
            conversation_hash = row['conversation_hash']
            selected_agent_column = row['Selected_Agent_Column']
            
            # Parse arrays for each column
            for col in columns_to_analyze:
                array_str = row[col]
                array = parse_array_string(array_str)
                column_data[col].append(array)
                conversation_data[conversation_hash][col].append(array)
                selected_agent_column_data[selected_agent_column][col].append(array)
    
    print(f"Total rows in dataset: {total_rows}")
    print(f"Total conversations: {len(conversation_data)}")
    print(f"Total Selected_Agent_Column values: {len(selected_agent_column_data)}")
    print()
    
    # Analyze each column
    for col in columns_to_analyze:
        print(f"=== Analysis for {col} ===")
        
        # 1. % of True in all elements
        all_elements = []
        for array in column_data[col]:
            all_elements.extend(array)
        
        total_elements = len(all_elements)
        true_elements = sum(1 for elem in all_elements if elem)
        pct_true_elements = (true_elements / total_elements) * 100 if total_elements > 0 else 0
        
        print(f"1. % of CW in all facts: {pct_true_elements:.2f}% ({true_elements}/{total_elements})")
        
        # 2. % of rows (utterances) have at least one True
        rows_with_at_least_one_true = 0
        
        for array in column_data[col]:
            if any(elem for elem in array):
                rows_with_at_least_one_true += 1
        
        pct_rows_with_at_least_one_true = (rows_with_at_least_one_true / total_rows) * 100 if total_rows > 0 else 0
        print(f"2. % of rows (utterances) have at least one CW fact: {pct_rows_with_at_least_one_true:.2f}% ({rows_with_at_least_one_true}/{total_rows})")
        
        # 3. % of conversations have at least one True
        conversations_with_true = 0
        total_conversations = len(conversation_data)
        
        for conv_hash, data in conversation_data.items():
            # Check if any turn in this conversation has at least one True
            has_true = False
            for array in data[col]:
                if any(elem for elem in array):
                    has_true = True
                    break
            if has_true:
                conversations_with_true += 1
        
        pct_conversations_with_true = (conversations_with_true / total_conversations) * 100 if total_conversations > 0 else 0
        print(f"3. % of conversations have at least one CW fact: {pct_conversations_with_true:.2f}% ({conversations_with_true}/{total_conversations})")
        
        print()
    

if __name__ == "__main__":
    main()
