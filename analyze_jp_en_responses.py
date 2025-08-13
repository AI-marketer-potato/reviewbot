#!/usr/bin/env python3
"""
Analyze Japanese and English responses from the final CSV
"""

import pandas as pd

def analyze_japanese_responses():
    """Analyze Japanese responses for quality issues"""
    print("=== 🇯🇵 Japanese Response Analysis ===")
    
    # Read the final CSV
    df = pd.read_csv('/Users/gravitylabs/Desktop/review/final_42_reviews_IMPROVED_CLEANED.csv', delimiter='|')
    
    # Filter Japanese responses
    jp_df = df[df['언어'] == 'JPN']
    print(f"📊 Total Japanese reviews: {len(jp_df)}")
    
    # Analyze each Japanese response
    issues = []
    
    for idx, row in jp_df.iterrows():
        response = row['생성된_응답']
        review_id = row['ID']
        original = row['원본_리뷰']
        
        print(f"\n🆔 ID: {review_id}")
        print(f"📝 Original: {original[:60]}...")
        print(f"💬 Response: {response[:100]}...")
        
        # Check Japanese response quality
        response_issues = []
        
        # Check length (Japanese responses seem too long)
        if len(response) > 400:
            response_issues.append("❌ 응답이 너무 길음 (400자 이상)")
        
        # Check for excessive formality
        if response.count('申し上げます') > 2:
            response_issues.append("❌ '申し上げます' 과다사용")
        
        # Check for repetitive patterns
        if response.count('この度は') > 1:
            response_issues.append("❌ 'この度は' 반복")
        
        # Check for appropriate greeting
        if not response.startswith('この度は'):
            response_issues.append("❌ 적절한 인사말 누락")
        
        # Check if response feels too robotic
        formal_phrases = ['何卒よろしくお願い申し上げます', '心よりお詫び申し上げます', '深くお詫び申し上げます']
        if sum(phrase in response for phrase in formal_phrases) >= 2:
            response_issues.append("❌ 과도하게 격식적임")
        
        if response_issues:
            print(f"⚠️ Issues: {', '.join(response_issues)}")
            issues.append({
                'id': review_id,
                'issues': response_issues,
                'response_length': len(response)
            })
        else:
            print("✅ No major issues found")
    
    print(f"\n📈 Japanese Summary:")
    print(f"   Total responses with issues: {len(issues)}")
    print(f"   Common issues:")
    all_issues = [issue for item in issues for issue in item['issues']]
    for issue_type in set(all_issues):
        count = all_issues.count(issue_type)
        print(f"     {issue_type}: {count}")

def analyze_english_responses():
    """Analyze English responses for quality issues"""
    print("\n\n=== 🇺🇸 English Response Analysis ===")
    
    # Read the final CSV
    df = pd.read_csv('/Users/gravitylabs/Desktop/review/final_42_reviews_IMPROVED_CLEANED.csv', delimiter='|')
    
    # Filter English responses
    en_df = df[df['언어'] == 'USA']
    print(f"📊 Total English reviews: {len(en_df)}")
    
    # Analyze each English response
    issues = []
    
    for idx, row in en_df.iterrows():
        response = row['생성된_응답']
        review_id = row['ID']
        original = row['원본_리뷰']
        
        print(f"\n🆔 ID: {review_id}")
        print(f"📝 Original: {original[:60]}...")
        print(f"💬 Response: {response[:100]}...")
        
        # Check English response quality
        response_issues = []
        
        # Check if too short (might be generic)
        if len(response) < 100:
            response_issues.append("❌ 응답이 너무 짧음 (100자 미만)")
        
        # Check for appropriate greeting
        if not any(greeting in response for greeting in ['Hi there', 'Hi', 'Hello', 'Thanks for']):
            response_issues.append("❌ 적절한 인사말 누락")
        
        # Check for FAQ mention
        if 'FAQ' not in response and 'Help Center' not in response:
            response_issues.append("❌ FAQ/Help Center 안내 누락")
        
        # Check if too generic
        generic_phrases = ['Thanks for your feedback', 'Sorry to hear', 'Hope this helps']
        if sum(phrase in response for phrase in generic_phrases) >= 2:
            response_issues.append("❌ 너무 일반적인 응답")
        
        # Check if addresses specific issue mentioned in review
        review_lower = original.lower()
        if 'withdrawal' in review_lower and 'withdrawal' not in response.lower():
            response_issues.append("❌ 출금 문제 구체적 언급 부족")
        if 'support' in review_lower and ('support' not in response.lower() and 'Help Center' not in response):
            response_issues.append("❌ 지원 문제 구체적 언급 부족")
        
        if response_issues:
            print(f"⚠️ Issues: {', '.join(response_issues)}")
            issues.append({
                'id': review_id,
                'issues': response_issues,
                'response_length': len(response)
            })
        else:
            print("✅ No major issues found")
    
    print(f"\n📈 English Summary:")
    print(f"   Total responses with issues: {len(issues)}")
    print(f"   Common issues:")
    all_issues = [issue for item in issues for issue in item['issues']]
    for issue_type in set(all_issues):
        count = all_issues.count(issue_type)
        print(f"     {issue_type}: {count}")

def suggest_improvements():
    """Suggest improvements for Japanese and English prompts"""
    print("\n\n=== 💡 Improvement Suggestions ===")
    
    print("🇯🇵 Japanese Improvements:")
    print("   1. 응답 길이 단축 (현재 400자+ → 250자 이하)")
    print("   2. '申し上げます' 사용 빈도 줄이기 (최대 1-2회)")
    print("   3. 격식적 표현 간소화")
    print("   4. 더 자연스럽고 간결한 경어 사용")
    
    print("\n🇺🇸 English Improvements:")
    print("   1. 더 구체적이고 개인화된 응답")
    print("   2. 일반적인 문구 사용 줄이기")
    print("   3. 리뷰의 구체적 문제점 더 정확하게 언급")
    print("   4. FAQ/Help Center 안내 일관성 있게 포함")

if __name__ == "__main__":
    print("🔍 Analyzing Japanese and English responses...")
    analyze_japanese_responses()
    analyze_english_responses()
    suggest_improvements()
    print("\n✅ Analysis completed!")