import os
import re

def resurrect():
    base_dir = r"content/ko/posts/2026/04"
    if not os.path.exists(base_dir):
        print("Directory not found.")
        return

    files = [f for f in os.listdir(base_dir) if f.endswith('.md')]
    print(f"Working on {len(files)} articles...")

    for f in files:
        path = os.path.join(base_dir, f)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()

            # If frontmatter already exists, skip
            if content.startswith('---'):
                continue

            # Generate Title from filename
            clean_name = f.replace('.md', '').replace('-', ' ')
            # Try to grab the first line if it looks like a title
            first_line = content.split('\n')[0].strip('# ')
            title = first_line if len(first_line) > 5 else clean_name.title()

            # Build Standard Hugo Frontmatter
            frontmatter = f"""---
title: "{title}"
date: "2026-04-13T10:00:00+09:00"
clusters: ["intelligence"]
categories: ["llm-tech"]
tags: ["recovered", "ai-news"]
featured: false
---

"""
            # Combine
            final_content = frontmatter + content
            
            with open(path, 'w', encoding='utf-8-sig') as file:
                file.write(final_content)
                
            print(f"Resurrected: {f}")
        except Exception as e:
            print(f"Error on {f}: {e}")

if __name__ == "__main__":
    resurrect()
