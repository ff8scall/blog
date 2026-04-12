import os
import re

def clean_markdown_files(root_dir):
    print(f"[*] Scanning {root_dir}...")
    count = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    
                    if not lines: continue
                    
                    modified = False
                    new_lines = []
                    in_frontmatter = False
                    frontmatter_count = 0
                    
                    for line in lines:
                        if line.strip() == "---":
                            in_frontmatter = not in_frontmatter
                            frontmatter_count += 1
                            new_lines.append(line)
                            continue
                        
                        if in_frontmatter:
                            new_lines.append(line)
                        else:
                            # 프론트매터 외부에서 첫 번째로 나타나는 # 헤더 제거
                            # 보통 AI가 생성한 제목이 맨 위에 옴
                            if not modified and line.strip().startswith("# "):
                                print(f" [CLEAN] Removed header from {file}")
                                modified = True
                                continue
                            new_lines.append(line)
                    
                    if modified:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.writelines(new_lines)
                        count += 1
                except Exception as e:
                    print(f" [!] Error processing {file}: {e}")
    print(f"[*] Done. Cleaned {count} files.")

if __name__ == "__main__":
    base_path = os.getcwd()
    clean_markdown_files(os.path.join(base_path, "content"))
