#!/usr/bin/env python3
"""
Clean the new script CSV file by removing line breaks
"""

import pandas as pd
import csv
import glob

def find_latest_script():
    """Find the latest NEW_SCRIPT file"""
    script_files = glob.glob('/Users/gravitylabs/Desktop/review/NEW_SCRIPT_42_reviews_*.csv')
    if not script_files:
        print("❌ No NEW_SCRIPT files found")
        return None
    
    # Get the latest file
    latest_file = max(script_files)
    print(f"📁 Found latest script: {latest_file}")
    return latest_file

def clean_new_script():
    """Clean the new script CSV file"""
    input_file = find_latest_script()
    if not input_file:
        return
    
    output_file = input_file.replace('.csv', '_CLEANED.csv')
    
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
    
    # Show quality analysis
    show_quality_analysis(df)
    
    return output_file

def show_quality_analysis(df):
    """Show quality analysis of the new responses"""
    print("\n=== 🎯 Final Quality Report ===")
    
    # Korean analysis
    korean_df = df[df['언어'] == 'KOR']
    japanese_df = df[df['언어'] == 'JPN']
    english_df = df[df['언어'] == 'USA']
    
    print(f"📊 Distribution:")
    print(f"   🇰🇷 Korean: {len(korean_df)} reviews")
    print(f"   🇯🇵 Japanese: {len(japanese_df)} reviews")
    print(f"   🇺🇸 English: {len(english_df)} reviews")
    
    # Korean quality check
    korean_issues = 0
    korean_perfect = 0
    
    for _, row in korean_df.iterrows():
        response = row['생성된_응답']
        issues = []
        
        if response.count('죄송합니다') > 1:
            issues.append("죄송합니다 과다")
        
        if any(pattern in response for pattern in ['군요', '네요', '으시네요', '는군요']):
            issues.append("관찰적 어투")
        
        if not response.startswith(('안녕하세요, 머니워크입니다', '안녕하세요, 머니워크 운영팀입니다')):
            issues.append("인사말 누락")
        
        if issues:
            korean_issues += 1
        else:
            korean_perfect += 1
    
    print(f"\n🇰🇷 Korean Quality:")
    print(f"   ✅ Perfect responses: {korean_perfect}/{len(korean_df)} ({korean_perfect/len(korean_df)*100:.1f}%)")
    print(f"   ⚠️ Issues found: {korean_issues}/{len(korean_df)} ({korean_issues/len(korean_df)*100:.1f}%)")
    
    # Japanese quality check
    japanese_long = sum(1 for _, row in japanese_df.iterrows() if len(row['생성된_응답']) > 250)
    japanese_good_length = len(japanese_df) - japanese_long
    
    print(f"\n🇯🇵 Japanese Quality:")
    print(f"   ✅ Appropriate length (≤250): {japanese_good_length}/{len(japanese_df)} ({japanese_good_length/len(japanese_df)*100:.1f}%)")
    print(f"   ⚠️ Too long (>250): {japanese_long}/{len(japanese_df)} ({japanese_long/len(japanese_df)*100:.1f}%)")
    
    # Show best examples
    print("\n=== 🌟 Best Examples ===")
    
    # Korean example
    if not korean_df.empty:
        good_korean = korean_df.iloc[3]  # Pick a different sample
        print(f"\n🇰🇷 Korean Example:")
        print(f"   ID: {good_korean['ID']}")
        print(f"   Original: {good_korean['원본_리뷰'][:60]}...")
        print(f"   Response: {good_korean['생성된_응답'][:100]}...")
        print(f"   Length: {len(good_korean['생성된_응답'])} characters")
    
    # Japanese example
    if not japanese_df.empty:
        good_japanese = japanese_df.iloc[0]
        print(f"\n🇯🇵 Japanese Example:")
        print(f"   ID: {good_japanese['ID']}")
        print(f"   Original: {good_japanese['원본_리뷰'][:60]}...")
        print(f"   Response: {good_japanese['생성된_응답'][:100]}...")
        print(f"   Length: {len(good_japanese['생성된_응답'])} characters")
    
    # English example
    if not english_df.empty:
        good_english = english_df.iloc[0]
        print(f"\n🇺🇸 English Example:")
        print(f"   ID: {good_english['ID']}")
        print(f"   Original: {good_english['원본_리뷰'][:60]}...")
        print(f"   Response: {good_english['생성된_응답'][:100]}...")

if __name__ == "__main__":
    print("🧹 Cleaning new script CSV file...")
    output_file = clean_new_script()
    if output_file:
        print(f"\n🎉 Final cleaned script ready: {output_file}")
    print("\n✨ New script generation complete!")