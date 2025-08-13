#!/usr/bin/env python3
"""
Clean the final improved CSV file by removing line breaks
"""

import pandas as pd
import csv

def clean_final_improved_csv():
    """Clean the final improved CSV file"""
    input_file = '/Users/gravitylabs/Desktop/review/final_42_reviews_IMPROVED_20250617_120746.csv'
    output_file = '/Users/gravitylabs/Desktop/review/final_42_reviews_IMPROVED_CLEANED.csv'
    
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
    
    # Show sample Korean responses
    print("\n=== 🔍 Sample Korean Responses ===")
    korean_df = df[df['언어'] == 'KOR']
    
    for i in range(min(3, len(korean_df))):
        row = korean_df.iloc[i]
        print(f"\n🆔 ID: {row['ID']}")
        print(f"📝 Original: {row['원본_리뷰'][:60]}...")
        print(f"💬 Response: {row['생성된_응답'][:100]}...")
        print(f"🏷️ Category: {row['카테고리']}")
        
        # Check for issues
        response_text = row['생성된_응답']
        issues = []
        
        if response_text.count('죄송합니다') > 1:
            issues.append("❌ '죄송합니다' 과다사용")
        
        observational_patterns = ['군요', '네요', '으시네요', '는군요', '했군요', '하시는군요', '하셨네요', '이네요']
        if any(pattern in response_text for pattern in observational_patterns):
            issues.append("❌ 관찰적 어투 사용")
        
        if issues:
            print(f"⚠️ Issues: {', '.join(issues)}")
        else:
            print("✅ Clean response")
        
        print("-" * 60)
    
    return df

if __name__ == "__main__":
    print("🧹 Cleaning final improved CSV file...")
    df = clean_final_improved_csv()
    print("\n🎉 Cleaning completed!")