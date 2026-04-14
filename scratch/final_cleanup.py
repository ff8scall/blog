import os
import glob
import shutil
import re

def final_cleanup():
    # 1. 모든 가이드/뉴스 파일의 images -> image 치환
    paths = glob.glob("content/**/*.md", recursive=True)
    for path in paths:
        with open(path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # images: ["path"] -> image: "path"
        new_content = re.sub(r'images:\s*\["(.*?)"\]', r'image: "\1"', content)
        
        # 2. 13일 폴더에 있는 14일 기사 탐지 및 이동 (가이드 파일 등)
        filename = os.path.basename(path)
        if "/04/13/" in path.replace("\\", "/") and filename.startswith("14-"):
            new_path = path.replace("/04/13/", "/04/14/").replace("\\", "/")
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            
            # 본문 내부 이미지 경로도 13 -> 14로 수정
            new_content = new_content.replace("/images/posts/2026/04/13/", "/images/posts/2026/04/14/")
            
            with open(new_path, 'w', encoding='utf-8-sig') as f:
                f.write(new_content)
            os.remove(path)
            print(f"Relocated & Patched: {filename}")
        else:
            if new_content != content:
                with open(path, 'w', encoding='utf-8-sig') as f:
                    f.write(new_content)
                print(f"Fixed Image Field: {filename}")

if __name__ == "__main__":
    final_cleanup()
