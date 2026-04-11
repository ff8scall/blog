import os

def fix_docs():
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    new_content = content.replace('blog.lego-sia.com', 'news.lego-sia.com').replace('블로그', '뉴스')
                    if content != new_content:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated: {path}")
                except Exception as e:
                    print(f"Error processing {path}: {e}")

if __name__ == '__main__':
    fix_docs()
