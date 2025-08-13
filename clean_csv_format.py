#!/usr/bin/env python3
"""
CSV 파일의 줄바꿈 정리 스크립트
"""

import csv
import re

def clean_csv_format():
    """CSV 파일에서 텍스트 내 줄바꿈을 공백으로 변환하여 한 행으로 정리"""
    
    input_file = '/Users/gravitylabs/Desktop/review/processed_reviews_with_responses.csv'
    output_file = '/Users/gravitylabs/Desktop/review/processed_reviews_cleaned.csv'
    
    print("🧹 CSV 파일 줄바꿈 정리 시작...")
    
    cleaned_rows = []
    
    # 파일 읽기 (UTF-8 BOM 처리)
    with open(input_file, 'r', encoding='utf-8-sig', newline='') as file:
        reader = csv.reader(file)
        
        for row_num, row in enumerate(reader, 1):
            if not row:  # 빈 행 건너뛰기
                continue
                
            cleaned_row = []
            
            for cell in row:
                # 줄바꿈 문자들을 공백으로 변환
                cleaned_cell = re.sub(r'[\r\n]+', ' ', cell)
                # 연속된 공백을 하나로 정리
                cleaned_cell = re.sub(r'\s+', ' ', cleaned_cell)
                # 앞뒤 공백 제거
                cleaned_cell = cleaned_cell.strip()
                
                cleaned_row.append(cleaned_cell)
            
            cleaned_rows.append(cleaned_row)
            
            if row_num % 10 == 0:
                print(f"   처리 완료: {row_num}행")
    
    # 정리된 데이터를 새 파일에 저장
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file, delimiter='|')
        
        for row in cleaned_rows:
            writer.writerow(row)
    
    print(f"✅ CSV 정리 완료!")
    print(f"📁 입력 파일: {input_file}")
    print(f"📁 출력 파일: {output_file}")
    print(f"📊 총 {len(cleaned_rows)}행 처리")
    
    # 몇 개 샘플 확인
    print("\n📋 정리된 샘플 확인:")
    for i, row in enumerate(cleaned_rows[:3], 1):
        if len(row) >= 6:  # 최소 6개 컬럼이 있는 경우
            print(f"\n{i}. ID: {row[0]}")
            print(f"   리뷰: {row[1][:50]}...")
            print(f"   응답: {row[5][:80]}...")

if __name__ == "__main__":
    clean_csv_format()