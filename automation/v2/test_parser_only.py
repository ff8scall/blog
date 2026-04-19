import sys
import os
import json
import glob
from pathlib import Path

# 프로젝트 루트 경로 추가
root_path = str(Path(__file__).parent.parent.parent)
sys.path.append(root_path)

from automation.nlm_parser import parse_structured_articles

def test_all_reports():
    report_dir = "scratch/premium_reports"
    reports = glob.glob(os.path.join(report_dir, "*.md"))
    
    print(f"\n--- [Phase 1: Parsing Validation] ---")
    results = {}
    
    for report_path in reports:
        filename = os.path.basename(report_path)
        print(f"[*] Testing {filename}...")
        
        with open(report_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
            
        articles = parse_structured_articles(raw_text)
        
        print(f"  - Articles Found: {len(articles)}")
        for i, a in enumerate(articles):
            id_val = a.get('id', 'N/A')
            title = a.get('kor_title', a.get('eng_title', 'Untitled'))
            has_content = "Yes" if a.get('kor_content') else "No"
            has_insight = "Yes" if a.get('kor_insight') else "No"
            has_orig_img = "Yes" if a.get('original_image') else "No"
            
            print(f"    [{i+1}] ID: {id_val} | Title: {title[:40]}...")
            print(f"        > KOR_CONTENT: {has_content} | KOR_INSIGHT: {has_insight} | ORIG_IMAGE: {has_orig_img}")
            
        results[filename] = articles

    # 상세 결과 저장
    with open("scratch/parsing_test_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    print(f"\n[DONE] Detailed parsing results saved to 'scratch/parsing_test_result.json'")

if __name__ == "__main__":
    test_all_reports()
