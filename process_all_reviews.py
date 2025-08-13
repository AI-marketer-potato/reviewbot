#!/usr/bin/env python3
"""
Process all review cases (Korean and US) using the improved prompt system
"""

import pandas as pd
import csv
from datetime import datetime
from services.response_generator import ResponseGenerator
from services.vector_store import VectorStoreService
from models.review import Review

def process_all_reviews():
    """Process all Korean and US review cases"""
    
    # Initialize services
    vector_store_service = VectorStoreService()
    response_generator = ResponseGenerator(vector_store_service)
    
    results = []
    
    # Process Korean reviews
    print("Processing Korean reviews...")
    kr_df = pd.read_csv('/Users/gravitylabs/Desktop/review/KR_User_Review_Cases (1).csv')
    
    for idx, row in kr_df.iterrows():
        print(f"Processing Korean review {idx + 1}/4...")
        
        # Create Review object
        review = Review(
            id=f"kr_{idx + 1:03d}",
            content=row['예시 리뷰'],
            author="",  # Not provided in dataset
            rating=3,   # Default rating
            country="KOR",
            platform="google_play",  # Default platform
            created_at=datetime.now()
        )
        
        # Generate response
        response = response_generator.generate_response(review, row['케이스'])
        
        # Add to results
        results.append({
            'ID': review.id,
            '원본_리뷰': review.content,
            '언어': 'KOR',
            '플랫폼': 'google_play',
            '평점': review.rating,
            '생성된_응답': response.response_text,
            '생성_시간': response.generated_at.strftime('%Y-%m-%d %H:%M:%S'),
            '사용된_소스_수': len(response.used_sources),
            '카테고리': row['케이스']
        })
    
    # Process US reviews
    print("Processing US reviews...")
    us_df = pd.read_csv('/Users/gravitylabs/Desktop/review/US_User_Review_Cases (1).csv')
    
    for idx, row in us_df.iterrows():
        print(f"Processing US review {idx + 1}/4...")
        
        # Create Review object
        review = Review(
            id=f"us_{idx + 1:03d}",
            content=row['Example Review'],
            author="",  # Not provided in dataset
            rating=3,   # Default rating
            country="USA",
            platform="google_play",  # Default platform
            created_at=datetime.now()
        )
        
        # Generate response
        response = response_generator.generate_response(review, row['Case'])
        
        # Add to results
        results.append({
            'ID': review.id,
            '원본_리뷰': review.content,
            '언어': 'USA',
            '플랫폼': 'google_play',
            '평점': review.rating,
            '생성된_응답': response.response_text,
            '생성_시간': response.generated_at.strftime('%Y-%m-%d %H:%M:%S'),
            '사용된_소스_수': len(response.used_sources),
            '카테고리': row['Case']
        })
    
    return results

def save_results_with_pipe_delimiter(results, filename):
    """Save results to CSV with pipe delimiter"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ID', '원본_리뷰', '언어', '플랫폼', '평점', '생성된_응답', '생성_시간', '사용된_소스_수', '카테고리']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)

if __name__ == "__main__":
    print("Starting review processing...")
    
    # Process all reviews
    all_results = process_all_reviews()
    
    # Save results with pipe delimiter
    output_filename = f'/Users/gravitylabs/Desktop/review/all_processed_reviews_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    save_results_with_pipe_delimiter(all_results, output_filename)
    
    print(f"\nProcessing completed!")
    print(f"Total reviews processed: {len(all_results)}")
    print(f"Results saved to: {output_filename}")
    
    # Show sample of Korean results
    print("\n=== Sample Korean Results ===")
    for result in all_results[:2]:
        if result['언어'] == 'KOR':
            print(f"ID: {result['ID']}")
            print(f"Original: {result['원본_리뷰'][:50]}...")
            print(f"Response: {result['생성된_응답'][:100]}...")
            print(f"Category: {result['카테고리']}")
            print("-" * 50)