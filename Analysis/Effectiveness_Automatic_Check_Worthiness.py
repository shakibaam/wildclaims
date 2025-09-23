
"""
Script to compute precision, recall, F1, and kappa for binary columns in relation to Gold standard.
"""

import csv
from collections import defaultdict
import math

def calculate_kappa(observed_agreement, expected_agreement):
    """Calculate Cohen's kappa coefficient."""
    if expected_agreement == 1:
        return 1.0  # Perfect agreement
    return (observed_agreement - expected_agreement) / (1 - expected_agreement)

def calculate_precision_recall_f1(true_positives, false_positives, false_negatives):
    """Calculate precision, recall, and F1 score."""
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1

def main():
    csv_file_path = '../Annotations/human_annotations.csv'
    
    print("Loading data from human_annotations.csv...")
    
    # Initialize data structures
    claim_methods = defaultdict(lambda: {
        'total_rows': 0,
        'gold_values': [],
        'Hassan_Binary_values': [],
        'Majer_Binary_values': [],
        'intersection_values': [],
        'union_values': []
    })
    
    total_rows = 0
    
    # Read the CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            total_rows += 1
            
            # Extract data
            claim_method = row['Claim_Extr_Method']
            gold = row['Gold']
            majer_binary = row['Majer_Binary']
            hassan_binary = row['Hassan_Binary']
            intersection = row['Intersection']
            union = row['Union']
            
            # Replace siqing with FHou and veriscore with FSong in claim_extr_method
            # if claim_method == 'siqing':
            #     claim_method = 'FHou'
            # elif claim_method == 'veriscore':
            #     claim_method = 'FSong'
            
            # Update counters for this claim method
            claim_methods[claim_method]['total_rows'] += 1
            
            # Convert to boolean values (case-insensitive)
            gold_is_true = gold.upper() == 'TRUE'
            majer_is_true = majer_binary.upper() == 'TRUE'
            hassan_is_true = hassan_binary.upper() == 'TRUE'
            intersection_is_true = intersection.upper() == 'TRUE'
            union_is_true = union.upper() == 'TRUE'
            
            # Store values
            claim_methods[claim_method]['gold_values'].append(gold_is_true)
            claim_methods[claim_method]['Majer_Binary_values'].append(majer_is_true)
            claim_methods[claim_method]['Hassan_Binary_values'].append(hassan_is_true)
            claim_methods[claim_method]['intersection_values'].append(intersection_is_true)
            claim_methods[claim_method]['union_values'].append(union_is_true)
    
    print(f"Total rows in dataset: {total_rows}")
    print(f"Number of claim extraction methods: {len(claim_methods)}")
    print()
    
    # Analyze each claim extraction method
    for method, data in claim_methods.items():
        print(f"=== Analysis for {method} ===")
        print(f"Total rows: {data['total_rows']}")
        print()
        
        # Define the columns to analyze
        columns_to_analyze = [
            ('Hassan_Binary', data['Hassan_Binary_values']),
            ('Majer_Binary', data['Majer_Binary_values']),
            ('Intersection', data['intersection_values']),
            ('Union', data['union_values'])
        ]
        
        gold_values = data['gold_values']
        
        for column_name, column_values in columns_to_analyze:
            print(f"--- {column_name} vs Gold ---")
            
            # Calculate confusion matrix
            true_positives = sum(1 for pred, gold in zip(column_values, gold_values) if pred and gold)
            false_positives = sum(1 for pred, gold in zip(column_values, gold_values) if pred and not gold)
            false_negatives = sum(1 for pred, gold in zip(column_values, gold_values) if not pred and gold)
            true_negatives = sum(1 for pred, gold in zip(column_values, gold_values) if not pred and not gold)
            
            # Calculate precision, recall, F1
            precision, recall, f1 = calculate_precision_recall_f1(true_positives, false_positives, false_negatives)
            
            # Calculate Kappa
            observed_agreement = (true_positives + true_negatives) / data['total_rows']
            
            # Expected agreement
            pred_true_rate = sum(column_values) / len(column_values) if len(column_values) > 0 else 0
            pred_false_rate = 1 - pred_true_rate
            gold_true_rate = sum(gold_values) / len(gold_values) if len(gold_values) > 0 else 0
            gold_false_rate = 1 - gold_true_rate
            
            expected_agreement = (pred_true_rate * gold_true_rate) + (pred_false_rate * gold_false_rate)
            kappa = calculate_kappa(observed_agreement, expected_agreement)
            
            print(f"Precision: {precision:.4f}")
            print(f"Recall: {recall:.4f}")
            print(f"F1 Score: {f1:.4f}")
            print(f"Kappa: {kappa:.4f}")
            print()
    


if __name__ == "__main__":
    main()