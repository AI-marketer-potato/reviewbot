#!/usr/bin/env python3
"""
Detailed analysis of English responses
"""

import pandas as pd

def analyze_english_detailed():
    """Provide detailed analysis of English responses"""
    print("🔍 Detailed English Response Analysis")
    print("=" * 50)
    
    # Read the final English results
    df = pd.read_csv('/Users/gravitylabs/Desktop/review/ENGLISH_FINAL_20250619_145727.csv', delimiter='|')
    
    for idx, row in df.iterrows():
        print(f"\n🎯 Review #{idx + 1}: {row['ID']}")
        print(f"📝 Original Review ({len(row['원본_리뷰'])} chars):")
        print(f"   {row['원본_리뷰']}")
        print(f"\n💬 Generated Response ({row['응답길이']} chars):")
        print(f"   {row['생성된_응답']}")
        
        # Detailed analysis
        response = row['생성된_응답']
        original = row['원본_리뷰']
        
        print(f"\n🔍 Analysis:")
        
        # 1. Greeting analysis
        if response.startswith("Hi,"):
            print(f"   ✅ Greeting: Perfect - starts with 'Hi,'")
        elif "Hi there" in response:
            print(f"   ❌ Greeting: Uses 'Hi there' (should be 'Hi,')")
        elif "Hi User" in response:
            print(f"   ❌ Greeting: Uses 'Hi User' (should be 'Hi,')")
        else:
            print(f"   ⚠️ Greeting: Unusual start - {response[:20]}...")
        
        # 2. Tone analysis
        tone_indicators = {
            "conversational": ["sorry to hear", "sounds frustrating", "thanks for sharing"],
            "formal": ["we sincerely apologize", "we are committed", "deeply regret"],
            "helpful": ["please try", "you can", "we recommend"]
        }
        
        tone_found = []
        for tone, phrases in tone_indicators.items():
            if any(phrase in response.lower() for phrase in phrases):
                tone_found.append(tone)
        
        print(f"   📈 Tone: {', '.join(tone_found) if tone_found else 'neutral'}")
        
        # 3. Problem acknowledgment
        original_keywords = []
        if "withdrawal" in original.lower():
            original_keywords.append("withdrawal")
        if "gift card" in original.lower():
            original_keywords.append("gift card")
        if "ad" in original.lower() or "pop up" in original.lower():
            original_keywords.append("ads")
        if "support" in original.lower():
            original_keywords.append("support")
        if "error" in original.lower():
            original_keywords.append("error")
        if "point" in original.lower():
            original_keywords.append("points")
        
        acknowledged = []
        for keyword in original_keywords:
            if keyword in response.lower():
                acknowledged.append(keyword)
        
        print(f"   🎯 Problem Recognition: {len(acknowledged)}/{len(original_keywords)} issues addressed")
        if original_keywords:
            print(f"      Original issues: {', '.join(original_keywords)}")
            print(f"      Acknowledged: {', '.join(acknowledged) if acknowledged else 'none'}")
        
        # 4. Solution guidance
        solutions = []
        if "faq" in response.lower():
            solutions.append("FAQ reference")
        if "help center" in response.lower():
            solutions.append("Help Center guidance")
        if "cache" in response.lower():
            solutions.append("Cache clearing")
        if "reinstall" in response.lower():
            solutions.append("Reinstall suggestion")
        if "details" in response.lower():
            solutions.append("Request for details")
        
        print(f"   🛠️ Solutions Provided: {', '.join(solutions) if solutions else 'general guidance only'}")
        
        # 5. Length assessment
        if row['응답길이'] < 200:
            print(f"   📏 Length: Short ({row['응답길이']} chars) - may need more detail")
        elif row['응답길이'] > 350:
            print(f"   📏 Length: Long ({row['응답길이']} chars) - may be too verbose")
        else:
            print(f"   📏 Length: Good ({row['응답길이']} chars) - appropriate")
        
        # 6. Specific improvements vs original feedback
        improvements = []
        issues = []
        
        if not response.startswith("Hi there"):
            improvements.append("No 'Hi there' usage")
        if not "we're really sorry" in response.lower():
            improvements.append("Avoids overly formal apologies")
        if "sorry to hear" in response.lower():
            improvements.append("Uses conversational sympathy")
        if "faq" in response.lower() and "help center" in response.lower():
            improvements.append("Includes both FAQ and Help Center")
        
        print(f"   ✅ Improvements: {', '.join(improvements) if improvements else 'none noted'}")
        if issues:
            print(f"   ⚠️ Issues: {', '.join(issues)}")
        
        print(f"   {'─' * 60}")
    
    # Overall summary
    print(f"\n📊 Overall English Quality Summary:")
    print(f"   Total Reviews: {len(df)}")
    
    # Greeting stats
    greeting_perfect = sum(1 for _, row in df.iterrows() if row['생성된_응답'].startswith("Hi,"))
    print(f"   Perfect Greetings: {greeting_perfect}/{len(df)} ({greeting_perfect/len(df)*100:.1f}%)")
    
    # Length stats
    avg_length = df['응답길이'].mean()
    print(f"   Average Length: {avg_length:.1f} characters")
    
    # FAQ/Help Center inclusion
    faq_mentions = sum(1 for _, row in df.iterrows() if "faq" in row['생성된_응답'].lower())
    help_center_mentions = sum(1 for _, row in df.iterrows() if "help center" in row['생성된_응답'].lower())
    print(f"   FAQ References: {faq_mentions}/{len(df)} ({faq_mentions/len(df)*100:.1f}%)")
    print(f"   Help Center References: {help_center_mentions}/{len(df)} ({help_center_mentions/len(df)*100:.1f}%)")
    
    print(f"\n🎉 Final Assessment: {'EXCELLENT' if greeting_perfect == len(df) and avg_length < 350 else 'GOOD with minor improvements needed'}")

if __name__ == "__main__":
    analyze_english_detailed()