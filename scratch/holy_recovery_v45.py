import os
import re
import logging

# [V4.5] Miraculous Language Restoration Engine
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LegoSia.Restoration")

def fix_garble(text):
    """
    Reverse Engineering Double Encoding Disaster.
    '우읊드소' -> '잠금 해제'
    UTF-8 bytes interpreted as CP949 and saved as UTF-8.
    """
    try:
        # Step 1: Recover the original raw bytes that were wrongly interpreted as CP949
        raw_bytes = text.encode('cp949', errors='ignore')
        # Step 2: Decode them correctly as UTF-8
        return raw_bytes.decode('utf-8', errors='ignore')
    except:
        return text

def restore_all_articles():
    base_path = "content/ko/posts/2026/04"
    if not os.path.exists(base_path):
        logger.error("Path not found.")
        return

    files = [f for f in os.listdir(base_path) if f.endswith('.md')]
    logger.info(f"Found {len(files)} files to restore.")

    for filename in files:
        file_path = os.path.join(base_path, filename)
        try:
            with open(file_path, "r", encoding="utf-8", errors='ignore') as f:
                content = f.read()

            # Fix title, description and body
            restored_content = fix_garble(content)
            
            # Ensure proper taxonomy (Forced Intelligence for visibility)
            restored_content = re.sub(r'clusters:.*', 'clusters: ["intelligence"]', restored_content)
            restored_content = re.sub(r'categories:.*', 'categories: ["llm-tech"]', restored_content)

            with open(file_path, "w", encoding="utf-8-sig") as f:
                f.write(restored_content)
            
            logger.info(f"Successfully Restored: {filename}")
        except Exception as e:
            logger.error(f"Failed to restore {filename}: {e}")

if __name__ == "__main__":
    restore_all_articles()
