import json
import re
import sys
import os

sys.path.append(os.path.join(os.getcwd(), "automation"))

from news_harvester import NewsHarvester
from news_main import group_articles_by_topic

def debug_grouping():
    print("=== [Grouping Algorithm Debug Mode: Threshold Comparison] ===")
    harvester = NewsHarvester()
    raw_news, _ = harvester.fetch_all(limit_per_cat=15)
    
    for th in [0.15, 0.10, 0.08]:
        print(f"\n--- Testing Threshold: {th} ---")
        groups = group_articles_by_topic(raw_news, threshold=th)
        merged = [g for g in groups if len(g) > 1]
        print(f"[*] Found {len(merged)} merged topics out of {len(groups)} total groups.")
        for idx, g in enumerate(merged[:3]): # Show first 3 for brevity
            print(f" Group {idx+1}:")
            for a in g:
                print(f"  - {a['title'][:60]}")

if __name__ == "__main__":
    debug_grouping()
