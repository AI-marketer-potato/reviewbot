#!/usr/bin/env python3
"""
Clean CSV file by removing line breaks from response text
"""

import pandas as pd
import csv

def clean_linebreaks_in_csv(input_file, output_file):
    """Remove line breaks from CSV file"""
    print(f"📖 Reading CSV file: {input_file}")
    
    # Read the CSV with pipe delimiter
    df = pd.read_csv(input_file, delimiter='|')
    
    print(f"📊 Found {len(df)} rows to clean")
    
    # Clean line breaks from all text columns
    for col in df.columns:
        if df[col].dtype == 'object':  # String columns
            df[col] = df[col].astype(str).str.replace('\n', ' ').str.replace('\r', ' ')
            # Also remove extra spaces
            df[col] = df[col].str.replace(r'\s+', ' ', regex=True).str.strip()
    
    # Save cleaned CSV with pipe delimiter
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        df.to_csv(csvfile, sep='|', index=False, quoting=csv.QUOTE_MINIMAL)
    
    print(f"✅ Cleaned CSV saved to: {output_file}")
    return df

if __name__ == "__main__":
    input_file = '/Users/gravitylabs/Desktop/review/final_42_reviews_improved_20250617_113055.csv'
    output_file = '/Users/gravitylabs/Desktop/review/final_42_reviews_cleaned.csv'
    
    print("🧹 Cleaning line breaks from CSV file...")
    df = clean_linebreaks_in_csv(input_file, output_file)
    
    print("\n=== 🔍 Sample Cleaned Results ===")
    # Show first few rows to verify cleaning
    for i in range(min(3, len(df))):
        print(f"ID: {df.iloc[i]['ID']}")
        print(f"Response: {df.iloc[i]['생성된_응답'][:100]}...")
        print("-" * 60)