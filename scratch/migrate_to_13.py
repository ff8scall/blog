import os
import glob
import shutil
import re

def migrate_to_13th():
    # 1. 대상 언어 및 폴더 정의
    langs = ['ko', 'en']
    content_types = ['posts', 'guides']
    
    # 2. 어제 날짜(13일) 폴더 생성
    for lang in langs:
        for ctype in content_types:
            target_dir = f"content/{lang}/{ctype}/2026/04/13"
            os.makedirs(target_dir, exist_ok=True)
            
            # 기존 04/ 폴더에 있던 .md 파일들 찾기 (14 서브폴더 제외)
            files = glob.glob(f"content/{lang}/{ctype}/2026/04/*.md")
            for f in files:
                filename = os.path.basename(f)
                dest = os.path.join(target_dir, filename)
                
                # 내부 이미지 경로 업데이트 및 파일 이동
                with open(f, 'r', encoding='utf-8-sig') as file:
                    content = file.read()
                
                # 이미지 경로를 04/ -> 04/13/ 으로 변경
                updated_content = content.replace('/images/posts/2026/04/', '/images/posts/2026/04/13/')
                
                with open(dest, 'w', encoding='utf-8-sig') as file:
                    file.write(updated_content)
                os.remove(f)
                print(f"Moved & Patched Content: {filename}")

    # 3. 이미지 파일 이동
    img_target_dir = "static/images/posts/2026/04/13"
    os.makedirs(img_target_dir, exist_ok=True)
    images = glob.glob("static/images/posts/2026/04/*.jpg")
    for img in images:
        filename = os.path.basename(img)
        shutil.move(img, os.path.join(img_target_dir, filename))
        print(f"Moved Image: {filename}")

if __name__ == "__main__":
    migrate_to_13th()
