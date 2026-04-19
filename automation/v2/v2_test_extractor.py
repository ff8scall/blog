import trafilatura
from newspaper import Article
import json
import sys

# Windows 콘솔 유니코드 출력 대응
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def test_extraction(url):
    print(f"Testing URL: {url}\n")
    
    # 1. Newspaper4k for Metadata
    print("--- Newspaper4k Metadata ---")
    article = Article(url)
    article.download()
    article.parse()
    
    meta = {
        "title": article.title,
        "authors": article.authors,
        "publish_date": str(article.publish_date),
        "top_image": article.top_image,
        "movies": article.movies,
        "keywords": article.keywords,
        "summary": article.summary[:200] + "..." if article.summary else ""
    }
    print(json.dumps(meta, indent=2, ensure_ascii=False))
    
    # 2. Trafilatura for Full Body (Markdown)
    print("\n--- Trafilatura Body (Markdown) ---")
    downloaded = trafilatura.fetch_url(url)
    content = trafilatura.extract(downloaded, output_format='markdown', include_links=True)
    
    if content:
        print(content[:1000] + "\n...")
        print(f"\n[Total Length: {len(content)} chars]")
    else:
        print("Failed to extract content with Trafilatura")

if __name__ == "__main__":
    test_url = "https://www.tomshardware.com/pc-components/cpus/amd-to-resurrect-ryzen-7-5800x3d-am4-with-10th-anniversary-edition-leaker-claims-return-of-legendary-cpu-a-sign-of-bleak-pc-building-landscape"
    test_extraction(test_url)
