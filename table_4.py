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
    csv_file_path = 'Annotations/Human_Annotation_100 .csv'
    
    print("Loading data from Human_Annotation_100.csv...")
    
    # Initialize data structures
    claim_methods = defaultdict(lambda: {
        'total_rows': 0,
        'sa_cw_true': 0,
        'hj_cw_true': 0,
        'gold_true': 0,  # Gold column is True
        'sa_cw_values': [],
        'hj_cw_values': [],
        'gold_values': []
    })
    
    total_rows = 0
    
    # Read the CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            total_rows += 1
            
            # Extract data
            claim_method = row['claim_extr_method']
            sa_cw = row['SA_CW']
            hj_cw = row['HJ_CW']
            gold = row['Gold']
            
            # Update counters for this claim method
            claim_methods[claim_method]['total_rows'] += 1
            
            # Count True values (case-insensitive)
            sa_cw_is_true = sa_cw.upper() == 'TRUE'
            hj_cw_is_true = hj_cw.upper() == 'TRUE'
            gold_is_true = gold.upper() == 'TRUE'
            
            if sa_cw_is_true:
                claim_methods[claim_method]['sa_cw_true'] += 1
                claim_methods[claim_method]['sa_cw_values'].append(True)
            else:
                claim_methods[claim_method]['sa_cw_values'].append(False)
                
            if hj_cw_is_true:
                claim_methods[claim_method]['hj_cw_true'] += 1
                claim_methods[claim_method]['hj_cw_values'].append(True)
            else:
                claim_methods[claim_method]['hj_cw_values'].append(False)
            
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
        sa_cw_pct = (data['sa_cw_true'] / data['total_rows']) * 100 if data['total_rows'] > 0 else 0
        hj_cw_pct = (data['hj_cw_true'] / data['total_rows']) * 100 if data['total_rows'] > 0 else 0
        gold_pct = (data['gold_true'] / data['total_rows']) * 100 if data['total_rows'] > 0 else 0
        
        print(f"1. Percentage of True for SA_CW: {sa_cw_pct:.2f}% ({data['sa_cw_true']}/{data['total_rows']})")
        print(f"2. Percentage of True for HJ_CW: {hj_cw_pct:.2f}% ({data['hj_cw_true']}/{data['total_rows']})")
        print(f"3. Percentage of True for Gold: {gold_pct:.2f}% ({data['gold_true']}/{data['total_rows']})")
        
        # Calculate Kappa score between SA_CW and Gold
        if len(data['sa_cw_values']) > 0 and len(data['gold_values']) > 0:
            # Count agreements and disagreements
            both_true = sum(1 for sa, gold in zip(data['sa_cw_values'], data['gold_values']) if sa and gold)
            both_false = sum(1 for sa, gold in zip(data['sa_cw_values'], data['gold_values']) if not sa and not gold)
            sa_true_gold_false = sum(1 for sa, gold in zip(data['sa_cw_values'], data['gold_values']) if sa and not gold)
            sa_false_gold_true = sum(1 for sa, gold in zip(data['sa_cw_values'], data['gold_values']) if not sa and gold)
            
            # Observed agreement
            observed_agreement = (both_true + both_false) / data['total_rows']
            
            # Expected agreement (chance agreement)
            sa_true_rate = data['sa_cw_true'] / data['total_rows']
            sa_false_rate = 1 - sa_true_rate
            gold_true_rate = data['gold_true'] / data['total_rows']
            gold_false_rate = 1 - gold_true_rate
            
            expected_agreement = (sa_true_rate * gold_true_rate) + (sa_false_rate * gold_false_rate)
            
            # Calculate Kappa
            kappa = calculate_kappa(observed_agreement, expected_agreement)
            
            print(f"4. Kappa score between SA_CW and Gold: {kappa:.4f}")
            # print(f"   - Observed agreement: {observed_agreement:.4f}")
            # print(f"   - Expected agreement: {expected_agreement:.4f}")
            # print(f"   - Agreement breakdown:")
            # print(f"     * Both True: {both_true}")
            # print(f"     * Both False: {both_false}")
            # print(f"     * SA True, Gold False: {sa_true_gold_false}")
            # print(f"     * SA False, Gold True: {sa_false_gold_true}")
        else:
            print("4. Kappa score: Cannot calculate (no data)")
        
        print()
    
    # Overall statistics across all methods
    print("=== Overall Statistics ===")
    total_sa_cw_true = sum(data['sa_cw_true'] for data in claim_methods.values())
    total_hj_cw_true = sum(data['hj_cw_true'] for data in claim_methods.values())
    total_gold_true = sum(data['gold_true'] for data in claim_methods.values())
    
    overall_sa_cw_pct = (total_sa_cw_true / total_rows) * 100 if total_rows > 0 else 0
    overall_hj_cw_pct = (total_hj_cw_true / total_rows) * 100 if total_rows > 0 else 0
    overall_gold_pct = (total_gold_true / total_rows) * 100 if total_rows > 0 else 0
    
    print(f"Overall percentage of True for SA_CW: {overall_sa_cw_pct:.2f}% ({total_sa_cw_true}/{total_rows})")
    print(f"Overall percentage of True for HJ_CW: {overall_hj_cw_pct:.2f}% ({total_hj_cw_true}/{total_rows})")
    print(f"Overall percentage of True for Gold: {overall_gold_pct:.2f}% ({total_gold_true}/{total_rows})")
    
    # Overall Kappa calculation between SA_CW and Gold
    all_sa_cw_values = []
    all_gold_values = []
    for data in claim_methods.values():
        all_sa_cw_values.extend(data['sa_cw_values'])
        all_gold_values.extend(data['gold_values'])
    
    if len(all_sa_cw_values) > 0 and len(all_gold_values) > 0:
        both_true = sum(1 for sa, gold in zip(all_sa_cw_values, all_gold_values) if sa and gold)
        both_false = sum(1 for sa, gold in zip(all_sa_cw_values, all_gold_values) if not sa and not gold)
        
        observed_agreement = (both_true + both_false) / total_rows
        expected_agreement = (overall_sa_cw_pct/100 * overall_gold_pct/100) + ((100-overall_sa_cw_pct)/100 * (100-overall_gold_pct)/100)
        
        overall_kappa = calculate_kappa(observed_agreement, expected_agreement)
        print(f"Overall Kappa score between SA_CW and Gold: {overall_kappa:.4f}")

if __name__ == "__main__":
    main()
