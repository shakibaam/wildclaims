#!/usr/bin/env python3
"""
Script to analyze human annotation data from Human_Annotation_100.csv file.
"""

import csv
from collections import defaultdict
import math

def calculate_kappa(observed_agreement, expected_agreement):
    """Calculate Cohen's kappa coefficient."""
    if expected_agreement == 1:
        return 1.0  # Perfect agreement
    return (observed_agreement - expected_agreement) / (1 - expected_agreement)

def main():
    csv_file_path = '../Annotations/Human_Annotation.csv'
    
    print("Loading data from Human_Annotation.csv...")
    
    # Initialize data structures
    claim_methods = defaultdict(lambda: {
        'total_rows': 0,
        'human1_cw_true': 0,
        'human2_cw_true': 0,
        'gold_true': 0,  # Gold column is True
        'human1_cw_values': [],
        'human2_cw_values': [],
        'gold_values': []
    })
    
    total_rows = 0
    
    # Read the CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            total_rows += 1
            
            # Extract data
            claim_method = row['Claim_Extr_Method']
            human1_cw = row['Human1_CW']
            human2_cw = row['Human2_CW']
            gold = row['Gold']
            
            
            # Update counters for this claim method
            claim_methods[claim_method]['total_rows'] += 1
            
            # Count True values (case-insensitive)
            human1_cw_is_true = human1_cw.upper() == 'TRUE'
            human2_cw_is_true = human2_cw.upper() == 'TRUE'
            gold_is_true = gold.upper() == 'TRUE'
            
            if human1_cw_is_true:
                claim_methods[claim_method]['human1_cw_true'] += 1
                claim_methods[claim_method]['human1_cw_values'].append(True)
            else:
                claim_methods[claim_method]['human1_cw_values'].append(False)
                
            if human2_cw_is_true:
                claim_methods[claim_method]['human2_cw_true'] += 1
                claim_methods[claim_method]['human2_cw_values'].append(True)
            else:
                claim_methods[claim_method]['human2_cw_values'].append(False)
            
            if gold_is_true:
                claim_methods[claim_method]['gold_true'] += 1
                claim_methods[claim_method]['gold_values'].append(True)
            else:
                claim_methods[claim_method]['gold_values'].append(False)
    
    print(f"Total rows in dataset: {total_rows}")
    print(f"Number of claim extraction methods: {len(claim_methods)}")
    print()
    
    # Analyze each claim extraction method
    for method, data in claim_methods.items():
        print(f"=== Analysis for {method} ===")
        print(f"Total rows: {data['total_rows']}")
        
        # Calculate percentages
        human1_cw_pct = (data['human1_cw_true'] / data['total_rows']) * 100 if data['total_rows'] > 0 else 0
        human2_cw_pct = (data['human2_cw_true'] / data['total_rows']) * 100 if data['total_rows'] > 0 else 0
        gold_pct = (data['gold_true'] / data['total_rows']) * 100 if data['total_rows'] > 0 else 0
        
        print(f"1. Percentage of True for Human1_CW: {human1_cw_pct:.2f}% ({data['human1_cw_true']}/{data['total_rows']})")
        print(f"2. Percentage of True for Human2_CW: {human2_cw_pct:.2f}% ({data['human2_cw_true']}/{data['total_rows']})")
        print(f"3. Percentage of True for Gold: {gold_pct:.2f}% ({data['gold_true']}/{data['total_rows']})")
        
        # Calculate Kappa score between Human1_CW and Gold
        if len(data['human1_cw_values']) > 0 and len(data['gold_values']) > 0:
            # Count agreements and disagreements
            both_true = sum(1 for human1, gold in zip(data['human1_cw_values'], data['gold_values']) if human1 and gold)
            both_false = sum(1 for human1, gold in zip(data['human1_cw_values'], data['gold_values']) if not human1 and not gold)
            human1_true_gold_false = sum(1 for human1, gold in zip(data['human1_cw_values'], data['gold_values']) if human1 and not gold)
            human1_false_gold_true = sum(1 for human1, gold in zip(data['human1_cw_values'], data['gold_values']) if not human1 and gold)
            
            # Observed agreement
            observed_agreement = (both_true + both_false) / data['total_rows']
            
            # Expected agreement (chance agreement)
            human1_true_rate = data['human1_cw_true'] / data['total_rows']
            human1_false_rate = 1 - human1_true_rate
            gold_true_rate = data['gold_true'] / data['total_rows']
            gold_false_rate = 1 - gold_true_rate
            
            expected_agreement = (human1_true_rate * gold_true_rate) + (human1_false_rate * gold_false_rate)
            
            # Calculate Kappa
            kappa = calculate_kappa(observed_agreement, expected_agreement)
            
            # print(f"4. Kappa score between Human1_CW and Gold: {kappa:.4f}")
            # print(f"   - Observed agreement: {observed_agreement:.4f}")
            # print(f"   - Expected agreement: {expected_agreement:.4f}")
            # print(f"   - Agreement breakdown:")
            # print(f"     * Both True: {both_true}")
            # print(f"     * Both False: {both_false}")
            # print(f"     * Human1 True, Gold False: {human1_true_gold_false}")
            # print(f"     * Human1 False, Gold True: {human1_false_gold_true}")
        else:
            print("4. Kappa score: Cannot calculate (no data)")
        
        # Calculate Kappa score between Human1_CW and Human2_CW
        if len(data['human1_cw_values']) > 0 and len(data['human2_cw_values']) > 0:
            # Count agreements and disagreements
            both_true = sum(1 for human1, human2 in zip(data['human1_cw_values'], data['human2_cw_values']) if human1 and human2)
            both_false = sum(1 for human1, human2 in zip(data['human1_cw_values'], data['human2_cw_values']) if not human1 and not human2)
            human1_true_human2_false = sum(1 for human1, human2 in zip(data['human1_cw_values'], data['human2_cw_values']) if human1 and not human2)
            human1_false_human2_true = sum(1 for human1, human2 in zip(data['human1_cw_values'], data['human2_cw_values']) if not human1 and human2)
            
            # Observed agreement
            observed_agreement = (both_true + both_false) / data['total_rows']
            
            # Expected agreement (chance agreement)
            human1_true_rate = data['human1_cw_true'] / data['total_rows']
            human1_false_rate = 1 - human1_true_rate
            human2_true_rate = data['human2_cw_true'] / data['total_rows']
            human2_false_rate = 1 - human2_true_rate
            
            expected_agreement = (human1_true_rate * human2_true_rate) + (human1_false_rate * human2_false_rate)
            
            # Calculate Kappa
            kappa_h1_h2 = calculate_kappa(observed_agreement, expected_agreement)
            
            print(f"5. Kappa score between Human1_CW and Human2_CW: {kappa_h1_h2:.4f}")
        else:
            print("5. Kappa score: Cannot calculate (no data)")
        
        print()
    
    # Overall statistics across all methods
    # print("=== Overall Statistics ===")
    # total_human1_cw_true = sum(data['human1_cw_true'] for data in claim_methods.values())
    # total_human2_cw_true = sum(data['human2_cw_true'] for data in claim_methods.values())
    # total_gold_true = sum(data['gold_true'] for data in claim_methods.values())
    
    # overall_human1_cw_pct = (total_human1_cw_true / total_rows) * 100 if total_rows > 0 else 0
    # overall_human2_cw_pct = (total_human2_cw_true / total_rows) * 100 if total_rows > 0 else 0
    # overall_gold_pct = (total_gold_true / total_rows) * 100 if total_rows > 0 else 0
    
    # print(f"Overall percentage of True for Human1_CW: {overall_human1_cw_pct:.2f}% ({total_human1_cw_true}/{total_rows})")
    # print(f"Overall percentage of True for Human2_CW: {overall_human2_cw_pct:.2f}% ({total_human2_cw_true}/{total_rows})")
    # print(f"Overall percentage of True for Gold: {overall_gold_pct:.2f}% ({total_gold_true}/{total_rows})")
    
    # # Overall Kappa calculation between Human1_CW and Gold
    # all_human1_cw_values = []
    # all_gold_values = []
    # for data in claim_methods.values():
    #     all_human1_cw_values.extend(data['human1_cw_values'])
    #     all_gold_values.extend(data['gold_values'])
    
    # if len(all_human1_cw_values) > 0 and len(all_gold_values) > 0:
    #     both_true = sum(1 for human1, gold in zip(all_human1_cw_values, all_gold_values) if human1 and gold)
    #     both_false = sum(1 for human1, gold in zip(all_human1_cw_values, all_gold_values) if not human1 and not gold)
        
    #     observed_agreement = (both_true + both_false) / total_rows
    #     expected_agreement = (overall_human1_cw_pct/100 * overall_gold_pct/100) + ((100-overall_human1_cw_pct)/100 * (100-overall_gold_pct)/100)
        
    #     overall_kappa = calculate_kappa(observed_agreement, expected_agreement)
    #     print(f"Overall Kappa score between Human1_CW and Gold: {overall_kappa:.4f}")

if __name__ == "__main__":
    main()
