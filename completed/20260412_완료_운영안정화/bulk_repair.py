import os
import re

# [V3.0.9] Bulk Repair Script for LEGO-SIA News Engine
# Goal: Fix invalid image fallbacks and cleanse Korean tags from EN posts.

FALLBACK_MAP = {
    "llm-tech": "ai-tech", "ai-policy": "ai-tech",
    "ai-agent": "ai-agents", "future-sw": "ai-agents",
    "semi-hbm": "hardware", "hpc-infra": "hardware", "robotics": "hardware",
    "monetization": "tech-biz", "startups-vc": "tech-biz", "market-trend": "tech-biz",
    "game-tech": "gaming", "spatial-tech": "gaming"
}

TAG_MAP = {
    "기사": "Article", "뉴스": "News", "분석": "Analysis", "기술": "Technology",
    "콘텐츠전략": "Content Strategy", "브랜딩": "Branding", "커뮤니티비즈니스": "Community Business",
    "시장": "Market", "전망": "Outlook", "데이터": "Data", "전략": "Strategy"
}

def repair_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Fix Image Paths
    for old, new in FALLBACK_MAP.items():
        bad_path = f"images/fallbacks/{old}.jpg"
        good_path = f"images/fallbacks/{new}.jpg"
        content = content.replace(bad_path, good_path)

    # 2. Fix Tags if English Post
    if 'content\\en\\' in filepath or 'content/en/' in filepath:
        # Simple Korean char detection
        if re.search(r'[ㄱ-ㅎㅏ-ㅣ가-힣]', content):
            # Try to map common tags
            for kor, eng in TAG_MAP.items():
                content = content.replace(f'"{kor}"', f'"{eng}"')
                content = content.replace(f"'{kor}'", f"'{eng}'")
            
            # Remove remaining Korean tags (brute force)
            def remove_kor(match):
                tags_str = match.group(1)
                tags = re.findall(r'"([^"]+)"|\'([^\']+)\'', tags_str)
                clean_tags = []
                for t_tuple in tags:
                    t = t_tuple[0] or t_tuple[1]
                    if not re.search(r'[ㄱ-ㅎㅏ-ㅣ가-힣]', t):
                        clean_tags.append(f'"{t}"')
                return f'tags: [{", ".join(clean_tags)}]'

            content = re.sub(r'tags: \[(.*?)\]', remove_kor, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    base_dir = r"c:\AI\Antigravity\News\content"
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".md"):
                repair_file(os.path.join(root, file))
    print("[SUCCESS] Bulk repair completed.")

if __name__ == "__main__":
    main()
