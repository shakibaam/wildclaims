#!/usr/bin/env python3
"""
Simple script to rename columns in run_factual_claim_extraction.csv to proper case formatting
"""

import csv
import os

def rename_factual_claim_columns():
    """Rename columns in run_factual_claim_extraction.csv to proper case"""
    input_file = "Annotations/run_factual_claim_extraction.csv"
    output_file = "Annotations/run_factual_claim_extraction_temp.csv"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return
    
    print(f"Processing {input_file}...")
    
    # Define column mappings for proper case formatting
    column_mappings = {
        'conversation_hash': 'Conversation_Hash',
        'claim_extr_method': 'Claim_Extr_Method',
        'hassan': 'Hassan',
        'major': 'Major'
    }
    
    # Read the CSV and rename columns
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Process header row
        headers = next(reader)
        
        # Rename the columns using the mapping
        renamed_headers = []
        renamed_count = 0
        for header in headers:
            if header in column_mappings:
                renamed_headers.append(column_mappings[header])
                renamed_count += 1
            else:
                renamed_headers.append(header)
        
        # Write renamed headers
        writer.writerow(renamed_headers)
        
        # Write all data rows unchanged
        rows_written = 0
        for row in reader:
            writer.writerow(row)
            rows_written += 1
    
    # Replace original file with updated file
    os.replace(output_file, input_file)
    
    print(f"✅ Successfully renamed columns in {input_file}")
    print(f"📊 Processed {rows_written} data rows")
    print(f"🔄 Renamed {renamed_count} columns to proper case format")
    print("\nColumn renaming summary:")
    for old_name, new_name in column_mappings.items():
        print(f"  - {old_name} => {new_name}")

if __name__ == "__main__":
    print("=" * 70)
    print("COLUMN RENAMING SCRIPT - FACTUAL CLAIM EXTRACTION")
    print("=" * 70)
    print()
    
    rename_factual_claim_columns()
    
    print()
    print("=" * 70)
    print("COLUMN RENAMING COMPLETED!")
    print("=" * 70)
