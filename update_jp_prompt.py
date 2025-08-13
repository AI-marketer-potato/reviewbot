#!/usr/bin/env python3
"""
Update Japanese prompt to be more natural and concise
"""

import re

def update_japanese_prompt():
    """Update the Japanese prompt in response_generator.py"""
    
    # Read the current file
    with open('/Users/gravitylabs/Desktop/review/services/response_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the new Japanese prompt (clean Japanese only)
    new_jp_prompt = '''あなたはMoneyWalkの顧客サポート担当者として、丁寧で自然なレビュー返信を作成します。

**基本応答構造:**
1. 簡潔な謝罪または感謝
2. 具体的な問題への言及
3. 解決策または改善取り組みの説明
4. アプリ内問い合わせ案内
5. 自然な締めくくり

**自然な表現指針:**
- **「申し上げます」使用制限**: 1回の応答につき最大1回まで
- **簡潔性重視**: 250文字以内で要点をまとめる
- **過度な敬語禁止**: 自然で親しみやすい敬語を使用
- **反復表現禁止**: 同じフレーズを複数回使用しない

**表現の多様化:**
- 開始: 「この度は」「ご利用ありがとうございます」「レビューをお寄せいただき」
- 謝罪: 「申し訳ございません」「ご不便をおかけしています」（過度な格式を避ける）
- 問題言及: 「〜の件について」「〜に関して」「〜の問題は」
- 解決策: 「改善に取り組んでいます」「確認いたします」「対応させていただきます」
- 締めくくり: 「ありがとうございます」「よろしくお願いします」

**CS対応指針:**
- レビュー内容の核心キーワードを必ず含める
- 具体的な解決策や改善状況を提示
- 「アプリ内1:1お問い合わせ」を通じた追加サポート案内
- 過度な格式よりも誠実な対応を重視

**問題別対応:**
- **広告関連**: 改善努力と具体的解決策の提示
- **性能問題**: キャッシュクリアなど実用的な対処案内
- **ポイント問題**: 確認手順と問い合わせ方法の案内

**トーン調整:**
- **肯定レビュー**: 感謝表現と継続的改善意志
- **問題レビュー**: 簡潔な謝罪と解決中心の対応
- **中立レビュー**: 情報提供と親しみやすい案内

**作成指針:**
1. 250文字以内で簡潔に作成
2. 「申し上げます」は最大1回のみ使用
3. レビューの具体的問題点を正確に言及
4. 実用的で役立つ情報を提供
5. 自然で親しみやすい日本語を使用

参考知識ベース:
{knowledge_context}'''
    
    # Find the start and end of the Japanese prompt section
    jp_start = content.find('self.jp_prompt = ChatPromptTemplate.from_messages([')
    if jp_start == -1:
        print("❌ Japanese prompt section not found")
        return
    
    # Find the end of the Japanese prompt section
    jp_system_start = content.find('("system", """', jp_start)
    jp_system_end = content.find('"""),', jp_system_start)
    
    if jp_system_start == -1 or jp_system_end == -1:
        print("❌ Could not locate Japanese system prompt boundaries")
        return
    
    # Replace the Japanese system prompt content
    before = content[:jp_system_start + len('("system", """')]
    after = content[jp_system_end:]
    
    new_content = before + new_jp_prompt + after
    
    # Write the updated content back
    with open('/Users/gravitylabs/Desktop/review/services/response_generator.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Japanese prompt updated successfully")
    print("📊 New prompt length:", len(new_jp_prompt), "characters")

if __name__ == "__main__":
    update_japanese_prompt()