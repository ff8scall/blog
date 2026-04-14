import os
import glob

# 가이드 파일들을 찾아 Hugo가 출력물(type: "posts")로 인식하게 수정
def patch_guides():
    paths = glob.glob("content/**/guides/2026/04/*.md", recursive=True)
    for path in paths:
        with open(path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        if 'type: "posts"' not in content:
            # description 바로 뒤에 type 주입
            patched = content.replace('description: "', 'type: "posts"\ndescription: "')
            with open(path, 'w', encoding='utf-8-sig') as f:
                f.write(patched)
            print(f"Patched: {path}")

if __name__ == "__main__":
    patch_guides()
